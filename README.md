# CyberLureAI

Developed by Jennifer Lascarro Sosa

CyberLureAI is an AI-powered cybersecurity project focused on two goals:

1. Detect digital threats such as phishing URLs, suspicious messages, and malware-related PE header patterns.
2. Help both technical users and the general public understand risks and protect themselves.

The project is being built incrementally, with small commits and short sprints, starting from a strong research and product foundation.

## Product Direction

CyberLureAI is not intended to be only a code vulnerability scanner.
Its differentiator is to combine:

- cybersecurity analysis
- practical prevention
- user-friendly explanations
- educational content for non-technical people

The current local MVP focuses on:

- suspicious URL analysis
- suspicious message analysis
- PE header malware classification from JSON feature input
- clear risk scoring and recommended actions
- an experimental ML comparison for URL and message analysis that does not replace the explainable heuristic verdict

## Current Repository Structure

```text
CyberLureAI/
├── backend/        # FastAPI app, routers, schemas, and analysis services
├── data/           # Local datasets, examples, and dataset notes
├── docs/           # Product, research, demo, and model documentation
├── frontend/       # React + Vite demo interface
├── models/         # Saved baseline and malware classifier artifacts
├── notebooks/      # Research notebooks and experiments
├── reports/        # Calibration and baseline reports
├── scripts/        # Data conversion, calibration, training, and demo utilities
├── tests/          # Automated tests
├── .env.example
├── .env.production.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Status

At this stage, the repository contains:

- a FastAPI backend with `/analyze/url`, `/analyze/message`, `/analyze/malware`, and `/analyze/malware/upload`
- a React + Vite frontend for the local MVP demo flow with a dashboard view
- structured feature extraction for URL and message risk signals (30+ signal types)
- an experimental separate-by-type baseline model comparison for URL and message analysis
- startup warm-up for the experimental baseline so the first request does not train lazily
- a RandomForest malware classifier bundle with model card and feature metadata
- rate limiting configured through `RATE_LIMIT`
- user feedback collection via `/analyze/feedback`
- system metrics dashboard at `/system/metrics`
- production-oriented environment examples, including optional static frontend serving
- automated tests for the API, analyzers, calibration, and baseline behavior
- GitHub Actions CI for backend tests and frontend build

Recent local validation:

- Backend tests: 308 passed
- Frontend build: code-split bundles (164 KB main + 374 KB dashboard)

Real-world calibration (2,091 examples):

- Heuristic accuracy: 51.5% (URL: 46.3%, Message: 56.6%)
- False positives: 67, False negatives: 947
- Limitation: many real phishing URLs are HTTP on hacked legitimate domains with no visible signals

## Tech Stack

- Python 3.10+
- FastAPI
- slowapi
- pandas
- numpy
- scikit-learn
- joblib
- matplotlib
- seaborn
- JupyterLab
- React
- Vite

## Datasets And Models

Current and planned datasets are documented in:

- [data/README.md](data/README.md)
- [data/examples/url_samples.csv](data/examples/url_samples.csv)
- [data/examples/message_samples.csv](data/examples/message_samples.csv)
- [data/examples/url_adversarial.csv](data/examples/url_adversarial.csv)
- [data/examples/message_adversarial.csv](data/examples/message_adversarial.csv)

Model artifacts and traceability files include:

- [models/baseline_model.joblib](models/baseline_model.joblib)
- [models/baseline_model_external.joblib](models/baseline_model_external.joblib)
- [models/separate_external/url_baseline_model.joblib](models/separate_external/url_baseline_model.joblib)
- [models/separate_external/message_baseline_model.joblib](models/separate_external/message_baseline_model.joblib)
- [models/malware_classifier.joblib](models/malware_classifier.joblib)
- [models/malware_features.json](models/malware_features.json)
- [models/malware_model_card.json](models/malware_model_card.json)

The URL and message ML baseline is experimental. The API keeps the explainable heuristic result as the primary user-facing verdict and exposes `experimental_model` only as comparison context.

## Local Setup

Create or update the Python environment:

```powershell
conda env update -f environment.yml
conda activate cyberlureai
```

Or use the existing local virtual environment if present:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Copy the environment template if needed:

```powershell
copy .env.example .env
```

Install frontend dependencies from `frontend/` if needed:

```powershell
npm install
```

## Local Demo

From the project root, validate the backend:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Start the backend:

```powershell
uvicorn backend.app.main:app --reload
```

From `frontend/`, validate and start the frontend:

```powershell
npm run -s build
npm run dev
```

Then open the local Vite URL and follow [docs/DEMO_CHECKLIST.md](docs/DEMO_CHECKLIST.md).

With the backend running, you can also run a quick endpoint smoke check:

```powershell
.\.venv\Scripts\python.exe scripts\demo_smoke_check.py
```

## Immediate Next Steps

1. Keep the local demo checklist current after frontend or API changes.
2. Continue expanding realistic safe, review, and suspicious examples, especially borderline `review` cases.
3. Track false positives and false negatives after every meaningful signal change.
4. Keep the heuristic API contract stable while the experimental ML comparison matures.
5. Decide later whether the production demo should serve Vite `dist/` from FastAPI or use a separate frontend host.
6. Consider integrating external reputation APIs (VirusTotal, Google Safe Browsing) to improve URL detection beyond visible signals.
7. Expand the review-class dataset with more borderline examples from real-world data.

## Legal And Ethical Note

CyberLureAI is an educational and defensive project.
It must not be used for malicious purposes.
All datasets should come from public or authorized research sources.
