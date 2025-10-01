# ===============================
# enhanced_gesture_system.py - WITH BIDIRECTIONAL COMMANDS
# ===============================

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import os
import threading
import win32clipboard
import win32con
from enhanced_secure_client import EnhancedSecureClient
from enhanced_secure_server import EnhancedSecureServer
from file_transfer_protocol import CommandProtocol

class EnhancedGestureSystem:
    def __init__(self, peer_ip, server_instance):
        self.peer_ip = peer_ip
        self.server = server_instance
        self.client = EnhancedSecureClient()
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Finger colors for visualization
        self.finger_colors = {
            "thumb": (220, 200, 180),
            "index": (120, 220, 120),
            "middle": (255, 240, 120),
            "ring": (200, 120, 255),
            "pinky": (120, 180, 255),
        }
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Smoothening for cursor movement
        self.prev_x, self.prev_y = 0, 0
        self.smoothening = 7
        
        # Gesture timing to prevent rapid triggering
        self.last_pinch_time = 0
        self.last_copy_time = 0
        self.last_paste_time = 0
        
        # Gesture thresholds
        self.pinch_threshold = 50
        self.fist_threshold = 35
        
        # P2P Transfer variables
        self.selected_file = None
        self.is_item_selected = False
        self.is_item_copied = False
        
        # NEW: Bidirectional command state
        self.file_ready_state = False  # This device has file ready
        self.peer_has_file_ready = False  # Peer has file ready
        self.pending_transfer_request = None  # Store incoming transfer request
        
        # Register command handlers
        self.register_command_handlers()
        
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
    
    def register_command_handlers(self):
        """NEW: Register handlers for incoming commands"""
        self.server.register_command_handler(
            CommandProtocol.FILE_READY,
            self.handle_peer_file_ready
        )
        self.server.register_command_handler(
            CommandProtocol.REQUEST_TRANSFER,
            self.handle_peer_transfer_request
        )
        self.server.register_command_handler(
            CommandProtocol.CANCEL_READY,
            self.handle_peer_cancel_ready
        )
    
    def handle_peer_file_ready(self, command, addr):
        """NEW: Handle FILE_READY command from peer"""
        filename = command.get('data', {}).get('filename', 'Unknown')
        print(f"📢 Peer has file ready: {filename}")
        print(f"🖐️ Make PALM gesture to request transfer from peer")
        self.peer_has_file_ready = True
    
    def handle_peer_transfer_request(self, command, addr):
        """NEW: Handle REQUEST_TRANSFER command from peer"""
        print(f"📥 Peer requested transfer of our file")
        
        if self.file_ready_state and self.selected_file:
            print(f"✅ Initiating transfer to peer: {os.path.basename(self.selected_file)}")
            self.transfer_file_to_peer()
        else:
            print(f"⚠️ No file ready to transfer")
    
    def handle_peer_cancel_ready(self, command, addr):
        """NEW: Handle CANCEL_READY command from peer"""
        print(f"❌ Peer canceled file ready state")
        self.peer_has_file_ready = False
    
    def broadcast_file_ready(self):
        """NEW: Broadcast FILE_READY state to peer"""
        if not self.selected_file:
            return
        
        filename = os.path.basename(self.selected_file)
        data = {'filename': filename}
        
        success = self.client.send_command(
            self.peer_ip,
            CommandProtocol.FILE_READY,
            data
        )
        
        if success:
            self.file_ready_state = True
            print(f"📢 Broadcasted FILE_READY: {filename}")
        else:
            print(f"❌ Failed to broadcast FILE_READY")
    
    def send_transfer_request(self):
        """NEW: Send REQUEST_TRANSFER to peer"""
        success = self.client.send_command(
            self.peer_ip,
            CommandProtocol.REQUEST_TRANSFER
        )
        
        if success:
            print(f"📤 Transfer request sent to peer")
        else:
            print(f"❌ Failed to send transfer request")
    
    def cancel_file_ready(self):
        """NEW: Cancel FILE_READY state"""
        if not self.file_ready_state:
            return
        
        success = self.client.send_command(
            self.peer_ip,
            CommandProtocol.CANCEL_READY
        )
        
        if success:
            self.file_ready_state = False
            print(f"❌ Canceled FILE_READY state")
    
    def fingers_up(self, lmList):
        """Detect which fingers are up - IMPROVED VERSION"""
        if len(lmList) < 21:
            return [0, 0, 0, 0, 0]
        
        fingers = []
        
        # Thumb (check x-coordinate difference for better detection)
        thumb_tip_x = lmList[4][1]
        thumb_ip_x = lmList[3][1]
        
        if thumb_tip_x > thumb_ip_x:  # Right hand or thumb extended right
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other four fingers (check y-coordinate)
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_pips = [6, 10, 14, 18]  # Previous joints
        
        for i in range(4):
            tip_y = lmList[finger_tips[i]][2]
            pip_y = lmList[finger_pips[i]][2]
            
            if tip_y < pip_y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)
    
    def handle_cursor_movement(self, lmList):
        """Handle cursor movement with index finger"""
        if len(lmList) < 9:
            return None, None
            
        index_x, index_y = lmList[8][1], lmList[8][2]
        
        frame_w = 640
        frame_h = 480
        
        screen_x = np.interp(index_x, [100, frame_w - 100], [0, self.screen_w])
        screen_y = np.interp(index_y, [50, frame_h - 50], [0, self.screen_h])
        
        screen_x = self.prev_x + (screen_x - self.prev_x) / self.smoothening
        screen_y = self.prev_y + (screen_y - self.prev_y) / self.smoothening
        
        try:
            pyautogui.moveTo(screen_x, screen_y)
            self.prev_x, self.prev_y = screen_x, screen_y
        except Exception as e:
            print(f"[GESTURE] Cursor movement error: {e}")
        
        return int(index_x), int(index_y)
    
    def handle_pinch_gesture(self, lmList):
        """Handle pinch gesture - SELECT file/folder for P2P transfer"""
        current_time = time.time()
        if current_time - self.last_pinch_time < 1.5:
            return False
            
        if len(lmList) < 9:
            return False
        
        thumb_tip = lmList[4]
        index_tip = lmList[8]
        distance = self.calculate_distance(thumb_tip, index_tip)
        
        if distance < self.pinch_threshold:
            print("🤏 Pinch Gesture - Selecting file/folder for transfer")
            
            try:
                pyautogui.click()
                time.sleep(0.3)
                
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.5)
                
                selected_path = self.get_clipboard_file_path()
                
                if selected_path:
                    self.selected_file = selected_path
                    self.is_item_selected = True
                    self.is_item_copied = False
                    self.file_ready_state = False  # Reset ready state
                    print(f"📁 File/folder selected: {os.path.basename(selected_path)}")
                else:
                    print("⚠️ Could not get file path from selection")
                    
            except Exception as e:
                print(f"❌ Pinch gesture error: {e}")
            
            self.last_pinch_time = current_time
            return True
        return False
    
    def get_clipboard_file_path(self):
        """Get file path from clipboard after copy operation"""
        try:
            win32clipboard.OpenClipboard()
            
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                paths = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                file_list = list(paths)
                if file_list:
                    return file_list[0]
            
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                if text and os.path.exists(text.strip()):
                    return text.strip()
            
            return None
            
        except Exception as e:
            print(f"❌ Clipboard read error: {e}")
            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
    
    def handle_copy_gesture_fingers(self, lmList):
        """MODIFIED: Fist gesture now BROADCASTS FILE_READY instead of local copy"""
        current_time = time.time()
        
        if len(lmList) < 9:
            return False
        
        distance = math.hypot(lmList[4][1] - lmList[8][1], lmList[4][2] - lmList[8][2])
        
        if distance < 100 and (current_time - self.last_copy_time > 1):
            if not self.selected_file or not self.is_item_selected:
                print("📁 No valid file selection. Use pinch gesture first.")
                self.last_copy_time = current_time
                return False
            
            # NEW BEHAVIOR: Broadcast FILE_READY to peer
            print(f"✊ Fist Gesture - Broadcasting FILE_READY: {os.path.basename(self.selected_file)}")
            self.broadcast_file_ready()
            
            self.is_item_copied = True
            self.last_copy_time = current_time
            return True
        
        return False
    
    def handle_paste_gesture(self, fingers):
        """MODIFIED: Palm gesture behavior depends on context"""
        current_time = time.time()
        if current_time - self.last_paste_time < 3:
            return False
        
        if sum(fingers) == 5:  # All fingers up
            print("🖐 Open Palm Gesture Detected")
            
            # Priority 1: Check for received files to paste
            received_files = self.server.get_received_files()
            if received_files:
                print(f"📥 Pasting received file from peer")
                self.paste_received_file(received_files[-1])
            
            # Priority 2: If peer has FILE_READY, request transfer
            elif self.peer_has_file_ready:
                print(f"📤 Requesting transfer from peer")
                self.send_transfer_request()
                self.peer_has_file_ready = False  # Reset after request
            
            # Priority 3: If we have file ready, initiate transfer
            elif self.file_ready_state and self.selected_file:
                print(f"📤 Transferring our file to peer: {os.path.basename(self.selected_file)}")
                self.transfer_file_to_peer()
            
            else:
                print("⚠️ No action available - no files ready or received")
            
            self.last_paste_time = current_time
            return True
        
        return False
    
    def paste_received_file(self, file_path):
        """Paste received file into current location"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(file_path)
            win32clipboard.CloseClipboard()
            
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v')
            print(f"📁 Pasted received file: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"❌ Paste error: {e}")
    
    def transfer_file_to_peer(self):
        """Transfer selected file to peer device"""
        def transfer_thread():
            try:
                success = self.client.send_file(self.peer_ip, 65432, self.selected_file)
                if success:
                    print("✅ P2P File transfer completed successfully!")
                    # Reset after successful transfer
                    self.selected_file = None
                    self.is_item_selected = False
                    self.is_item_copied = False
                    self.file_ready_state = False
                else:
                    print("❌ P2P File transfer failed!")
            except Exception as e:
                print(f"❌ Transfer error: {e}")
        
        threading.Thread(target=transfer_thread, daemon=True).start()
    
    def draw_ui_overlay(self, frame, current_gesture, index_pos=None):
        """Draw UI information overlay"""
        h, w = frame.shape[:2]
        
        if index_pos and current_gesture == "Navigation":
            cv2.circle(frame, index_pos, 12, (255, 0, 255), 2)
            cv2.circle(frame, index_pos, 6, (255, 255, 255), -1)
        
        y_offset = 30
        
        # Show our file status
        if self.selected_file:
            filename = os.path.basename(self.selected_file)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            
            if self.file_ready_state:
                status_text = f"READY (broadcasted): {filename}"
                status_color = (0, 255, 255)  # Cyan
            elif self.is_item_copied:
                status_text = f"Preparing: {filename}"
                status_color = (255, 255, 0)  # Yellow
            else:
                status_text = f"Selected: {filename}"
                status_color = (0, 255, 0)  # Green
            
            cv2.putText(frame, status_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            y_offset += 30
        
        # Show peer file ready status
        if self.peer_has_file_ready:
            cv2.putText(frame, "PEER HAS FILE READY - Palm to request", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            y_offset += 30
        
        # Current gesture
        cv2.putText(frame, f"Gesture: {current_gesture}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += 30
        
        # Peer IP
        cv2.putText(frame, f"Peer: {self.peer_ip}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 2)
        
        # Instructions
        instructions = [
            "Index Up = Navigate | Pinch = Select",
            "Fist = Broadcast Ready | Palm = Request/Send"
        ]
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, h - 50 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Received files indicator
        received_count = len(self.server.get_received_files())
        if received_count > 0:
            cv2.putText(frame, f"Received: {received_count} files", (w-200, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    def draw_hand_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks with custom styling"""
        self.mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
        )
    
    def run(self):
        """Main gesture recognition loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        with self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands:
            
            print("🎥 BIDIRECTIONAL P2P Gesture System Started!")
            print("👆 Index = Navigate | 🤏 Pinch = Select")
            print("✊ Fist = Broadcast FILE_READY to peer")
            print("🖐 Palm = Request transfer from peer OR send our file")
            print(f"🌐 Peer: {self.peer_ip}")
            print("❌ Press 'q' to quit")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read from camera")
                    break
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(img_rgb)
                
                current_gesture = "None"
                index_pos = None
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.draw_hand_landmarks(frame, hand_landmarks)
                        
                        lmList = []
                        for id, lm in enumerate(hand_landmarks.landmark):
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            lmList.append([id, cx, cy])
                        
                        fingers = self.fingers_up(lmList)
                        
                        # Navigation Mode
                        if fingers == [0, 1, 0, 0, 0]:
                            current_gesture = "Navigation"
                            index_x, index_y = self.handle_cursor_movement(lmList)
                            if index_x and index_y:
                                index_pos = (index_x, index_y)
                        
                        # Selection Mode
                        elif fingers == [1, 1, 0, 0, 0]:
                            current_gesture = "Selection"
                            if self.handle_pinch_gesture(lmList):
                                current_gesture = "File Selected!"
                        
                        # Broadcast Ready Mode
                        elif fingers == [0, 0, 0, 0, 0]:
                            current_gesture = "Broadcasting Ready" 
                            if self.handle_copy_gesture_fingers(lmList): 
                                current_gesture = "FILE_READY Sent!"
                        
                        # Transfer Mode
                        elif fingers == [1, 1, 1, 1, 1]:
                            current_gesture = "Transfer Action"
                            if self.handle_paste_gesture(fingers):
                                current_gesture = "Action Complete!"
                        
                        else:
                            finger_count = sum(fingers)
                            current_gesture = f"Fingers: {finger_count}"
                
                self.draw_ui_overlay(frame, current_gesture, index_pos)
                
                cv2.imshow('Bidirectional P2P Gesture Transfer', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("👋 Quitting gesture system...")
                    break
                elif key == ord('c'):
                    self.server.clear_received_files()
                    print("🗑️ Cleared received files list")
                elif key == ord('r'):
                    self.selected_file = None
                    self.is_item_selected = False
                    self.is_item_copied = False
                    self.file_ready_state = False
                    if self.file_ready_state:
                        self.cancel_file_ready()
                    print("🔄 Reset file selection")
        
        cap.release()
        cv2.destroyAllWindows()
        print("📷 Camera released and windows closed")