import {
  formatConfidence,
  formatSignalCode,
  formatVerdict,
  getRiskMetadata,
  getSafeChecklist,
  getVerdictMeaning,
} from "../config/analysisContent";

export default function ResultPanel({ title, state }) {
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
  const experimentalModel = state.data.experimental_model;
  const modelDisagrees = experimentalModel?.agrees_with_heuristic === false;

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
      <div className="verdict-meaning">
        <span>{formatVerdict(state.data.verdict)}</span>
        <p>{getVerdictMeaning(state.data.verdict)}</p>
      </div>
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
      {experimentalModel && (
        <>
          <h3>Experimental model</h3>
          <p className={modelDisagrees ? "model-note model-warning" : "model-note"}>
            {modelDisagrees
              ? "The experimental model disagrees with the explainable heuristic. Use the heuristic verdict as the user-facing decision for now."
              : "The experimental model agrees with the explainable heuristic for this check."}
          </p>
          <div className="model-comparison">
            <div>
              <span className="comparison-label">Strategy</span>
              <strong>{experimentalModel.strategy}</strong>
            </div>
            <div>
              <span className="comparison-label">Model verdict</span>
              <strong>
                {experimentalModel.verdict
                  ? formatVerdict(experimentalModel.verdict)
                  : "Unavailable"}
              </strong>
            </div>
            <div>
              <span className="comparison-label">Confidence</span>
              <strong>{formatConfidence(experimentalModel.confidence)}</strong>
            </div>
            <div>
              <span className="comparison-label">Heuristic match</span>
              <strong>
                {experimentalModel.agrees_with_heuristic === true
                  ? "Yes"
                  : experimentalModel.agrees_with_heuristic === false
                    ? "No"
                    : "Unavailable"}
              </strong>
            </div>
          </div>
          <p className="model-note">{experimentalModel.note}</p>
        </>
      )}
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
