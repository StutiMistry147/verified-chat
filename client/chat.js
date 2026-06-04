let currentWebSocket = null;
let currentChannel = null;
let messageHandlers = [];
let statusHandlers = [];

export function onMessage(handler) {
    messageHandlers.push(handler);
}

export function onConnectionStatus(handler) {
    statusHandlers.push(handler);
}

function notifyStatusHandlers(status, channel) {
    statusHandlers.forEach(handler => handler(status, channel));
}

function notifyMessageHandlers(message) {
    messageHandlers.forEach(handler => handler(message));
}

export function connectToChannel(channelName, token) {
    // Close existing connection if any
    if (currentWebSocket) {
        currentWebSocket.close();
        currentWebSocket = null;
    }

    currentChannel = channelName;
    notifyStatusHandlers('connecting', channelName);
    
    const wsUrl = `ws://localhost:8000/ws/${channelName}?token=${token}`;
    currentWebSocket = new WebSocket(wsUrl);

    currentWebSocket.onopen = () => {
        console.log(`Connected to channel: ${channelName}`);
        notifyStatusHandlers('connected', channelName);
    };

    currentWebSocket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            notifyMessageHandlers(message);
        } catch (error) {
            console.error('Failed to parse message:', error);
        }
    };

    currentWebSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        notifyStatusHandlers('error', channelName);
    };

    currentWebSocket.onclose = (event) => {
        console.log(`Disconnected from channel: ${channelName}`, event.code, event.reason);
        if (event.code === 1008) {
            notifyStatusHandlers('auth-failed', channelName);
            alert(`Authentication failed: ${event.reason}. Please login again.`);
        } else {
            notifyStatusHandlers('disconnected', channelName);
        }
    };
}

export function sendMessage(content) {
    if (!currentWebSocket || currentWebSocket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not connected');
        return false;
    }

    const payload = JSON.stringify({ content });
    currentWebSocket.send(payload);
    return true;
}

export function getCurrentChannel() {
    return currentChannel;
}

export async function loadChannels(token) {
    try {
        const response = await fetch('http://localhost:8000/channels/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load channels');
        }

        return await response.json();
    } catch (error) {
        console.error('Load channels error:', error);
        return [];
    }
}

export function disconnect() {
    if (currentWebSocket) {
        currentWebSocket.close();
        currentWebSocket = null;
    }
    currentChannel = null;
    notifyStatusHandlers('disconnected', null);
}

export function isConnected() {
    return currentWebSocket && currentWebSocket.readyState === WebSocket.OPEN;
}
