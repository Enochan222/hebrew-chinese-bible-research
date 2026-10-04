const modules = ["Translations", "Analysis", "Corpus", "Evidence"] as const;

export function AvailabilityPanel() {
  return (
    <section className="availability" aria-labelledby="availability-heading">
      <h2 id="availability-heading">Reserved research modules</h2>
      <div className="module-grid">
        {modules.map((module) => (
          <article key={module}>
            <h3>{module}</h3>
            <p>Not part of P1-VS-001. This fixture shell does not invent later-phase scholarly data.</p>
          </article>
        ))}
      </div>
    </section>
  );
}
