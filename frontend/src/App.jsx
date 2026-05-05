import { useMemo, useState } from "react";

const DEFAULT_API_URL = "http://127.0.0.1:8000";
const HISTORY_KEY = "cyberlureai.analysisHistory";
const HISTORY_LIMIT = 6;
const URL_EXAMPLES = [
  {
    label: "Trusted site",
    tone: "low",
    hint: "Expected: likely safe",
    value: "https://www.openai.com",
  },
  {
    label: "Review URL",
    tone: "medium",
    hint: "Expected: needs review",
    value: "https://account-update-center.example.org",
  },
  {
    label: "Short link",
    tone: "medium",
    hint: "Expected: needs review",
    value: "https://bit.ly/account-update",
  },
  {
    label: "Bank warning",
    tone: "high",
    hint: "Expected: suspicious",
    value: "http://bank-account-verify-login.example.com",
  },
];
const MESSAGE_EXAMPLES = [
  {
    label: "Meeting note",
    tone: "low",
    hint: "Expected: likely safe",
    value: "Hi, just checking in to confirm our meeting tomorrow.",
  },
  {
    label: "Delivery check",
    tone: "medium",
    hint: "Expected: needs review",
    value:
      "Please verify the delivery address today at https://example.com/address-check",
  },
  {
    label: "Account threat",
    tone: "high",
    hint: "Expected: suspicious",
    value:
      "Security alert: your account will be locked today. Verify now at https://bit.ly/secure-login",
  },
  {
    label: "Prize lure",
    tone: "high",
    hint: "Expected: suspicious",
    value: "Winner!!! Claim your bonus now at www.reward-center.example with code 884422",
  },
];
const RISK_METADATA = {
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
const VERDICT_LABELS = {
  likely_safe: "Likely safe",
  review: "Needs review",
  suspicious: "Suspicious",
};
const SAFE_CHECKLIST = {
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

function loadAnalysisHistory() {
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

function saveAnalysisHistory(history) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch {
    // Local storage can be unavailable in private or restricted browser contexts.
  }
}

function createHistoryEntry(kind, input, data) {
  return {
    id: `${Date.now()}-${kind}`,
    kind,
    input,
    risk_level: data.risk_level,
    risk_score: data.risk_score,
    verdict: data.verdict,
    created_at: new Date().toLocaleString(),
  };
}

function getRiskMetadata(riskLevel) {
  return (
    RISK_METADATA[riskLevel] || {
      label: "Unknown risk",
      summary: "The backend returned a risk level the interface does not recognize yet.",
      insight: "Review the detailed reasons and verify the source before taking action.",
    }
  );
}

function formatVerdict(verdict) {
  const value = String(verdict || "unknown");
  return VERDICT_LABELS[value] || value.replaceAll("_", " ");
}

function getSafeChecklist(verdict) {
  return SAFE_CHECKLIST[verdict] || SAFE_CHECKLIST.review;
}

function formatSignalCode(code) {
  return String(code || "unknown_signal").replaceAll("_", " ");
}

function parseAppError(error) {
  try {
    return JSON.parse(error.message);
  } catch {
    return {
      message: "The request could not be completed.",
      details: [error.message],
    };
  }
}

async function fetchJson(baseUrl, path, options = {}) {
  const response = await fetch(`${baseUrl.replace(/\/+$/, "")}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const details = Array.isArray(data.details)
      ? data.details.map((detail) => `${detail.field}: ${detail.message}`)
      : [];
    throw new Error(
      JSON.stringify({
        message: data.message || "Request failed.",
        details,
      })
    );
  }

  return data;
}

function ResultPanel({ title, state }) {
  if (state.kind === "empty") {
    return (
      <div className="result-panel empty-state" aria-live="polite">
        {state.message}
      </div>
    );
  }

  if (state.kind === "loading") {
    return (
      <div className="result-panel loading-state" aria-live="polite">
        {state.message}
      </div>
    );
  }

  if (state.kind === "error") {
    return (
      <div className="result-panel result-error" aria-live="polite">
        <div className="result-meta">
          <span className="pill pill-risk-high">Error</span>
        </div>
        <h3>{title}</h3>
        <p>{state.message}</p>
        {state.details.length > 0 && (
          <ul>
            {state.details.map((detail) => (
              <li key={detail}>{detail}</li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  const riskClass = `pill-risk-${state.data.risk_level}`;
  const risk = getRiskMetadata(state.data.risk_level);
  const score = Math.min(100, Math.max(0, Number(state.data.risk_score) || 0));
  const signals = Array.isArray(state.data.signals) ? state.data.signals : [];
  const checklist = getSafeChecklist(state.data.verdict);

  return (
    <div className="result-panel result-success" data-risk={state.data.risk_level} aria-live="polite">
      <div className="result-score-row">
        <div>
          <p className="result-label">Risk summary</p>
          <h3>{risk.label}</h3>
        </div>
        <span className={`score-badge ${riskClass}`}>{score}/100</span>
      </div>
      <div className="score-track" aria-label={`Risk score ${score} out of 100`}>
        <span style={{ width: `${score}%` }} />
      </div>
      <p className="result-summary">{risk.summary}</p>
      <div className="result-meta result-meta-grid">
        <span className={`pill ${riskClass}`}>Risk: {risk.label}</span>
        <span className={`pill ${riskClass}`}>Verdict: {formatVerdict(state.data.verdict)}</span>
        <span className="pill pill-neutral">Signals: {signals.length}</span>
      </div>
      <h3>Explanation</h3>
      <p>{state.data.explanation}</p>
      <h3>Why it matters</h3>
      <p>{risk.insight}</p>
      <h3>Recommended action</h3>
      <p>{state.data.recommended_action}</p>
      <h3>Safe next steps</h3>
      <ul className="compact-list">
        {checklist.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ul>
      {signals.length > 0 && (
        <>
          <h3>Detected signals</h3>
          <div className="signal-list">
            {signals.map((signal) => (
              <article className="signal-item" key={signal.code}>
                <div>
                  <span className="signal-code">{formatSignalCode(signal.code)}</span>
                  <p>{signal.description}</p>
                </div>
                <span className={`signal-meta signal-${signal.severity}`}>
                  {signal.severity} +{signal.score}
                </span>
              </article>
            ))}
          </div>
        </>
      )}
      <h3>Reasons</h3>
      <ul>
        {state.data.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    </div>
  );
}

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_API_URL);
  const [analysisHistory, setAnalysisHistory] = useState(loadAnalysisHistory);
  const [connectionState, setConnectionState] = useState({
    tone: "neutral",
    message: "Use this before testing the analysis forms.",
  });
  const [urlInput, setUrlInput] = useState("");
  const [messageInput, setMessageInput] = useState("");
  const [urlResult, setUrlResult] = useState({
    kind: "empty",
    message: "Run a URL analysis to see risk level, reasons, and recommended action.",
  });
  const [messageResult, setMessageResult] = useState({
    kind: "empty",
    message: "Run a message analysis to inspect social engineering indicators.",
  });

  const cleanBaseUrl = useMemo(() => apiBaseUrl.trim().replace(/\/+$/, ""), [apiBaseUrl]);
  const isUrlLoading = urlResult.kind === "loading";
  const isMessageLoading = messageResult.kind === "loading";
  const canAnalyzeUrl = urlInput.trim().length > 0 && !isUrlLoading;
  const canAnalyzeMessage = messageInput.trim().length > 0 && !isMessageLoading;

  function addHistoryEntry(kind, input, data) {
    const entry = createHistoryEntry(kind, input, data);
    setAnalysisHistory((currentHistory) => {
      const nextHistory = [entry, ...currentHistory].slice(0, HISTORY_LIMIT);
      saveAnalysisHistory(nextHistory);
      return nextHistory;
    });
  }

  function clearHistory() {
    saveAnalysisHistory([]);
    setAnalysisHistory([]);
  }

  function useHistoryEntry(item) {
    if (item.kind === "URL") {
      setUrlInput(item.input);
      return;
    }

    setMessageInput(item.input);
  }

  async function checkConnection() {
    setConnectionState({ tone: "neutral", message: "Checking backend..." });

    try {
      const data = await fetchJson(cleanBaseUrl, "/");
      setConnectionState({
        tone: "success",
        message: `Connected to ${data.name} (${data.environment})`,
      });
    } catch {
      setConnectionState({
        tone: "error",
        message: "Could not reach the backend. Check the API URL and run the server.",
      });
    }
  }

  async function handleUrlSubmit(event) {
    event.preventDefault();
    setUrlResult({ kind: "loading", message: "Analyzing URL..." });

    try {
      const data = await fetchJson(cleanBaseUrl, "/analyze/url", {
        method: "POST",
        body: JSON.stringify({ url: urlInput }),
      });
      setUrlResult({ kind: "success", data });
      addHistoryEntry("URL", urlInput.trim(), data);
    } catch (error) {
      const parsed = parseAppError(error);
      setUrlResult({
        kind: "error",
        message: parsed.message,
        details: parsed.details,
      });
    }
  }

  async function handleMessageSubmit(event) {
    event.preventDefault();
    setMessageResult({ kind: "loading", message: "Analyzing message..." });

    try {
      const data = await fetchJson(cleanBaseUrl, "/analyze/message", {
        method: "POST",
        body: JSON.stringify({ message: messageInput }),
      });
      setMessageResult({ kind: "success", data });
      addHistoryEntry("Message", messageInput.trim(), data);
    } catch (error) {
      const parsed = parseAppError(error);
      setMessageResult({
        kind: "error",
        message: parsed.message,
        details: parsed.details,
      });
    }
  }

  return (
    <div className="page-shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">CyberLureAI MVP</p>
          <h1>Spot suspicious links and messages before they become a real problem.</h1>
          <p className="hero-text">
            CyberLureAI is an AI-assisted cybersecurity project focused on helping people
            understand digital risk in clear language.
          </p>
        </div>

        <aside className="hero-panel">
          <h2>API connection</h2>
          <label className="field-label" htmlFor="api-base-url">
            Backend URL
          </label>
          <input
            id="api-base-url"
            className="text-input"
            type="url"
            value={apiBaseUrl}
            onChange={(event) => setApiBaseUrl(event.target.value)}
            spellCheck="false"
          />
          <button className="secondary-button" type="button" onClick={checkConnection}>
            Check API status
          </button>
          <p className="status-note" data-tone={connectionState.tone}>
            {connectionState.message}
          </p>
        </aside>
      </header>

      <main className="content-grid">
        <section className="card analysis-card">
          <div className="card-header">
            <p className="section-kicker">Analyze a link</p>
            <h2>Suspicious URL review</h2>
          </div>

          <form className="analysis-form" onSubmit={handleUrlSubmit}>
            <label className="field-label" htmlFor="url-input">
              Paste a URL
            </label>
            <input
              id="url-input"
              className="text-input"
              type="url"
              placeholder="http://secure-login-example.com/verify"
              value={urlInput}
              onChange={(event) => setUrlInput(event.target.value)}
              required
            />
            <div className="example-row">
              {URL_EXAMPLES.map((example) => (
                <button
                  key={example.label}
                  className="ghost-button"
                  data-tone={example.tone}
                  type="button"
                  title={example.hint}
                  onClick={() => setUrlInput(example.value)}
                >
                  <span>{example.label}</span>
                  <small>{example.hint}</small>
                </button>
              ))}
            </div>
            <button className="primary-button" type="submit" disabled={!canAnalyzeUrl}>
              {isUrlLoading ? "Analyzing..." : "Analyze URL"}
            </button>
          </form>

          <ResultPanel title="URL analysis failed" state={urlResult} />
        </section>

        <section className="card analysis-card">
          <div className="card-header">
            <p className="section-kicker">Analyze a message</p>
            <h2>Suspicious message review</h2>
          </div>

          <form className="analysis-form" onSubmit={handleMessageSubmit}>
            <label className="field-label" htmlFor="message-input">
              Paste a message
            </label>
            <textarea
              id="message-input"
              className="text-area"
              rows="6"
              placeholder="Urgent: verify your bank account now by clicking https://fake-bank-alert.example"
              value={messageInput}
              onChange={(event) => setMessageInput(event.target.value)}
              required
            />
            <div className="example-row">
              {MESSAGE_EXAMPLES.map((example) => (
                <button
                  key={example.label}
                  className="ghost-button"
                  data-tone={example.tone}
                  type="button"
                  title={example.hint}
                  onClick={() => setMessageInput(example.value)}
                >
                  <span>{example.label}</span>
                  <small>{example.hint}</small>
                </button>
              ))}
            </div>
            <button className="primary-button" type="submit" disabled={!canAnalyzeMessage}>
              {isMessageLoading ? "Analyzing..." : "Analyze message"}
            </button>
          </form>

          <ResultPanel title="Message analysis failed" state={messageResult} />
        </section>

        <section className="learn-section">
          <div className="card-header">
            <p className="section-kicker">What this MVP does</p>
            <h2>How to read the results</h2>
          </div>

          <div className="tips-list">
            <article className="tip-item">
              <h3>Risk score</h3>
              <p>Shows the current heuristic score from 0 to 100 for fast comparison.</p>
            </article>
            <article className="tip-item">
              <h3>Signals</h3>
              <p>Names the patterns that triggered the current explainable analysis.</p>
            </article>
            <article className="tip-item">
              <h3>Safe next steps</h3>
              <p>Turns the verdict into practical actions for non-technical users.</p>
            </article>
            <article className="tip-item">
              <h3>Next sprint focus</h3>
              <p>Keep comparing heuristic results against the experimental baseline.</p>
            </article>
          </div>
        </section>

        <section className="history-section">
          <div className="history-header">
            <div>
              <p className="section-kicker">Recent checks</p>
              <h2>Analysis history</h2>
            </div>
            <button
              className="ghost-button"
              type="button"
              onClick={clearHistory}
              disabled={analysisHistory.length === 0}
            >
              Clear history
            </button>
          </div>

          {analysisHistory.length === 0 ? (
            <p className="history-empty">Successful analyses will appear here for quick comparison.</p>
          ) : (
            <div className="history-list">
              {analysisHistory.map((item) => {
                const itemRisk = getRiskMetadata(item.risk_level);
                const itemRiskClass = `pill-risk-${item.risk_level}`;

                return (
                  <article className="history-item" data-risk={item.risk_level} key={item.id}>
                    <div>
                      <span className="history-kind">{item.kind}</span>
                      <h3>
                        {itemRisk.label} | {item.risk_score}/100
                      </h3>
                      <p>{item.input}</p>
                      <span className="history-time">{item.created_at}</span>
                    </div>
                    <div className="history-actions">
                      <span className={`pill ${itemRiskClass}`}>{formatVerdict(item.verdict)}</span>
                      <button
                        className="ghost-button compact-button"
                        type="button"
                        onClick={() => useHistoryEntry(item)}
                      >
                        Reuse
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
