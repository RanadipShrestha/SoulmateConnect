function initializeWebSocket(receiverId, userId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/chat/${receiverId}/`);

    socket.onopen = function() {
        console.log('WebSocket connected');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const messagesDiv = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', data.sender === document.getElementById('chat-messages').dataset.username ? 'sent' : 'received');
        messageDiv.innerHTML = `
            <p><strong>${data.sender}</strong>: ${data.message}</p>
            <span>${new Date(data.timestamp).toLocaleString()}</span>
        `;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };

    socket.onclose = function() {
        console.log('WebSocket closed');
    };

    document.getElementById('send-button').onclick = function() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        if (message) {
            socket.send(JSON.stringify({ message }));
            input.value = '';
        }
    };

    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('send-button').click();
        }
    });
}