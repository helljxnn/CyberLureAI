# Backend

This folder will contain the API and analysis services for CyberLureAI.

Suggested near-term structure:

- `app/` for FastAPI application code
- `services/` for threat analysis logic
- `schemas/` for request and response models
- `routers/` for API endpoints

First implementation target:

- an endpoint to analyze suspicious URLs
- an endpoint to analyze suspicious messages

## Current structure

- `app/main.py` contains the FastAPI entry point

## Run locally

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Current endpoint

### `GET /health`

Returns a small health response for the API:

```json
{
  "status": "ok",
  "service": "CyberLureAI API"
}
```
