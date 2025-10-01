# ===============================
# enhanced_secure_client.py - WITH COMMAND SENDING
# ===============================

import ssl
import socket
import time
import os
import json
import struct
import tempfile
from file_transfer_protocol import FileTransferProtocol, CommandProtocol

class EnhancedSecureClient:
    def __init__(self):
        self.protocol = FileTransferProtocol()
        self.command_port = 65433  # NEW: Command channel port
    
    def send_command(self, peer_ip, command_type, data=None):
        """NEW: Send a command to peer device"""
        print(f"[CLIENT] Sending command {command_type} to {peer_ip}:{self.command_port}")
        
        try:
            # Create command
            command_bytes = CommandProtocol.create_command(command_type, data)
            command_size = len(command_bytes)
            
            # Connect to peer's command port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((peer_ip, self.command_port))
            
            # Send command size
            sock.sendall(struct.pack('>I', command_size))
            
            # Send command
            sock.sendall(command_bytes)
            
            # Wait for acknowledgment
            ack = sock.recv(1024)
            if ack == b"COMMAND_ACK":
                print(f"[CLIENT] Command {command_type} acknowledged")
                sock.close()
                return True
            else:
                print(f"[CLIENT] Unexpected ack: {ack}")
                sock.close()
                return False
                
        except Exception as e:
            print(f"[CLIENT] Failed to send command: {e}")
            return False
    
    def create_ssl_context(self):
        """Create improved SSL context"""
        try:
            # Use more compatible SSL settings
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Enable more cipher suites for better compatibility
            try:
                context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
            except:
                pass  # Use defaults if setting ciphers fails
            
            # Set minimum TLS version if available
            try:
                context.minimum_version = ssl.TLSVersion.TLSv1_2
            except:
                pass  # Older Python versions might not support this
            
            return context
        except Exception as e:
            print(f"[CLIENT] SSL context creation error: {e}")
            # Fallback to default context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
    
    def send_file(self, peer_ip, port, file_path):
        """Send a file or folder to peer device - IMPROVED VERSION"""
        print(f"[CLIENT] Preparing to send: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"[CLIENT] Error: File/folder does not exist: {file_path}")
            return False
        
        # Step 1: Prepare file for transfer
        transfer_path = file_path
        metadata = self.protocol.create_file_metadata(file_path)
        
        # If it's a folder, compress it first
        if os.path.isdir(file_path):
            print(f"[CLIENT] Compressing folder: {file_path}")
            transfer_path = self.protocol.compress_folder(file_path)
            metadata['name'] = metadata['name'] + '.zip'
            metadata['size'] = os.path.getsize(transfer_path)
        
        print(f"[CLIENT] File metadata: {metadata}")
        
        # Step 2: Establish SSL connection with improved retry logic
        max_retries = 3
        for attempt in range(max_retries):
            sock = None
            ssock = None
            
            try:
                print(f"[CLIENT] Connecting to {peer_ip}:{port} (attempt {attempt + 1})")
                
                # Create improved SSL context
                context = self.create_ssl_context()
                
                # Create socket with longer timeout
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(15)  # Connection timeout
                sock.connect((peer_ip, port))
                print("[CLIENT] TCP connection established")
                
                # Wrap with SSL
                ssock = context.wrap_socket(sock, server_hostname=peer_ip)
                ssock.settimeout(30)  # Set timeout on SSL socket
                print("[CLIENT] SSL connection established")
                
                # Step 3: Send metadata
                success = self.send_metadata(ssock, metadata)
                if not success:
                    raise Exception("Failed to send metadata")
                
                # Step 4: Send file data
                success = self.send_file_data(ssock, transfer_path)
                if not success:
                    raise Exception("Failed to send file data")
                
                # Step 5: Wait for acknowledgment with timeout
                success = self.wait_for_acknowledgment(ssock)
                if not success:
                    raise Exception("Failed to receive acknowledgment")
                
                print("[CLIENT] File transfer successful!")
                
                # Clean up temporary zip if created
                if transfer_path != file_path and transfer_path.endswith('.zip'):
                    try:
                        os.remove(transfer_path)
                    except:
                        pass
                
                return True
                
            except ssl.SSLError as e:
                print(f"[CLIENT] SSL error on attempt {attempt + 1}: {e}")
                if "EOF occurred in violation of protocol" in str(e):
                    print("[CLIENT] SSL protocol violation - server may have closed connection")
                elif "WRONG_VERSION_NUMBER" in str(e):
                    print("[CLIENT] SSL version mismatch - check server SSL configuration")
                    
            except socket.timeout:
                print(f"[CLIENT] Timeout on attempt {attempt + 1}")
                
            except ConnectionRefusedError:
                print(f"[CLIENT] Connection refused on attempt {attempt + 1} - is server running?")
                
            except Exception as e:
                print(f"[CLIENT] Attempt {attempt + 1} failed: {e}")
                
            finally:
                # Clean up connections
                if ssock:
                    try:
                        ssock.close()
                    except:
                        pass
                elif sock:
                    try:
                        sock.close()
                    except:
                        pass
            
            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                retry_delay = 2 + attempt  # Increasing delay
                print(f"[CLIENT] Waiting {retry_delay}s before retry...")
                time.sleep(retry_delay)
        
        print("[CLIENT] All connection attempts failed")
        
        # Clean up temporary zip if created
        if transfer_path != file_path and transfer_path.endswith('.zip'):
            try:
                os.remove(transfer_path)
            except:
                pass
        
        return False
    
    def send_metadata(self, ssock, metadata):
        """Send metadata to server"""
        try:
            metadata_json = json.dumps(metadata).encode('utf-8')
            metadata_size = len(metadata_json)
            
            # Send metadata size first
            ssock.sendall(struct.pack('>I', metadata_size))
            
            # Send metadata
            ssock.sendall(metadata_json)
            print("[CLIENT] Metadata sent successfully")
            return True
            
        except Exception as e:
            print(f"[CLIENT] Error sending metadata: {e}")
            return False
    
    def send_file_data(self, ssock, transfer_path):
        """Send file data with better error handling"""
        try:
            file_size = os.path.getsize(transfer_path)
            bytes_sent = 0
            
            print(f"[CLIENT] Sending file data ({file_size} bytes)")
            
            with open(transfer_path, 'rb') as f:
                while bytes_sent < file_size:
                    chunk = f.read(self.protocol.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    try:
                        ssock.sendall(chunk)
                        bytes_sent += len(chunk)
                        
                        # Progress update (every 10% or large chunks)
                        progress_interval = max(file_size // 10, self.protocol.CHUNK_SIZE * 10)
                        if bytes_sent % progress_interval == 0 or bytes_sent == file_size:
                            progress = (bytes_sent / file_size) * 100
                            print(f"[CLIENT] Progress: {progress:.1f}% ({bytes_sent}/{file_size} bytes)")
                    
                    except (ssl.SSLError, socket.error) as e:
                        print(f"[CLIENT] Error sending data at {bytes_sent}/{file_size}: {e}")
                        return False
            
            print(f"[CLIENT] File data sent successfully ({bytes_sent} bytes)")
            return bytes_sent == file_size
            
        except Exception as e:
            print(f"[CLIENT] Error in send_file_data: {e}")
            return False
    
    def wait_for_acknowledgment(self, ssock):
        """Wait for server acknowledgment"""
        try:
            ssock.settimeout(10)  # Shorter timeout for ack
            response = ssock.recv(1024)
            
            if response == b"TRANSFER_COMPLETE":
                print("[CLIENT] Server acknowledged transfer completion")
                return True
            else:
                print(f"[CLIENT] Unexpected response from server: {response}")
                return False
                
        except socket.timeout:
            print("[CLIENT] Timeout waiting for acknowledgment")
            return False
        except Exception as e:
            print(f"[CLIENT] Error waiting for acknowledgment: {e}")
            return False