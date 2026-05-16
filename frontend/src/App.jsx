import { useMemo, useState } from "react";

import AnalysisForm from "./components/AnalysisForm";
import ApiConnectionPanel from "./components/ApiConnectionPanel";
import EducationSection from "./components/EducationSection";
import HistoryPanel from "./components/HistoryPanel";
import ResultPanel from "./components/ResultPanel";
import {
  DEFAULT_API_URL,
  MALWARE_EXAMPLES,
  MESSAGE_EXAMPLES,
  URL_EXAMPLES,
} from "./config/analysisContent";
import {
  analyzeMalware,
  analyzeMessage,
  analyzeUrl,
  checkApiConnection,
  parseAppError,
} from "./services/apiClient";
import {
  createHistoryEntry,
  HISTORY_LIMIT,
  loadAnalysisHistory,
  saveAnalysisHistory,
} from "./services/historyStorage";

const INITIAL_URL_RESULT = {
  kind: "empty",
  message: "Run a URL analysis to see risk level, reasons, and recommended action.",
};

const INITIAL_MESSAGE_RESULT = {
  kind: "empty",
  message: "Run a message analysis to inspect social engineering indicators.",
};

const INITIAL_MALWARE_RESULT = {
  kind: "empty",
  message: "Paste PE header feature values (JSON) to detect malware with the ML classifier.",
};

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_API_URL);
  const [analysisHistory, setAnalysisHistory] = useState(loadAnalysisHistory);
  const [connectionState, setConnectionState] = useState({
    tone: "neutral",
    message: "Use this before testing the analysis forms.",
  });
  const [urlInput, setUrlInput] = useState("");
  const [messageInput, setMessageInput] = useState("");
  const [malwareInput, setMalwareInput] = useState("");
  const [urlResult, setUrlResult] = useState(INITIAL_URL_RESULT);
  const [messageResult, setMessageResult] = useState(INITIAL_MESSAGE_RESULT);
  const [malwareResult, setMalwareResult] = useState(INITIAL_MALWARE_RESULT);

  const cleanBaseUrl = useMemo(() => apiBaseUrl.trim().replace(/\/+$/, ""), [apiBaseUrl]);
  const isUrlLoading = urlResult.kind === "loading";
  const isMessageLoading = messageResult.kind === "loading";
  const isMalwareLoading = malwareResult.kind === "loading";

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
      const data = await checkApiConnection(cleanBaseUrl);
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
      const data = await analyzeUrl(cleanBaseUrl, urlInput);
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
      const data = await analyzeMessage(cleanBaseUrl, messageInput);
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

  async function handleMalwareSubmit(event) {
    event.preventDefault();
    setMalwareResult({ kind: "loading", message: "Analyzing malware features..." });

    let parsedFeatures;
    try {
      parsedFeatures = JSON.parse(malwareInput);
    } catch {
      setMalwareResult({
        kind: "error",
        message: "Invalid JSON. Paste a valid JSON object with PE header feature values.",
        details: [],
      });
      return;
    }

    if (typeof parsedFeatures !== "object" || parsedFeatures === null || Array.isArray(parsedFeatures)) {
      setMalwareResult({
        kind: "error",
        message: "Expected a JSON object with PE header feature names and values.",
        details: [],
      });
      return;
    }

    try {
      const data = await analyzeMalware(cleanBaseUrl, parsedFeatures);
      setMalwareResult({ kind: "success", data });
      addHistoryEntry("Malware", malwareInput.trim().substring(0, 80) + "...", data);
    } catch (error) {
      const parsed = parseAppError(error);
      setMalwareResult({
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

        <ApiConnectionPanel
          apiBaseUrl={apiBaseUrl}
          connectionState={connectionState}
          onApiBaseUrlChange={setApiBaseUrl}
          onCheckConnection={checkConnection}
        />
      </header>

      <main className="content-grid">
        <section className="card analysis-card">
          <div className="card-header">
            <p className="section-kicker">Analyze a link</p>
            <h2>Suspicious URL review</h2>
          </div>

          <AnalysisForm
            actionLabel="Analyze URL"
            examples={URL_EXAMPLES}
            inputId="url-input"
            inputMode="input"
            isLoading={isUrlLoading}
            label="Paste a URL"
            loadingLabel="Analyzing..."
            placeholder="http://secure-login-example.com/verify"
            value={urlInput}
            onChange={setUrlInput}
            onSubmit={handleUrlSubmit}
          />

          <ResultPanel title="URL analysis failed" state={urlResult} />
        </section>

        <section className="card analysis-card">
          <div className="card-header">
            <p className="section-kicker">Analyze a message</p>
            <h2>Suspicious message review</h2>
          </div>

          <AnalysisForm
            actionLabel="Analyze message"
            examples={MESSAGE_EXAMPLES}
            inputId="message-input"
            inputMode="textarea"
            isLoading={isMessageLoading}
            label="Paste a message"
            loadingLabel="Analyzing..."
            placeholder="Urgent: verify your bank account now by clicking https://fake-bank-alert.example"
            value={messageInput}
            onChange={setMessageInput}
            onSubmit={handleMessageSubmit}
          />

          <ResultPanel title="Message analysis failed" state={messageResult} />
        </section>

        <section className="card analysis-card">
          <div className="card-header">
            <p className="section-kicker">Malware detection</p>
            <h2>PE header classifier</h2>
          </div>

          <AnalysisForm
            actionLabel="Analyze file"
            examples={MALWARE_EXAMPLES}
            inputId="malware-input"
            inputMode="textarea"
            isLoading={isMalwareLoading}
            label="Paste PE header features (JSON)"
            loadingLabel="Analyzing..."
            placeholder='{ "e_cblp": 144, "e_cp": 3, "packer_type": "NoPacker", ... }'
            value={malwareInput}
            onChange={setMalwareInput}
            onSubmit={handleMalwareSubmit}
          />

          <ResultPanel title="Malware analysis failed" state={malwareResult} />
        </section>

        <EducationSection />

        <HistoryPanel
          history={analysisHistory}
          onClearHistory={clearHistory}
          onUseHistoryEntry={useHistoryEntry}
        />
      </main>
    </div>
  );
}
