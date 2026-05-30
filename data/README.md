# CyberLureAI Datasets

This folder stores local datasets and dataset references used by CyberLureAI.

## MVP calibration examples

- `examples/url_samples.csv` contains labeled URL examples for safe, review, and suspicious cases.
- `examples/message_samples.csv` contains labeled message examples for social engineering checks.
- `examples/url_adversarial.csv` contains adversarial URL edge cases for calibration stress testing.
- `examples/message_adversarial.csv` contains adversarial message edge cases for calibration stress testing.

## External datasets

### URL phishing

- `external/url_real.csv` contains 1,033 real-world URL examples (550 suspicious, 400 likely_safe, 83 review).
  - Sources: Kaggle taruntiwarihp phishing URL dataset and OpenPhish public feed.
  - Converted with `scripts/convert_external_data.py`.

### SMS spam

- `external/message_real.csv` contains 1,058 real-world SMS examples (500 suspicious, 500 likely_safe, 58 review).
  - Source: UCI SMS Spam Collection dataset.
  - Converted with `scripts/convert_external_data.py`.

### Raw downloads

- `phishing_urls/` stores the raw Kaggle phishing URL dataset before conversion.
- `sms_spam/` stores the raw UCI SMS Spam Collection dataset before conversion.

## Malware detection

- `malware/` stores the ClaMP Integrated dataset used to train the RandomForest malware classifier.
- Source: [Classification of Malwares](https://www.kaggle.com/datasets/saurabhshahane/classification-of-malwares)

## Future datasets

- `data_future/` contains notes and download instructions for planned datasets (email spam, malware behavior, additional phishing URLs).

## Notes

- Keep raw datasets organized by domain.
- Avoid committing unnecessary generated files.
- Add a short description whenever a new dataset is included.
- Keep small calibration examples readable and manually reviewable before using them for model training.
