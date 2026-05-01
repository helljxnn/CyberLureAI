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

## Next Data Priorities

- Add more `review` URLs that contain only a shortener or only moderate visual
  structure signals.
- Add more `suspicious` shortener-plus-banking and deep-chain phishing URLs.
- Add more `review` delivery verification messages that stay benign while still
  containing account or contact confirmation language.
- Keep heuristic and baseline results side by side until the dataset is larger
  and model metrics are less sensitive to individual examples.
