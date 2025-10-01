# # ===============================
# # enhanced_gesture_system.py - WITH TRUE BIDIRECTIONAL GESTURE CONTROL
# # ===============================

# import cv2
# import mediapipe as mp
# import pyautogui
# import numpy as np
# import math
# import time
# import os
# import threading
# import win32clipboard
# import win32con
# from enhanced_secure_client import EnhancedSecureClient
# from enhanced_secure_server import EnhancedSecureServer
# from file_transfer_protocol import CommandProtocol

# class EnhancedGestureSystem:
#     def __init__(self, peer_ip, server_instance):
#         self.peer_ip = peer_ip
#         self.server = server_instance
#         self.client = EnhancedSecureClient()
        
#         # MediaPipe setup
#         self.mp_hands = mp.solutions.hands
#         self.mp_drawing = mp.solutions.drawing_utils
        
#         # Finger colors for visualization
#         self.finger_colors = {
#             "thumb": (220, 200, 180),
#             "index": (120, 220, 120),
#             "middle": (255, 240, 120),
#             "ring": (200, 120, 255),
#             "pinky": (120, 180, 255),
#         }
        
#         # Screen dimensions
#         self.screen_w, self.screen_h = pyautogui.size()
        
#         # Smoothening for cursor movement
#         self.prev_x, self.prev_y = 0, 0
#         self.smoothening = 7
        
#         # Gesture timing to prevent rapid triggering
#         self.last_pinch_time = 0
#         self.last_copy_time = 0
#         self.last_paste_time = 0
        
#         # Gesture thresholds
#         self.pinch_threshold = 50
#         self.fist_threshold = 35
        
#         # P2P Transfer variables
#         self.selected_file = None
#         self.is_item_selected = False
#         self.is_item_copied = False
        
#         # CRITICAL: Pending transfer state (gesture approval needed)
#         self.file_ready_state = False
#         self.peer_has_file_ready = False
#         self.pending_incoming_transfer = None  # Stores peer's transfer request details
        
#         # Register command handlers - BUT DON'T AUTO-ACCEPT
#         self.register_command_handlers()
        
#         # Disable pyautogui failsafe for smoother operation
#         pyautogui.FAILSAFE = False
#         pyautogui.PAUSE = 0.01
    
#     def register_command_handlers(self):
#         """Register handlers for incoming commands - NO AUTO-ACCEPT"""
#         self.server.register_command_handler(
#             CommandProtocol.FILE_READY,
#             self.handle_peer_file_ready
#         )
#         self.server.register_command_handler(
#             CommandProtocol.REQUEST_TRANSFER,
#             self.handle_peer_transfer_request
#         )
#         self.server.register_command_handler(
#             CommandProtocol.CANCEL_READY,
#             self.handle_peer_cancel_ready
#         )
    
#     def handle_peer_file_ready(self, command, addr):
#         """Handle FILE_READY command - ONLY STORE, DON'T AUTO-ACCEPT"""
#         filename = command.get('data', {}).get('filename', 'Unknown')
#         print(f"\n[NOTIFICATION] Peer has file ready: {filename}")
#         print(f"[ACTION REQUIRED] Make PALM gesture to request transfer\n")
#         self.peer_has_file_ready = True
#         self.pending_incoming_transfer = {
#             'filename': filename,
#             'addr': addr,
#             'type': 'file_ready'
#         }
    
#     def handle_peer_transfer_request(self, command, addr):
#         """Handle REQUEST_TRANSFER - Only store request, gesture approves"""
#         print(f"\n[NOTIFICATION] Peer requested our file")
        
#         if self.file_ready_state and self.selected_file:
#             print(f"[AUTO-APPROVE] Sending file: {os.path.basename(self.selected_file)}")
#             # This is OK because WE initiated the ready state
#             self.transfer_file_to_peer()
#         else:
#             print(f"[REJECTED] No file ready to send")
    
#     def handle_peer_cancel_ready(self, command, addr):
#         """Handle CANCEL_READY command"""
#         print(f"\n[NOTIFICATION] Peer canceled file ready state\n")
#         self.peer_has_file_ready = False
#         self.pending_incoming_transfer = None
    
#     def broadcast_file_ready(self):
#         """Broadcast FILE_READY state to peer"""
#         if not self.selected_file:
#             return
        
#         filename = os.path.basename(self.selected_file)
#         data = {'filename': filename}
        
#         success = self.client.send_command(
#             self.peer_ip,
#             CommandProtocol.FILE_READY,
#             data
#         )
        
#         if success:
#             self.file_ready_state = True
#             print(f"\n[BROADCAST] FILE_READY sent: {filename}\n")
#         else:
#             print(f"\n[ERROR] Failed to broadcast FILE_READY\n")
    
#     def send_transfer_request(self):
#         """Send REQUEST_TRANSFER to peer - REQUIRES PALM GESTURE"""
#         if not self.peer_has_file_ready:
#             print("[ERROR] No peer file ready to request")
#             return
            
#         success = self.client.send_command(
#             self.peer_ip,
#             CommandProtocol.REQUEST_TRANSFER
#         )
        
#         if success:
#             print(f"\n[SENT] Transfer request sent to peer\n")
#             print(f"[WAITING] File transfer incoming...\n")
#         else:
#             print(f"\n[ERROR] Failed to send transfer request\n")
    
#     def cancel_file_ready(self):
#         """Cancel FILE_READY state"""
#         if not self.file_ready_state:
#             return
        
#         success = self.client.send_command(
#             self.peer_ip,
#             CommandProtocol.CANCEL_READY
#         )
        
#         if success:
#             self.file_ready_state = False
#             print(f"\n[CANCELED] FILE_READY state canceled\n")
    
#     def fingers_up(self, lmList):
#         """Detect which fingers are up"""
#         if len(lmList) < 21:
#             return [0, 0, 0, 0, 0]
        
#         fingers = []
        
#         # Thumb
#         thumb_tip_x = lmList[4][1]
#         thumb_ip_x = lmList[3][1]
        
#         if thumb_tip_x > thumb_ip_x:
#             fingers.append(1)
#         else:
#             fingers.append(0)
        
#         # Other four fingers
#         finger_tips = [8, 12, 16, 20]
#         finger_pips = [6, 10, 14, 18]
        
#         for i in range(4):
#             tip_y = lmList[finger_tips[i]][2]
#             pip_y = lmList[finger_pips[i]][2]
            
#             if tip_y < pip_y:
#                 fingers.append(1)
#             else:
#                 fingers.append(0)
        
#         return fingers
    
#     def calculate_distance(self, point1, point2):
#         """Calculate Euclidean distance between two points"""
#         return math.sqrt((point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)
    
#     def handle_cursor_movement(self, lmList):
#         """Handle cursor movement with index finger"""
#         if len(lmList) < 9:
#             return None, None
            
#         index_x, index_y = lmList[8][1], lmList[8][2]
        
#         frame_w = 640
#         frame_h = 480
        
#         screen_x = np.interp(index_x, [100, frame_w - 100], [0, self.screen_w])
#         screen_y = np.interp(index_y, [50, frame_h - 50], [0, self.screen_h])
        
#         screen_x = self.prev_x + (screen_x - self.prev_x) / self.smoothening
#         screen_y = self.prev_y + (screen_y - self.prev_y) / self.smoothening
        
#         try:
#             pyautogui.moveTo(screen_x, screen_y)
#             self.prev_x, self.prev_y = screen_x, screen_y
#         except Exception as e:
#             print(f"[GESTURE] Cursor movement error: {e}")
        
#         return int(index_x), int(index_y)
    
#     def handle_pinch_gesture(self, lmList):
#         """Handle pinch gesture - SELECT file/folder"""
#         current_time = time.time()
#         if current_time - self.last_pinch_time < 1.5:
#             return False
            
#         if len(lmList) < 9:
#             return False
        
#         thumb_tip = lmList[4]
#         index_tip = lmList[8]
#         distance = self.calculate_distance(thumb_tip, index_tip)
        
#         if distance < self.pinch_threshold:
#             print("\n[GESTURE] Pinch - Selecting file/folder\n")
            
#             try:
#                 pyautogui.click()
#                 time.sleep(0.3)
                
#                 pyautogui.hotkey('ctrl', 'c')
#                 time.sleep(0.5)
                
#                 selected_path = self.get_clipboard_file_path()
                
#                 if selected_path:
#                     self.selected_file = selected_path
#                     self.is_item_selected = True
#                     self.is_item_copied = False
#                     self.file_ready_state = False
#                     print(f"[SELECTED] {os.path.basename(selected_path)}\n")
#                 else:
#                     print("[ERROR] Could not get file path\n")
                    
#             except Exception as e:
#                 print(f"[ERROR] Pinch gesture: {e}\n")
            
#             self.last_pinch_time = current_time
#             return True
#         return False
    
#     def get_clipboard_file_path(self):
#         """Get file path from clipboard"""
#         try:
#             win32clipboard.OpenClipboard()
            
#             if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
#                 paths = win32clipboard.GetClipboardData(win32con.CF_HDROP)
#                 file_list = list(paths)
#                 if file_list:
#                     return file_list[0]
            
#             if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
#                 text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
#                 if text and os.path.exists(text.strip()):
#                     return text.strip()
            
#             return None
            
#         except Exception as e:
#             print(f"[ERROR] Clipboard: {e}")
#             return None
#         finally:
#             try:
#                 win32clipboard.CloseClipboard()
#             except:
#                 pass
    
#     def handle_copy_gesture_fingers(self, lmList):
#         """Fist gesture - BROADCAST FILE_READY"""
#         current_time = time.time()
        
#         if len(lmList) < 9:
#             return False
        
#         distance = math.hypot(lmList[4][1] - lmList[8][1], lmList[4][2] - lmList[8][2])
        
#         if distance < 100 and (current_time - self.last_copy_time > 1):
#             if not self.selected_file or not self.is_item_selected:
#                 print("\n[ERROR] No file selected. Use pinch gesture first.\n")
#                 self.last_copy_time = current_time
#                 return False
            
#             print(f"\n[GESTURE] Fist - Broadcasting FILE_READY\n")
#             self.broadcast_file_ready()
            
#             self.is_item_copied = True
#             self.last_copy_time = current_time
#             return True
        
#         return False
    
#     def handle_paste_gesture(self, fingers):
#         """CRITICAL: Palm gesture with THREE-WAY LOGIC"""
#         current_time = time.time()
#         if current_time - self.last_paste_time < 3:
#             return False
        
#         if sum(fingers) == 5:  # All fingers up
#             print("\n[GESTURE] Palm Detected\n")
            
#             # PRIORITY 1: Paste received files (requires gesture confirmation)
#             received_files = self.server.get_received_files()
#             if received_files:
#                 print(f"[ACTION] Pasting received file: {os.path.basename(received_files[-1])}\n")
#                 self.paste_received_file(received_files[-1])
#                 self.server.received_files.pop()
#                 self.last_paste_time = current_time
#                 return True
            
#             # PRIORITY 2: Request transfer from peer (requires gesture confirmation)
#             elif self.peer_has_file_ready:
#                 print(f"[ACTION] Requesting file from peer\n")
#                 self.send_transfer_request()
#                 self.peer_has_file_ready = False
#                 self.pending_incoming_transfer = None
#                 self.last_paste_time = current_time
#                 return True
            
#             # PRIORITY 3: Send our file to peer
#             elif self.file_ready_state and self.selected_file:
#                 print(f"[ACTION] Sending file to peer: {os.path.basename(self.selected_file)}\n")
#                 self.transfer_file_to_peer()
#                 self.last_paste_time = current_time
#                 return True
            
#             else:
#                 print("[INFO] No action available\n")
#                 self.last_paste_time = current_time
#                 return False
        
#         return False
    
#     def paste_received_file(self, file_path):
#         """Paste received file to clipboard and execute paste"""
#         try:
#             win32clipboard.OpenClipboard()
#             win32clipboard.EmptyClipboard()
#             win32clipboard.SetClipboardText(file_path)
#             win32clipboard.CloseClipboard()
            
#             time.sleep(0.3)
#             pyautogui.hotkey('ctrl', 'v')
#             print(f"[PASTED] {os.path.basename(file_path)}\n")
            
#         except Exception as e:
#             print(f"[ERROR] Paste: {e}\n")
    
#     def transfer_file_to_peer(self):
#         """Transfer file to peer"""
#         def transfer_thread():
#             try:
#                 print(f"[TRANSFER] Starting file transfer...\n")
#                 success = self.client.send_file(self.peer_ip, 65432, self.selected_file)
#                 if success:
#                     print("\n[SUCCESS] File transfer complete!\n")
#                     self.selected_file = None
#                     self.is_item_selected = False
#                     self.is_item_copied = False
#                     self.file_ready_state = False
#                 else:
#                     print("\n[FAILED] File transfer failed\n")
#             except Exception as e:
#                 print(f"\n[ERROR] Transfer: {e}\n")
        
#         threading.Thread(target=transfer_thread, daemon=True).start()
    
#     def draw_ui_overlay(self, frame, current_gesture, index_pos=None):
#         """Draw UI overlay with clear status indicators"""
#         h, w = frame.shape[:2]
        
#         if index_pos and current_gesture == "Navigation":
#             cv2.circle(frame, index_pos, 12, (255, 0, 255), 2)
#             cv2.circle(frame, index_pos, 6, (255, 255, 255), -1)
        
#         y_offset = 30
        
#         # Our file status
#         if self.selected_file:
#             filename = os.path.basename(self.selected_file)
#             if len(filename) > 30:
#                 filename = filename[:27] + "..."
            
#             if self.file_ready_state:
#                 status_text = f"READY: {filename}"
#                 status_color = (0, 255, 255)
#             elif self.is_item_copied:
#                 status_text = f"Preparing: {filename}"
#                 status_color = (255, 255, 0)
#             else:
#                 status_text = f"Selected: {filename}"
#                 status_color = (0, 255, 0)
            
#             cv2.putText(frame, status_text, (10, y_offset), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
#             y_offset += 30
        
#         # CRITICAL: Show peer file ready (needs palm gesture)
#         if self.peer_has_file_ready:
#             cv2.putText(frame, "!!! PEER HAS FILE READY !!!", (10, y_offset), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
#             y_offset += 30
#             cv2.putText(frame, ">>> PALM gesture to request <<<", (10, y_offset), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
#             y_offset += 30
        
#         # CRITICAL: Show received files (needs palm gesture to paste)
#         received_count = len(self.server.get_received_files())
#         if received_count > 0:
#             cv2.putText(frame, f"!!! {received_count} FILE(S) RECEIVED !!!", (10, y_offset), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
#             y_offset += 30
#             cv2.putText(frame, ">>> PALM gesture to paste <<<", (10, y_offset), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
#             y_offset += 30
        
#         # Current gesture
#         cv2.putText(frame, f"Gesture: {current_gesture}", (10, y_offset), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
#         y_offset += 30
        
#         # Peer IP
#         cv2.putText(frame, f"Peer: {self.peer_ip}", (10, y_offset), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 2)
        
#         # Instructions at bottom
#         instructions = [
#             "Index=Nav | Pinch=Select | Fist=Ready | Palm=Confirm",
#         ]
#         for i, instruction in enumerate(instructions):
#             cv2.putText(frame, instruction, (10, h - 30 + i*20), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    
#     def draw_hand_landmarks(self, frame, hand_landmarks):
#         """Draw hand landmarks"""
#         self.mp_drawing.draw_landmarks(
#             frame, 
#             hand_landmarks, 
#             self.mp_hands.HAND_CONNECTIONS,
#             self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
#             self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
#         )
    
#     def run(self):
#         """Main gesture loop - RUNS ON BOTH DEVICES"""
#         cap = cv2.VideoCapture(0)
        
#         if not cap.isOpened():
#             print("\n[ERROR] Cannot open camera!")
#             print("[TROUBLESHOOT] Check if camera is being used by another application\n")
#             return
        
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#         cap.set(cv2.CAP_PROP_FPS, 30)
        
#         with self.mp_hands.Hands(
#             max_num_hands=1,
#             min_detection_confidence=0.7,
#             min_tracking_confidence=0.7
#         ) as hands:
            
#             print("\n" + "="*60)
#             print("CAMERA ACTIVE - GESTURE SYSTEM RUNNING")
#             print("="*60)
#             print("Pinch = Select file")
#             print("Fist = Broadcast ready")
#             print("Palm = Request/Paste/Send")
#             print("="*60)
#             print(f"Peer: {self.peer_ip}")
#             print("Press 'q' to quit | 'r' to reset | 'c' to clear")
#             print("="*60 + "\n")
            
#             while cap.isOpened():
#                 ret, frame = cap.read()
#                 if not ret:
#                     print("[ERROR] Failed to read from camera")
#                     break
                
#                 frame = cv2.flip(frame, 1)
#                 h, w, _ = frame.shape
                
#                 img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 results = hands.process(img_rgb)
                
#                 current_gesture = "None"
#                 index_pos = None
                
#                 if results.multi_hand_landmarks:
#                     for hand_landmarks in results.multi_hand_landmarks:
#                         self.draw_hand_landmarks(frame, hand_landmarks)
                        
#                         lmList = []
#                         for id, lm in enumerate(hand_landmarks.landmark):
#                             cx, cy = int(lm.x * w), int(lm.y * h)
#                             lmList.append([id, cx, cy])
                        
#                         fingers = self.fingers_up(lmList)
                        
#                         # Navigation
#                         if fingers == [0, 1, 0, 0, 0]:
#                             current_gesture = "Navigation"
#                             index_x, index_y = self.handle_cursor_movement(lmList)
#                             if index_x and index_y:
#                                 index_pos = (index_x, index_y)
                        
#                         # Selection
#                         elif fingers == [1, 1, 0, 0, 0]:
#                             current_gesture = "Selection"
#                             if self.handle_pinch_gesture(lmList):
#                                 current_gesture = "File Selected!"
                        
#                         # Broadcast Ready
#                         elif fingers == [0, 0, 0, 0, 0]:
#                             current_gesture = "Broadcasting" 
#                             if self.handle_copy_gesture_fingers(lmList): 
#                                 current_gesture = "Ready Sent!"
                        
#                         # Confirm/Transfer
#                         elif fingers == [1, 1, 1, 1, 1]:
#                             current_gesture = "Confirming"
#                             if self.handle_paste_gesture(fingers):
#                                 current_gesture = "Action Done!"
                        
#                         else:
#                             finger_count = sum(fingers)
#                             current_gesture = f"Fingers: {finger_count}"
                
#                 self.draw_ui_overlay(frame, current_gesture, index_pos)
                
#                 cv2.imshow('P2P Gesture Transfer - BOTH DEVICES ACTIVE', frame)
                
#                 key = cv2.waitKey(1) & 0xFF
#                 if key == ord('q'):
#                     print("\n[QUIT] Stopping gesture system...\n")
#                     break
#                 elif key == ord('c'):
#                     self.server.clear_received_files()
#                     print("\n[CLEARED] Received files list\n")
#                 elif key == ord('r'):
#                     self.selected_file = None
#                     self.is_item_selected = False
#                     self.is_item_copied = False
#                     if self.file_ready_state:
#                         self.cancel_file_ready()
#                     self.file_ready_state = False
#                     print("\n[RESET] File selection cleared\n")
        
#         cap.release()
#         cv2.destroyAllWindows()
#         print("\n[CLOSED] Camera released\n")


# ===============================
# enhanced_gesture_system.py - WITH SMART PASTE TO CURRENT DIRECTORY
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
import win32gui
import win32process
import psutil
import shutil
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
        
        # Bidirectional command state
        self.file_ready_state = False
        self.peer_has_file_ready = False
        self.pending_transfer_request = None
        
        # Register command handlers
        self.register_command_handlers()
        
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
    
    def register_command_handlers(self):
        """Register handlers for incoming commands"""
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
        """Handle FILE_READY command from peer"""
        filename = command.get('data', {}).get('filename', 'Unknown')
        print(f"Peer has file ready: {filename}")
        print(f"Make PALM gesture to request transfer from peer")
        self.peer_has_file_ready = True
    
    def handle_peer_transfer_request(self, command, addr):
        """Handle REQUEST_TRANSFER command from peer"""
        print(f"Peer requested transfer of our file")
        
        if self.file_ready_state and self.selected_file:
            print(f"Initiating transfer to peer: {os.path.basename(self.selected_file)}")
            self.transfer_file_to_peer()
        else:
            print(f"No file ready to transfer")
    
    def handle_peer_cancel_ready(self, command, addr):
        """Handle CANCEL_READY command from peer"""
        print(f"Peer canceled file ready state")
        self.peer_has_file_ready = False
    
    def broadcast_file_ready(self):
        """Broadcast FILE_READY state to peer"""
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
            print(f"Broadcasted FILE_READY: {filename}")
        else:
            print(f"Failed to broadcast FILE_READY")
    
    def send_transfer_request(self):
        """Send REQUEST_TRANSFER to peer"""
        success = self.client.send_command(
            self.peer_ip,
            CommandProtocol.REQUEST_TRANSFER
        )
        
        if success:
            print(f"Transfer request sent to peer")
        else:
            print(f"Failed to send transfer request")
    
    def cancel_file_ready(self):
        """Cancel FILE_READY state"""
        if not self.file_ready_state:
            return
        
        success = self.client.send_command(
            self.peer_ip,
            CommandProtocol.CANCEL_READY
        )
        
        if success:
            self.file_ready_state = False
            print(f"Canceled FILE_READY state")
    
    def fingers_up(self, lmList):
        """Detect which fingers are up"""
        if len(lmList) < 21:
            return [0, 0, 0, 0, 0]
        
        fingers = []
        
        # Thumb
        thumb_tip_x = lmList[4][1]
        thumb_ip_x = lmList[3][1]
        
        if thumb_tip_x > thumb_ip_x:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other four fingers
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
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
        """Handle pinch gesture - SELECT file/folder"""
        current_time = time.time()
        if current_time - self.last_pinch_time < 1.5:
            return False
            
        if len(lmList) < 9:
            return False
        
        thumb_tip = lmList[4]
        index_tip = lmList[8]
        distance = self.calculate_distance(thumb_tip, index_tip)
        
        if distance < self.pinch_threshold:
            print("Pinch Gesture - Selecting file/folder for transfer")
            
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
                    self.file_ready_state = False
                    print(f"File/folder selected: {os.path.basename(selected_path)}")
                else:
                    print("Could not get file path from selection")
                    
            except Exception as e:
                print(f"Pinch gesture error: {e}")
            
            self.last_pinch_time = current_time
            return True
        return False
    
    def get_clipboard_file_path(self):
        """Get file path from clipboard"""
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
            print(f"Clipboard read error: {e}")
            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
    
    def handle_copy_gesture_fingers(self, lmList):
        """Fist gesture - Broadcast FILE_READY"""
        current_time = time.time()
        
        if len(lmList) < 9:
            return False
        
        distance = math.hypot(lmList[4][1] - lmList[8][1], lmList[4][2] - lmList[8][2])
        
        if distance < 100 and (current_time - self.last_copy_time > 1):
            if not self.selected_file or not self.is_item_selected:
                print("No valid file selection. Use pinch gesture first.")
                self.last_copy_time = current_time
                return False
            
            print(f"Fist Gesture - Broadcasting FILE_READY: {os.path.basename(self.selected_file)}")
            self.broadcast_file_ready()
            
            self.is_item_copied = True
            self.last_copy_time = current_time
            return True
        
        return False
    
    def handle_paste_gesture(self, fingers):
        """Palm gesture - Context-aware transfer/paste"""
        current_time = time.time()
        if current_time - self.last_paste_time < 3:
            return False
        
        if sum(fingers) == 5:
            print("Open Palm Gesture Detected")
            
            # Priority 1: Paste received files
            received_files = self.server.get_received_files()
            if received_files:
                print(f"Pasting received file from peer")
                self.paste_received_file(received_files[-1])
            
            # Priority 2: Request from peer
            elif self.peer_has_file_ready:
                print(f"Requesting transfer from peer")
                self.send_transfer_request()
                self.peer_has_file_ready = False
            
            # Priority 3: Send our file
            elif self.file_ready_state and self.selected_file:
                print(f"Transferring our file to peer: {os.path.basename(self.selected_file)}")
                self.transfer_file_to_peer()
            
            else:
                print("No action available")
            
            self.last_paste_time = current_time
            return True
        
        return False
    
    def get_active_explorer_path(self):
        """Get current File Explorer directory path"""
        try:
            import win32com.client
            shell = win32com.client.Dispatch("Shell.Application")
            
            for window in shell.Windows():
                try:
                    hwnd = window.HWND
                    if win32gui.GetForegroundWindow() == hwnd:
                        path = window.LocationURL
                        if path:
                            import urllib.parse
                            path = urllib.parse.unquote(path)
                            path = path.replace('file:///', '')
                            path = path.replace('/', '\\')
                            return path
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Error getting explorer path: {e}")
            return None
    
    def is_file_explorer_focused(self):
        """Check if File Explorer is active"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name().lower()
            
            if process_name == "explorer.exe" and window_title:
                if window_title not in ["", "Program Manager"]:
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def paste_received_file(self, file_path):
        """Smart paste to current File Explorer location"""
        try:
            # Check if File Explorer is focused
            if self.is_file_explorer_focused():
                current_dir = self.get_active_explorer_path()
                
                if current_dir and os.path.isdir(current_dir):
                    print(f"Pasting to current directory: {current_dir}")
                    
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(current_dir, filename)
                    
                    # Handle duplicates
                    counter = 1
                    original_dest = dest_path
                    while os.path.exists(dest_path):
                        name, ext = os.path.splitext(original_dest)
                        dest_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # Copy file or folder
                    if os.path.isfile(file_path):
                        shutil.copy2(file_path, dest_path)
                    elif os.path.isdir(file_path):
                        shutil.copytree(file_path, dest_path)
                    
                    print(f"File copied to: {dest_path}")
                    pyautogui.press('f5')  # Refresh explorer
                    return
            
            # Fallback: Use clipboard method
            print("Using clipboard paste method")
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_HDROP, [file_path])
            win32clipboard.CloseClipboard()
            
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v')
            print(f"Pasted: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Paste error: {e}")
            # Last resort: Open file location
            try:
                os.startfile(os.path.dirname(file_path))
            except:
                pass
    
    def transfer_file_to_peer(self):
        """Transfer file to peer"""
        def transfer_thread():
            try:
                success = self.client.send_file(self.peer_ip, 65432, self.selected_file)
                if success:
                    print("File transfer completed successfully!")
                    self.selected_file = None
                    self.is_item_selected = False
                    self.is_item_copied = False
                    self.file_ready_state = False
                else:
                    print("File transfer failed!")
            except Exception as e:
                print(f"Transfer error: {e}")
        
        threading.Thread(target=transfer_thread, daemon=True).start()
    
    def draw_ui_overlay(self, frame, current_gesture, index_pos=None):
        """Draw UI overlay"""
        h, w = frame.shape[:2]
        
        if index_pos and current_gesture == "Navigation":
            cv2.circle(frame, index_pos, 12, (255, 0, 255), 2)
            cv2.circle(frame, index_pos, 6, (255, 255, 255), -1)
        
        y_offset = 30
        
        if self.selected_file:
            filename = os.path.basename(self.selected_file)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            
            if self.file_ready_state:
                status_text = f"READY (broadcasted): {filename}"
                status_color = (0, 255, 255)
            elif self.is_item_copied:
                status_text = f"Preparing: {filename}"
                status_color = (255, 255, 0)
            else:
                status_text = f"Selected: {filename}"
                status_color = (0, 255, 0)
            
            cv2.putText(frame, status_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            y_offset += 30
        
        if self.peer_has_file_ready:
            cv2.putText(frame, "PEER HAS FILE READY - Palm to request", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            y_offset += 30
        
        cv2.putText(frame, f"Gesture: {current_gesture}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += 30
        
        cv2.putText(frame, f"Peer: {self.peer_ip}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 2)
        
        instructions = [
            "Index = Navigate | Pinch = Select | Fist = Ready | Palm = Transfer",
        ]
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, h - 30 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        received_count = len(self.server.get_received_files())
        if received_count > 0:
            cv2.putText(frame, f"Received: {received_count}", (w-150, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    def draw_hand_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks"""
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
            
            print("Bidirectional P2P Gesture System Started!")
            print("Pinch = Select | Fist = Broadcast Ready | Palm = Transfer")
            print(f"Peer: {self.peer_ip}")
            print("Press 'q' to quit, 'r' to reset, 'c' to clear received")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
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
                        
                        if fingers == [0, 1, 0, 0, 0]:
                            current_gesture = "Navigation"
                            index_x, index_y = self.handle_cursor_movement(lmList)
                            if index_x and index_y:
                                index_pos = (index_x, index_y)
                        
                        elif fingers == [1, 1, 0, 0, 0]:
                            current_gesture = "Selection"
                            if self.handle_pinch_gesture(lmList):
                                current_gesture = "File Selected!"
                        
                        elif fingers == [0, 0, 0, 0, 0]:
                            current_gesture = "Broadcasting" 
                            if self.handle_copy_gesture_fingers(lmList): 
                                current_gesture = "Ready Sent!"
                        
                        elif fingers == [1, 1, 1, 1, 1]:
                            current_gesture = "Transfer"
                            if self.handle_paste_gesture(fingers):
                                current_gesture = "Complete!"
                        
                        else:
                            current_gesture = f"Fingers: {sum(fingers)}"
                
                self.draw_ui_overlay(frame, current_gesture, index_pos)
                cv2.imshow('Bidirectional P2P Transfer', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.server.clear_received_files()
                    print("Cleared received files")
                elif key == ord('r'):
                    self.selected_file = None
                    self.is_item_selected = False
                    self.is_item_copied = False
                    self.file_ready_state = False
                    print("Reset selection")
        
        cap.release()
        cv2.destroyAllWindows()