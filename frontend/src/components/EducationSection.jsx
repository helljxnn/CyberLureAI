export default function EducationSection() {
  return (
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
  );
}
