// artifacts.js
import { renderTableArtifact } from './tableArtifacts.js';
import { renderListArtifact } from './listArtifacts.js';
import { renderFilingArtifact } from './filingArtifacts.js';

export let artifactContent = null;
export let artifactContainer = null;
export let suggestionContainer = null;
export let toggleArtifactsBtn = null;
export let allArtifacts = [];

export function initializeArtifacts() {
    artifactContent = document.getElementById('artifact-content');
    artifactContainer = document.getElementById('artifact-container');
    suggestionContainer = document.querySelector('.suggestion-box');
    toggleArtifactsBtn = document.getElementById('toggle-artifacts');

    if (toggleArtifactsBtn) {
        toggleArtifactsBtn.addEventListener('click', toggleArtifacts);
    }

    // Initially hide artifacts
    hideArtifacts();
}

export function renderArtifact(artifactData, artifactType) {
    if (artifactType === 'artifact-table') {
        const newArtifacts = Array.isArray(artifactData) ? artifactData : [artifactData];
        newArtifacts.forEach(artifact => {
            artifact.type = artifactType;
        });
        allArtifacts = [...allArtifacts, ...newArtifacts];
        renderTableArtifact(artifactData[0]);
    }
    else if (artifactType === 'artifact-list') {
        renderListArtifact(artifactData);
    }
    else if (artifactType === 'artifact-filing') {
        renderFilingArtifact(artifactData);
    }
    else {
        console.log('Unsupported artifact type:', artifactType);
    }
}

export function showArtifacts() {
    if (artifactContainer && suggestionContainer) {
        artifactContainer.style.display = 'block';
        suggestionContainer.style.display = 'none';
        if (toggleArtifactsBtn) toggleArtifactsBtn.textContent = 'Hide Artifacts';
    }
}

export function hideArtifacts() {
    if (artifactContainer && suggestionContainer) {
        artifactContainer.style.display = 'none';
        suggestionContainer.style.display = 'block';
        if (toggleArtifactsBtn) toggleArtifactsBtn.textContent = 'Show Artifacts';
    }
}

function toggleArtifacts() {
    if (artifactContainer.style.display === 'none') {
        showArtifacts();
    } else {
        hideArtifacts();
    }
}