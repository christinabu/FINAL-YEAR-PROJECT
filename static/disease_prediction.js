// script.js

function updateLabel() {
    const fileInput = document.getElementById('file');
    const fileNameSpan = document.getElementById('file-name');

    if (fileInput.files.length > 0) {
        fileNameSpan.textContent = fileInput.files[0].name;
    } else {
        fileNameSpan.textContent = 'No file chosen';
    }
}
