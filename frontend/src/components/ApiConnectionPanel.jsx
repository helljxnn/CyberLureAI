export default function ApiConnectionPanel({
  apiBaseUrl,
  connectionState,
  onApiBaseUrlChange,
  onCheckConnection,
}) {
  return (
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
        onChange={(event) => onApiBaseUrlChange(event.target.value)}
        spellCheck="false"
      />
      <button className="secondary-button" type="button" onClick={onCheckConnection}>
        Check API status
      </button>
      <p className="status-note" data-tone={connectionState.tone}>
        {connectionState.message}
      </p>
    </aside>
  );
}
