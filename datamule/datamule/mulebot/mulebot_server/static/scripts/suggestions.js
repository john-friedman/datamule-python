// suggestions.js

document.addEventListener('DOMContentLoaded', function () {
    const userInput = document.getElementById('user-input');
    const chatForm = document.getElementById('chat-form');
    const suggestionItems = document.querySelectorAll('.suggestion-item');

    // Function to handle suggestion click
    function handleSuggestionClick(event) {
        const suggestionText = event.target.textContent;
        userInput.value = suggestionText;
        executeChatRequest(suggestionText);
        userInput.value = ''; // Clear the input after executing the request
    }

    // Add click event listeners to all suggestion items
    suggestionItems.forEach(item => {
        item.addEventListener('click', handleSuggestionClick);
    });

    // Function to execute chat request
    async function executeChatRequest(message) {
        try {
            appendMessage('You', message); // Add user message to chat
            const response = await sendMessage(message);
            handleResponse(response);
        } catch (error) {
            console.error('Error executing chat request:', error);
            appendMessage('Bot', 'Sorry, there was an error processing your request.');
        }
    }

    // Reuse the sendMessage function from the main script
    async function sendMessage(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        return response.json();
    }

    // Reuse the handleResponse function from the main script
    function handleResponse(response) {
        if (response.response.type === 'text') {
            appendMessage('Bot', response.response.content);
        } else if (response.response.type === 'artifact') {
            let artifactType = response.response.artifact_type;
            let artifactContent = response.response.content;

            if (artifactType === 'artifact-filing') {
                artifactContent = {
                    content: response.response.content,
                    data: response.response.data,
                    section_id: response.response.section_id
                };
            }

            appendMessage('Bot', `I have prepared an ${artifactType} for you. Please check the artifact view.`);
            renderArtifact(artifactContent, artifactType);
            showArtifacts();
        } else {
            appendMessage('Bot', 'I have received a response, but it is not a supported type.');
        }
    }

    // Reuse the appendMessage function from the main script
    function appendMessage(sender, message) {
        const chatContainer = document.getElementById('chat-container');
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Note: You'll need to make sure the renderArtifact and showArtifacts functions
    // are available in the global scope or imported properly

    // Prevent default form submission
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            executeChatRequest(message);
            userInput.value = ''; // Clear the input after executing the request
        }
    });
});