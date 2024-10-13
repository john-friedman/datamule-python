// main.js
import { appendMessage, sendMessage, handleResponse } from './chat.js';
import { showArtifacts, hideArtifacts, initializeArtifacts } from './artifacts.js';

export let chatContainer;

function initializeChat() {
    chatContainer = document.getElementById('chat-container');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const toggleArtifactsBtn = document.getElementById('toggle-artifacts');

    initializeArtifacts();

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

    if (toggleArtifactsBtn) {
        toggleArtifactsBtn.addEventListener('click', () => {
            const artifactContainer = document.getElementById('artifact-container');
            if (artifactContainer.style.display === 'none') {
                showArtifacts();
            } else {
                hideArtifacts();
            }
        });
    }

    // Initially hide artifacts
    hideArtifacts();
}

// Wait for the DOM to be fully loaded before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChat);
} else {
    initializeChat();
}