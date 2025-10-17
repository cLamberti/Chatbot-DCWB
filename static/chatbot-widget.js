(function() {
    // Estilos del widget
    const styles = `
        #dcwb-chat-button {
            position: fixed;
            bottom: 20px;
            right: 90px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        #dcwb-chat-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        #dcwb-chat-button svg {
            width: 30px;
            height: 30px;
            fill: white;
        }

        #dcwb-chat-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
            display: none;
            flex-direction: column;
            z-index: 9998;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        #dcwb-chat-window.active {
            display: flex;
            animation: dcwbSlideUp 0.3s ease;
        }

        @keyframes dcwbSlideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .dcwb-chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .dcwb-chat-header-content h3 {
            font-size: 18px;
            font-weight: 600;
            margin: 0 0 4px 0;
        }

        .dcwb-chat-header-content p {
            font-size: 12px;
            opacity: 0.9;
            margin: 0;
        }

        .dcwb-close-btn {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            transition: transform 0.2s;
        }

        .dcwb-close-btn:hover {
            transform: rotate(90deg);
        }

        #dcwb-chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f5f5f5;
        }

        #dcwb-chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        #dcwb-chat-messages::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        #dcwb-chat-messages::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 3px;
        }

        .dcwb-message {
            margin-bottom: 15px;
            display: flex;
            animation: dcwbSlideIn 0.3s ease;
        }

        @keyframes dcwbSlideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .dcwb-message.user {
            justify-content: flex-end;
        }

        .dcwb-message-content {
            max-width: 75%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
            font-size: 14px;
        }

        .dcwb-message.bot .dcwb-message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .dcwb-message.user .dcwb-message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .dcwb-typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            width: fit-content;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .dcwb-typing-indicator.active {
            display: block;
        }

        .dcwb-typing-indicator span {
            height: 8px;
            width: 8px;
            background: #667eea;
            border-radius: 50%;
            display: inline-block;
            margin-right: 4px;
            animation: dcwbTyping 1.4s infinite;
        }

        .dcwb-typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .dcwb-typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes dcwbTyping {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }

        .dcwb-chat-input-container {
            padding: 15px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }

        #dcwb-user-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        #dcwb-user-input:focus {
            border-color: #667eea;
        }

        #dcwb-send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        #dcwb-send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        #dcwb-send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        @media (max-width: 480px) {
            #dcwb-chat-button {
                right: 20px;
                bottom: 90px;
            }

            #dcwb-chat-window {
                width: calc(100% - 20px);
                height: calc(100% - 100px);
                right: 10px;
                bottom: 160px;
            }
        }
    `;

    // Inyectar estilos
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // HTML del widget
    const widgetHTML = `
        <button id="dcwb-chat-button" aria-label="Abrir chat">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
            </svg>
        </button>

        <div id="dcwb-chat-window">
            <div class="dcwb-chat-header">
                <div class="dcwb-chat-header-content">
                    <h3>💻 DCWB</h3>
                    <p>Diseño y Creación Web Bijagua</p>
                </div>
                <button class="dcwb-close-btn" id="dcwb-close-chat">&times;</button>
            </div>

            <div id="dcwb-chat-messages">
                <div class="dcwb-message bot">
                    <div class="dcwb-message-content">
                        ¡Hola! 👋 Bienvenido a Diseño y Creación Web Bijagua (DCWB). Somos Christopher y Atilio, y estamos aquí para ayudarte a crear tu página web ideal. ¿En qué podemos ayudarte hoy?
                    </div>
                </div>
            </div>

            <div class="dcwb-chat-input-container">
                <input type="text" id="dcwb-user-input" placeholder="Escribe tu mensaje..." />
                <button id="dcwb-send-btn">Enviar</button>
            </div>
        </div>
    `;

    // Insertar widget en el DOM
    document.addEventListener('DOMContentLoaded', function() {
        const container = document.createElement('div');
        container.innerHTML = widgetHTML;
        document.body.appendChild(container);

        // Variables
        const chatButton = document.getElementById('dcwb-chat-button');
        const chatWindow = document.getElementById('dcwb-chat-window');
        const closeChat = document.getElementById('dcwb-close-chat');
        const userInput = document.getElementById('dcwb-user-input');
        const sendBtn = document.getElementById('dcwb-send-btn');
        const chatMessages = document.getElementById('dcwb-chat-messages');

        // Event listeners
        chatButton.addEventListener('click', () => {
            chatWindow.classList.toggle('active');
            if (chatWindow.classList.contains('active')) {
                userInput.focus();
            }
        });

        closeChat.addEventListener('click', () => {
            chatWindow.classList.remove('active');
        });

        // Typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'dcwb-typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';

        // Función para enviar mensaje
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            userInput.value = '';
            sendBtn.disabled = true;

            chatMessages.appendChild(typingIndicator);
            typingIndicator.classList.add('active');
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const response = await fetch('http://127.0.0.1:5000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();

                typingIndicator.classList.remove('active');
                addMessage(data.reply, 'bot');
            } catch (error) {
                typingIndicator.classList.remove('active');
                addMessage('Lo siento, ocurrió un error. Por favor, intentá de nuevo.', 'bot');
            } finally {
                sendBtn.disabled = false;
                userInput.focus();
            }
        }

        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `dcwb-message ${sender}`;
            messageDiv.innerHTML = `<div class="dcwb-message-content">${text}</div>`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    });
})();