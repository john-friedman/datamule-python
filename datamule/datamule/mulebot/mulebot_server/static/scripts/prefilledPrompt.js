// prefilledPrompt.js
import { sendMessage, handleResponse } from './chat.js';

export function handlePrefilledPrompt() {
    const urlParams = new URLSearchParams(window.location.search);
    const prefilled_prompt = urlParams.get('prompt');
    if (prefilled_prompt) {
        const userInput = document.getElementById('user-input');
        if (userInput) {
            userInput.value = prefilled_prompt;
        }
        if (typeof sendMessage === 'function') {
            sendMessage(prefilled_prompt).then(response => {
                handleResponse(response);
            }).catch(error => {
                console.error('Error processing prefilled prompt:', error);
            });
        }
    }
}