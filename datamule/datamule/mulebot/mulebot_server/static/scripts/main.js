// main.js
import { appendMessage, sendMessage, handleResponse } from './chat.js';
import { initializeArtifacts } from './artifacts.js';
import { handleDocumentClick } from './tableArtifacts.js';
import { initializeSuggestions } from './suggestions.js';

function initializeChat() {
    initializeArtifacts();
    initializeSuggestions();

    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = userInput.value.trim();
            if (message) {
                appendMessage('You', message);
                userInput.value = '';
                const response = await sendMessage(message);
                handleResponse(response);
            }
        });
    }

    document.addEventListener('click', handleDocumentClick);
}

// Wait for the DOM to be fully loaded before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChat);
} else {
    initializeChat();
}