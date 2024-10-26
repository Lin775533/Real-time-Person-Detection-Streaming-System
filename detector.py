# detector.py
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime
import os
import torch
import time
class FaceDetector:
    def __init__(self, config):
        self.config = config
        self.model = self._load_model()
        self.camera = None
        self.is_running = False
        self.recording = False
        self.video_writer = None
        self.processed_frame = None
        self.num_faces = 0
        self.detection_enabled = True  # Add this line for toggle functionality
        print("FaceDetector initialized")
        
    def _load_model(self):
        try:
            print("Loading YOLO model...")
            model = YOLO("yolov8n.pt")
            model.conf = self.config.MODEL_CONFIDENCE
            model.classes = [0]  # person class only
            print("YOLO model loaded successfully")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def start_camera(self):
        try:
            print("Starting camera...")
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                print("Failed to open camera")
                return False
                
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.VIDEO_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.VIDEO_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.FPS)
            
            self.is_running = True
            print("Camera started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        print("Stopping camera...")
        self.is_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        print("Camera stopped")
    
    def get_current_frame(self):
        if not self.camera or not self.is_running:
            return None, 0
            
        try:
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to read frame")
                return None, 0
            
            num_faces = 0
            # Only process frame if detection is enabled
            if self.detection_enabled:
                # Process frame with YOLO
                results = self.model(frame, conf=self.config.MODEL_CONFIDENCE, verbose=False)
                
                if len(results) > 0:
                    result = results[0]
                    for box in result.boxes:
                        coords = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        
                        if confidence > self.config.MODEL_CONFIDENCE:
                            num_faces += 1
                            x1, y1, x2, y2 = map(int, coords)
                            
                            cv2.rectangle(frame, 
                                        (x1, y1), 
                                        (x2, y2), 
                                        (0, 255, 0), 2)
                            
                            cv2.putText(frame,
                                       f'Person {num_faces}: {confidence:.2f}',
                                       (x1, y1-10),
                                       cv2.FONT_HERSHEY_SIMPLEX,
                                       0.9,
                                       (0, 255, 0),
                                       2)
            
            # Always show detection status, even when disabled
            status_text = "Detection: ON" if self.detection_enabled else "Detection: OFF"
            cv2.putText(frame,
                       f'{status_text} | Detected: {num_faces if self.detection_enabled else 0}',
                       (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       1,
                       (0, 255, 255),
                       2)
            
            # Handle recording
            if self.recording and self.video_writer:
                self.video_writer.write(frame)
            
            return frame, num_faces
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return None, 0
    
    def toggle_detection(self, enabled):
        """Toggle detection on/off"""
        print(f"Detection toggled: {enabled}")
        self.detection_enabled = enabled