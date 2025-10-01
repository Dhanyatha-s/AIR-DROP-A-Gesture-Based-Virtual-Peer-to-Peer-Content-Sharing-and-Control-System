
AIR DROP: A Gesture-Based Virtual Peer-to-Peer Content Sharing and Control System
### ---- Installation ----  

#### create a virtual environment
-------------------------------   
```python -m venv venv    ```       -- run this first

#### Activate the virtual environment
----------------------------------   
```venv\Scripts\activate ```


#### Libraries needed -- install then ---   

```pip install opencv-python mediapipe pyautogui pywin32 cryptography   ```


##### create ssl-certificates   

```python create_ssl_certificate.py   ```


##### run the main script   

```python main_app.py   ```


- Index to navigate across the window (cursor)  
- Thumb + Index == pinch to select the file/folder  
- all fingers closed == Fist to copy  
- all fingers up == open palm to paste   


