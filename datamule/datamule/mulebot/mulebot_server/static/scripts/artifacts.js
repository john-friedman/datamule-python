// artifacts.js
import { renderTableArtifact, handleArtifactSelectInput, handleArtifactSelectFocus, handleDocumentClick } from './tableArtifacts.js';
import { renderListArtifact } from './listArtifacts.js';
import { renderFilingArtifact } from './filingArtifacts.js';

export let artifactContent = null;
export let artifactContainer = null;
export let suggestionContainer = null;
export let toggleArtifactsBtn = null;
export let allArtifacts = [];

function debugLog(message, data = null) {
    console.log(`[Debug ${new Date().toISOString()}] ${message}`, data);
}

export function initializeArtifacts() {
    artifactContent = document.getElementById('artifact-content');
    artifactContainer = document.getElementById('artifact-container');
    suggestionContainer = document.getElementById('suggestion-container');
    toggleArtifactsBtn = document.getElementById('toggle-artifacts');

    setupArtifactEventListeners();
    debugLog('Artifacts initialized', {
        artifactContent: !!artifactContent,
        artifactContainer: !!artifactContainer,
        suggestionContainer: !!suggestionContainer,
        toggleArtifactsBtn: !!toggleArtifactsBtn
    });
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
    debugLog('Artifact event listeners set up');
}

export function renderArtifact(artifactData, artifactType) {
    debugLog('Rendering artifact', { type: artifactType, data: artifactData });

    if (artifactType === 'artifact-table') {
        const newArtifacts = Array.isArray(artifactData) ? artifactData : [artifactData];
        newArtifacts.forEach(artifact => {
            artifact.type = artifactType;
            debugLog('Processing artifact', artifact);
        });
        allArtifacts = [...allArtifacts, ...newArtifacts];
        debugLog('Updated allArtifacts', allArtifacts.map(a => ({ fact: a.fact, type: a.type })));
        renderTableArtifact(artifactData[0]);
    }
    else if (artifactType === 'artifact-list') {
        renderListArtifact(artifactData);
    }
    else if (artifactType === 'artifact-filing') {
        renderFilingArtifact(artifactData);
    }
    else {
        debugLog('Unsupported artifact type', artifactType);
    }
}

export function showArtifacts() {
    if (artifactContainer && suggestionContainer && toggleArtifactsBtn) {
        artifactContainer.style.display = 'block';
        suggestionContainer.style.display = 'none';
        toggleArtifactsBtn.textContent = 'Hide Artifacts';
        debugLog('Artifacts shown');
    } else {
        debugLog('Error: Could not show artifacts', {
            artifactContainer: !!artifactContainer,
            suggestionContainer: !!suggestionContainer,
            toggleArtifactsBtn: !!toggleArtifactsBtn
        });
    }
}

export function hideArtifacts() {
    if (artifactContainer && suggestionContainer && toggleArtifactsBtn) {
        artifactContainer.style.display = 'none';
        suggestionContainer.style.display = 'block';
        toggleArtifactsBtn.textContent = 'Show Artifacts';
        debugLog('Artifacts hidden');
    } else {
        debugLog('Error: Could not hide artifacts', {
            artifactContainer: !!artifactContainer,
            suggestionContainer: !!suggestionContainer,
            toggleArtifactsBtn: !!toggleArtifactsBtn
        });
    }
}