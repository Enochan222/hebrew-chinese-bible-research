const fixtureModules = ["Translations", "Analysis", "Corpus", "Evidence"] as const;

const servingModules = [
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

export function AvailabilityPanel({
  isServing = false,
  translationWitnessCount = 0,
}: {
  isServing?: boolean;
  translationWitnessCount?: number;
}) {
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
        <article>
          <h3>Translations</h3>
          <p>
            {translationWitnessCount > 0
              ? `${translationWitnessCount} rights-approved release-pinned witness${translationWitnessCount === 1 ? "" : "es"} available above.`
              : "No translation witness is published for this passage in the selected ResearchRelease."}
          </p>
        </article>
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
