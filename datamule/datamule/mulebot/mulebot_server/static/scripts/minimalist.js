const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const artifactContainer = document.getElementById('artifact-container');
const artifactContent = document.getElementById('artifact-content');
const toggleArtifactsBtn = document.getElementById('toggle-artifacts');
const suggestionContainer = document.querySelector('.suggestion-box');

let artifacts = [];

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

function appendMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage(message) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
    });
    return response.json();
}

function handleResponse(response) {
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

function renderArtifact(artifactData, artifactType) {
    console.log('Artifact type:', artifactType);
    console.log('Artifact data:', artifactData);

    if (artifactType === 'artifact-table') {
        artifacts = Array.isArray(artifactData) ? artifactData : [artifactData];
        artifacts.forEach(artifact => {
            artifact.type = artifactType;
            console.log('Processed artifact:', artifact);
        });
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

function renderTableArtifact(tableData) {
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

    artifactContent.innerHTML = html;
    renderMetadata(tableData);
    setupTableEventListeners(tableData);
}

function renderListArtifact(listData) {
    let html = `<h4>URLs</h4><ul class="list-group">`;

    listData.forEach(url => {
        html += `<li class="list-group-item"><a href="${url}" target="_blank">${url}</a></li>`;
    });

    html += '</ul>';

    artifactContent.innerHTML = html;
}

function renderFilingArtifact(artifactData) {
    const { content: html, data, section_id } = artifactData;

    const container = document.createElement('div');
    container.className = 'filing-container';
    container.style.width = '100%';
    container.style.height = '600px';

    const iframe = document.createElement('iframe');
    iframe.srcdoc = html;
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';

    container.appendChild(iframe);

    artifactContent.innerHTML = '';
    artifactContent.appendChild(container);

    iframe.onload = () => {
        if (section_id) {
            const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
            const targetElement = iframeDocument.getElementById(section_id);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    };

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'mt-3';

    const downloadHtmlBtn = document.createElement('button');
    downloadHtmlBtn.className = 'btn btn-secondary me-2';
    downloadHtmlBtn.textContent = 'Download Filing HTML';
    downloadHtmlBtn.onclick = () => {
        const blob = new Blob([html], { type: 'text/html' });
        saveAs(blob, 'filing.html');
    };
    buttonContainer.appendChild(downloadHtmlBtn);

    const downloadJsonBtn = document.createElement('button');
    downloadJsonBtn.className = 'btn btn-secondary';
    downloadJsonBtn.textContent = 'Download Filing Data (JSON)';
    downloadJsonBtn.onclick = () => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        saveAs(blob, 'filing_data.json');
    };
    buttonContainer.appendChild(downloadJsonBtn);

    artifactContent.appendChild(buttonContainer);
}

function renderMetadata(artifactData) {
    const metadataHtml = `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Metadata</h5>
                <p><strong>Fact:</strong> ${artifactData.fact}</p>
                ${artifactData.cik ? `<p><strong>CIK:</strong> ${artifactData.cik}</p>` : ''}
                ${artifactData.category ? `<p><strong>Category:</strong> ${artifactData.category}</p>` : ''}
                ${artifactData.label ? `<p><strong>Label:</strong> ${artifactData.label}</p>` : ''}
                ${artifactData.description ? `<p><strong>Description:</strong> ${artifactData.description}</p>` : ''}
                ${artifactData.unit ? `<p><strong>Unit:</strong> ${artifactData.unit}</p>` : ''}
            </div>
        </div>
    `;
    document.getElementById('metadata-content').innerHTML = metadataHtml;
}

function setupTableEventListeners(tableData) {
    const artifactSelect = document.getElementById('artifact-select');
    const autocompleteList = document.getElementById('autocomplete-list');
    const downloadCsvBtn = document.getElementById('download-csv');
    const downloadAllZipBtn = document.getElementById('download-all-zip');

    artifactSelect.addEventListener('input', function (e) {
        const val = this.value.toLowerCase();
        createAutocompleteList(artifacts.filter(artifact =>
            artifact.fact.toLowerCase().includes(val)
        ));
    });

    artifactSelect.addEventListener('focus', function () {
        createAutocompleteList(artifacts);
    });

    downloadCsvBtn.addEventListener('click', () => {
        downloadCSV(tableData);
    });

    downloadAllZipBtn.addEventListener('click', async () => {
        const tables = artifacts.filter(artifact => artifact.type === 'artifact-table');
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
    });
}

function createAutocompleteList(filteredArtifacts) {
    const autocompleteList = document.getElementById('autocomplete-list');
    autocompleteList.innerHTML = '';
    filteredArtifacts.forEach(artifact => {
        const div = document.createElement("div");
        div.innerHTML = artifact.fact;
        div.addEventListener("click", function (e) {
            document.getElementById('artifact-select').value = this.innerHTML;
            renderTableArtifact(artifact);
            closeAutocompleteList();
        });
        autocompleteList.appendChild(div);
    });
}

function closeAutocompleteList() {
    document.getElementById('autocomplete-list').style.display = 'none';
}

function downloadCSV(table) {
    let csv = '';
    const headers = Object.keys(table.table[0]);
    csv += headers.join(',') + '\n';
    table.table.forEach(row => {
        csv += Object.values(row).join(',') + '\n';
    });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, `${table.fact}.csv`);
}

document.addEventListener("click", function (e) {
    if (e.target.id !== 'artifact-select') {
        closeAutocompleteList();
    }
});

function showArtifacts() {
    artifactContainer.style.display = 'block';
    suggestionContainer.style.display = 'none';
    toggleArtifactsBtn.textContent = 'Hide Artifacts';
}

function hideArtifacts() {
    artifactContainer.style.display = 'none';
    suggestionContainer.style.display = 'block';
    toggleArtifactsBtn.textContent = 'Show Artifacts';
}

toggleArtifactsBtn.addEventListener('click', () => {
    if (artifactContainer.style.display === 'none') {
        showArtifacts();
    } else {
        hideArtifacts();
    }
});

// Initially hide artifacts and show suggestions
hideArtifacts();