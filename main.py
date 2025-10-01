# ===============================
# main.py - WITH BIDIRECTIONAL COMMAND SYSTEM
# ===============================

import threading
import time
import sys
import os
from discovery import broadcast_presence, discover_peer_with_retry, start_gesture_state_monitor, update_gesture_state
from enhanced_secure_server import EnhancedSecureServer
from enhanced_gesture_system import EnhancedGestureSystem
from create_ssl_certs import create_ssl_certificates

def get_device_name():
    """Get device name dynamically or from command line"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    print("🚀 Enhanced Gesture AirDrop System")
    print("Select your device:")
    print("1. Laptop A")
    print("2. Laptop B") 
    print("3. Custom name")
    choice = input("Enter choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        return "Laptop A"
    elif choice == "2":
        return "Laptop B"
    elif choice == "3":
        custom_name = input("Enter device name: ").strip()
        return custom_name if custom_name else "Unknown Device"
    else:
        hostname = os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'Unknown'))
        return f"Device_{hostname}"

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import mediapipe
    except ImportError:
        missing_deps.append("mediapipe")
    
    try:
        import pyautogui
    except ImportError:
        missing_deps.append("pyautogui")
    
    try:
        import win32clipboard
    except ImportError:
        missing_deps.append("pywin32")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Install with:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("🚀 BIDIRECTIONAL GESTURE AIRDROP P2P SYSTEM")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please install missing dependencies first")
        return
    
    # Configuration
    SHARED_SECRET = "e94a3d7c4eaa9f62c341d27e5f72ab90"
    FILE_PORT = 65432
    COMMAND_PORT = 65433
    
    # Get device name
    MY_NAME = get_device_name()
    print(f"📱 Device: {MY_NAME}")
    
    # Create SSL certificates if needed
    print("🔐 Checking SSL certificates...")
    try:
        create_ssl_certificates()
    except Exception as e:
        print(f"❌ SSL certificate creation failed: {e}")
        return
    
    # Create server instance (handles both file transfers and commands)
    print("🖥️ Initializing secure server...")
    server = EnhancedSecureServer(port=FILE_PORT)
    
    # Start server in background (includes command listener on port 65433)
    print(f"🚀 Starting file server (port {FILE_PORT}) and command listener (port {COMMAND_PORT})...")
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    
    # Start broadcasting presence
    print("📡 Starting presence broadcast...")
    broadcast_thread = threading.Thread(
        target=broadcast_presence, 
        args=(MY_NAME,), 
        daemon=True
    )
    broadcast_thread.start()
    
    # Discover peer
    print(f"🔍 [{MY_NAME}] Discovering peers...")
    peer_ip = discover_peer_with_retry(SHARED_SECRET, MY_NAME, max_attempts=8)
    
    if not peer_ip:
        print(f"❌ [{MY_NAME}] Failed to discover peers")
        print("💡 Troubleshooting:")
        print("   1. Make sure both devices are on the same network")
        print("   2. Check firewall settings")
        print("   3. Ensure the other device is running")
        print("   4. Try different device names")
        
        choice = input("\n⚠️ Continue without peer discovery? (y/N): ").strip().lower()
        if choice != 'y':
            return
        
        peer_ip = input("🔧 Enter peer IP manually (or press Enter to skip): ").strip()
        if not peer_ip:
            print("❌ Cannot continue without peer IP")
            return
    
    print(f"✅ [{MY_NAME}] Peer found/configured: {peer_ip}")
    
    # NEW: Start continuous gesture state monitoring
    def handle_peer_gesture_state(peer_name, peer_ip_addr, gesture_state):
        """Callback for when peer's gesture state changes"""
        if gesture_state.get("file_ready"):
            filename = gesture_state.get("filename", "Unknown")
            print(f"\n🔔 NOTIFICATION: {peer_name} has file ready: {filename}")
            print("🖐️ Make PALM gesture to request transfer\n")
    
    print("📡 Starting continuous gesture state monitoring...")
    monitor_thread = start_gesture_state_monitor(
        SHARED_SECRET, 
        MY_NAME, 
        handle_peer_gesture_state
    )
    
    print(f"🎥 [{MY_NAME}] Starting gesture recognition system...")
    
    # Initialize and start gesture system
    try:
        gesture_system = EnhancedGestureSystem(peer_ip, server)
        
        print("\n" + "=" * 60)
        print("🎮 BIDIRECTIONAL GESTURE CONTROLS:")
        print("=" * 60)
        print("👆 Index finger up = Navigate cursor")
        print("🤏 Pinch (thumb + index) = Select file/folder")
        print("✊ Fist = Broadcast FILE_READY to peer")
        print("🖐 Open palm = Request from peer OR send to peer")
        print("=" * 60)
        print("\n📋 WORKFLOW:")
        print("1. Device A: Pinch to select → Fist to broadcast FILE_READY")
        print("2. Device B: Sees notification → Palm to request transfer")
        print("3. Device A: Receives request → Automatically sends file")
        print("=" * 60)
        print("❌ Press 'q' in camera window to quit")
        print("🔄 Press 'r' to reset selection")
        print("🗑️ Press 'c' to clear received files")
        print("=" * 60)
        
        # Start gesture system (blocking call)
        gesture_system.run()
        
    except KeyboardInterrupt:
        print(f"\n👋 [{MY_NAME}] System stopped by user")
    except ImportError as e:
        print(f"❌ [{MY_NAME}] Import error: {e}")
        print("💡 Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ [{MY_NAME}] Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🛑 [{MY_NAME}] System shutdown complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()