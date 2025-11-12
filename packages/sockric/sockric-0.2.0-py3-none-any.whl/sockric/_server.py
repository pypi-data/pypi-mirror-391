from sockric._packet import encode, decode, decode_from_stream
from sockric._events import EventManager, EventDefaults
from sockric._utils import serialize, deserialize
from sockric._transport import TCP
import socket, threading, time, json
import loggerric as lr

class Server:
    def __init__(self, host_ip:str, port:int, password:str=None):
        # Expand parameters scopes
        self.__host_ip = host_ip
        self.__port = port
        self.password = password
    
        self.__is_running = False
        self.__client_id_counter = 0
        self.__clients:dict[int, dict] = {}
        self.__events = EventManager()

        self.__tcp_socket:socket.socket = None
        self.__clients_lock:threading.Lock = None
        self.__recv_threads:list[threading.Thread] = None
        self.__accept_thread:threading.Thread = None

    def get_host(self) -> tuple[str, int]:
        return self.__host_ip, self.__port

    def start(self) -> None:
        # Check if the server is already running
        if self.__is_running:
            lr.Log.warn('Server is already running!')
            return
        
        lr.Log.debug(f'Starting server, hosting on: {self.__host_ip}:{self.__port}')

        # Set up the TCP socket as a server
        self.__tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__tcp_socket.bind((self.__host_ip, self.__port))
        self.__tcp_socket.listen(8) # Queue size

        self.__is_running = True
        self.__clients_lock = threading.Lock()
        self.__recv_threads:dict[int, threading.Thread] = {}

        # Set up the client accept thread
        self.__accept_thread = threading.Thread(target=self.__client_accept_loop, daemon=True)
        self.__accept_thread.start()

        lr.Log.info(f'Server successfully started, hosting on ({self.__host_ip}:{self.__port})')

    def stop(self) -> None:
        # Check if the server is running
        if not self.__is_running:
            lr.Log.warn('Server is not running!')
            return

        self.broadcast(EventDefaults.SERVER_STOPPED, '__server_stopped__')

        self.__is_running = False

        lr.Log.debug('Stopping server!')

    def send(self, packet_id:str, client_ids:int|list, data) -> bool:
        """Send packet to specific client(s). Returns True if sent to at least one client"""
        if isinstance(client_ids, int):
            client_ids = [client_ids]
        
        frame = encode(packet_id, data)
        sent_count = 0
        
        with self.__clients_lock:
            for client_id in list(client_ids):
                info = self.__clients.get(client_id)
                if not info:
                    continue
                
                try:
                    tcp:TCP = info.get('tcp')
                    if tcp and tcp.send(frame):
                        sent_count += 1
                except Exception as error:
                    lr.Log.debug(f'Failed to send to client {client_id}: {error}')
        
        return sent_count > 0

    def broadcast(self, packet_id:str, data, exclude_clients:list[int]=None) -> int:
        """Broadcast packet to all connected clients. Returns number of clients sent to"""
        if exclude_clients is None:
            exclude_clients = []
        
        frame = encode(packet_id, data)
        sent_count = 0
        
        with self.__clients_lock:
            for client_id in list(self.__clients.keys()):
                if client_id in exclude_clients:
                    continue

                info = self.__clients.get(client_id)
                if not info:
                    continue
                
                try:
                    tcp:TCP = info.get('tcp')
                    if tcp and tcp.send(frame):
                        sent_count += 1
                except Exception as error:
                    lr.Log.debug(f'Failed to broadcast to client {client_id}: {error}')
        
        return sent_count

    def on_packet(self, id:str):
        def decorator(func):
            self.__events.register(id, func)
            return func
        
        return decorator

    def __client_accept_loop(self) -> None:
        lr.Log.debug('Client accepting loop started!')

        while self.__is_running:
            try:
                connection, address = self.__tcp_socket.accept()
                lr.Log.debug(f'Incoming TCP connection from: {address}')

                tcp_wrapper = TCP(connection, address)

                response = None
                try:
                    response = decode_from_stream(tcp_wrapper)
                except Exception as error:
                    lr.Log.debug(f'Handshake decode error: {error}')
                    tcp_wrapper.close()
                    continue
                
                if response == b'':
                    lr.Log.debug('Connection closed by peer during handshake')
                    tcp_wrapper.close()
                    continue
                
                if response is None:
                    lr.Log.debug('Timeout during handshake')
                    tcp_wrapper.close()
                    continue
                
                # Parse handshake
                header, payload = response
                meta = deserialize(header.get('content_type'), payload)

                password = meta.get('password')
                if header.get('id') == '__handshake__':
                    if self.password and self.password != password:
                        lr.Log.info(f'Rejecting connection from {address}: incorrect password')

                        failure = encode('__auth_failed__', { 'reason': 'bad_password' })
                        tcp_wrapper.send(failure)
                        tcp_wrapper.close()
                        continue
                    else:
                        success = encode('__auth_success__', { 'reason': ('good_password' if self.password else 'no_password_set') })
                        if not tcp_wrapper.send(success):
                            lr.Log.debug(f'Failed to send auth success to {address}')
                            tcp_wrapper.close()
                            continue
                
                # Register client
                with self.__clients_lock:
                    client_id = self.__client_id_counter
                    self.__client_id_counter += 1
                    self.__clients[client_id] = { 'tcp': tcp_wrapper, 'address': address }
                
                lr.Log.info(f'Client {client_id} connected from: {address}')
                self.__events.trigger(EventDefaults.CLIENT_CONNECTED, { 'client_id': client_id, 'address': address })

                # Start receive thread for this client
                thread = threading.Thread(target=self.__tcp_client_loop, args=(client_id,), daemon=True)
                thread.start()
                self.__recv_threads[client_id] = thread
                
            except OSError as error:
                # Expected when server is stopping
                if self.__is_running:
                    lr.Log.debug(f'Accept loop error: {error}')
            except Exception as error:
                if self.__is_running:
                    lr.Log.error(f'Unexpected accept loop error: {error}')

    def __tcp_client_loop(self, client_id:int) -> None:
        """Receive loop for a specific client"""
        lr.Log.debug(f'TCP recv loop for client {client_id} started!')

        tcp_wrapper = None
        with self.__clients_lock:
            info = self.__clients.get(client_id)
            if not info:
                lr.Log.debug(f'Client {client_id} not found during loop start')
                return
            
            tcp_wrapper = info.get('tcp')
        
        # Start heartbeat sender thread for this client
        heartbeat_thread = threading.Thread(target=self.__heartbeat_sender, args=(client_id,), daemon=True)
        heartbeat_thread.start()
        
        while self.__is_running and self.is_connected(client_id):
            try:
                response = decode_from_stream(tcp_wrapper)
                
                if response is None:
                    continue

                if response == b'':
                    lr.Log.debug(f'Client {client_id} closed connection')
                    break

                header, payload = response
                packet_id = header.get('id')
                
                # Handle graceful disconnect packet
                if packet_id == '__disconnect__':
                    lr.Log.debug(f'Client {client_id} sent graceful disconnect')
                    break
                
                # Silently ignore heartbeat packets from client
                if packet_id == '__heartbeat__':
                    lr.Log.debug(f'Received heartbeat from client {client_id}')
                    continue

                # Process normal packet
                data = deserialize(header.get('content_type'), payload)
                self.__events.trigger(packet_id, { 'client_id': client_id, 'data': data, 'header': header })
                
            except Exception as error:
                lr.Log.debug(f'TCP recv loop error for client {client_id}: {error}')
                break
        
        self.__cleanup_client(client_id)
    
    def is_connected(self, client_id:int) -> bool:
        """Check if a client is still connected"""
        with self.__clients_lock:
            return client_id in self.__clients
    
    def __heartbeat_sender(self, client_id:int) -> None:
        """Send periodic heartbeat packets to a client"""
        lr.Log.debug(f'Heartbeat sender for client {client_id} started!')
        heartbeat_interval = 1.0  # Send heartbeat every 1 second
        last_heartbeat = time.time()
        
        while self.__is_running and self.is_connected(client_id):
            try:
                current_time = time.time()
                
                if current_time - last_heartbeat >= heartbeat_interval:
                    if not self.send('__heartbeat__', client_id, None):
                        lr.Log.debug(f'Failed to send heartbeat to client {client_id}')
                        break
                    last_heartbeat = current_time
                    lr.Log.debug(f'Sent heartbeat to client {client_id}')
                
                time.sleep(0.1)
            except Exception as error:
                lr.Log.debug(f'Heartbeat sender error for client {client_id}: {error}')
                break
        
        lr.Log.debug(f'Heartbeat sender for client {client_id} stopped!')
    
    
    def __cleanup_client(self, client_id:int) -> None:
        """Clean up client resources and trigger disconnect event"""
        with self.__clients_lock:
            client_info = self.__clients.pop(client_id, None)
            client_thread = self.__recv_threads.pop(client_id, None)
        
        if not client_info:
            return
        
        address = client_info.get('address')
        
        # Trigger disconnect event immediately
        self.__events.trigger(EventDefaults.CLIENT_DISCONNECTED, 
                            {'client_id': client_id, 'address': address})
        
        # Clean up TCP connection
        tcp_wrapper = client_info.get('tcp')
        if tcp_wrapper and not tcp_wrapper.closed:
            try:
                tcp_wrapper.close(graceful=True)
                lr.Log.debug(f'Closed TCP socket for client {client_id}')
            except Exception as error:
                lr.Log.debug(f'Error closing TCP socket for client {client_id}: {error}')
        
        # Clean up thread (only join if called from a different thread)
        if client_thread and threading.current_thread() != client_thread:
            try:
                client_thread.join(timeout=0.5)
            except Exception:
                pass
        
        lr.Log.info(f'Client {client_id} cleaned up')