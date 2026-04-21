from backend.app.schemas.url_analysis import URLAnalysisResponse


SUSPICIOUS_KEYWORDS = (
    "login",
    "verify",
    "update",
    "secure",
    "account",
    "confirm",
    "signin",
    "bank",
)


def analyze_url(url: str) -> URLAnalysisResponse:
    lowered_url = url.lower()
    reasons: list[str] = []
    risk_score = 5
    keyword_hits = [keyword for keyword in SUSPICIOUS_KEYWORDS if keyword in lowered_url]

    if "@" in lowered_url:
        risk_score += 30
        reasons.append("The URL contains '@', which can hide the real destination.")

    if lowered_url.count("-") >= 2:
        risk_score += 15
        reasons.append("The URL uses multiple hyphens, a common phishing pattern.")

    if keyword_hits:
        risk_score += 25
        reasons.append("The URL contains keywords commonly used in phishing attempts.")

    if len(keyword_hits) >= 3:
        risk_score += 20
        reasons.append("The URL combines multiple phishing-related keywords in the same address.")

    if lowered_url.count(".") >= 3:
        risk_score += 15
        reasons.append("The URL has many subdomains, which can be used to mimic trusted brands.")

    if lowered_url.startswith("http://"):
        risk_score += 10
        reasons.append("The URL does not use HTTPS.")

    if lowered_url.startswith("http://") and len(keyword_hits) >= 2:
        risk_score += 10
        reasons.append("The URL mixes an insecure protocol with several suspicious phishing terms.")

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "high"
        verdict = "suspicious"
        recommended_action = "Do not open the link or enter personal information."
    elif risk_score >= 40:
        risk_level = "medium"
        verdict = "review"
        recommended_action = "Verify the sender and inspect the domain carefully before continuing."
    else:
        risk_level = "low"
        verdict = "likely_safe"
        recommended_action = "The link looks relatively safe, but keep normal caution."

    if not reasons:
        reasons.append("No strong phishing indicators were detected by the initial heuristic rules.")

    explanation = (
        f"This initial analysis marked the URL as {risk_level} risk "
        f"based on simple phishing heuristics."
    )

    return URLAnalysisResponse(
        url=url,
        risk_level=risk_level,
        risk_score=risk_score,
        verdict=verdict,
        explanation=explanation,
        recommended_action=recommended_action,
        reasons=reasons,
    )
