// tableArtifacts.js
import { renderMetadata, downloadCSV } from './utils.js';
import { allArtifacts } from './artifacts.js';

export function renderTableArtifact(tableData) {
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

    const artifactContent = document.getElementById('artifact-content');
    if (artifactContent) {
        artifactContent.innerHTML = html;
    }
    renderMetadata(tableData);
    setupTableEventListeners(tableData);
}

function setupTableEventListeners(tableData) {
    const artifactSelect = document.getElementById('artifact-select');
    const downloadCsvBtn = document.getElementById('download-csv');
    const downloadAllZipBtn = document.getElementById('download-all-zip');

    if (artifactSelect) {
        artifactSelect.addEventListener('input', handleArtifactSelectInput);
        artifactSelect.addEventListener('focus', handleArtifactSelectFocus);
    }

    if (downloadCsvBtn) {
        downloadCsvBtn.addEventListener('click', () => downloadCSV(tableData));
    }

    if (downloadAllZipBtn) {
        downloadAllZipBtn.addEventListener('click', handleDownloadAllZip);
    }
}

export function handleArtifactSelectInput(e) {
    const inputValue = e.target.value.toLowerCase().trim();
    const filteredTables = allArtifacts.filter(table =>
        table.fact.toLowerCase().includes(inputValue)
    );
    createAutocompleteList(filteredTables);
}

export function handleArtifactSelectFocus() {
    createAutocompleteList(allArtifacts);
}

function createAutocompleteList(tables) {
    const autocompleteList = document.getElementById('autocomplete-list');
    if (!autocompleteList) return;

    autocompleteList.innerHTML = '';
    autocompleteList.style.display = 'block';

    if (tables.length === 0) {
        autocompleteList.innerHTML = '<div style="color: #999;">No matching tables found</div>';
    } else {
        tables.forEach(table => {
            const div = document.createElement("div");
            div.textContent = table.fact;
            div.addEventListener("click", function () {
                document.getElementById('artifact-select').value = this.textContent;
                renderTableArtifact(table);
                closeAutocompleteList();
            });
            autocompleteList.appendChild(div);
        });
    }
}

export function handleDocumentClick(e) {
    if (e.target.id !== 'artifact-select') {
        closeAutocompleteList();
    }
}

function closeAutocompleteList() {
    const autocompleteList = document.getElementById('autocomplete-list');
    if (autocompleteList) {
        autocompleteList.style.display = 'none';
    }
}

async function handleDownloadAllZip() {
    const tables = allArtifacts.filter(artifact => artifact.type === 'artifact-table');
    if (tables.length === 0) {
        alert('No tables available to download.');
        return;
    }
    const zip = new JSZip();
    tables.forEach(table => {
        let csv = '';
        const headers = Object.keys(table.table[0]);
        csv += headers.join(',') + '\n';
        table.table.forEach(row => {
            csv += Object.values(row).join(',') + '\n';
        });
        zip.file(`${table.fact}.csv`, csv);
    });
    const content = await zip.generateAsync({ type: "blob" });
    saveAs(content, "all_tables.zip");
}