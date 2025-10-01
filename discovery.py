# ===============================
# discovery.py - WITH GESTURE STATE BROADCASTING
# ===============================

import socket
import json
import time
import threading

BROADCAST_PORT = 50000
DISCOVERY_MSG = {
    "type": "peer_announcement",
    "name": "Unknown Device",
    "secret": "e94a3d7c4eaa9f62c341d27e5f72ab90",
    "gesture_state": None  # NEW: Add gesture state to discovery
}

# NEW: Shared state for gesture broadcasting
gesture_state_lock = threading.Lock()
current_gesture_state = {
    "file_ready": False,
    "filename": None
}

def update_gesture_state(file_ready=False, filename=None):
    """NEW: Update the gesture state that will be broadcast"""
    global current_gesture_state
    with gesture_state_lock:
        current_gesture_state["file_ready"] = file_ready
        current_gesture_state["filename"] = filename

def get_gesture_state():
    """NEW: Get current gesture state"""
    with gesture_state_lock:
        return current_gesture_state.copy()

def broadcast_presence(name):
    """Broadcast device presence on network with gesture state"""
    DISCOVERY_MSG["name"] = name
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print(f"[DISCOVERY] Starting broadcast for {name}")
        
        while True:
            try:
                # NEW: Include current gesture state in broadcast
                gesture_state = get_gesture_state()
                DISCOVERY_MSG["gesture_state"] = gesture_state
                
                msg = json.dumps(DISCOVERY_MSG).encode()
                sock.sendto(msg, ('<broadcast>', BROADCAST_PORT))
                
                # Show state if file is ready
                if gesture_state.get("file_ready"):
                    print(f"[{name}] Broadcasting with FILE_READY: {gesture_state.get('filename')}")
                else:
                    print(f"[{name}] Broadcasting presence...")
                
                time.sleep(3)
            except Exception as e:
                print(f"[DISCOVERY] Broadcast error: {e}")
                time.sleep(5)
                
    except Exception as e:
        print(f"[DISCOVERY] Failed to setup broadcast: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

def listen_for_peers(shared_secret, my_name, timeout=10, gesture_callback=None):
    """Listen for peer announcements with gesture state monitoring"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', BROADCAST_PORT))
        sock.settimeout(timeout)
        
        print(f"[DISCOVERY] Listening for peers (timeout: {timeout}s)")
        
        peer_ip = None
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                message = json.loads(data.decode())
                
                if (message.get("type") == "peer_announcement" and
                    message.get("secret") == shared_secret and
                    message.get("name") != my_name):
                    
                    peer_name = message.get('name')
                    current_peer_ip = addr[0]
                    
                    # NEW: Check for gesture state in discovery message
                    gesture_state = message.get("gesture_state", {})
                    if gesture_state.get("file_ready"):
                        filename = gesture_state.get("filename", "Unknown")
                        print(f"[{my_name}] 📢 Peer {peer_name} has FILE_READY: {filename}")
                        
                        # Call gesture callback if provided
                        if gesture_callback:
                            gesture_callback(peer_name, current_peer_ip, gesture_state)
                    
                    # Only return on first discovery if we don't have a peer yet
                    if peer_ip is None:
                        peer_ip = current_peer_ip
                        print(f"[{my_name}] ✅ Found peer: {peer_name} at {peer_ip}")
                        
                        # If no gesture monitoring needed, return immediately
                        if gesture_callback is None:
                            return peer_ip
                
            except socket.timeout:
                if peer_ip:
                    return peer_ip
                print(f"[{my_name}] Discovery timeout - no peers found")
                return None
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"[DISCOVERY] Listen error: {e}")
                continue
                
    except Exception as e:
        print(f"[DISCOVERY] Failed to setup listener: {e}")
        return None
    finally:
        try:
            sock.close()
        except:
            pass

def discover_peer_with_retry(shared_secret, my_name, max_attempts=5):
    """Discover peer with multiple attempts"""
    for attempt in range(max_attempts):
        print(f"[DISCOVERY] Attempt {attempt + 1}/{max_attempts}")
        
        peer_ip = listen_for_peers(shared_secret, my_name, timeout=8)
        if peer_ip:
            return peer_ip
        
        if attempt < max_attempts - 1:
            print(f"[DISCOVERY] Retrying in 3 seconds...")
            time.sleep(3)
    
    return None

def start_gesture_state_monitor(shared_secret, my_name, gesture_callback):
    """NEW: Continuously monitor peer gesture states via discovery"""
    def monitor_loop():
        print("[DISCOVERY] Starting continuous gesture state monitoring...")
        while True:
            try:
                listen_for_peers(
                    shared_secret, 
                    my_name, 
                    timeout=5,
                    gesture_callback=gesture_callback
                )
            except Exception as e:
                print(f"[DISCOVERY] Monitor error: {e}")
                time.sleep(5)
    
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    return monitor_thread