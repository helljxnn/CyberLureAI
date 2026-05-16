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
  Malware: "Malware check",
};

export const MALWARE_EXAMPLES = [
  {
    label: "Benign file",
    tone: "low",
    hint: "Expected: likely safe",
    value: JSON.stringify({
      e_cblp: 0, e_cp: 3, e_cparhdr: 4, e_maxalloc: 65535, e_sp: 184,
      e_lfanew: 64, NumberOfSections: 1, CreationYear: 0,
      FH_char0: 0, FH_char1: 1, FH_char2: 0, FH_char3: 0,
      FH_char4: 0, FH_char5: 0, FH_char6: 0, FH_char7: 1,
      FH_char8: 0, FH_char9: 0, FH_char10: 0, FH_char11: 0,
      FH_char12: 0, FH_char13: 0, FH_char14: 0,
      MajorLinkerVersion: 1, MinorLinkerVersion: 0,
      SizeOfCode: 0, SizeOfInitializedData: 1024, SizeOfUninitializedData: 0,
      AddressOfEntryPoint: 0, BaseOfCode: 0, BaseOfData: 0, ImageBase: 0,
      SectionAlignment: 1, FileAlignment: 1,
      MajorOperatingSystemVersion: 1, MinorOperatingSystemVersion: 0,
      MajorImageVersion: 0, MinorImageVersion: 0,
      MajorSubsystemVersion: 3, MinorSubsystemVersion: 10,
      SizeOfImage: 1, SizeOfHeaders: 1, CheckSum: 0, Subsystem: 3,
      OH_DLLchar0: 1, OH_DLLchar1: 0, OH_DLLchar2: 0, OH_DLLchar3: 0,
      OH_DLLchar4: 0, OH_DLLchar5: 0, OH_DLLchar6: 0, OH_DLLchar7: 0,
      OH_DLLchar8: 0, OH_DLLchar9: 0, OH_DLLchar10: 0,
      SizeOfStackReserve: 65536, SizeOfStackCommit: 4096,
      SizeOfHeapReserve: 1048576, SizeOfHeapCommit: 4096, LoaderFlags: 0,
      sus_sections: 0, non_sus_sections: 1, packer: 0,
      packer_type: "NoPacker",
      E_text: 0.0, E_data: 5.2, filesize: 1024, E_file: 3.2, fileinfo: 0,
    }),
  },
  {
    label: "Suspicious packed",
    tone: "high",
    hint: "Expected: suspicious",
    value: JSON.stringify({
      e_cblp: 0, e_cp: 3, e_cparhdr: 4, e_maxalloc: 65535, e_sp: 184,
      e_lfanew: 128, NumberOfSections: 16, CreationYear: 1,
      FH_char0: 0, FH_char1: 0, FH_char2: 0, FH_char3: 0,
      FH_char4: 0, FH_char5: 0, FH_char6: 0, FH_char7: 0,
      FH_char8: 0, FH_char9: 0, FH_char10: 0, FH_char11: 0,
      FH_char12: 0, FH_char13: 0, FH_char14: 0,
      MajorLinkerVersion: 0, MinorLinkerVersion: 0,
      SizeOfCode: 0, SizeOfInitializedData: 0, SizeOfUninitializedData: 0,
      AddressOfEntryPoint: 0, BaseOfCode: 0, BaseOfData: 0, ImageBase: 0,
      SectionAlignment: 1, FileAlignment: 1,
      MajorOperatingSystemVersion: 0, MinorOperatingSystemVersion: 0,
      MajorImageVersion: 0, MinorImageVersion: 0,
      MajorSubsystemVersion: 0, MinorSubsystemVersion: 0,
      SizeOfImage: 1, SizeOfHeaders: 1, CheckSum: 0, Subsystem: 2,
      OH_DLLchar0: 0, OH_DLLchar1: 0, OH_DLLchar2: 0, OH_DLLchar3: 0,
      OH_DLLchar4: 0, OH_DLLchar5: 0, OH_DLLchar6: 0, OH_DLLchar7: 0,
      OH_DLLchar8: 0, OH_DLLchar9: 0, OH_DLLchar10: 0,
      SizeOfStackReserve: 1048576, SizeOfStackCommit: 4096,
      SizeOfHeapReserve: 1048576, SizeOfHeapCommit: 4096, LoaderFlags: 1,
      sus_sections: 12, non_sus_sections: 4, packer: 1,
      packer_type: "MPRESS",
      E_text: 8.8, E_data: 6.5, filesize: 51200, E_file: 7.8, fileinfo: 1,
    }),
  },
];

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
