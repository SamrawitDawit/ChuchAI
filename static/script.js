function navigateToChat(){
    window.location.href = '/chat';
}
function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim()) {
        const messagesDiv = document.getElementById('messages');
        const userMessage = document.createElement('div');
        userMessage.classList.add('message', 'user');
        userMessage.textContent = userInput;
        messagesDiv.appendChild(userMessage);

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => response.json())
        .then(data => {
            const botMessage = document.createElement('div');
            botMessage.classList.add('message');
            if (data.response) {
                botMessage.textContent = data.response;
            } else if (data.problem) {
                botMessage.textContent = data.problem + " Answer: " + data.answer;
            }
            messagesDiv.appendChild(botMessage);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });

        document.getElementById('userInput').value = '';
    }
}