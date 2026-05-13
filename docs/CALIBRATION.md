# Calibration And Feature Rows

CyberLureAI keeps small labeled examples in:

- `data/examples/url_samples.csv`
- `data/examples/message_samples.csv`

The calibration utility compares those expected labels against the current
heuristic analyzers. It reports:

- verdict matches
- expected signal matches
- false positives
- false negatives
- examples that need review

Run the default calibration summary from the project root:

```powershell
.venv\Scripts\python.exe -m backend.app.services.calibration
```

Current local calibration summary:

```text
Calibration examples: 246
Verdict matches: 246
Expected signal matches: 246
False positives: 0
False negatives: 0
```

Export per-example calibration results:

```powershell
.venv\Scripts\python.exe -m backend.app.services.calibration --report-csv data/generated/calibration_report.csv
```

Export tabular signal features for the first baseline model:

```powershell
.venv\Scripts\python.exe -m backend.app.services.calibration --features-csv data/generated/calibration_features.csv
```

The feature rows include metadata, the expected verdict, the current heuristic
verdict, risk score, severity counts, and one `signal_*` column per observed
structured signal.
