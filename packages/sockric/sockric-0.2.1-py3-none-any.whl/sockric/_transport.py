import socket, threading, time, json
import loggerric as lr

class TCP:
    def __init__(self, connection:socket.socket, address:tuple[str, int]):
        # Expand parameters scopes
        self.connection = connection
        self.address = address

        self.connection.settimeout(1)

        self.closed = False
        self.__explicitly_closed = False

        # Thread locks
        self.__recv_lock = threading.Lock()
        self.__send_lock = threading.Lock()
    
    def send(self, raw_bytes:bytes) -> bool:
        """Send bytes, returns True if successful, False if connection is closed or error"""
        if self.closed:
            return False
        
        try:
            with self.__send_lock:
                if self.closed:
                    return False
                    
                total_sent = 0
                while total_sent < len(raw_bytes):
                    sent = self.connection.send(raw_bytes[total_sent:])

                    if sent == 0:
                        raise RuntimeError('Socket connection broken')

                    total_sent += sent
            return True
        except Exception as error:
            lr.Log.debug(f'TCP send error to {self.address}: {error}')
            self.close()
            return False

    def receive(self, num_bytes:int) -> bytes | None:
        """Receive bytes. Returns bytes data, None if timeout, or b'' if peer closed"""
        if self.closed:
            return b''
            
        data = bytearray()

        try:
            while len(data) < num_bytes:
                try:
                    chunk = self.connection.recv(num_bytes - len(data))
                except socket.timeout:
                    # No data yet — just return None to let higher-level loop continue
                    return None

                if chunk == b'':
                    # The peer gracefully closed the connection
                    self.close(graceful=True)
                    return b''

                data.extend(chunk)

            return bytes(data)
        
        except (ConnectionResetError, BrokenPipeError):
            # Expected when peer closes connection
            lr.Log.debug(f'TCP connection reset from {self.address}')
            self.close(graceful=True)
            return b''
        except OSError as error:
            # Expected on shutdown
            lr.Log.debug(f'TCP connection error from {self.address}: {error}')
            self.close(graceful=True)
            return b''
        except Exception as error:
            lr.Log.error(f'Unexpected TCP receive error from {self.address}: {error}')
            self.close()
            return b''

    def close(self, graceful:bool=False) -> None:
        """Close the connection. graceful=True means peer closed cleanly"""
        if self.closed:
            return
        
        self.closed = True
        if not graceful:
            self.__explicitly_closed = True

        try:
            # Only shutdown if not already closed by peer
            if not graceful:
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    # Already closed or in a state where shutdown isn't valid
                    pass
        except Exception:
            pass

        try:
            self.connection.close()
        except Exception:
            pass