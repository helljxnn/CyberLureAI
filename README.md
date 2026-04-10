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

More context is documented in [docs/PRODUCT_VISION.md](docs/PRODUCT_VISION.md).

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
- a cleaned base structure for future backend and frontend work

## Tech Stack

- Python 3.10+
- FastAPI
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- JupyterLab

Frontend technology will be defined during the first implementation sprint.

## Datasets

Current and planned datasets are documented in:

- [data/readme_datasets.txt](data/readme_datasets.txt)
- [data/README.md](data/README.md)

Examples already referenced by the project:

- Malware classification
- Malware behavior analysis
- Phishing URLs
- SMS spam / malicious messaging

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template if needed:

```bash
copy .env.example .env
```

## Immediate Next Steps

1. Organize the first sprint.
2. Scaffold the backend API.
3. Scaffold the frontend interface.
4. Build the first phishing or message-analysis flow.

## Legal and Ethical Note

CyberLureAI is an educational and defensive project.
It must not be used for malicious purposes.
All datasets should come from public or authorized research sources.
