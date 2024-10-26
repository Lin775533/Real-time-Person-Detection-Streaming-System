# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from config import Config
from detector import FaceDetector
from video_utils import VideoUtils
import os
import torch
import threading
import time

app = Flask(__name__, 
    static_folder='static',  # Define static folder
    template_folder='templates'  # Define templates folder
)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'])

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join('static', 'css'), exist_ok=True)
os.makedirs(os.path.join('static', 'js'), exist_ok=True)

# Initialize detector
detector = FaceDetector(Config)
connected_clients = {}
processing_enabled = True

def broadcast_frames():
    """Continuously broadcast frames to all clients"""
    while True:
        try:
            if connected_clients:
                frame, num_faces = detector.get_current_frame()
                if frame is not None:
                    encoded_frame = VideoUtils.encode_frame_to_base64(frame)
                    if encoded_frame:
                        socketio.emit('processed_frame', {
                            'frame': encoded_frame,
                            'num_faces': num_faces if detector.detection_enabled else 0,
                            'client_count': len(connected_clients)
                        })
            time.sleep(1/30)  # Limit to 30 FPS
        except Exception as e:
            print(f"Error in broadcast: {e}")
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_joined')
def handle_user_joined(data):
    client_id = request.sid
    if client_id in connected_clients:
        connected_clients[client_id]['username'] = data.get('username', 'Anonymous')
        
        # Notify all clients about the update
        emit('client_update', {
            'count': len(connected_clients),
            'clients': list(connected_clients.values())
        }, broadcast=True)
        
# Socket event handlers remain the same as in your original app.py
@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    connected_clients[client_id] = {
        'id': client_id,
        'username': 'Anonymous',  # Default username
        'connected_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if len(connected_clients) > Config.MAX_CLIENTS:
        return False
        
    if len(connected_clients) == 1:
        if not detector.start_camera():
            print("Failed to start camera")
        else:
            print("Camera started successfully")
    
    emit('client_update', {
        'count': len(connected_clients),
        'clients': list(connected_clients.values())
    }, broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(data):
    emit('chat_message', {
        'username': data['username'],
        'message': data['message']
    }, broadcast=True)
    
@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
        
    if len(connected_clients) == 0:
        detector.stop_camera()
        print("Camera stopped - no clients connected")
    
    emit('client_update', {
        'count': len(connected_clients),
        'clients': list(connected_clients.values())
    }, broadcast=True)

@socketio.on('toggle_processing')
def handle_toggle_processing(enabled):
    global processing_enabled
    processing_enabled = True
    detector.toggle_detection(enabled)
    emit('processing_status', {'enabled': enabled}, broadcast=True)

@socketio.on('start_recording')
def handle_start_recording():
    if not detector.recording:
        filename = VideoUtils.generate_filename()
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        detector.start_recording(output_path)
        emit('recording_status', {'status': 'started', 'filename': filename})

@socketio.on('stop_recording')
def handle_stop_recording():
    if detector.recording:
        detector.stop_recording()
        emit('recording_status', {'status': 'stopped'})

def start_server():
    broadcast_thread = threading.Thread(target=broadcast_frames, daemon=True)
    broadcast_thread.start()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    start_server()