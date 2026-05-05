# Frontend

This folder will contain the CyberLureAI web interface.

Main product goals for the first version:

- a landing page with the project message
- a URL analysis screen
- a suspicious message analysis screen
- an educational section for non-technical users

## Current state

The frontend now uses a lightweight React + Vite setup:

- `index.html`
- `src/main.jsx`
- `src/App.jsx`
- `src/styles.css`

It connects directly to the backend API endpoints.
Successful URL and message checks are also stored in a small local browser history so recent results can be compared during manual testing.
The interface includes quick examples for likely safe, review, and suspicious
cases, clearer signal descriptions, safe next-step guidance, and a reuse action
for recent history items.

## How to test manually

1. Activate the conda backend environment from the project root:

```bash
conda activate cyberlureai
```

2. Install frontend dependencies:

```bash
cd frontend
npm install
```

3. Run the backend API from the project root:

```bash
uvicorn backend.app.main:app --reload
```

4. Start the frontend:

```bash
npm run dev
```

5. Open the local Vite URL shown in the terminal.

6. Confirm the backend URL is set to:

```text
http://127.0.0.1:8000
```

7. Test:

- API connection
- URL analysis
- message analysis
- quick example buttons for each risk category
- safe next-step guidance in the result panel
- local analysis history

## Notes

- The backend allows CORS in development so the React frontend can call the local API.
