const fixtureModules = ["Translations", "Analysis", "Corpus", "Evidence"] as const;

const servingModules = [
  {
    name: "Translations",
    text: "Not in the current OSHB-only ResearchRelease. Translation witnesses remain provider- and rights-gated.",
  },
  {
    name: "Analysis",
    text: "OSHB lemma and morphology are available above. BHSA and bridging remain Authoring-only pending public rights approval.",
  },
  {
    name: "Corpus",
    text: "Whole-Bible OSHB passage coverage is release-pinned. The public reader does not depend on Research Pro.",
  },
  {
    name: "Evidence",
    text: "Research Pro scholarly evidence is a later overlay and is not required for base passage availability.",
  },
] as const;

export function AvailabilityPanel({ isServing = false }: { isServing?: boolean }) {
  if (!isServing) {
    return (
      <section className="availability" aria-labelledby="availability-heading">
        <h2 id="availability-heading">Reserved research modules</h2>
        <div className="module-grid">
          {fixtureModules.map((module) => (
            <article key={module}>
              <h3>{module}</h3>
              <p>Not part of P1-VS-001. This fixture shell does not invent later-phase scholarly data.</p>
            </article>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="availability" aria-labelledby="availability-heading">
      <h2 id="availability-heading">Published module availability</h2>
      <div className="module-grid">
        {servingModules.map((module) => (
          <article key={module.name}>
            <h3>{module.name}</h3>
            <p>{module.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
