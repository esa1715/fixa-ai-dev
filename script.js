
const chatHistory = document.getElementById('chatHistory');
const userMessageInput = document.getElementById('userMessage');
const sendButton = document.getElementById('generateButton');

function addMessageToChat(message, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add(type + '-message');
    messageElement.innerHTML = `<p>${message}</p>`;

    chatHistory.appendChild(messageElement);

    chatHistory.scrollTop = chatHistory.scrollHeight;
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


    try {
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        });

        if (!response.ok) {
            let errorMsg = `Erro no backend: Status ${response.status}`;
             try {
                 const errorData = await response.json();
                 if (errorData.error) {
                     errorMsg = `Erro do Backend: ${errorData.error}`;
                 } else if (errorData.message) {
                      errorMsg = `Erro do Backend: ${errorData.message}`;
                 }
             } catch (e) {
                 console.error("Erro ao parsear resposta de erro:", e);
             }
            throw new Error(errorMsg);
        }

        const result = await response.json();

        const botReply = result.reply || "Desculpe, não recebi uma resposta válida do bot.";
        addMessageToChat(botReply, 'ai');

    } catch (error) {
        console.error("Erro na comunicação com o backend:", error);
        addMessageToChat(`❌ Erro: Não foi possível conectar ao servidor ou processar a resposta. (${error.message})`, 'ai');

    } finally {
        userMessageInput.disabled = false;
        sendButton.disabled = false;
        userMessageInput.focus();
    }
}

sendButton.addEventListener('click', sendMessage);

userMessageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});