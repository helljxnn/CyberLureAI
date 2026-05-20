# CyberLureAI Local Demo Checklist

Use this checklist before showing the local MVP or after changing the frontend flow.

## Preflight

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

From `frontend/`:

```powershell
npm run -s build
```

Expected current baseline:

- Backend tests pass.
- Vite creates `frontend/dist/`.
- The backend API contract still exposes `/health`, `/analyze/url`, `/analyze/message`, and `/analyze/malware`.

## Start Services

Terminal 1, from the project root:

```powershell
uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Terminal 2, from `frontend/`:

```powershell
npm run dev
```

Open the Vite local URL shown in the terminal, usually:

```text
http://127.0.0.1:5173
```

## Optional Smoke Check

With the backend running, from the project root:

```powershell
.\.venv\Scripts\python.exe scripts\demo_smoke_check.py
```

This script verifies the demo endpoints only. It does not replace the full `pytest` suite.

## Manual Demo Path

1. Open the local Vite URL.
2. Confirm the backend URL is `http://127.0.0.1:8000`.
3. Click `Check API status` and verify the success message appears.
4. Run a likely safe URL example and confirm a low-risk result.
5. Run a suspicious URL example and confirm a high-risk result.
6. Run a likely safe message example and confirm a low-risk result.
7. Run a suspicious message example and confirm a high-risk result.
8. Run the PE header classifier with one JSON malware example and confirm the response includes `label`, `confidence`, `probabilities`, `risk_level`, `risk_score`, `reasons`, and `signals`.
9. Confirm each URL and message result shows the heuristic verdict as the primary decision.
10. Confirm URL and message results display `experimental_model` as comparison context only.
11. Confirm malware results do not include an experimental URL/message comparison.
12. Reuse one URL, message, and malware item from analysis history and verify the matching form is populated again.
13. Clear history and verify the empty state returns.
14. Stop the backend, click `Check API status`, and verify the connection error is clear.

## Acceptance Notes

- The heuristic verdict remains the primary user-facing decision for URL and message analysis.
- The experimental model remains secondary comparison context and does not replace the explainable analysis path.
- The malware endpoint uses the saved RandomForest classifier and returns a standalone malware response.
- No backend endpoint contract changes are required for this demo flow.
- This checklist targets a local demo, not a public deployment.
