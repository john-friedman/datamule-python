// suggestions.js
import { appendMessage, sendMessage, handleResponse, showThinkingIndicator, hideThinkingIndicator } from './chat.js';
import { renderArtifact, showArtifacts } from './artifacts.js';

export function initializeSuggestions() {
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
            appendMessage('You', message);
            showThinkingIndicator();
            const response = await sendMessage(message);
            handleResponse(response);
        } catch (error) {
            console.error('Error executing chat request:', error);
            appendMessage('Bot', 'Sorry, there was an error processing your request.');
        } finally {
            hideThinkingIndicator();
        }
    }

    // Prevent default form submission
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            executeChatRequest(message);
            userInput.value = ''; // Clear the input after executing the request
        }
    });
}