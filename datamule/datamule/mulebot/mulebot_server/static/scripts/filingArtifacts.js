// filingArtifacts.js
export function renderFilingArtifact(artifactData) {
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

    const artifactContent = document.getElementById('artifact-content');
    if (artifactContent) {
        artifactContent.innerHTML = '';
        artifactContent.appendChild(container);
    }

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