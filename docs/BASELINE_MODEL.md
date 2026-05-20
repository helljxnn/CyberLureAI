# Experimental Baseline Classifier

This baseline is an experiment. It does not replace the current heuristic API.
Its job is to show whether the structured signals are useful as model features.

## Current Runtime Behavior

The `/analyze/url` and `/analyze/message` endpoints include an
`experimental_model` object. The API still treats the heuristic verdict as the
primary user-facing behavior.

At application startup, `backend.app.main` calls
`warm_up_baseline_model()`. That pre-loads and caches the separate URL and
message baseline bundle so the first demo request does not train the baseline
inside the request path.

The `/analyze/malware` endpoint does not use this baseline comparison. Malware
analysis uses the saved RandomForest classifier documented in
`models/malware_model_card.json`.

The comparison reports:

- the `separate_by_type` strategy
- the model verdict and confidence when available
- whether the model agrees with the heuristic verdict
- a note that the model is experimental and does not replace the explainable
  analysis path

## How It Works

1. Load labeled examples from the calibration datasets.
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

From the project root, run the hand-crafted calibration baseline:

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier
```

Run the external real-world sample baseline:

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --external
```

Run both hand-crafted and external samples:

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --include-default --external
```

## Export Predictions And Metrics

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --predictions-csv reports/baseline_predictions.csv
```

Export per-class and per-sample-type metrics:

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --class-metrics-csv reports/baseline_class_metrics.csv --sample-type-metrics-csv reports/baseline_sample_type_metrics.csv
```

The current local report exports are:

- `reports/baseline_predictions.csv`
- `reports/baseline_class_metrics.csv`
- `reports/baseline_sample_type_metrics.csv`

## Persist Trained Experimental Models

Persist one unified experimental model:

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --model-path models/baseline_model.joblib
```

Persist separate experimental models:

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --separate-model-dir models/separate_baselines
```

Persist models trained on external real-world samples:

```powershell
.\.venv\Scripts\python.exe -m backend.app.services.baseline_classifier --external --model-path models/baseline_model_external.joblib --separate-model-dir models/separate_external
```

Existing external artifacts:

- `models/baseline_model_external.joblib`
- `models/separate_external/url_baseline_model.joblib`
- `models/separate_external/message_baseline_model.joblib`

Use saved baseline models for local experiments only until the project has a
larger and more representative dataset.

## Interpretation

The heuristic remains the primary API behavior because it is explainable and
stable for the local MVP demo. The baseline proves that the signal table can
feed an ML model, but it should remain comparison-only while the dataset grows.

Known limitations:

- phishing URLs without visible suspicious keywords are hard to catch without
  content analysis or reputation checks
- spam or social engineering messages without obvious scam phrases require
  better NLP features
- phishing hosted on legitimate platforms can bypass URL-only heuristics
- the `review` class needs more realistic borderline examples

Keep the heuristic API path in place and treat the saved baseline models as
local experiments until the data quality and class balance improve.
