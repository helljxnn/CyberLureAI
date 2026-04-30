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
- added an experimental scikit-learn baseline classifier

## Next Development Path

1. Export and inspect the calibration report after each meaningful signal change.
2. Compare future model changes against the current heuristic score before replacing any behavior.
3. Keep adding realistic safe, review, and suspicious examples as new gaps appear.
4. Expand the calibration dataset before trusting model metrics.

## Guardrails

- Keep all work defensive and educational.
- Use public or authorized datasets only.
- Keep the heuristic path available while the baseline model is experimental.
