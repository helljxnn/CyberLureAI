# Baseline Error Analysis

This analysis compares the experimental baseline classifier against the current
heuristic verdicts and the expected labels in the calibration CSV files. The
baseline is still experimental and does not replace the API behavior.

## Starting Point

Before adding targeted examples:

```text
Calibration examples: 30
Feature columns: 30
Heuristic accuracy: 100.0%
Baseline CV accuracy: 70.0%
Heuristic misses: 0
Baseline CV misses: 9
```

Initial misses:

| Sample | Expected | Baseline | Pattern |
| --- | --- | --- | --- |
| `safe_trusted_login_path` | `likely_safe` | `review` | Trusted login path looked risky to the model. |
| `review_shortener` | `review` | `likely_safe` | Single shortener signal looked too weak. |
| `review_insecure_account_page` | `review` | `likely_safe` | Low-friction HTTP/account signal looked too weak. |
| `review_many_subdomains` | `review` | `likely_safe` | Subdomain-only review case looked too weak. |
| `review_repeated_hyphen_update` | `review` | `suspicious` | Hyphen and phishing terms looked too strong. |
| `suspicious_deep_bank_chain` | `suspicious` | `review` | Deep phishing chain looked underweighted. |
| `safe_agenda_link` | `likely_safe` | `review` | Normal link in a safe message looked risky. |
| `review_verify_delivery` | `review` | `suspicious` | Verification language looked too strong. |
| `review_code_login` | `review` | `suspicious` | Code language looked too strong. |

## Targeted Data Added

The calibration CSVs now include more examples for:

- trusted safe URLs with `login`, `account`, and `signin` terms on known domains
- review URLs with shorteners or HTTP verification pages
- normal safe messages that contain ordinary links
- review messages with verification codes or contact verification language
- suspicious cases that combine strong signals such as brand impersonation,
  account threats, rewards, codes, and shorteners

## Midpoint Result

After the first targeted expansion:

```text
Calibration examples: 46
Feature columns: 30
Heuristic accuracy: 100.0%
Baseline CV accuracy: 80.4%
Heuristic misses: 0
Baseline CV misses: 9
```

Remaining misses:

| Sample | Expected | Baseline | Pattern |
| --- | --- | --- | --- |
| `review_many_subdomains` | `review` | `likely_safe` | Subdomain-only review still needs more examples. |
| `review_repeated_hyphen_update` | `review` | `suspicious` | Hyphen plus keyword boundary is still too sharp. |
| `suspicious_brand_impersonation` | `suspicious` | `review` | Brand impersonation needs more high-risk variants. |
| `suspicious_whatsapp_impersonation` | `suspicious` | `review` | Brand impersonation needs more high-risk variants. |
| `suspicious_shortener_bank_terms` | `suspicious` | `review` | Shortener plus banking terms needs more high-risk variants. |
| `review_verify_delivery` | `review` | `suspicious` | Benign verification language still trends too risky. |
| `review_code_login` | `review` | `suspicious` | Benign code language still trends too risky. |
| `review_two_factor_code` | `review` | `suspicious` | Two-factor code language still trends too risky. |
| `review_shortened_event_link` | `review` | `likely_safe` | Shortened event link still needs review-class support. |

## Final Result

After a second pass focused on the remaining review/suspicious boundaries:

```text
Calibration examples: 67
Feature columns: 30
Heuristic accuracy: 100.0%
Baseline CV accuracy: 92.5%
Heuristic misses: 0
Baseline CV misses: 5
```

Remaining misses:

| Sample | Expected | Baseline | Pattern |
| --- | --- | --- | --- |
| `review_tinyurl_notice` | `review` | `likely_safe` | A mild shortener-only review case still looks too safe. |
| `review_repeated_hyphen_update` | `review` | `suspicious` | Hyphen plus phishing keyword boundary is still a bit too sharp. |
| `suspicious_deep_bank_chain` | `suspicious` | `review` | Deep phishing chains still need more high-risk support. |
| `suspicious_shortener_bank_terms` | `suspicious` | `review` | Shortener plus bank terms still needs more strong suspicious variants. |
| `review_verify_delivery` | `review` | `suspicious` | Legitimate delivery verification still trends too risky. |

## Current Result

After a third calibration pass focused on shortener-only review URLs,
hyphen-heavy review URLs, deep phishing URL chains, shortener-plus-bank URLs,
limited-time review messages, and benign delivery/contact verification messages:

```text
Calibration examples: 82
Feature columns: 30
Heuristic accuracy: 100.0%
Unified baseline accuracy: 96.3%
Unified baseline misses: 3
Separate baseline accuracy: 97.6%
Separate baseline misses: 2
```

Current separate-model misses:

| Sample | Expected | Baseline | Pattern |
| --- | --- | --- | --- |
| `review_repeated_hyphen_update` | `review` | `suspicious` | Hyphen plus phishing keyword boundary still looks too strong. |
| `review_verify_delivery` | `review` | `suspicious` | Legitimate delivery verification still trends too risky. |

## Unified Vs Separate Models

Current comparison:

```text
Unified baseline accuracy: 96.3%
Separate baseline accuracy: 97.6%

Unified per-type accuracy:
- message: 94.3%
- url: 97.9%

Separate per-type accuracy:
- message: 97.1%
- url: 97.9%
```

Interpretation:

- The added targeted examples removed the previous shortener-only URL miss and
  limited-time message miss from the separate baseline.
- Separate URL and message baselines remain the stronger experimental default.
- The remaining misses are still `review` versus `suspicious` boundaries around
  hyphen-heavy account URLs and delivery verification language.

## Next Data Priorities

- Add more benign-but-cautionary `review` URLs with hyphen-heavy account or
  update language.
- Add more `review` delivery verification messages that stay benign while still
  containing account, address, or contact confirmation language.
- Keep watching for `suspicious` shortener-plus-banking and deep-chain phishing
  regressions as the dataset grows.
- Keep heuristic and baseline results side by side until the dataset is larger
  and model metrics are less sensitive to individual examples.
- Treat separate URL and message baselines as the stronger experimental default
  for future comparisons.
