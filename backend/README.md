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

- `app/core/` contains shared configuration helpers
- `app/main.py` contains the FastAPI entry point
- `app/routers/` contains API routes
- `app/schemas/` contains request and response models
- `app/services/` contains lightweight analysis logic

## Settings

The backend now reads configuration from environment variables through:

- `app/core/settings.py`

Defaults come from `.env.example`, and local values can be placed in `.env`.

## Run locally

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Current endpoint

### `GET /`

Returns a simple API summary with version and available endpoints.

### `GET /health`

Returns a small health response for the API:

```json
{
  "status": "ok",
  "service": "CyberLureAI API"
}
```

### `POST /analyze/url`

Accepts a URL and returns an initial heuristic-based analysis.

Request body:

```json
{
  "url": "http://secure-login-example.com/verify"
}
```

Example response:

```json
{
  "url": "http://secure-login-example.com/verify",
  "risk_level": "medium",
  "risk_score": 55,
  "verdict": "review",
  "explanation": "This initial analysis marked the URL as medium risk based on simple phishing heuristics.",
  "recommended_action": "Verify the sender and inspect the domain carefully before continuing.",
  "reasons": [
    "The URL uses multiple hyphens, a common phishing pattern.",
    "The URL contains keywords commonly used in phishing attempts.",
    "The URL does not use HTTPS."
  ]
}
```

### `POST /analyze/message`

Accepts a suspicious message and returns an initial heuristic-based analysis.

Validation notes:

- leading and trailing spaces are removed before analysis
- blank messages are rejected
- the message must contain at least 5 meaningful characters

Request body:

```json
{
  "message": "Urgent: verify your bank account now by clicking https://fake-bank-alert.example"
}
```

Example response:

```json
{
  "message": "Urgent: verify your bank account now by clicking https://fake-bank-alert.example",
  "risk_level": "high",
  "risk_score": 80,
  "verdict": "suspicious",
  "explanation": "This initial analysis marked the message as high risk based on simple social engineering heuristics.",
  "recommended_action": "Do not reply or click links. Verify the source through a trusted channel.",
  "reasons": [
    "The message includes phrases commonly used in scams or phishing attempts.",
    "The message contains a link and should be checked carefully before opening.",
    "The message uses urgency language to pressure quick action.",
    "The message asks for sensitive information or account verification."
  ]
}
```
