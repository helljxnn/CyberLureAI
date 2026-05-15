# CyberLureAI Demo Checklist

Use this checklist before showing the MVP or after changing the frontend flow.

## Start Services

From the project root:

```powershell
.venv\Scripts\python.exe -m pytest
uvicorn backend.app.main:app --reload
```

From `frontend/`:

```powershell
npm run build
npm run dev
```

## Manual Demo Path

1. Open the local Vite URL.
2. Confirm the backend URL is `http://127.0.0.1:8000`.
3. Click `Check API status` and verify the success message appears.
4. Run one likely safe URL example and confirm a low-risk result.
5. Run one review URL example and confirm a medium-risk result.
6. Run one suspicious URL example and confirm a high-risk result.
7. Run one likely safe message example and confirm a low-risk result.
8. Run one review message example and confirm a medium-risk result.
9. Run one suspicious message example and confirm a high-risk result.
10. Confirm each result shows explanation, recommended action, safe next steps, and detected signals when available.
11. Confirm the experimental model is displayed as a comparison and not as the primary verdict.
12. Reuse an item from analysis history and verify the form is populated again.
13. Clear history and verify the empty state returns.
14. Stop the backend, click `Check API status`, and verify the connection error is clear.

## Acceptance Notes

- The heuristic verdict remains the primary user-facing decision.
- The experimental model remains secondary comparison context.
- No backend endpoint contract changes are required for this demo flow.
