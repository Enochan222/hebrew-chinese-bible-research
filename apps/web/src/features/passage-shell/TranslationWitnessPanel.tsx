import type { TranslationWitnessListV1 } from "@/domain/translation/port";

export function TranslationWitnessPanel({ list }: { list: TranslationWitnessListV1 }) {
  return (
    <section className="translation-witnesses" aria-labelledby="translation-witness-heading" data-testid="translation-witnesses">
      <div>
        <p className="eyebrow">Translation witnesses</p>
        <h2 id="translation-witness-heading">Release-pinned comparison witnesses</h2>
      </div>
      {list.witnesses.length === 0 ? (
        <p data-testid="translation-witness-empty">
          No translation witness is published for this passage in the selected ResearchRelease.
        </p>
      ) : (
        <div className="module-grid">
          {list.witnesses.map((witness) => (
            <article key={witness.digitalExpressionId} data-display-status={witness.displayStatus}>
              <h3>{witness.displayName}</h3>
              <p>
                {witness.languageTag} · {witness.coverageStatus} · {witness.deliveryStatus} · {witness.displayStatus}
              </p>
              {witness.displayStatus === "DISPLAYABLE" ? (
                <div data-testid="translation-witness-text">
                  {witness.segments.map((segment) => (
                    <p key={segment.textSegmentId} lang={witness.languageTag}>{segment.text}</p>
                  ))}
                </div>
              ) : (
                <p>Translation text is not displayable in this release.</p>
              )}
              {witness.attribution ? <p className="attribution">{witness.attribution}</p> : null}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
