class StreamViewer {
    constructor() {
        this.socket = io();
        this.streamImage = document.getElementById('streamImage');
        this.username = '';
        this.setupUsernameModal();
    }
    
    setupUsernameModal() {
        const usernameInput = document.getElementById('usernameInput');
        const joinButton = document.getElementById('joinStream');
        const modal = document.getElementById('usernameModal');
        const container = document.querySelector('.container');
        
        const joinStream = () => {
            const username = usernameInput.value.trim();
            if (username) {
                this.username = username;
                modal.style.display = 'none';
                container.style.display = 'grid';
                this.initializeConnection();
            } else {
                usernameInput.classList.add('error');
            }
        };
        
        joinButton.onclick = joinStream;
        usernameInput.onkeypress = (e) => {
            if (e.key === 'Enter') joinStream();
        };
        
        // Remove error class when typing
        usernameInput.oninput = () => {
            usernameInput.classList.remove('error');
        };
    }
    
    initializeConnection() {
        this.setupSocketHandlers();
        this.setupControls();
        this.setupChat();
    }
    
    setupSocketHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.socket.emit('user_joined', { username: this.username });
            this.addChatMessage('System', 'Connected to stream');
        });
        
        this.socket.on('processed_frame', (data) => {
            this.streamImage.src = data.frame;
            document.getElementById('faceCount').textContent = 
                `Faces Detected: ${data.num_faces}`;
        });
        
        this.socket.on('client_update', (data) => {
            document.getElementById('clientCount').textContent = 
                `Total Viewers: ${data.count}`;
            
            const clientList = document.getElementById('clientList');
            clientList.innerHTML = data.clients.map(client => {
                const initials = client.username ? client.username.charAt(0).toUpperCase() : '?';
                return `
                    <div class="client-item">
                        <div class="user-avatar">${initials}</div>
                        <div>
                            <div>${client.username || 'Anonymous'}</div>
                            <small>Joined: ${client.connected_at}</small>
                        </div>
                    </div>
                `;
            }).join('');
        });
        
        this.socket.on('chat_message', (data) => {
            this.addChatMessage(data.username, data.message);
        });
        
        this.socket.on('recording_status', (data) => {
            const startBtn = document.getElementById('startRecording');
            const stopBtn = document.getElementById('stopRecording');
            const indicator = document.getElementById('recordingIndicator');
            
            if (data.status === 'started') {
                startBtn.disabled = true;
                stopBtn.disabled = false;
                indicator.classList.add('active');
                this.addChatMessage('System', 'Recording started');
            } else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
                indicator.classList.remove('active');
                this.addChatMessage('System', 'Recording stopped');
            }
        });
    }
    
    setupControls() {
        document.getElementById('toggleProcessing').onclick = () => {
            const statusBadge = document.getElementById('detectionStatus');
            const isEnabled = statusBadge.textContent === 'Detection: ON';
            const newState = !isEnabled;
            
            this.socket.emit('toggle_processing', newState);
            statusBadge.textContent = newState ? 'Detection: ON' : 'Detection: OFF';
            this.addChatMessage('System', `Detection ${newState ? 'enabled' : 'disabled'}`);
        };
        
        document.getElementById('startRecording').onclick = () => {
            this.socket.emit('start_recording');
        };
        
        document.getElementById('stopRecording').onclick = () => {
            this.socket.emit('stop_recording');
        };
    }
    
    setupChat() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendMessage');
        
        const sendMessage = () => {
            const message = chatInput.value.trim();
            if (message) {
                this.socket.emit('chat_message', {
                    username: this.username,
                    message: message
                });
                chatInput.value = '';
            }
        };
        
        sendButton.onclick = sendMessage;
        chatInput.onkeypress = (e) => {
            if (e.key === 'Enter') sendMessage();
        };
    }
    
    addChatMessage(username, message) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';
        messageDiv.innerHTML = `
            <span class="author">${username}:</span>
            <span class="message">${message}</span>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

window.onload = () => {
    new StreamViewer();
};