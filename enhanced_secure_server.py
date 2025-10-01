# ===============================
# enhanced_secure_server.py - WITH COMMAND LISTENER
# ===============================

import ssl
import socket
import threading
import time
import os
import json
import struct
import tempfile
import zipfile
from pathlib import Path
from file_transfer_protocol import FileTransferProtocol, CommandProtocol

class EnhancedSecureServer:
    def __init__(self, host="0.0.0.0", port=65432, save_directory=None):
        self.host = host
        self.port = port
        self.command_port = 65433  # NEW: Command channel port
        self.save_directory = save_directory or os.path.join(os.path.expanduser("~"), "AirDropReceivedFinalVersion")
        self.received_files = []
        self.transfer_status = {}
        self.command_handlers = {}  # NEW: Command callback handlers
        self.command_server_running = False
        
        # Ensure save directory exists
        os.makedirs(self.save_directory, exist_ok=True)
    
    def register_command_handler(self, command_type, handler):
        """Register a callback for a specific command type"""
        self.command_handlers[command_type] = handler
        print(f"[SERVER] Registered handler for command: {command_type}")
    
    def handle_file_transfer(self, conn, addr):
        """Handle incoming file transfer"""
        try:
            # Step 1: Receive metadata
            print(f"[SERVER] Receiving metadata from {addr}")
            metadata_size_bytes = conn.recv(4)
            metadata_size = struct.unpack('>I', metadata_size_bytes)[0]
            
            metadata_json = conn.recv(metadata_size).decode('utf-8')
            metadata = json.loads(metadata_json)
            
            print(f"[SERVER] File metadata: {metadata}")
            
            # Step 2: Prepare to receive file
            filename = metadata['name']
            expected_size = metadata.get('size', 0)
            is_folder = metadata.get('is_folder', False)
            
            # Create unique filename if exists
            save_path = os.path.join(self.save_directory, filename)
            counter = 1
            original_path = save_path
            while os.path.exists(save_path):
                name, ext = os.path.splitext(original_path)
                save_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # Step 3: Receive file data
            print(f"[SERVER] Receiving file data to: {save_path}")
            bytes_received = 0
            
            with open(save_path, 'wb') as f:
                while bytes_received < expected_size:
                    chunk_size = min(FileTransferProtocol.CHUNK_SIZE, expected_size - bytes_received)
                    chunk = conn.recv(chunk_size)
                    
                    if not chunk:
                        break
                        
                    f.write(chunk)
                    bytes_received += len(chunk)
                    
                    # Progress update
                    if bytes_received % (expected_size // 10 or 1) == 0 or bytes_received == expected_size:
                        progress = (bytes_received / expected_size) * 100
                        print(f"[SERVER] Progress: {progress:.1f}% ({bytes_received}/{expected_size} bytes)")
            
            # Step 4: Handle folder extraction
            if is_folder and save_path.endswith('.zip'):
                extract_path = save_path.replace('.zip', '')
                with zipfile.ZipFile(save_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                os.remove(save_path)  # Remove zip after extraction
                save_path = extract_path
                print(f"[SERVER] Folder extracted to: {save_path}")
            
            # Step 5: Send acknowledgment
            conn.send(b"TRANSFER_COMPLETE")
            
            print(f"[SERVER] File transfer complete: {save_path}")
            self.received_files.append(save_path)
            
        except Exception as e:
            print(f"[SERVER] Error handling file transfer: {e}")
            try:
                conn.send(b"TRANSFER_ERROR")
            except:
                pass
        finally:
            try:
                conn.close()
            except:
                pass
    
    def handle_command(self, conn, addr):
        """NEW: Handle incoming command messages"""
        try:
            # Receive command size
            size_bytes = conn.recv(4)
            if not size_bytes:
                return
            
            command_size = struct.unpack('>I', size_bytes)[0]
            
            # Receive command data
            command_bytes = conn.recv(command_size)
            command = CommandProtocol.parse_command(command_bytes)
            
            if not command:
                print(f"[SERVER] Failed to parse command from {addr}")
                return
            
            command_type = command.get('command')
            print(f"[SERVER] Received command: {command_type} from {addr}")
            
            # Call registered handler if exists
            if command_type in self.command_handlers:
                handler = self.command_handlers[command_type]
                handler(command, addr)
            else:
                print(f"[SERVER] No handler registered for command: {command_type}")
            
            # Send acknowledgment
            conn.send(b"COMMAND_ACK")
            
        except Exception as e:
            print(f"[SERVER] Error handling command: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
    
    def start_command_listener(self):
        """NEW: Start the command listener on port 65433"""
        print(f"[SERVER] Starting command listener on {self.host}:{self.command_port}")
        
        try:
            # Create socket for commands (no SSL needed for simple commands)
            command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            command_socket.bind((self.host, self.command_port))
            command_socket.listen(5)
            
            print(f"[SERVER] Command listener active on port {self.command_port}")
            self.command_server_running = True
            
            while self.command_server_running:
                try:
                    conn, addr = command_socket.accept()
                    print(f"[SERVER] Command connection from {addr}")
                    
                    # Handle command in separate thread
                    threading.Thread(
                        target=self.handle_command,
                        args=(conn, addr),
                        daemon=True
                    ).start()
                    
                except Exception as e:
                    if self.command_server_running:
                        print(f"[SERVER] Command listener error: {e}")
                    
        except Exception as e:
            print(f"[SERVER] Failed to start command listener: {e}")
        finally:
            try:
                command_socket.close()
            except:
                pass
    
    def start_server(self):
        """Start the enhanced secure server (file transfers)"""
        print(f"[SERVER] Starting file transfer server on {self.host}:{self.port}")
        print(f"[SERVER] Files will be saved to: {self.save_directory}")
        
        # Check certificates
        if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
            print("[SERVER] SSL certificates not found! Please run create_ssl_certs.py first")
            return
        
        try:
            # Create SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
            
            # Create and bind socket
            bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bindsocket.bind((self.host, self.port))
            bindsocket.listen(5)
            
            print(f"[SERVER] File transfer server listening on {self.host}:{self.port}")
            
            # Start command listener in separate thread
            command_thread = threading.Thread(target=self.start_command_listener, daemon=True)
            command_thread.start()
            
            while True:
                try:
                    print(f"[SERVER] Waiting for file transfer connections...")
                    newsocket, fromaddr = bindsocket.accept()
                    print(f"[SERVER] File transfer connection from {fromaddr}")
                    
                    # Wrap with SSL
                    conn = context.wrap_socket(newsocket, server_side=True)
                    print(f"[SERVER] SSL handshake successful with {fromaddr}")
                    
                    # Handle file transfer in separate thread
                    transfer_thread = threading.Thread(
                        target=self.handle_file_transfer,
                        args=(conn, fromaddr),
                        daemon=True
                    )
                    transfer_thread.start()
                    
                except ssl.SSLError as e:
                    print(f"[SERVER] SSL error: {e}")
                except Exception as e:
                    print(f"[SERVER] Error: {e}")
                    
        except Exception as e:
            print(f"[SERVER] Failed to start server: {e}")
        finally:
            self.command_server_running = False
            try:
                bindsocket.close()
            except:
                pass
    
    def get_received_files(self):
        """Get list of received files"""
        return self.received_files.copy()
    
    def clear_received_files(self):
        """Clear received files list"""
        self.received_files.clear()