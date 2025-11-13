#!/usr/bin/env python3
"""
Velora Server - Chat server with file sharing capabilities
"""

import socket
import threading
import json
import base64


def recv_exact(conn, n):
    """Receive exactly n bytes or return fewer if the connection closed."""
    data = b''
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return data
        data += chunk
    return data


class VeloraServer:
    """Velora chat server with file sharing"""
    
    def __init__(self, host='0.0.0.0', port=5003):
        self.host = host
        self.port = port
        self.clients = []
        self.lock = threading.Lock()
        self.running = False
        
    def start(self):
        """Start the server"""
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind((self.host, self.port))
            server.listen()
            print(f"[SERVER STARTED] File sharing server listening on {self.host}:{self.port}")
            print("[INFO] Supports text messages and file transfers")

            while self.running:
                try:
                    conn, addr = server.accept()
                    with self.lock:
                        self.clients.append(conn)
                    
                    thread = threading.Thread(target=self._handle_client, args=(conn, addr))
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"[ERROR] Server startup error: {e}")
        finally:
            server.close()
            print("[INFO] Server stopped")

    def stop(self):
        """Stop the server"""
        self.running = False
        # Close all client connections
        with self.lock:
            for client in self.clients[:]:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
    
    def _handle_client(self, conn, addr):
        """Handle individual client connections"""
        print(f"[NEW CONNECTION] {addr} connected.")
        
        try:
            while self.running:
                # Read an exact 10-byte header
                length_data = recv_exact(conn, 10)
                if len(length_data) != 10:
                    break
                    
                try:
                    header_text = length_data.decode('utf-8')
                except Exception:
                    break

                if not header_text.isdigit():
                    break
                    
                message_length = int(header_text)
                
                # Receive the full message
                msg_data = recv_exact(conn, message_length)
                if len(msg_data) != message_length:
                    break
                    
                try:
                    msg = msg_data.decode('utf-8')
                    
                    # Try to parse as JSON (file message)
                    try:
                        data = json.loads(msg)
                        if data.get('type') == 'file':
                            print(f"[FILE TRANSFER] {data['sender']} sending {data['filename']} ({data['size']} bytes)")
                            self._broadcast_file(data, conn)
                            continue
                    except json.JSONDecodeError:
                        pass
                    
                    # Regular text message (length-prefixed)
                    self._broadcast_message(msg, conn)
                    
                except Exception as e:
                    print(f"[ERROR] Failed to parse message: {e}")
                    break
                    
        except Exception as e:
            print(f"[ERROR] Error handling client {addr}: {e}")
        finally:
            # Clean up connection
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
            try:
                conn.close()
            except:
                pass
            print(f"[DISCONNECTED] {addr} left.")

    def _broadcast_message(self, message, sender_conn):
        """Broadcast text message to all clients except sender"""
        with self.lock:
            disconnected_clients = []
            for client in self.clients:
                if client != sender_conn:
                    try:
                        # Send as length-prefixed message for protocol consistency
                        msg_bytes = message.encode('utf-8')
                        msg_len = len(msg_bytes)
                        header = f"{msg_len:010d}".encode('utf-8')
                        client.sendall(header)
                        client.sendall(msg_bytes)
                    except:
                        disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                if client in self.clients:
                    self.clients.remove(client)
                try:
                    client.close()
                except:
                    pass

    def _broadcast_file(self, file_data, sender_conn):
        """Broadcast file to all clients except sender"""
        with self.lock:
            disconnected_clients = []
            file_message = json.dumps(file_data)
            message_length = len(file_message.encode('utf-8'))
            length_header = f"{message_length:010d}".encode('utf-8')
            
            for client in self.clients:
                if client != sender_conn:
                    try:
                        client.sendall(length_header)
                        client.sendall(file_message.encode('utf-8'))
                    except:
                        disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                if client in self.clients:
                    self.clients.remove(client)
                try:
                    client.close()
                except:
                    pass


# For backward compatibility and direct usage
def start(host='0.0.0.0', port=5003):
    """Start server with given host and port"""
    server = VeloraServer(host, port)
    server.start()


def main():
    """Main server entry point"""
    try:
        start()
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")


if __name__ == "__main__":
    main()