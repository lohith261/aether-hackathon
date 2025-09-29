document.addEventListener('DOMContentLoaded', () => {
    const analyzeButton = document.getElementById('analyze-button');
    const statusDisplay = document.getElementById('status-display');
    const spinner = document.getElementById('spinner');
    const resultsContainer = document.getElementById('results-container');

    const API_URL = 'http://127.0.0.1:8000/analyze';

    analyzeButton.addEventListener('click', async () => {
        // 1. Reset the UI
        statusDisplay.textContent = 'Contacting Aether Engine...';
        resultsContainer.innerHTML = '';
        spinner.style.display = 'block';
        analyzeButton.disabled = true;

        try {
            // 2. Make the API call
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();

            // 3. Process and display the results
            spinner.style.display = 'none';
            statusDisplay.textContent = 'Analysis Complete.';
            
            if (data.status === "Anomaly Detected") {
                displayResults(data);
            } else {
                statusDisplay.textContent = data.status || 'No anomaly found.';
            }

        } catch (error) {
            console.error('Fetch error:', error);
            spinner.style.display = 'none';
            statusDisplay.textContent = 'Error: Could not connect to the Aether engine. Is the Docker container running?';
        } finally {
            analyzeButton.disabled = false;
        }
    });

    function displayResults(data) {
        // Card for Raw Anomaly
        const rawCard = document.createElement('div');
        rawCard.className = 'result-card';
        rawCard.innerHTML = `
            <h2>Raw Anomaly Detected</h2>
            <pre>${JSON.stringify(data.raw_anomaly_details, null, 2)}</pre>
        `;

        // Card for Strategic Analysis
        const strategicCard = document.createElement('div');
        strategicCard.className = 'result-card';
        strategicCard.innerHTML = `
            <h2>Cerebras Strategic Analysis</h2>
            <pre>${data.strategic_analysis}</pre>
        `;

        resultsContainer.appendChild(rawCard);
        resultsContainer.appendChild(strategicCard);
    }
});