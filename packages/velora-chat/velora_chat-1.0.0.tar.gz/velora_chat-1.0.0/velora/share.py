#!/usr/bin/env python3
"""
Velora Share - Quick file sharing functionality
"""

import os
import socket
import time
import subprocess
from .client import VeloraClient


def quick_share(file_path, server_address=None, sender_name="Anonymous"):
    """
    Quick share a file to a Velora server
    
    Args:
        file_path (str): Path to file to share
        server_address (str, optional): Server address (IP:port or ngrok URL). 
                                      If None, starts local server.
        sender_name (str): Name to display as sender
    """
    # Validate file
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    
    if file_size == 0:
        print(f"[ERROR] File is empty: {file_path}")
        return False
    
    if file_size > 1 * 1024 * 1024 * 1024:  # 1GB limit
        print(f"[ERROR] File too large ({file_size} bytes). Maximum size is 1GB.")
        return False
    
    print(f"=== Velora Quick Share ===")
    print(f"File: {filename} ({file_size} bytes)")
    print()
    
    # Determine connection details
    if server_address:
        # Connect to existing server
        try:
            if ":" in server_address:
                host, port_str = server_address.split(":", 1)
                port = int(port_str)
            else:
                host = server_address
                port = 5003
            
            print(f"[INFO] Connecting to server: {host}:{port}")
            
        except ValueError:
            print("[ERROR] Invalid server address format")
            return False
    else:
        # Start local server
        print("[INFO] Starting local server...")
        start_server_process()
        host = "127.0.0.1"
        port = 5003
        print("[INFO] Local server started. Others can connect to your IP on port 5003")
    
    # Clean sender name
    sender_name = sender_name.replace('\\', '').replace('\n', '').replace('\r', '')
    
    try:
        # Use VeloraClient for file sharing
        client = VeloraClient()
        if client.connect(host, port):
            client.name = sender_name
            print("[INFO] Connected!")
            
            # Send the file
            print(f"[INFO] Sending {filename}...")
            success = client.send_file(file_path)
            
            if success:
                print("[INFO] File sent successfully!")
                print("[INFO] Keeping connection open for 30 seconds...")
                time.sleep(30)
                return True
            else:
                return False
        else:
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to share file: {e}")
        return False
    finally:
        print("[INFO] Connection closed.")


def start_server_process():
    """Start server as subprocess"""
    import subprocess
    subprocess.Popen(
        ["python3", "-c", "from velora.server import start; start()"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
