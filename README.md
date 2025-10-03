
# 🚀 AIR DROP: A Gesture-Based Virtual Peer-to-Peer Content Sharing and Control System


[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)](https://mediapipe.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A revolutionary touchless file transfer system that uses hand gestures and computer vision to enable secure peer-to-peer file sharing between devices on a local network.

![Demo](assets/demo.gif)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Gesture Controls](#gesture-controls)
- [Technical Stack](#technical-stack)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project implements an innovative gesture-based file transfer system that eliminates the need for traditional mouse/keyboard interactions. Using real-time hand tracking and computer vision, users can navigate their system, select files, and transfer them securely to peer devices through intuitive hand gestures.

### Key Highlights

- 🤚 **Touchless Control**: Navigate and control your computer using hand gestures
- 🔒 **Secure Transfer**: SSL/TLS encrypted peer-to-peer file transfer
- 🌐 **Zero Server**: Direct device-to-device communication without central servers
- ⚡ **Real-time Processing**: Low-latency gesture recognition and file transfer
- 🎨 **Visual Feedback**: Intuitive UI overlays showing gesture states

## ✨ Features

### Gesture Recognition
- Real-time hand tracking using MediaPipe
- 5-finger state detection system
- Custom gesture mapping for file operations
- Visual hand skeleton overlay with color-coded fingers

### File Transfer
- Peer-to-peer architecture using socket programming
- SSL/TLS encryption for secure data transfer
- Automatic peer discovery on local network
- Multi-threaded file sending/receiving
- Progress tracking and status notifications

### User Interface
- Live camera feed with gesture overlays
- Real-time gesture state display
- File transfer status indicators
- Received files counter
- On-screen gesture guide

## 🏗️ System Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Device A      │         │   Device B      │
│                 │         │                 │
│  ┌───────────┐  │         │  ┌───────────┐  │
│  │  Camera   │  │         │  │  Camera   │  │
│  └─────┬─────┘  │         │  └─────┬─────┘  │
│        │        │         │        │        │
│  ┌─────▼─────┐  │         │  ┌─────▼─────┐  │
│  │ MediaPipe │  │         │  │ MediaPipe │  │
│  │  Hands    │  │         │  │  Hands    │  │
│  └─────┬─────┘  │         │  └─────┬─────┘  │
│        │        │         │        │        │
│  ┌─────▼─────┐  │         │  ┌─────▼─────┐  │
│  │ Gesture   │  │         │  │ Gesture   │  │
│  │ System    │  │         │  │ System    │  │
│  └─────┬─────┘  │         │  └─────┬─────┘  │
│        │        │         │        │        │
│  ┌─────▼─────┐  │  SSL/   │  ┌─────▼─────┐  │
│  │  Secure   │◄─┼─  TLS  ─┼─►│  Secure   │  │
│  │  Client   │  │ Sockets │  │  Server   │  │
│  └───────────┘  │         │  └───────────┘  │
│                 │         │                 │
│  UDP Broadcast  │◄───────►│  UDP Broadcast  │
│  (Discovery)    │         │  (Discovery)    │
└─────────────────┘         └─────────────────┘
```

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- Webcam/Camera
- Windows OS (for full clipboard integration)
- Local network connection

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/gesture-file-transfer.git
cd gesture-file-transfer
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
opencv-python==4.8.0
mediapipe==0.10.8
pyautogui==0.9.54
numpy==1.24.3
pywin32==306
```

### Step 3: Generate SSL Certificates

```bash
python create_ssl_certs.py
```

This will generate `server.crt` and `server.key` files for secure communication.

## 🚀 Usage

### Starting the Application

**On Device A (Laptop A):**
```bash
python enhanced_main_app.py
# Select option 1 when prompted
```

**On Device B (Laptop B):**
```bash
python enhanced_main_app.py
# Select option 2 when prompted
```

### Alternative: Command Line Arguments
```bash
python enhanced_main_app.py "Laptop A"
python enhanced_main_app.py "Laptop B"
```

## 🤚 Gesture Controls

| Gesture | Finger Pattern | Action | Description |
|---------|---------------|--------|-------------|
| **Navigate** | `[0,1,0,0,0]` | Move Cursor | Index finger up - move cursor across screen |
| **Single Click** | `[1,0,1,0,0]` | Click | Thumb + middle finger pinch - single click |
| **Double Click** | `[0,1,1,0,0]` (close) | Double Click | Index + middle fingers close together |
| **Select All** | `[0,1,1,0,0]` (apart) | Select All | Index + middle fingers far apart |
| **Copy & Send** | `[0,0,0,0,0]` | Transfer File | Fist gesture - copy file and send to peer |
| **Paste Received** | `[1,1,1,1,1]` | Paste File | All fingers up - paste received file |

### Finger Pattern Notation
`[Thumb, Index, Middle, Ring, Pinky]`
- `1` = Finger Extended/Up
- `0` = Finger Closed/Down

## 🛠️ Technical Stack

### Core Technologies

- **Python 3.8+**: Primary programming language
- **OpenCV**: Video capture and image processing
- **MediaPipe**: Hand tracking and landmark detection
- **Socket Programming**: Network communication
- **SSL/TLS**: Secure data encryption

### Libraries & Modules

- `cv2` - Computer vision operations
- `mediapipe` - Hand gesture recognition
- `pyautogui` - System control automation
- `numpy` - Numerical operations
- `threading` - Concurrent operations
- `win32clipboard` - Clipboard integration
- `ssl` - Secure socket layer

### Key Algorithms

- **Hand Landmark Detection**: 21-point hand skeleton tracking
- **Finger State Detection**: Tip-PIP comparison algorithm
- **Cursor Smoothing**: Exponential moving average
- **Peer Discovery**: UDP broadcast with HMAC authentication
- **File Streaming**: Chunked transfer with progress tracking

## 📁 Project Structure

```
gesture-file-transfer/
│
├── enhanced_main_app.py          # Main application entry point
├── gesture_system.py              # Gesture recognition system
├── enhanced_secure_server.py     # SSL server for receiving files
├── enhanced_secure_client.py     # SSL client for sending files
├── discovery.py                   # Peer discovery module
├── create_ssl_certs.py           # SSL certificate generator
├── requirements.txt               # Python dependencies
│
├── server.crt                     # SSL certificate (generated)
├── server.key                     # SSL private key (generated)
│
├── AirDropReceived/              # Default received files directory
│
├── assets/                        # Images and demos
│   ├── demo.gif
│   ├── architecture.png
│   └── gestures.png
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   └── USER_GUIDE.md
│
├── tests/                         # Unit tests
│   ├── test_gestures.py
│   ├── test_transfer.py
│   └── test_discovery.py
│
├── LICENSE                        # MIT License
└── README.md                      # This file
```

## 🐛 Troubleshooting

### Common Issues

**1. Camera Not Detected**
```python
# Solution: Check camera index
cap = cv2.VideoCapture(0)  # Try 0, 1, 2, etc.
```

**2. Peer Discovery Fails**
- Ensure both devices are on same network
- Check firewall settings (allow UDP port 37020)
- Verify network allows broadcast packets

**3. SSL Certificate Errors**
```bash
# Regenerate certificates
python create_ssl_certs.py
```

**4. Gesture Not Recognized**
- Ensure good lighting
- Keep hand at arm's length from camera
- Check MediaPipe confidence thresholds

**5. File Transfer Fails**
- Verify peer IP address
- Check firewall allows TCP port 65432
- Ensure sufficient disk space

### Performance Optimization

**Low FPS:**
```python
# Reduce camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

**High CPU Usage:**
```python
# Decrease MediaPipe detection confidence
hands = mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
```

## 🧪 Testing

Run unit tests:
```bash
python -m pytest tests/
```

Test individual modules:
```bash
# Test gesture recognition
python tests/test_gestures.py

# Test file transfer
python tests/test_transfer.py

# Test peer discovery
python tests/test_discovery.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guide
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

## 📊 Performance Metrics

- **Gesture Recognition**: ~30 FPS on average hardware
- **File Transfer Speed**: ~10-50 MB/s (network dependent)
- **Latency**: <100ms gesture to action
- **Accuracy**: 95%+ gesture recognition rate

## 🔮 Future Enhancements

- [ ] Cross-platform support (macOS, Linux)
- [ ] Multiple file selection and batch transfer
- [ ] Gesture customization interface
- [ ] Transfer history and analytics
- [ ] Mobile app integration
- [ ] Cloud backup option
- [ ] Multi-device support (>2 devices)
- [ ] Voice command integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- LinkedIn: https://www.linkedin.com/in/dhanyatha-s
- GitHub: https://github.com/Dhanyatha-s

- Email: dhanyatha237.y@gmail.com

## Acknowledgments

- MediaPipe team for hand tracking library
- OpenCV community for computer vision tools
- Final year students who inspired this project
- All contributors and testers

