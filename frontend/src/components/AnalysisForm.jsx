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
  const canSubmit = inputMode === "file" ? (value !== null && !isLoading) : (typeof value === 'string' && value.trim().length > 0 && !isLoading);

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
      ) : inputMode === "file" ? (
        <div className="file-drop-area">
          <input
            id={inputId}
            type="file"
            accept=".exe,.dll,.bin"
            onChange={(event) => {
              if (event.target.files && event.target.files.length > 0) {
                onChange(event.target.files[0]);
              }
            }}
            required
          />
          <div className="file-drop-text">
            {value ? (
              <strong>{value.name}</strong>
            ) : (
              <span>Arrastra un archivo aquí o <strong>haz clic para buscar</strong></span>
            )}
          </div>
        </div>
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
      
      {examples && examples.length > 0 && (
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
      )}
      
      <button className="primary-button" type="submit" disabled={!canSubmit}>
        {isLoading ? loadingLabel : actionLabel}
      </button>
    </form>
  );
}
