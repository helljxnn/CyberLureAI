# Sprint 02 - Feature Extraction And Calibration

## Goal

Turn the current heuristic MVP into a more testable analysis foundation.

## Completed In This Block

- moved URL and message signal detection into reusable feature extraction modules
- added structured analysis signals to keep scoring explainable
- added small labeled URL and message calibration examples
- added tests that verify the labeled examples match expected verdicts
- added local frontend history for recent successful analyses
- added calibration reporting for false positives and false negatives
- added tabular signal feature rows for baseline model experiments

## Next Development Path

1. Export and inspect the calibration report after each meaningful signal change.
2. Train a first baseline classifier with scikit-learn.
3. Compare the model output with the current heuristic score before replacing any behavior.
4. Keep adding realistic safe, review, and suspicious examples as new gaps appear.

## Guardrails

- Keep all work defensive and educational.
- Use public or authorized datasets only.
- Keep the heuristic path available while the baseline model is experimental.
