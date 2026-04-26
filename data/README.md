# CyberLureAI Datasets

This folder stores local datasets and dataset references used by CyberLureAI.

## Current dataset source

### MVP calibration examples

- `examples/url_samples.csv` contains small labeled URL examples for safe, review, and suspicious cases.
- `examples/message_samples.csv` contains small labeled message examples for social engineering checks.

### Malware detection

- [Classification of Malwares](https://www.kaggle.com/datasets/saurabhshahane/classification-of-malwares)

## Notes

- Keep raw datasets organized by domain.
- Avoid committing unnecessary generated files.
- Add a short description whenever a new dataset is included.
- Keep small calibration examples readable and manually reviewable before using them for model training.
