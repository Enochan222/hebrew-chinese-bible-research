import Link from "next/link";
import type { ExperienceCapabilitiesV1, ExperienceMode } from "@/domain/experience/port";
import type { PassageCoreV1 } from "@/domain/passage/port";
import type { TranslationWitnessListV1 } from "@/domain/translation/port";
import { AvailabilityPanel } from "./AvailabilityPanel";
import { FixtureBanner } from "./FixtureBanner";
import { ModeSwitch } from "./ModeSwitch";
import type { PassagePageFailure } from "./page-state";
import { ReleaseBadge } from "./ReleaseBadge";
import { ReferenceNavigator } from "./ReferenceNavigator";
import { TranslationWitnessPanel } from "./TranslationWitnessPanel";

export function PassageShell(props: {
  passage: PassageCoreV1;
  capabilities: ExperienceCapabilitiesV1;
  translations?: TranslationWitnessListV1;
  mode: ExperienceMode;
}) {
  const resolved = props.passage.resolvedReference;
  const reference = resolved?.referenceLabel ?? "Direct ReferenceSpan request";
  const referenceSystemCode = resolved?.referenceSystemCode ?? "UNSPECIFIED";
  const isServing = props.passage.dataSource === "SERVING";
  const navigation = props.passage.navigation;

  const passageHref = (target: string) =>
    `/releases/${encodeURIComponent(props.passage.researchReleaseId)}/passages/${encodeURIComponent(target)}?referenceSystemCode=${encodeURIComponent(referenceSystemCode)}&mode=${encodeURIComponent(props.mode)}`;

  return (
    <main className="page-shell" data-testid="passage-shell" data-source-mode={isServing ? "SERVING" : "FIXTURE"}>
      {isServing ? (
        <div className="serving-banner" role="status" data-testid="serving-banner">
          Published database-backed passage from an immutable ResearchRelease.
        </div>
      ) : (
        <FixtureBanner />
      )}

      <header className="hero">
        <div>
          <p className="eyebrow">Hebrew-Chinese Bible Research</p>
          <h1>{reference}</h1>
          <p className="subtitle">
            {isServing
              ? "Release-pinned OSHB word tokens and morphology from the published Serving projection."
              : "Phase 1 serving-shell fixture for release and reference identity only."}
          </p>
        </div>
        <ReleaseBadge researchReleaseId={props.passage.researchReleaseId} />
      </header>

      <ModeSwitch
        mode={props.mode}
        releaseId={props.passage.researchReleaseId}
        reference={reference}
        referenceSystemCode={referenceSystemCode}
      />

      {isServing && navigation?.books?.length ? (
        <ReferenceNavigator
          researchReleaseId={props.passage.researchReleaseId}
          referenceSystemCode={referenceSystemCode}
          currentReference={reference}
          mode={props.mode}
          navigation={navigation}
        />
      ) : null}

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
          <span className="label">{isServing ? "Passage capability" : "Fixture capability"}</span>
          <strong>{props.capabilities.featureDecisions.PASSAGE_STUDY ?? "UNSPECIFIED"}</strong>
        </article>
      </section>

      {isServing ? (
        <>
          <section className="passage-reader" aria-labelledby="passage-heading">
            <div className="passage-reader-heading">
              <div>
                <p className="eyebrow">OSHB source tokens</p>
                <h2 id="passage-heading">{reference}</h2>
              </div>
              <nav className="passage-navigation" aria-label="Passage navigation">
                {navigation?.previousReference ? (
                  <Link href={passageHref(navigation.previousReference)}>Previous</Link>
                ) : (
                  <span aria-disabled="true">Previous</span>
                )}
                {navigation?.nextReference ? (
                  <Link href={passageHref(navigation.nextReference)}>Next</Link>
                ) : (
                  <span aria-disabled="true">Next</span>
                )}
              </nav>
            </div>
            <p className="hebrew-text" dir="rtl" lang="he" data-testid="hebrew-text">
              {props.passage.hebrewText}
            </p>
            {props.passage.textReconstructionStatus === "OSHB_WORD_TOKENS_ONLY" ? (
              <p className="reconstruction-note">
                Word-token display only. Independent OSHB punctuation segments such as maqqef, paseq and sof pasuq
                are not yet reconstructed into this display string.
              </p>
            ) : null}
            <div className="token-grid" aria-label="OSHB word morphology">
              {(props.passage.tokens ?? []).map((token, index) => (
                <article key={token.analysisNodeId} className="token-card">
                  <strong dir="rtl" lang="he">{token.surface}</strong>
                  <span>#{index + 1}</span>
                  {token.lemmaRaw ? <code>lemma {token.lemmaRaw}</code> : null}
                  {token.morphRaw ? <code>morph {token.morphRaw}</code> : null}
                </article>
              ))}
            </div>
            <p className="attribution" data-testid="passage-attribution">
              {props.passage.attribution}
            </p>
          </section>
          {props.translations ? <TranslationWitnessPanel list={props.translations} /> : null}
          <AvailabilityPanel
            isServing
            translationWitnessCount={props.translations?.witnesses.length ?? 0}
          />
        </>
      ) : (
        <>
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
        </>
      )}
    </main>
  );
}

export function PassageFailureView({ failure }: { failure: PassagePageFailure }) {
  return (
    <main className="page-shell failure-shell" data-testid="passage-failure" data-error-code={failure.code}>
      <section className="failure-card">
        <p className="eyebrow">Hebrew-Chinese Bible Research</p>
        <h1>{failure.title}</h1>
        <p>{failure.message}</p>
        <code>{failure.code}</code>
      </section>
    </main>
  );
}
