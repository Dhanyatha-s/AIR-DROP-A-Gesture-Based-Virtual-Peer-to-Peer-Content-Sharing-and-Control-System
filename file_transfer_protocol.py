# ===============================
# file_transfer_protocol.py - WITH COMMAND PROTOCOL
# ===============================

import os
import json
import hashlib
import zipfile
import tempfile
from pathlib import Path
import struct

class FileTransferProtocol:
    CHUNK_SIZE = 8192
    
    @staticmethod
    def create_file_metadata(file_path):
        """Create metadata for a file transfer"""
        if os.path.isfile(file_path):
            return {
                'type': 'file',
                'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'path': file_path,
                'is_folder': False
            }
        elif os.path.isdir(file_path):
            return {
                'type': 'folder',
                'name': os.path.basename(file_path),
                'path': file_path,
                'is_folder': True
            }
    
    @staticmethod
    def compress_folder(folder_path, output_path=None):
        """Compress folder into zip for transfer"""
        if not output_path:
            output_path = tempfile.mktemp(suffix='.zip')
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arc_name)
        
        return output_path
    
    @staticmethod
    def calculate_file_hash(file_path):
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


class CommandProtocol:
    """Protocol for command messages between peers"""
    
    # Command types
    FILE_READY = "FILE_READY"
    REQUEST_TRANSFER = "REQUEST_TRANSFER"
    TRANSFER_ACCEPTED = "TRANSFER_ACCEPTED"
    TRANSFER_REJECTED = "TRANSFER_REJECTED"
    CANCEL_READY = "CANCEL_READY"
    
    @staticmethod
    def create_command(command_type, data=None):
        """Create a command message"""
        command = {
            'command': command_type,
            'timestamp': int(time.time() * 1000),
            'data': data or {}
        }
        return json.dumps(command).encode('utf-8')
    
    @staticmethod
    def parse_command(command_bytes):
        """Parse a command message"""
        try:
            command = json.loads(command_bytes.decode('utf-8'))
            return command
        except Exception as e:
            print(f"[PROTOCOL] Error parsing command: {e}")
            return None

import time