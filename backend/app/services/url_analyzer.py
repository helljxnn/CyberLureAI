from ipaddress import ip_address
from urllib.parse import urlparse

from backend.app.schemas.analysis_signal import AnalysisSignal
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
SHORTENER_DOMAINS = {
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
}
BRAND_TRUSTED_ROOTS = {
    "amazon": "amazon.com",
    "apple": "apple.com",
    "bancolombia": "bancolombia.com",
    "facebook": "facebook.com",
    "google": "google.com",
    "instagram": "instagram.com",
    "microsoft": "microsoft.com",
    "netflix": "netflix.com",
    "paypal": "paypal.com",
    "whatsapp": "whatsapp.com",
}


def _root_domain(hostname: str) -> str:
    labels = [label for label in hostname.split(".") if label]
    if len(labels) < 2:
        return hostname
    return ".".join(labels[-2:])


def _is_ip_address(hostname: str) -> bool:
    try:
        ip_address(hostname)
    except ValueError:
        return False
    return True


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


def analyze_url(url: str) -> URLAnalysisResponse:
    lowered_url = url.lower()
    parsed_url = urlparse(lowered_url)
    hostname = parsed_url.hostname or ""
    normalized_hostname = hostname.removeprefix("www.")
    host_labels = [label for label in hostname.split(".") if label]
    root_domain = _root_domain(normalized_hostname)
    signals: list[AnalysisSignal] = []
    risk_score = 5
    keyword_hits = [keyword for keyword in SUSPICIOUS_KEYWORDS if keyword in lowered_url]
    brand_hits = [
        brand
        for brand, trusted_root in BRAND_TRUSTED_ROOTS.items()
        if brand in normalized_hostname and root_domain != trusted_root
    ]

    if "@" in lowered_url:
        risk_score += _add_signal(
            signals,
            "hidden_destination_marker",
            "high",
            30,
            "The URL contains '@', which can hide the real destination.",
        )

    if normalized_hostname in SHORTENER_DOMAINS:
        risk_score += _add_signal(
            signals,
            "link_shortener",
            "high",
            35,
            "The URL uses a link shortener, which can hide the final destination.",
        )

    if _is_ip_address(hostname):
        risk_score += _add_signal(
            signals,
            "ip_address_destination",
            "high",
            35,
            "The URL uses an IP address instead of a recognizable domain name.",
        )

    if hostname.count("-") >= 2:
        risk_score += _add_signal(
            signals,
            "repeated_hyphens",
            "medium",
            15,
            "The URL uses multiple hyphens, a common phishing pattern.",
        )

    if keyword_hits:
        risk_score += _add_signal(
            signals,
            "phishing_keywords",
            "medium",
            25,
            "The URL contains keywords commonly used in phishing attempts.",
        )

    if len(keyword_hits) >= 3:
        risk_score += _add_signal(
            signals,
            "multiple_phishing_keywords",
            "high",
            20,
            "The URL combines multiple phishing-related keywords in the same address.",
        )

    if len(host_labels) >= 4:
        risk_score += _add_signal(
            signals,
            "many_subdomains",
            "medium",
            15,
            "The URL has many subdomains, which can be used to mimic trusted brands.",
        )

    if len(host_labels) >= 5:
        risk_score += _add_signal(
            signals,
            "deep_subdomain_chain",
            "medium",
            10,
            "The URL uses an unusually deep subdomain chain.",
        )

    if brand_hits and keyword_hits:
        risk_score += _add_signal(
            signals,
            "brand_impersonation",
            "high",
            25,
            "The URL appears to combine a known brand name with an untrusted domain.",
        )

    if parsed_url.scheme == "http":
        risk_score += _add_signal(
            signals,
            "insecure_http",
            "medium",
            10,
            "The URL does not use HTTPS.",
        )

    if parsed_url.scheme == "http" and len(keyword_hits) >= 2:
        risk_score += _add_signal(
            signals,
            "http_with_phishing_terms",
            "high",
            10,
            "The URL mixes an insecure protocol with several suspicious phishing terms.",
        )

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

    if not signals:
        _add_signal(
            signals,
            "no_strong_indicators",
            "info",
            0,
            "No strong phishing indicators were detected by the initial heuristic rules.",
        )

    reasons = [signal.description for signal in signals]

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
        signals=signals,
    )
