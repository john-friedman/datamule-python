// chat.js
import { renderArtifact, showArtifacts } from './artifacts.js';

let thinkingIndicator = null;

export function appendMessage(sender, message) {
    const chatContainer = document.getElementById('chat-container');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatContainer.appendChild(messageElement);
    scrollChatToBottom();
}

function scrollChatToBottom() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

export function showThinkingIndicator() {
    if (!thinkingIndicator) {
        thinkingIndicator = document.createElement('div');
        thinkingIndicator.className = 'thinking-indicator';
        thinkingIndicator.innerHTML = '<span>Bot is thinking</span><span class="dot-animation">...</span>';
        document.getElementById('chat-container').appendChild(thinkingIndicator);
    }
    thinkingIndicator.style.display = 'block';
    scrollChatToBottom();
}

export function hideThinkingIndicator() {
    if (thinkingIndicator) {
        thinkingIndicator.style.display = 'none';
    }
}

export async function sendMessage(message) {
    showThinkingIndicator();
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        return response.json();
    } finally {
        hideThinkingIndicator();
    }
}

export function handleResponse(response) {
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