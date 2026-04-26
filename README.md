# CyberLureAI

Developed by Jennifer Lascarro Sosa

CyberLureAI is an AI-powered cybersecurity project focused on two goals:

1. Detect digital threats such as phishing, malicious messages, and malware-related patterns.
2. Help both technical users and the general public understand risks and protect themselves.

The project is being built incrementally, with small commits and short sprints, starting from a strong research and product foundation.

## Product Direction

CyberLureAI is not intended to be only a code vulnerability scanner.
Its differentiator is to combine:

- cybersecurity analysis
- practical prevention
- user-friendly explanations
- educational content for non-technical people

The first recommended MVP focuses on:

- suspicious URL analysis
- suspicious message analysis
- clear risk scoring
- simple recommendations for end users

## Current Repository Structure

```text
CyberLureAI/
├── backend/        # Backend API scaffold and future analysis services
├── data/           # Local datasets and dataset notes
├── docs/           # Product, research, and project documentation
├── frontend/       # Frontend scaffold and future user interface
├── notebooks/      # Research notebooks and experiments
├── tests/          # Automated tests
├── .env.example    # Example environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Status

At this stage, the repository contains:

- initial dataset files for malware-related work
- one exploratory notebook
- research notes
- product vision documentation
- a FastAPI backend with URL and message analysis endpoints
- a React + Vite frontend for testing the first analysis flow
- structured feature extraction for URL and message risk signals
- small labeled calibration examples for phishing and message analysis
- automated tests for the current API and analysis services

## Tech Stack

- Python 3.10+
- FastAPI
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- JupyterLab
- React
- Vite

## Datasets

Current and planned datasets are documented in:

- [data/readme_datasets.txt](data/readme_datasets.txt)
- [data/README.md](data/README.md)
- [data/examples/url_samples.csv](data/examples/url_samples.csv)
- [data/examples/message_samples.csv](data/examples/message_samples.csv)

Examples already referenced by the project:

- Malware classification
- Malware behavior analysis
- Phishing URLs
- SMS spam / malicious messaging

## Setup

Create or update the conda environment, then activate it:

```bash
conda env update -f environment.yml
conda activate cyberlureai
```

Copy the environment template if needed:

```bash
copy .env.example .env
```

Run the backend tests from the project root:

```bash
python -m pytest
```

## Immediate Next Steps

1. Expand the labeled calibration examples with more realistic safe, review, and suspicious cases.
2. Start a baseline phishing classifier using the existing structured signals as features.
3. Track false positives and false negatives from the calibration examples.
4. Keep the frontend history and API response contract aligned as new signals are added.

## Legal and Ethical Note

CyberLureAI is an educational and defensive project.
It must not be used for malicious purposes.
All datasets should come from public or authorized research sources.
