const HISTORY_KEY = "cyberlureai.analysisHistory";
export const HISTORY_LIMIT = 6;

export function loadAnalysisHistory() {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const storedHistory = window.localStorage.getItem(HISTORY_KEY);
    const parsedHistory = JSON.parse(storedHistory || "[]");
    return Array.isArray(parsedHistory) ? parsedHistory.slice(0, HISTORY_LIMIT) : [];
  } catch {
    return [];
  }
}

export function saveAnalysisHistory(history) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch {
    // Local storage can be unavailable in private or restricted browser contexts.
  }
}

export function createHistoryEntry(kind, input, data) {
  return {
    id: `${Date.now()}-${kind}`,
    kind,
    input,
    risk_level: data.risk_level,
    risk_score: data.risk_score,
    verdict: data.verdict,
    experimental_verdict: data.experimental_model?.verdict || null,
    experimental_agrees: data.experimental_model?.agrees_with_heuristic ?? null,
    created_at: new Date().toLocaleString(),
  };
}
