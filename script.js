// script.js - Para a interface de CHAT conversacional

// Obter referências para os elementos HTML
const chatHistory = document.getElementById('chatHistory'); // Onde as mensagens aparecem
const userMessageInput = document.getElementById('userMessage'); // Campo de input do usuário
const sendButton = document.getElementById('generateButton'); // Botão de enviar

// Função para adicionar uma mensagem ao histórico do chat
// type pode ser 'user' ou 'ai' para aplicar os estilos CSS corretos
function addMessageToChat(message, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add(type + '-message'); // Adiciona classe 'user-message' ou 'ai-message'
    messageElement.innerHTML = `<p>${message}</p>`; // Usa innerHTML para permitir quebras de linha, etc.

    chatHistory.appendChild(messageElement); // Adiciona a nova mensagem ao final do histórico

    // Rolagem automática para a mensagem mais recente
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Função assíncrona para enviar a mensagem para o backend e receber a resposta
async function sendMessage() {
    const userMessage = userMessageInput.value.trim(); // Pega o texto e remove espaços extras

    // Não faz nada se a mensagem estiver vazia
    if (userMessage === '') {
        return;
    }

    // 1. Adicionar a mensagem do usuário ao chat
    addMessageToChat(userMessage, 'user');

    // 2. Limpar o campo de input
    userMessageInput.value = '';

    // 3. Desabilitar o input e o botão enquanto espera a resposta
    userMessageInput.disabled = true;
    sendButton.disabled = true;

    // Opcional: Adicionar um indicador visual que o bot está "digitando"
    // addMessageToChat('...', 'ai'); // Pode adicionar um balão temporário ou usar um CSS loading indicator

    // --- AGORA, ENVIAR ESSA MENSAGEM PARA O BACKEND ---

    try {
        // Usar fetch para enviar a mensagem para o backend
        // A URL '/chat' é um exemplo, você definirá isso no seu Flask/FastAPI
        const response = await fetch('http://127.0.0.1:5000/chat', { // <--- URL do seu endpoint no backend
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage }) // Envia a mensagem do usuário como JSON
        });

        // Verificar se a resposta foi bem sucedida
        if (!response.ok) {
            // Se houver erro HTTP (ex: 404, 500), tentar ler a resposta de erro do backend
            let errorMsg = `Erro no backend: Status ${response.status}`;
             try {
                 const errorData = await response.json();
                 if (errorData.error) {
                     errorMsg = `Erro do Backend: ${errorData.error}`;
                 } else if (errorData.message) { // Backend pode retornar 'message' para erros também
                      errorMsg = `Erro do Backend: ${errorData.message}`;
                 }
             } catch (e) {
                 // Se não conseguir ler o JSON de erro, usa a mensagem padrão
                 console.error("Erro ao parsear resposta de erro:", e);
             }
            throw new Error(errorMsg);
        }

        // Pegar a resposta JSON do backend
        const result = await response.json(); // Esperamos um JSON como { "reply": "..." }

        // Opcional: Remover o indicador "digitando" se você adicionou um
        // (Precisa de lógica para encontrar e remover o último balão AI temporário)

        // 4. Adicionar a resposta do bot ao chat
        // Assumindo que o backend retorna a resposta na chave 'reply'
        const botReply = result.reply || "Desculpe, não recebi uma resposta válida do bot."; // Fallback caso a chave 'reply' não exista
        addMessageToChat(botReply, 'ai');

    } catch (error) {
        // Lidar com erros de rede ou erros do backend
        console.error("Erro na comunicação com o backend:", error);
        addMessageToChat(`❌ Erro: Não foi possível conectar ao servidor ou processar a resposta. (${error.message})`, 'ai');

    } finally {
        // 5. Reabilitar o input e o botão
        userMessageInput.disabled = false;
        sendButton.disabled = false;
        userMessageInput.focus(); // Coloca o foco de volta no campo de input
    }
}

// Adicionar o "ouvinte" de evento ao botão
sendButton.addEventListener('click', sendMessage);

// Opcional: Permite enviar a mensagem pressionando Enter no campo de input
userMessageInput.addEventListener('keypress', function(event) {
    // Verifica se a tecla pressionada foi Enter (código 13) e se Shift NÃO foi pressionado (para permitir Shift+Enter para nova linha)
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Impede a quebra de linha padrão do Enter na textarea
        sendMessage(); // Chama a função de enviar mensagem
    }
});

// Adicionar uma mensagem inicial do bot ao carregar a página
// A mensagem inicial já está no HTML, então não precisamos adicionar aqui, a menos que queira fazer dinamicamente.
// addMessageToChat('Olá! Qual conceito técnico você gostaria de entender hoje?', 'ai');