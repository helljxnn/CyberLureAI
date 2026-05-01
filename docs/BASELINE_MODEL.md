# Experimental Baseline Classifier

This baseline is an experiment. It does not replace the current heuristic API.
Its job is to show whether the structured signals are useful as model features.

## How It Works

1. Load the labeled examples from `data/examples/url_samples.csv` and
   `data/examples/message_samples.csv`.
2. Run the current URL and message analyzers against each example.
3. Convert the resulting structured signals into numeric features:
   `risk_score`, signal counts, severity counts, and one `signal_*` column per
   observed signal.
4. Add `sample_type_message` and `sample_type_url` so the model can distinguish
   between message and URL examples.
5. Train a small `LogisticRegression` classifier with balanced class weights.
6. Evaluate it with stratified cross-validation, so each example is predicted by
   a model that was trained without that example.
7. Compare a unified baseline against separate URL and message baselines.
8. Compare predictions against the expected labels and against the current
   heuristic verdicts.

## Run The Baseline

From the project root:

```powershell
.venv\Scripts\python.exe -m backend.app.services.baseline_classifier
```

Current local result:

```text
Unified baseline:
- Calibration examples: 67
- Feature columns: 30
- Heuristic accuracy: 100.0%
- Baseline CV accuracy: 92.5%
- Baseline CV misses: 5

Separate baselines by type:
- Calibration examples: 67
- Feature columns: 30
- Heuristic accuracy: 100.0%
- Baseline CV accuracy: 94.0%
- Baseline CV misses: 4

Per-type baseline accuracy:
- Unified: `message 96.7%`, `url 89.2%`
- Separate: `message 93.3%`, `url 94.6%`
```

## Export Predictions

```powershell
.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --predictions-csv reports/baseline_predictions.csv
```

Export per-class metrics:

```powershell
.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --class-metrics-csv reports/baseline_class_metrics.csv --sample-type-metrics-csv reports/baseline_sample_type_metrics.csv
```

## Persist A Trained Experimental Model

```powershell
.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --model-path models/baseline_model.joblib
```

Persist separate experimental models:

```powershell
.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --separate-model-dir models/separate_baselines
```

The saved model is trained on all current calibration examples. Use it for local
experiments only until the project has a larger and more representative dataset.

## Interpretation

The heuristic currently wins on the small calibration set because those examples
were designed around known rules. The baseline improved after adding targeted
examples, but it is still experimental. It proves that the signal table can feed
a model, and it gives CyberLureAI a repeatable way to compare future model
improvements against the explainable heuristic path. At the moment, separate
models perform better overall than one shared model, mainly because URL mistakes
drop more than message mistakes increase. The current gaps are concentrated in a
small number of `review` versus `suspicious` boundary cases.
