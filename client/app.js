import { login, getToken, logout as authLogout, isAuthenticated } from './auth.js';
import { connectToChannel, sendMessage, loadChannels, onMessage, onConnectionStatus, disconnect, getCurrentChannel, isConnected } from './chat.js';

// DOM elements
const loginView = document.getElementById('login-view');
const chatView = document.getElementById('chat-view');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const channelsList = document.getElementById('channels-list');
const messagesContainer = document.getElementById('messages-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const currentChannelSpan = document.getElementById('current-channel');
const currentUsernameSpan = document.getElementById('current-username');
const connectionStatusSpan = document.getElementById('connection-status');

let currentUsername = null;

// Helper to render messages
function addMessageToUI(message, isOwn = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isOwn ? 'own-message' : 'other-message'}`;
    
    const timestamp = new Date(message.timestamp).toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-username">${escapeHtml(message.username)}</span>
            <span class="message-time">${timestamp}</span>
        </div>
        <div class="message-content">${escapeHtml(message.content)}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Simple escape to prevent XSS
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Update connection status in UI
function updateConnectionStatus(status, channel) {
    if (!connectionStatusSpan) return;
    
    connectionStatusSpan.className = `connection-status ${status}`;
    
    switch(status) {
        case 'connecting':
            connectionStatusSpan.textContent = 'Connecting...';
            break;
        case 'connected':
            connectionStatusSpan.textContent = '● Connected';
            break;
        case 'disconnected':
            connectionStatusSpan.textContent = '○ Disconnected';
            break;
        case 'error':
            connectionStatusSpan.textContent = '⚠ Connection Error';
            break;
        case 'auth-failed':
            connectionStatusSpan.textContent = '✗ Auth Failed';
            break;
        default:
            connectionStatusSpan.textContent = status;
    }
}

// Render channels in sidebar
function renderChannels(channels, currentChannelName) {
    channelsList.innerHTML = '';
    channels.forEach(channel => {
        const channelDiv = document.createElement('div');
        channelDiv.className = `channel-item ${channel.name === currentChannelName ? 'active' : ''}`;
        channelDiv.textContent = `# ${channel.name}`;
        channelDiv.addEventListener('click', async () => {
            const token = getToken();
            if (token && channel.name !== getCurrentChannel()) {
                messagesContainer.innerHTML = ''; // Clear messages when switching channels
                connectToChannel(channel.name, token);
                currentChannelSpan.textContent = channel.name;
                highlightActiveChannel(channel.name);
            }
        });
        channelsList.appendChild(channelDiv);
    });
}

function highlightActiveChannel(channelName) {
    const channelItems = document.querySelectorAll('.channel-item');
    channelItems.forEach(item => {
        const itemName = item.textContent.replace('# ', '');
        if (itemName === channelName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Switch between login and chat views
function showLoginView() {
    loginView.classList.add('active');
    chatView.classList.remove('active');
    usernameInput.value = '';
    passwordInput.value = '';
    messagesContainer.innerHTML = '';
}

function showChatView() {
    loginView.classList.remove('active');
    chatView.classList.add('active');
}

// Handle login
loginBtn.addEventListener('click', async () => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    
    if (!username || !password) {
        alert('Please enter username and password');
        return;
    }
    
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';
    
    const result = await login(username, password);
    
    if (result.success) {
        currentUsername = username;
        currentUsernameSpan.textContent = username;
        
        const token = getToken();
        const channels = await loadChannels(token);
        
        if (channels.length > 0) {
            renderChannels(channels, channels[0].name);
            connectToChannel(channels[0].name, token);
            currentChannelSpan.textContent = channels[0].name;
        }
        
        showChatView();
    } else {
        alert(`Login failed: ${result.error}`);
    }
    
    loginBtn.disabled = false;
    loginBtn.textContent = 'Login';
});

// Handle logout
logoutBtn.addEventListener('click', () => {
    disconnect();
    authLogout();
    currentUsername = null;
    messagesContainer.innerHTML = '';
    showLoginView();
});

// Handle sending messages
sendBtn.addEventListener('click', () => {
    const content = messageInput.value.trim();
    if (content && isAuthenticated()) {
        if (sendMessage(content)) {
            messageInput.value = '';
        } else {
            alert('Not connected to channel. Please wait for connection.');
        }
    }
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendBtn.click();
    }
});

// Register message handler
onMessage((message) => {
    const isOwn = message.username === currentUsername;
    addMessageToUI(message, isOwn);
});

// Register connection status handler
onConnectionStatus((status, channel) => {
    updateConnectionStatus(status, channel);
    
    // Enable/disable send button based on connection
    if (sendBtn) {
        sendBtn.disabled = (status !== 'connected');
    }
    
    // Show reconnection message if disconnected
    if (status === 'disconnected' && chatView.classList.contains('active')) {
        const statusMsg = document.createElement('div');
        statusMsg.className = 'system-message';
        statusMsg.textContent = '⚠ Disconnected from server. Please refresh the page.';
        messagesContainer.appendChild(statusMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});

// Initial view
showLoginView();
