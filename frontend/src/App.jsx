import { useMemo, useState } from "react";

const DEFAULT_API_URL = "http://127.0.0.1:8000";
const URL_EXAMPLES = [
  {
    label: "Safe example",
    value: "https://www.openai.com",
  },
  {
    label: "Suspicious example",
    value: "http://secure-login-bank-verify.example.com",
  },
];
const MESSAGE_EXAMPLES = [
  {
    label: "Safe example",
    value: "Hi, just checking in to confirm our meeting tomorrow.",
  },
  {
    label: "Suspicious example",
    value: "Urgent: verify your bank account now by clicking https://fake-bank-alert.example",
  },
];

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
    return <div className="result-panel empty-state">{state.message}</div>;
  }

  if (state.kind === "loading") {
    return <div className="result-panel">{state.message}</div>;
  }

  if (state.kind === "error") {
    return (
      <div className="result-panel">
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

  return (
    <div className="result-panel">
      <div className="result-meta">
        <span className={`pill ${riskClass}`}>Risk: {state.data.risk_level}</span>
        <span className={`pill ${riskClass}`}>Score: {state.data.risk_score}</span>
        <span className={`pill ${riskClass}`}>Verdict: {state.data.verdict}</span>
      </div>
      <h3>Explanation</h3>
      <p>{state.data.explanation}</p>
      <h3>Recommended action</h3>
      <p>{state.data.recommended_action}</p>
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
                  type="button"
                  onClick={() => setUrlInput(example.value)}
                >
                  {example.label}
                </button>
              ))}
            </div>
            <button className="primary-button" type="submit">
              Analyze URL
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
                  type="button"
                  onClick={() => setMessageInput(example.value)}
                >
                  {example.label}
                </button>
              ))}
            </div>
            <button className="primary-button" type="submit">
              Analyze message
            </button>
          </form>

          <ResultPanel title="Message analysis failed" state={messageResult} />
        </section>

        <section className="card learn-card">
          <div className="card-header">
            <p className="section-kicker">What this MVP does</p>
            <h2>How to read the results</h2>
          </div>

          <div className="tips-list">
            <article className="tip-item">
              <h3>Risk level</h3>
              <p>Shows whether the backend thinks the content looks low, medium, or high risk.</p>
            </article>
            <article className="tip-item">
              <h3>Reasons</h3>
              <p>Lists the patterns that triggered the current heuristic analysis.</p>
            </article>
            <article className="tip-item">
              <h3>Recommended action</h3>
              <p>Gives the next safe step a normal user should take.</p>
            </article>
            <article className="tip-item">
              <h3>Tomorrow&apos;s review focus</h3>
              <p>Check if the scores feel too aggressive, too weak, or just right.</p>
            </article>
          </div>
        </section>
      </main>
    </div>
  );
}
