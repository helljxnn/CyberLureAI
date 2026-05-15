import {
  formatHistoryKind,
  formatVerdict,
  getRiskMetadata,
} from "../config/analysisContent";

export default function HistoryPanel({ history, onClearHistory, onUseHistoryEntry }) {
  return (
    <section className="history-section">
      <div className="history-header">
        <div>
          <p className="section-kicker">Recent checks</p>
          <h2>Analysis history</h2>
        </div>
        <button
          className="ghost-button"
          type="button"
          onClick={onClearHistory}
          disabled={history.length === 0}
        >
          Clear history
        </button>
      </div>

      {history.length === 0 ? (
        <p className="history-empty">Successful analyses will appear here for quick comparison.</p>
      ) : (
        <div className="history-list">
          {history.map((item) => {
            const itemRisk = getRiskMetadata(item.risk_level);
            const itemRiskClass = `pill-risk-${item.risk_level}`;

            return (
              <article className="history-item" data-risk={item.risk_level} key={item.id}>
                <div>
                  <span className="history-kind">{formatHistoryKind(item.kind)}</span>
                  <h3>
                    {formatHistoryKind(item.kind)} | {itemRisk.label} | {item.risk_score}/100
                  </h3>
                  <p>{item.input}</p>
                  <span className="history-time">{item.created_at}</span>
                </div>
                <div className="history-actions">
                  <span className={`pill ${itemRiskClass}`}>{formatVerdict(item.verdict)}</span>
                  {item.experimental_verdict && (
                    <span
                      className={`pill ${
                        item.experimental_agrees === false ? "pill-risk-medium" : "pill-neutral"
                      }`}
                    >
                      {item.experimental_agrees === false ? "Model differs: " : "Model: "}
                      {formatVerdict(item.experimental_verdict)}
                    </span>
                  )}
                  <button
                    className="ghost-button compact-button"
                    type="button"
                    onClick={() => onUseHistoryEntry(item)}
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
  );
}
