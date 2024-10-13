// tableArtifacts.js
import { artifactContent, allArtifacts } from './artifacts.js';
import { renderMetadata, downloadCSV } from './utils.js';

let currentTableData = null;
let renderCount = 0;

function debugLog(message, data = null) {
    console.log(`[Debug ${new Date().toISOString()}] ${message}`, data);
}

export function renderTableArtifact(tableData) {
    renderCount++;
    debugLog(`Rendering table artifact (count: ${renderCount})`, tableData);
    currentTableData = tableData;
    let html = `
        <div class="mb-3 select-wrapper">
            <input type="text" id="artifact-select" class="form-control" placeholder="Select a table..." value="${tableData.fact}">
            <div id="autocomplete-list" class="autocomplete-items"></div>
        </div>
        <div class="mb-3">
            <button id="download-csv" class="btn btn-secondary me-2">Download Selected Table (CSV)</button>
            <button id="download-all-zip" class="btn btn-secondary">Download All Tables (ZIP)</button>
        </div>
        <div id="metadata-content"></div>
        <div id="debug-info"></div>
    `;

    if (tableData.table && tableData.table.length > 0) {
        html += '<table class="table table-striped mt-3"><thead><tr>';
        Object.keys(tableData.table[0]).forEach(header => {
            html += `<th>${header}</th>`;
        });
        html += '</tr></thead><tbody>';
        tableData.table.forEach(row => {
            html += '<tr>';
            Object.values(row).forEach(cell => {
                html += `<td>${cell}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
    } else {
        html += '<p>No table data available.</p>';
    }

    artifactContent.innerHTML = html;
    debugLog('HTML content set', html);
    renderMetadata(tableData);
    updateDebugInfo();
}

export function handleArtifactSelectInput(e) {
    debugLog('Artifact select input event', e.target.value);
    const val = e.target.value.toLowerCase();
    debugLog('All artifacts before filtering:', allArtifacts);
    const filteredArtifacts = allArtifacts.filter(artifact => {
        if (artifact && artifact.fact) {
            return artifact.fact.toLowerCase().includes(val);
        }
        return false;
    });
    debugLog('Filtered artifacts', filteredArtifacts);
    createAutocompleteList(filteredArtifacts);
}

export function handleArtifactSelectFocus() {
    debugLog('Artifact select focus event');
    createAutocompleteList(allArtifacts);
}

function handleDownloadCsv() {
    debugLog('Download CSV clicked', currentTableData);
    if (currentTableData) {
        downloadCSV(currentTableData);
    } else {
        alert('Please select a valid table first.');
    }
}

async function handleDownloadAllZip() {
    debugLog('Download all ZIP clicked');
    const tables = allArtifacts.filter(artifact => artifact.type === 'artifact-table');
    if (tables.length === 0) {
        alert('No tables available to download.');
        return;
    }
    // ... (rest of the function remains the same)
}

export function handleDocumentClick(e) {
    debugLog('Document clicked', e.target);
    if (e.target.id !== 'artifact-select') {
        closeAutocompleteList();
    }
}

function createAutocompleteList(filteredArtifacts) {
    debugLog('Creating autocomplete list', filteredArtifacts);
    const autocompleteList = document.getElementById('autocomplete-list');
    if (!autocompleteList) {
        debugLog('Error: autocompleteList element not found');
        return;
    }
    autocompleteList.innerHTML = '';
    autocompleteList.style.display = 'block';

    if (filteredArtifacts.length === 0) {
        const div = document.createElement("div");
        div.innerHTML = "No matching tables found";
        div.style.color = "#999";
        autocompleteList.appendChild(div);
    } else {
        filteredArtifacts.forEach(artifact => {
            const div = document.createElement("div");
            div.innerHTML = artifact.fact;
            div.addEventListener("click", function (e) {
                debugLog('Autocomplete item clicked', this.innerHTML);
                document.getElementById('artifact-select').value = this.innerHTML;
                const selectedArtifact = allArtifacts.find(a => a.fact === this.innerHTML);
                if (selectedArtifact) {
                    renderTableArtifact(selectedArtifact);
                }
                closeAutocompleteList();
            });
            autocompleteList.appendChild(div);
        });
    }
    debugLog('Autocomplete list created', autocompleteList.innerHTML);
}

function closeAutocompleteList() {
    debugLog('Closing autocomplete list');
    const autocompleteList = document.getElementById('autocomplete-list');
    if (autocompleteList) {
        autocompleteList.style.display = 'none';
    }
}

function updateDebugInfo() {
    const debugInfo = document.getElementById('debug-info');
    debugInfo.innerHTML = `
        <h4>Debug Info</h4>
        <p>Render Count: ${renderCount}</p>
        <p>Current Table: ${currentTableData ? currentTableData.fact : 'None'}</p>
        <p>Total Artifacts: ${allArtifacts.length}</p>
        <button onclick="window.testAutocomplete()">Test Autocomplete</button>
    `;
}

// Test function to simulate autocomplete behavior
window.testAutocomplete = function () {
    debugLog('Running autocomplete test');
    const artifactSelect = document.getElementById('artifact-select');
    if (artifactSelect) {
        artifactSelect.value = 'test';
        artifactSelect.dispatchEvent(new Event('input'));
        setTimeout(() => {
            const autocompleteItems = document.querySelectorAll('#autocomplete-list div');
            debugLog('Autocomplete items', autocompleteItems);
            if (autocompleteItems.length > 0) {
                debugLog('Clicking first autocomplete item');
                autocompleteItems[0].click();
            } else {
                debugLog('No autocomplete items found');
            }
        }, 100);
    } else {
        debugLog('Error: artifactSelect element not found');
    }
};