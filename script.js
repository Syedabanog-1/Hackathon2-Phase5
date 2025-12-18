document.addEventListener('DOMContentLoaded', function() {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const todoItems = document.getElementById('todo-items');

    // Replace with your Railway backend URL when deployed
    const BACKEND_URL = 'https://your-railway-app-url.railway.app'; // Placeholder - update after deploying to Railway

    // Function to add a message to the chat
    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');

        const strong = document.createElement('strong');
        strong.textContent = isUser ? 'You:' : 'Bot:';

        const textNode = document.createTextNode(' ' + text);

        messageDiv.appendChild(strong);
        messageDiv.appendChild(textNode);

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Function to get todos from backend
    async function getTodos() {
        try {
            const response = await fetch(`${BACKEND_URL}/api/todos`);
            if (response.ok) {
                const todos = await response.json();
                updateTodoList(todos);
            } else {
                console.error('Failed to fetch todos:', response.status);
            }
        } catch (error) {
            console.error('Error fetching todos:', error);
        }
    }

    // Function to update the todo list display
    function updateTodoList(todos) {
        todoItems.innerHTML = '';
        if (Array.isArray(todos)) {
            todos.forEach(todo => {
                const li = document.createElement('li');
                li.textContent = `${todo.title} ${todo.completed ? '(Completed)' : ''}`;
                todoItems.appendChild(li);
            });
        }
    }

    // Function to send message to backend
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';

        try {
            // Send message to backend
            const response = await fetch(`${BACKEND_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            if (response.ok) {
                const data = await response.json();

                // Add bot response to chat
                if (data.response) {
                    addMessage(data.response, false);
                }

                // Update todo list if included in response
                if (data.todos) {
                    updateTodoList(data.todos);
                }
            } else {
                addMessage('Sorry, there was an error processing your request.', false);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('Sorry, there was an error connecting to the server.', false);
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Initialize by getting current todos
    getTodos();
});