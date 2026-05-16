import re
import unicodedata

from backend.app.schemas.analysis_signal import AnalysisSignal
from backend.app.services.features.common import add_signal


SUSPICIOUS_PATTERNS = (
    "urgent",
    "urgente",
    "verify your account",
    "verifica tu cuenta",
    "verificar tu cuenta",
    "click here",
    "haz clic",
    "limited time",
    "tiempo limitado",
    "bank",
    "banco",
    "password",
    "contrasena",
    "security alert",
    "alerta de seguridad",
    "suspend",
    "suspender",
    "suspendida",
    "bloqueada",
    "winner",
    "ganador",
    "claim",
    "reclama",
    "otp",
    "code",
    "codigo",
    "clave",
    "gift",
    "regalo",
    "premio",
    "congratulations",
    "you have been selected",
    "your account has been",
    "unusual activity",
    "flagged",
    "marcada",
    "microsoft support",
    "soporte microsoft",
    "wire transfer",
    "transferencia",
    "tax document",
    "approve this",
    "apruebe",
    "locked",
    "bloqueado",
    "renew your",
    "renovar su",
    "compromised",
    "comprometido",
)
URGENCY_TERMS = (
    "urgent",
    "urgente",
    "immediately",
    "inmediatamente",
    "now",
    "ahora",
    "asap",
    "today",
    "hoy",
    "last chance",
    "ultima oportunidad",
    "limited",
    "limitado",
    "expires",
    "expira",
    "24 hour",
    "24 horas",
    "do not close",
    "do not ignore",
    "no cierre",
)
SENSITIVE_TERMS = (
    "password",
    "contrasena",
    "code",
    "codigo",
    "otp",
    "pin",
    "clave",
    "verify",
    "verifica",
    "verificar",
    "credentials",
    "credenciales",
    "confirm your",
    "confirma tu",
    "personal details",
    "datos personales",
    "card details",
    "bank details",
    "datos bancarios",
    "social security",
    "seguro social",
    "w-2",
    "tax id",
    "identificacion tributaria",
)
THREAT_TERMS = (
    "suspend",
    "suspended",
    "suspendido",
    "suspendida",
    "locked",
    "blocked",
    "bloqueado",
    "bloqueada",
    "disabled",
    "expire",
    "expira",
    "vencera",
    "unusual activity",
    "actividad inusual",
    "flagged",
    "marcada",
    "violation",
    "violacion",
    "compromised",
    "comprometido",
    "comprometida",
)
REWARD_TERMS = (
    "winner",
    "ganador",
    "claim",
    "reclama",
    "gift",
    "regalo",
    "prize",
    "premio",
    "bonus",
    "bono",
    "refund",
    "reembolso",
    "reward",
    "recompensa",
    "congratulations",
    "felicidades",
    "selected",
    "seleccionado",
    "seleccionada",
    "free",
    "gratis",
    "guaranteed",
    "garantizado",
    "investment",
    "inversion",
    "returns",
    "retornos",
    "double your",
    "duplica tu",
)
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


def _normalize_for_matching(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def extract_message_signals(message: str) -> list[AnalysisSignal]:
    lowered_message = _normalize_for_matching(message)
    links = URL_PATTERN.findall(lowered_message)
    signals: list[AnalysisSignal] = []

    if any(pattern in lowered_message for pattern in SUSPICIOUS_PATTERNS):
        add_signal(
            signals,
            "scam_phrase",
            "medium",
            25,
            "The message includes phrases commonly used in scams or phishing attempts.",
        )

    if links:
        add_signal(
            signals,
            "contains_link",
            "medium",
            20,
            "The message contains a link and should be checked carefully before opening.",
        )

    if any(shortener in link for link in links for shortener in SHORTENER_DOMAINS):
        add_signal(
            signals,
            "shortened_link",
            "high",
            20,
            "The message uses a shortened link, which can hide the final destination.",
        )

    if any(word in lowered_message for word in URGENCY_TERMS):
        add_signal(
            signals,
            "urgency_pressure",
            "medium",
            15,
            "The message uses urgency language to pressure quick action.",
        )

    if any(word in lowered_message for word in SENSITIVE_TERMS):
        add_signal(
            signals,
            "sensitive_information_request",
            "high",
            20,
            "The message asks for sensitive information or account verification.",
        )

    if any(word in lowered_message for word in THREAT_TERMS):
        add_signal(
            signals,
            "account_restriction_threat",
            "high",
            15,
            "The message threatens account restriction or loss of access.",
        )

    if any(word in lowered_message for word in REWARD_TERMS):
        add_signal(
            signals,
            "reward_lure",
            "medium",
            15,
            "The message uses reward or prize language often seen in scams.",
        )

    if ONE_TIME_CODE_PATTERN.search(message) and any(
        word in lowered_message for word in ("code", "codigo", "otp", "pin", "clave")
    ):
        add_signal(
            signals,
            "code_like_number",
            "medium",
            10,
            "The message includes a code-like number connected to verification language.",
        )

    if any(symbol in message for symbol in ("!!!", "$", "%")):
        add_signal(
            signals,
            "aggressive_formatting",
            "low",
            10,
            "The message uses aggressive punctuation or promotional symbols.",
        )

    if not signals:
        add_signal(
            signals,
            "no_strong_indicators",
            "info",
            0,
            "No strong scam indicators were detected by the initial heuristic rules.",
        )

    return signals
