const chatHistory = document.getElementById('chatHistory');
const userMessageInput = document.getElementById('userMessage');
const sendButton = document.getElementById('generateButton');
const statusArea = document.getElementById('statusArea');

function addMessageToChat(message, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add(type + '-message');
    messageElement.innerHTML = `<p>${message}</p>`;

    chatHistory.appendChild(messageElement);

    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function updateStatusArea(message) {
    statusArea.innerHTML = `<p>${message}</p>`;
    statusArea.style.display = 'block';
}

function clearStatusArea() {
    statusArea.innerHTML = '';
    statusArea.style.display = 'none';
}

function enableInput() {
    userMessageInput.disabled = false;
    sendButton.disabled = false;
    userMessageInput.focus();
}

async function sendMessage() {
    const userMessage = userMessageInput.value.trim();

    if (userMessage === '') {
        return;
    }

    addMessageToChat(userMessage, 'user');

userMessageInput.value = '';
userMessageInput.disabled = true;
sendButton.disabled = true;
clearStatusArea();

try {
    const encodedMessage = encodeURIComponent(userMessage);
        const eventSource = new EventSource(`http://127.0.0.1:5000/stream?message=${encodedMessage}`);

        eventSource.onmessage = function(event) {
            console.log("Evento SSE recebido:", event.data);
            const data = JSON.parse(event.data);

            if (data.type === 'progress') {
                updateStatusArea(data.message);

            } else if (data.type === 'final') {
                addMessageToChat(data.reply, 'ai');
                clearStatusArea();
                enableInput();
                eventSource.close();

            } else if (data.type === 'error') {
                addMessageToChat(`❌ Erro do Backend: ${data.message}`, 'ai');
                clearStatusArea();
                enableInput();
                eventSource.close();
            }
        };

        eventSource.onerror = function(event) {
            console.error("Erro no EventSource:", event);
            let errorMessage = "Erro na comunicação com o servidor.";

            if (event.target && event.target.readyState === EventSource.CLOSED) {
                errorMessage = "Conexão com o servidor foi fechada inesperadamente.";
            } else if (event.message) {
                 errorMessage = `Erro: ${event.message}`;
            }

            addMessageToChat(`❌ Erro: ${errorMessage}. Tente novamente.`, 'ai');
            clearStatusArea();
            enableInput();
            eventSource.close();
        };

    } catch (error) {
        console.error("Erro ao iniciar EventSource:", error);
        addMessageToChat(`❌ Erro fatal ao iniciar a comunicação: ${error.message}`, 'ai');
        clearStatusArea();
        enableInput();
    }
}

sendButton.addEventListener('click', sendMessage);

userMessageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});