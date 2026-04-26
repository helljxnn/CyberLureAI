import re

from backend.app.schemas.analysis_signal import AnalysisSignal
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
URGENCY_TERMS = ("urgent", "immediately", "now", "asap", "today", "last chance")
SENSITIVE_TERMS = ("password", "code", "otp", "pin", "verify", "credentials")
THREAT_TERMS = ("suspend", "suspended", "locked", "blocked", "disabled", "expire")
REWARD_TERMS = ("winner", "claim", "gift", "prize", "bonus", "refund", "reward")
SHORTENER_DOMAINS = (
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
    "rebrand.ly",
    "shorturl.at",
    "lnkd.in",
)
URL_PATTERN = re.compile(r"(?:https?://|www\.)[^\s]+", re.IGNORECASE)
ONE_TIME_CODE_PATTERN = re.compile(r"\b\d{4,8}\b")


def _add_signal(
    signals: list[AnalysisSignal],
    code: str,
    severity: str,
    score: int,
    description: str,
) -> int:
    signals.append(
        AnalysisSignal(
            code=code,
            severity=severity,
            score=score,
            description=description,
        )
    )
    return score


def analyze_message(message: str) -> MessageAnalysisResponse:
    lowered_message = message.lower()
    links = URL_PATTERN.findall(lowered_message)
    signals: list[AnalysisSignal] = []
    risk_score = 5

    if any(pattern in lowered_message for pattern in SUSPICIOUS_PATTERNS):
        risk_score += _add_signal(
            signals,
            "scam_phrase",
            "medium",
            25,
            "The message includes phrases commonly used in scams or phishing attempts.",
        )

    if links:
        risk_score += _add_signal(
            signals,
            "contains_link",
            "medium",
            20,
            "The message contains a link and should be checked carefully before opening.",
        )

    if any(shortener in link for link in links for shortener in SHORTENER_DOMAINS):
        risk_score += _add_signal(
            signals,
            "shortened_link",
            "high",
            20,
            "The message uses a shortened link, which can hide the final destination.",
        )

    if any(word in lowered_message for word in URGENCY_TERMS):
        risk_score += _add_signal(
            signals,
            "urgency_pressure",
            "medium",
            15,
            "The message uses urgency language to pressure quick action.",
        )

    if any(word in lowered_message for word in SENSITIVE_TERMS):
        risk_score += _add_signal(
            signals,
            "sensitive_information_request",
            "high",
            20,
            "The message asks for sensitive information or account verification.",
        )

    if any(word in lowered_message for word in THREAT_TERMS):
        risk_score += _add_signal(
            signals,
            "account_restriction_threat",
            "high",
            15,
            "The message threatens account restriction or loss of access.",
        )

    if any(word in lowered_message for word in REWARD_TERMS):
        risk_score += _add_signal(
            signals,
            "reward_lure",
            "medium",
            15,
            "The message uses reward or prize language often seen in scams.",
        )

    if ONE_TIME_CODE_PATTERN.search(message) and any(
        word in lowered_message for word in ("code", "otp", "pin")
    ):
        risk_score += _add_signal(
            signals,
            "code_like_number",
            "medium",
            10,
            "The message includes a code-like number connected to verification language.",
        )

    if any(symbol in message for symbol in ("!!!", "$", "%")):
        risk_score += _add_signal(
            signals,
            "aggressive_formatting",
            "low",
            10,
            "The message uses aggressive punctuation or promotional symbols.",
        )

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

    if not signals:
        _add_signal(
            signals,
            "no_strong_indicators",
            "info",
            0,
            "No strong scam indicators were detected by the initial heuristic rules.",
        )

    reasons = [signal.description for signal in signals]

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
        signals=signals,
    )
