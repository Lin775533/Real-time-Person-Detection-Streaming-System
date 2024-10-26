# video_utils.py
import base64
import cv2
import numpy as np
import os
from datetime import datetime

class VideoUtils:
    @staticmethod
    def decode_base64_frame(base64_string):
        try:
            encoded_data = base64_string.split(',')[1]
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"Error decoding frame: {e}")
            return None
    
    @staticmethod
    def encode_frame_to_base64(frame):
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None
    
    @staticmethod
    def generate_filename(prefix='recording', extension='avi'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp}.{extension}"