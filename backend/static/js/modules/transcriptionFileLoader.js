// transcriptionFileLoader.js

export async function loadTranscriptionFiles() {
    try {
        const response = await fetch('/list-transcription-files');
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const fileList = document.querySelector('#transcribed-files .file-list');
        fileList.innerHTML = ''; // Clear existing content

        // Loop through the list of transcription file paths and create links
        data.files.forEach(filePath => {
            const listItem = document.createElement('div');
            listItem.className = 'file-item';

            // Create a clickable link for each transcription file
            const fileLink = document.createElement('a');
            fileLink.href = `/static/${filePath}`;  // Use relative path to static folder
            fileLink.textContent = filePath.split('/').pop();  // Display only the file name
            fileLink.target = '_blank';  // Open in a new tab

            // Append the link to the list item
            listItem.appendChild(fileLink);
            fileList.appendChild(listItem);
        });
    } catch (err) {
        console.error('Error loading transcription files:', err);
    }
}