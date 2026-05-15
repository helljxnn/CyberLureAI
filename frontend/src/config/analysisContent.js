export const DEFAULT_API_URL = "http://127.0.0.1:8000";

export const URL_EXAMPLES = [
  {
    label: "Trusted help",
    tone: "low",
    hint: "Expected: likely safe",
    value: "https://www.gov.co/servicios-y-tramites",
  },
  {
    label: "Portal update",
    tone: "medium",
    hint: "Expected: needs review",
    value: "https://account-update-center.example.org",
  },
  {
    label: "Short link ES",
    tone: "medium",
    hint: "Expected: needs review",
    value: "https://bit.ly/actualizacion-reunion",
  },
  {
    label: "Bank warning ES",
    tone: "high",
    hint: "Expected: suspicious",
    value: "https://bit.ly/bank-account-verify-login-colombia",
  },
];

export const MESSAGE_EXAMPLES = [
  {
    label: "Reunion segura",
    tone: "low",
    hint: "Expected: likely safe",
    value: "Hola, confirmo la reunion con soporte para manana a las nueve.",
  },
  {
    label: "Codigo entrega",
    tone: "medium",
    hint: "Expected: needs review",
    value: "Tu codigo 123456 para recoger el paquete vence al final del dia.",
  },
  {
    label: "Cuenta bloqueada",
    tone: "high",
    hint: "Expected: suspicious",
    value:
      "Urgente: tu cuenta del banco fue bloqueada hoy. Verifica ahora en https://bit.ly/banco-ayuda",
  },
  {
    label: "Premio falso",
    tone: "high",
    hint: "Expected: suspicious",
    value: "Ganador!!! Reclama tu premio ahora en www.premio-centro.example con codigo 481920",
  },
];

export const RISK_METADATA = {
  low: {
    label: "Low risk",
    summary: "No strong indicators were found in this first-pass review.",
    insight:
      "This does not guarantee safety, but it means the current rules did not find strong warning signs.",
  },
  medium: {
    label: "Medium risk",
    summary: "Some indicators deserve a careful manual check before continuing.",
    insight:
      "Pause before clicking or replying, especially if the sender is unexpected or asks for personal data.",
  },
  high: {
    label: "High risk",
    summary: "Multiple indicators suggest this content should be treated as suspicious.",
    insight:
      "Treat this as unsafe until verified through a trusted channel outside the message or link.",
  },
};

export const VERDICT_LABELS = {
  likely_safe: "Likely safe",
  review: "Needs review",
  suspicious: "Suspicious",
};

export const VERDICT_MEANINGS = {
  likely_safe:
    "The current rules did not find strong warning signs. Keep normal caution before sharing data.",
  review:
    "There are warning signs worth checking manually before clicking, replying, or entering information.",
  suspicious:
    "Treat this as unsafe. Verify through an official channel instead of trusting the message or link.",
};

export const HISTORY_KIND_LABELS = {
  URL: "URL check",
  Message: "Message check",
};

export const SAFE_CHECKLIST = {
  likely_safe: [
    "Confirm the domain or sender is the one you expected.",
    "Avoid entering sensitive data unless you initiated the action.",
  ],
  review: [
    "Verify the sender through a trusted channel before clicking.",
    "Inspect the full domain and avoid entering passwords or codes.",
  ],
  suspicious: [
    "Do not click, reply, or enter personal information.",
    "Report or delete it, then verify the issue through an official channel.",
  ],
};

export function getRiskMetadata(riskLevel) {
  return (
    RISK_METADATA[riskLevel] || {
      label: "Unknown risk",
      summary: "The backend returned a risk level the interface does not recognize yet.",
      insight: "Review the detailed reasons and verify the source before taking action.",
    }
  );
}

export function formatVerdict(verdict) {
  const value = String(verdict || "unknown");
  return VERDICT_LABELS[value] || value.replaceAll("_", " ");
}

export function getVerdictMeaning(verdict) {
  return VERDICT_MEANINGS[verdict] || VERDICT_MEANINGS.review;
}

export function formatHistoryKind(kind) {
  return HISTORY_KIND_LABELS[kind] || kind;
}

export function getSafeChecklist(verdict) {
  return SAFE_CHECKLIST[verdict] || SAFE_CHECKLIST.review;
}

export function formatSignalCode(code) {
  return String(code || "unknown_signal").replaceAll("_", " ");
}

export function formatConfidence(confidence) {
  if (typeof confidence !== "number") {
    return "Unavailable";
  }

  return `${Math.round(confidence * 100)}%`;
}
