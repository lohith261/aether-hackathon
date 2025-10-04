# Aether - Anomaly & Strategy Engine 🚀

**Live Demo: [https://aether-engine.netlify.app/](https://aether-engine.netlify.app/)**

---

## The Problem

Financial markets generate an overwhelming amount of data every second. For a human trader, it's impossible to monitor thousands of data points in real-time to spot significant, actionable events before they become widespread news. This information overload leads to missed opportunities and increased risk.

## Our Solution: Aether

Aether is a full-stack, AI-powered web application that acts as a vigilant trading assistant. It automates the process of finding the "signal in the noise" by:

1.  **Detecting:** It runs a statistical analysis on market data to find significant anomalies that deviate from recent trends.
2.  **Analyzing:** When a critical event is detected, the raw data is sent to a powerful Large Language Model hosted on the **Cerebras Cloud**.
3.  **Advising:** The Cerebras AI model provides a concise, professional analysis, suggesting potential causes for the event and outlining a strategic next step for a trader.

This creates a seamless workflow from raw data to actionable intelligence, accessible through a clean, simple user interface.

---

## Architecture

Aether is built with a modern, decoupled architecture, with the frontend and backend deployed independently.

```
+----------------+      +----------------------+      +--------------------+
|                |      |                      |      |                    |
| User Browser   +----->+  Netlify Frontend    +----->+  Render Backend    |
| (HTML/CSS/JS)  |      | (Static Hosting)     |      | (Docker Container) |
|                |      |                      |      |                    |
+----------------+      +----------------------+      +--------+-----------+
                                                                |
                                                                | API Call
                                                                V
                                                      +---------+----------+
                                                      |                    |
                                                      |  Cerebras Cloud AI |
                                                      |      (LLM)         |
                                                      |                    |
                                                      +--------------------+
```

---

## Tech Stack

* **Backend:** Python, FastAPI
* **AI Engine:** Pandas, Cerebras Cloud SDK
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Deployment:** Docker, Render (for backend), Netlify (for frontend)

---

## How to Run Locally

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd aether-hackathon
    ```

2.  **Create a `.env` file** for your API keys. A `.env.example` is included.
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and add your actual API keys.

3.  **Build the Docker image:**
    ```bash
    docker build -t aether-app .
    ```

4.  **Run the Docker container:** This will start the backend server on port 8000.
    ```bash
    docker run --env-file .env -d -p 8000:8000 --name aether-container aether-app
    ```

5.  **Run the frontend:** Open a new terminal window and start a simple web server on port 8080.
    ```bash
    python3 -m http.server 8080
    ```

6.  Open your browser and navigate to `http://127.0.0.1:8080`.

---

## Hackathon Submission

This project was built for the **WeMakeDevs FutureStack'25 GenAI Hackathon**.