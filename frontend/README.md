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

## How to test manually

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Run the backend API:

```bash
uvicorn backend.app.main:app --reload
```

3. Start the frontend:

```bash
npm run dev
```

4. Open the local Vite URL shown in the terminal.

5. Confirm the backend URL is set to:

```text
http://127.0.0.1:8000
```

6. Test:

- API connection
- URL analysis
- message analysis

## Notes

- The backend allows CORS in development so the React frontend can call the local API.
