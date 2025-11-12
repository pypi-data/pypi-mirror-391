from sockric._packet import encode, decode, decode_from_stream
from sockric._events import EventManager, EventDefaults
from sockric._utils import serialize, deserialize
from sockric._transport import TCP
import socket, threading, time, json
import loggerric as lr

class Client:
    def __init__(self, host_ip:str, port:int):
        self.__host_ip = host_ip
        self.__port = port

        self.password:str = None
        self.is_connected = False
        self.__events = EventManager()
    
        self.__socket:socket.socket = None
        self.__tcp_wrapper:TCP = None
        self.__recv_thread:threading.Thread = None
        self.__heartbeat_thread:threading.Thread = None
        self.__heartbeat_timeout = 5.0  # seconds

    def get_host(self) -> tuple[str, int]:
        return self.__host_ip, self.__port

    def connect(self, password:str=None) -> bool:
        """Connect to server. Returns True if successful, False otherwise"""
        if self.is_connected:
            lr.Log.warn('Client is already connected!')
            return False
    
        self.password = password

        lr.Log.debug(f'Client connecting to {self.__host_ip}:{self.__port}')

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(2.0)

        try:
            self.__socket.connect((self.__host_ip, self.__port))
        except Exception as error:
            lr.Log.error(f'TCP connection failed: {error}')
            self.__socket.close()
            return False

        self.__tcp_wrapper = TCP(self.__socket, (self.__host_ip, self.__port))

        self.is_connected = True

        # Start receive thread
        self.__recv_thread = threading.Thread(target=self.__tcp_recv_loop, daemon=True)
        self.__recv_thread.start()

        lr.Log.info('Client successfully connected (awaiting handshake confirmation)')

        handshake = { 'password': self.password }
        frame = encode('__handshake__', handshake)
        if not self.__tcp_wrapper.send(frame):
            lr.Log.error('Handshake send failed')
            self.disconnect()
            return False
        
        # Start heartbeat thread
        self.__heartbeat_thread = threading.Thread(target=self.__heartbeat_loop, daemon=True)
        self.__heartbeat_thread.start()
        
        return True
    
    def send(self, packet_id:str, data) -> bool:
        """Send a packet. Returns True if successful, False if not connected"""
        if not self.is_connected:
            lr.Log.warn('Cannot send while client not connected!')
            return False
        
        frame = encode(packet_id, data)
        return self.__tcp_wrapper.send(frame)

    def disconnect(self) -> None:
        """Gracefully disconnect from the server"""
        if not self.is_connected:
            return

        lr.Log.info("Client disconnecting!")
        self.is_connected = False

        try:
            if self.__tcp_wrapper and not self.__tcp_wrapper.closed:
                # Send disconnect packet
                try:
                    frame = encode('__disconnect__', None)
                    self.__tcp_wrapper.send(frame)
                    time.sleep(0.05)
                except Exception:
                    pass
                self.__tcp_wrapper.close()
        except Exception as e:
            lr.Log.debug(f"Error closing TCP: {e}")

        # Stop heartbeat thread
        if self.__heartbeat_thread and self.__heartbeat_thread.is_alive():
            try:
                self.__heartbeat_thread.join(timeout=0.5)
            except Exception:
                pass

        # Wait for receive thread
        if self.__recv_thread and self.__recv_thread.is_alive():
            try:
                self.__recv_thread.join(timeout=1.0)
            except Exception:
                pass

    def on_packet(self, id:str):
        def decorator(func):
            self.__events.register(id, func)
            return func
        
        return decorator

    def __heartbeat_loop(self) -> None:
        """Periodically send heartbeat packets and check if server is responsive"""
        lr.Log.debug('Client heartbeat loop started!')
        heartbeat_interval = 2.0  # Send heartbeat every 2 seconds
        last_heartbeat_sent = time.time()
        
        while self.is_connected:
            try:
                current_time = time.time()
                
                # Send heartbeat packet every interval
                if current_time - last_heartbeat_sent >= heartbeat_interval:
                    try:
                        frame = encode('__heartbeat__', None)
                        if self.__tcp_wrapper.send(frame):
                            last_heartbeat_sent = current_time
                            lr.Log.debug('Sent heartbeat to server')
                    except Exception as e:
                        lr.Log.debug(f'Failed to send heartbeat: {e}')
                
                time.sleep(0.1)  # Check more frequently
                    
            except Exception as error:
                lr.Log.debug(f'Heartbeat loop error: {error}')
                break

    def __tcp_recv_loop(self) -> None:
        """Main receive loop for incoming packets from server"""
        lr.Log.debug('Client TCP recv loop started!')
        last_activity = time.time()
        
        while self.is_connected:
            try:
                response = decode_from_stream(self.__tcp_wrapper)
                
                if response is None:
                    # Check for timeout even when no data received
                    if time.time() - last_activity > self.__heartbeat_timeout:
                        lr.Log.warn('Server heartbeat timeout - no response from server')
                        self.is_connected = False
                        self.__events.trigger(EventDefaults.SERVER_DISCONNECTED.value, 
                                            {'reason': 'heartbeat_timeout'})
                        break
                    continue
                    
                if response == b'':
                    lr.Log.info('Server closed connection')
                    break

                last_activity = time.time()  # Reset heartbeat timer on data received
                header, payload = response

                # Check if this is the handshake response
                packet_id = header.get('id')
                if packet_id == '__auth_success__':
                    lr.Log.info('Handshake authentication passed!')
                elif packet_id == '__auth_failed__':
                    lr.Log.info('Handshake authentication failed!')
                    break
                elif packet_id == '__server_stopped__':
                    lr.Log.info('Server gracefully stopped')
                    break
                elif packet_id == '__heartbeat__':
                    # Silently ignore heartbeat responses from server
                    lr.Log.debug('Received heartbeat from server')
                    continue

                data = deserialize(header.get('content_type'), payload)
                self.__events.trigger(packet_id, { 'data': data, 'header': header })
                
            except Exception as error:
                lr.Log.debug(f'Client TCP recv loop error: {error}')
                break
        
        # Mark as disconnected and trigger event if not already done
        was_connected = self.is_connected
        self.is_connected = False
        
        if was_connected:
            self.__events.trigger(EventDefaults.SERVER_DISCONNECTED.value, {'reason': 'connection_lost'})
        
        # Clean up
        if self.__tcp_wrapper and not self.__tcp_wrapper.closed:
            try:
                self.__tcp_wrapper.close(graceful=True)
            except Exception:
                pass