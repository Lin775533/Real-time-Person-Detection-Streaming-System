# config.py
import os
import torch

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    
    # Model configurations
    MODEL_CONFIDENCE = 0.5  # Detection confidence threshold
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Video configurations
    VIDEO_WIDTH = 640
    VIDEO_HEIGHT = 480
    FPS = 30
    
    # WebSocket configurations
    MAX_CLIENTS = 5
    CORS_ORIGINS = '*'