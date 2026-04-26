from backend.app.schemas.message_analysis import MessageAnalysisResponse
from backend.app.services.features.common import BASE_RISK_SCORE, total_signal_score
from backend.app.services.features.message_features import extract_message_signals


def analyze_message(message: str) -> MessageAnalysisResponse:
    signals = extract_message_signals(message)
    risk_score = min(BASE_RISK_SCORE + total_signal_score(signals), 100)

    if risk_score >= 70:
        risk_level = "high"
        verdict = "suspicious"
        recommended_action = "Do not reply or click links. Verify the source through a trusted channel."
    elif risk_score >= 40:
        risk_level = "medium"
        verdict = "review"
        recommended_action = "Inspect the message carefully and confirm the sender before taking action."
    else:
        risk_level = "low"
        verdict = "likely_safe"
        recommended_action = "The message looks relatively safe, but continue using normal caution."

    explanation = (
        f"This initial analysis marked the message as {risk_level} risk "
        f"based on simple social engineering heuristics."
    )

    return MessageAnalysisResponse(
        message=message,
        risk_level=risk_level,
        risk_score=risk_score,
        verdict=verdict,
        explanation=explanation,
        recommended_action=recommended_action,
        reasons=[signal.description for signal in signals],
        signals=signals,
    )
