// listArtifacts.js
export function renderListArtifact(listData) {
    let html = `<h4>URLs</h4><ul class="list-group">`;

    listData.forEach(url => {
        html += `<li class="list-group-item"><a href="${url}" target="_blank">${url}</a></li>`;
    });

    html += '</ul>';

    const artifactContent = document.getElementById('artifact-content');
    if (artifactContent) {
        artifactContent.innerHTML = html;
    }
}