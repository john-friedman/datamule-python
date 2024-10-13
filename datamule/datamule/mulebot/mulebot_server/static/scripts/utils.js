// utils.js
export function renderMetadata(artifactData) {
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

export function downloadCSV(table) {
    let csv = '';
    const headers = Object.keys(table.table[0]);
    csv += headers.join(',') + '\n';
    table.table.forEach(row => {
        csv += Object.values(row).join(',') + '\n';
    });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, `${table.fact}.csv`);
}