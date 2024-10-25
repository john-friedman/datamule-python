// main.js
import { appendMessage, sendMessage, handleResponse, showThinkingIndicator, hideThinkingIndicator } from './chat.js';
import { initializeArtifacts } from './artifacts.js';
import { handleDocumentClick } from './tableArtifacts.js';
import { initializeSuggestions } from './suggestions.js';
import { handlePrefilledPrompt } from './prefilledPrompt.js';

let chatInitialized = false;

function initializeChat() {
    if (chatInitialized) return;
    chatInitialized = true;

    console.log('Initializing chat');

    initializeArtifacts();
    initializeSuggestions();

    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Form submitted');
            const message = userInput.value.trim();
            if (message) {
                appendMessage('You', message);
                userInput.value = '';
                showThinkingIndicator();
                try {
                    const response = await sendMessage(message);
                    handleResponse(response);
                } catch (error) {
                    console.error('Error processing message:', error);
                } finally {
                    hideThinkingIndicator();
                }
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

// Add this new event listener for the window load event
window.addEventListener('load', () => {
    console.log('Window fully loaded, handling prefilled prompt');
    handlePrefilledPrompt();
});