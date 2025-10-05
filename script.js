document.addEventListener('DOMContentLoaded', () => {
    const analyzeButton = document.getElementById('analyze-button');
    const statusDisplay = document.getElementById('status-display');
    const spinner = document.getElementById('spinner');
    const resultsContainer = document.getElementById('results-container');

    const API_URL = 'https://aether-backend-enpt.onrender.com/analyze';

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
                // This will catch errors like 503 while the server wakes up
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();

            // 3. Process and display the results
            spinner.style.display = 'none';
            statusDisplay.textContent = 'Analysis Complete.';
            
            // --- THIS IS THE UPDATED LOGIC ---
            if (data.status === "Anomaly Detected") {
                displayResults(data);
            } else if (data.status === "No significant anomaly detected.") {
                displayStatus(data); // Call the new function for market status
            } else {
                // This handles any other messages or errors from the backend
                statusDisplay.textContent = data.error || 'An unknown response was received.';
            }
            // ------------------------------------

        } catch (error) {
            console.error('Fetch error:', error);
            spinner.style.display = 'none';
            statusDisplay.textContent = 'Engine is waking up or unavailable. This can take up to a minute. Please try again shortly.';
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

    // --- THIS IS THE NEW FUNCTION ---
    function displayStatus(data) {
        const statusCard = document.createElement('div');
        statusCard.className = 'status-card'; // We styled this in style.css
        
        const latest = data.latest_data;
        statusCard.innerHTML = `
            <h2>Market Status: Normal</h2>
            <p><strong>Symbol:</strong> ${latest.symbol}</p>
            <p><strong>Last Close Price:</strong> $${parseFloat(latest.close_price).toFixed(2)}</p>
            <p><strong>Timestamp:</strong> ${latest.timestamp}</p>
        `;
        resultsContainer.appendChild(statusCard);
    }
    // --------------------------------
});