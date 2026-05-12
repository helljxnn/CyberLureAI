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

## Fourth Calibration Result

After a fourth calibration pass focused on the two remaining separate-model
misses, the CSVs include more benign-but-cautionary `review` URLs with
hyphen-heavy account/update/login language, more legitimate delivery and contact
verification messages, and nearby suspicious controls with account threats,
shorteners, HTTP, and code language:

```text
Calibration examples: 116
Feature columns: 30
Heuristic accuracy: 100.0%
Unified baseline accuracy: 96.6%
Unified baseline misses: 4
Separate baseline accuracy: 100.0%
Separate baseline misses: 0
```

Current unified-model misses:

| Sample | Expected | Baseline | Pattern |
| --- | --- | --- | --- |
| `suspicious_brand_impersonation` | `suspicious` | `review` | Unified training still underweights some brand impersonation URLs. |
| `suspicious_apple_impersonation` | `suspicious` | `review` | Unified training still underweights some brand impersonation URLs. |
| `suspicious_netflix_impersonation` | `suspicious` | `review` | Unified training still underweights some brand impersonation URLs. |
| `suspicious_whatsapp_impersonation` | `suspicious` | `review` | Unified training still underweights some brand impersonation URLs. |

Current separate-model misses: none.

## Fifth Calibration Result

After expanding the brand impersonation URL family, adding nearby `review`
controls for account/update/login and multi-subdomain URLs, and reinforcing
deep-chain and sensitive-code suspicious examples:

```text
Calibration examples: 178
Feature columns: 30
Heuristic accuracy: 100.0%
Unified baseline accuracy: 100.0%
Unified baseline misses: 0
Separate baseline accuracy: 100.0%
Separate baseline misses: 0
```

Current unified-model misses: none.

Current separate-model misses: none.

## Sixth Calibration Result

After adding 40 bilingual calibration examples focused on realistic safe
messages, trusted-account URLs, shortener-only review cases, code/contact review
messages, and nearby suspicious controls:

```text
Calibration examples: 218
Feature columns: 30
Heuristic accuracy: 100.0%
Unified baseline accuracy: 100.0%
Unified baseline misses: 0
Separate baseline accuracy: 100.0%
Separate baseline misses: 0
```

Current unified-model misses: none.

Current separate-model misses: none.

## Seventh Calibration Result

After adding Spanish-language message signals for urgency, credentials, account
threats, rewards, and code-like numbers:

```text
Calibration examples: 222
Feature columns: 30
Heuristic accuracy: 100.0%
Unified baseline accuracy: 100.0%
Unified baseline misses: 0
Separate baseline accuracy: 100.0%
Separate baseline misses: 0
```

Current unified-model misses: none.

Current separate-model misses: none.

## Eighth Calibration Result

After adding a URL lookalike signal for brand-like domains using common
character substitutions such as `0`, `1`, and `rn`:

```text
Calibration examples: 230
Feature columns: 31
Heuristic accuracy: 100.0%
Unified baseline accuracy: 99.6%
Unified baseline misses: 1
Separate baseline accuracy: 99.6%
Separate baseline misses: 1
```

Current unified-model misses:

| Sample | Expected | Baseline | Pattern |
| --- | --- | --- | --- |
| `review_paypal_lookalike` | `review` | `suspicious` | A simple lookalike-only URL is intentionally cautionary, while the model treats the new signal as high risk. |

Current separate-model misses:

| Sample | Expected | Baseline | Pattern |
| --- | --- | --- | --- |
| `review_paypal_lookalike` | `review` | `suspicious` | The separate URL model also overweights the new lookalike signal without nearby review variants. |

## Unified Vs Separate Models

Current comparison:

```text
Unified baseline accuracy: 99.6%
Separate baseline accuracy: 99.6%

Unified per-type accuracy:
- message: 100.0%
- url: 99.3%

Separate per-type accuracy:
- message: 100.0%
- url: 99.3%
```

Interpretation:

- The added targeted examples removed the previous separate-model misses around
  hyphen-heavy account URLs and legitimate delivery verification messages.
- A fifth targeted pass added more suspicious brand impersonation URL variants,
  nearby `review` URL controls, deep phishing chains, and sensitive-code message
  examples.
- A sixth targeted pass added bilingual realistic examples, especially
  `likely_safe` cases, to reduce overfitting to suspicious and review patterns.
- A seventh targeted pass added Spanish-language social engineering terms with
  accent normalization, without introducing calibration misses.
- An eighth targeted pass added URL lookalike detection and surfaced one model
  miss where a simple lookalike-only URL is expected to stay in `review`.
- Keep comparing unified and separate baselines side by side because the dataset
  is still intentionally small and highly curated.

## Next Data Priorities

- Add fresh brand impersonation, deep-chain, shortener, and sensitive-code
  examples only when they represent new user-facing patterns.
- Add new delivery/contact verification examples only when fresh user-facing
  patterns appear, since the current separate message baseline has no misses.
- Keep watching for `suspicious` shortener-plus-banking, deep-chain phishing,
  and account-code regressions as the dataset grows.
- Add nearby `review` lookalike variants so the baseline learns the boundary
  between cautionary lookalike URLs and high-risk lookalike phishing clusters.
- Keep adding benign bilingual examples with ordinary support, delivery,
  invoice, and meeting language so `likely_safe` remains well represented.
- Keep heuristic and baseline results side by side until the dataset is larger
  and model metrics are less sensitive to individual examples.
- Treat both baseline strategies as experimental comparisons; the heuristic API
  behavior remains the primary user-facing path.
