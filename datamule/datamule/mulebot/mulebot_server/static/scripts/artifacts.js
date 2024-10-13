// artifacts.js
import { renderTableArtifact } from './tableArtifacts.js';
import { renderListArtifact } from './listArtifacts.js';
import { renderFilingArtifact } from './filingArtifacts.js';
import { handleArtifactSelectInput, handleArtifactSelectFocus, handleDocumentClick } from './tableArtifacts.js';

export let artifactContent = null;
export let artifactContainer = null;
export let suggestionContainer = null;
export let toggleArtifactsBtn = null;
export let allArtifacts = [];

export function initializeArtifacts() {
    artifactContent = document.getElementById('artifact-content');
    artifactContainer = document.getElementById('artifact-container');
    suggestionContainer = document.getElementById('suggestion-container');
    toggleArtifactsBtn = document.getElementById('toggle-artifacts');

    setupArtifactEventListeners();
}

function setupArtifactEventListeners() {
    document.addEventListener('input', function (e) {
        if (e.target && e.target.id === 'artifact-select') {
            handleArtifactSelectInput(e);
        }
    });

    document.addEventListener('focus', function (e) {
        if (e.target && e.target.id === 'artifact-select') {
            handleArtifactSelectFocus(e);
        }
    }, true);

    document.addEventListener('click', handleDocumentClick);
}

export function renderArtifact(artifactData, artifactType) {
    console.log('Artifact type:', artifactType);
    console.log('Artifact data:', artifactData);

    if (artifactType === 'artifact-table') {
        const newArtifacts = Array.isArray(artifactData) ? artifactData : [artifactData];
        newArtifacts.forEach(artifact => {
            artifact.type = artifactType;
            console.log('Processed artifact:', artifact);
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
    if (artifactContainer && suggestionContainer && toggleArtifactsBtn) {
        artifactContainer.style.display = 'block';
        suggestionContainer.style.display = 'none';
        toggleArtifactsBtn.textContent = 'Hide Artifacts';
    }
}

export function hideArtifacts() {
    if (artifactContainer && suggestionContainer && toggleArtifactsBtn) {
        artifactContainer.style.display = 'none';
        suggestionContainer.style.display = 'block';
        toggleArtifactsBtn.textContent = 'Show Artifacts';
    }
}