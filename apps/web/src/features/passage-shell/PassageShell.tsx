import type { ExperienceCapabilitiesV1, ExperienceMode } from "@/domain/experience/port";
import type { PassageCoreV1 } from "@/domain/passage/port";
import { AvailabilityPanel } from "./AvailabilityPanel";
import { FixtureBanner } from "./FixtureBanner";
import { ModeSwitch } from "./ModeSwitch";
import type { PassagePageFailure } from "./page-state";
import { ReleaseBadge } from "./ReleaseBadge";

export function PassageShell(props: {
  passage: PassageCoreV1;
  capabilities: ExperienceCapabilitiesV1;
  mode: ExperienceMode;
}) {
  const resolved = props.passage.resolvedReference;
  const reference = resolved?.referenceLabel ?? "Direct ReferenceSpan request";
  const referenceSystemCode = resolved?.referenceSystemCode ?? "UNSPECIFIED";

  return (
    <main className="page-shell" data-testid="passage-shell">
      <FixtureBanner />
      <header className="hero">
        <div>
          <p className="eyebrow">Hebrew-Chinese Bible Research</p>
          <h1>{reference}</h1>
          <p className="subtitle">Phase 1 serving-shell fixture for release and reference identity only.</p>
        </div>
        <ReleaseBadge researchReleaseId={props.passage.researchReleaseId} />
      </header>

      <ModeSwitch
        mode={props.mode}
        releaseId={props.passage.researchReleaseId}
        reference={reference}
        referenceSystemCode={referenceSystemCode}
      />

      <section className="identity-grid" aria-label="Resolved scholarly identity">
        <article>
          <span className="label">Experience</span>
          <strong data-testid="active-mode">{props.mode === "STUDY" ? "Study" : "Research"}</strong>
        </article>
        <article>
          <span className="label">Reference system</span>
          <strong data-testid="reference-system">{referenceSystemCode}</strong>
        </article>
        <article>
          <span className="label">ReferenceSpan</span>
          <code data-testid="reference-span">{props.passage.referenceSpanId}</code>
        </article>
        <article>
          <span className="label">Fixture capability</span>
          <strong>{props.capabilities.featureDecisions.PASSAGE_STUDY ?? "UNSPECIFIED"}</strong>
        </article>
      </section>

      <section className="passage-placeholder" aria-labelledby="passage-heading">
        <div>
          <p className="eyebrow">Passage</p>
          <h2 id="passage-heading">Serving projection intentionally not frozen</h2>
        </div>
        <p>
          P1-VS-001 verifies a release-pinned ReferenceSpan envelope. Hebrew text, translations, linguistic
          analysis and evidence remain outside this fixture slice until their database and publication paths are
          implemented.
        </p>
      </section>

      <AvailabilityPanel />
    </main>
  );
}

export function PassageFailureView({ failure }: { failure: PassagePageFailure }) {
  return (
    <main className="page-shell failure-shell" data-testid="passage-failure" data-error-code={failure.code}>
      <FixtureBanner />
      <section className="failure-card">
        <p className="eyebrow">P1-VS-001 fixture shell</p>
        <h1>{failure.title}</h1>
        <p>{failure.message}</p>
        <code>{failure.code}</code>
      </section>
    </main>
  );
}
