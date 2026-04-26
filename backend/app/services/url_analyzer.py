from backend.app.schemas.url_analysis import URLAnalysisResponse
from backend.app.services.features.common import BASE_RISK_SCORE, total_signal_score
from backend.app.services.features.url_features import extract_url_signals


def analyze_url(url: str) -> URLAnalysisResponse:
    signals = extract_url_signals(url)
    risk_score = min(BASE_RISK_SCORE + total_signal_score(signals), 100)

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
        reasons=[signal.description for signal in signals],
        signals=signals,
    )
