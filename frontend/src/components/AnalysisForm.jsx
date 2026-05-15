export default function AnalysisForm({
  actionLabel,
  examples,
  inputId,
  inputMode,
  isLoading,
  label,
  loadingLabel,
  placeholder,
  value,
  onChange,
  onSubmit,
}) {
  const canSubmit = value.trim().length > 0 && !isLoading;

  return (
    <form className="analysis-form" onSubmit={onSubmit}>
      <label className="field-label" htmlFor={inputId}>
        {label}
      </label>
      {inputMode === "textarea" ? (
        <textarea
          id={inputId}
          className="text-area"
          rows="6"
          placeholder={placeholder}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          required
        />
      ) : (
        <input
          id={inputId}
          className="text-input"
          type="url"
          placeholder={placeholder}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          required
        />
      )}
      <div className="example-row">
        {examples.map((example) => (
          <button
            key={example.label}
            className="ghost-button"
            data-tone={example.tone}
            type="button"
            title={example.hint}
            onClick={() => onChange(example.value)}
          >
            <span>{example.label}</span>
            <small>{example.hint}</small>
          </button>
        ))}
      </div>
      <button className="primary-button" type="submit" disabled={!canSubmit}>
        {isLoading ? loadingLabel : actionLabel}
      </button>
    </form>
  );
}
