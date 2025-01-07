const form = document.getElementById('uploadForm');
const summaryOutput = document.getElementById('summaryOutput');
const body = document.body; // To append the spinner to the body

// Function to show loading spinner
function showLoading() {
    const spinner = document.createElement('div');
    spinner.classList.add('spinner');
    body.appendChild(spinner);
}

// Function to hide loading spinner
function hideLoading() {
    const spinner = document.querySelector('.spinner');
    if (spinner) {
        spinner.remove();
    }
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file!");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Show the loading spinner
    showLoading();

    try {
        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(`Error: ${errorData.error}`);
            return;
        }

        const data = await response.json();
        summaryOutput.value = data.summary;
    } catch (error) {
        alert(`An error occurred: ${error.message}`);
    } finally {
        // Hide the loading spinner after the process is complete
        hideLoading();
    }
});
