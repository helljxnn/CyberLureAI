from backend.app.schemas.message_analysis import MessageAnalysisResponse


SUSPICIOUS_PATTERNS = (
    "urgent",
    "verify your account",
    "click here",
    "limited time",
    "bank",
    "password",
    "security alert",
    "suspend",
    "winner",
    "claim",
    "otp",
    "code",
    "gift",
)


def analyze_message(message: str) -> MessageAnalysisResponse:
    lowered_message = message.lower()
    reasons: list[str] = []
    risk_score = 5

    if any(pattern in lowered_message for pattern in SUSPICIOUS_PATTERNS):
        risk_score += 25
        reasons.append("The message includes phrases commonly used in scams or phishing attempts.")

    if "http://" in lowered_message or "https://" in lowered_message or "www." in lowered_message:
        risk_score += 20
        reasons.append("The message contains a link and should be checked carefully before opening.")

    if any(word in lowered_message for word in ("urgent", "immediately", "now", "asap")):
        risk_score += 15
        reasons.append("The message uses urgency language to pressure quick action.")

    if any(word in lowered_message for word in ("password", "code", "otp", "verify")):
        risk_score += 20
        reasons.append("The message asks for sensitive information or account verification.")

    if any(symbol in message for symbol in ("!!!", "$", "%")):
        risk_score += 10
        reasons.append("The message uses aggressive punctuation or promotional symbols.")

    risk_score = min(risk_score, 100)

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

    if not reasons:
        reasons.append("No strong scam indicators were detected by the initial heuristic rules.")

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
        reasons=reasons,
    )
