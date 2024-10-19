// prefilledPrompt.js
import { sendMessage, handleResponse, appendMessage } from './chat.js';

export function handlePrefilledPrompt() {
    const urlParams = new URLSearchParams(window.location.search);
    const prefilled_prompt = urlParams.get('prompt');
    if (prefilled_prompt) {
        const userInput = document.getElementById('user-input');
        if (userInput) {
            userInput.value = prefilled_prompt;
            appendMessage('You', prefilled_prompt); // Show the user's message in the chat
        }
        if (typeof sendMessage === 'function') {
            sendMessage(prefilled_prompt).then(response => {
                handleResponse(response);
                if (userInput) {
                    userInput.value = ''; // Clear the input field after sending
                }
            }).catch(error => {
                console.error('Error processing prefilled prompt:', error);
                if (userInput) {
                    userInput.value = ''; // Clear the input field even if there's an error
                }
            });
        }
    }
}