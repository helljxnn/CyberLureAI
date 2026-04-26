# Sprint 02 - Feature Extraction And Calibration

## Goal

Turn the current heuristic MVP into a more testable analysis foundation.

## Completed In This Block

- moved URL and message signal detection into reusable feature extraction modules
- added structured analysis signals to keep scoring explainable
- added small labeled URL and message calibration examples
- added tests that verify the labeled examples match expected verdicts
- added local frontend history for recent successful analyses

## Next Development Path

1. Expand the labeled examples with more realistic phishing and safe samples.
2. Track false positives and false negatives from the calibration files.
3. Convert structured signals into tabular features.
4. Train a first baseline classifier with scikit-learn.
5. Compare the model output with the current heuristic score before replacing any behavior.

## Guardrails

- Keep all work defensive and educational.
- Use public or authorized datasets only.
- Keep the heuristic path available while the baseline model is experimental.
