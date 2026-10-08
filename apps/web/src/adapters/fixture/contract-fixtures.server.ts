import "server-only";

import { assertContract } from "@/contracts/validate.server";
import { readContractJson } from "@/contracts/schema-registry.server";
import type { ReleasePointerV1 } from "@/domain/release/port";
import type { PassageCoreV1, PassageLabelLocator } from "@/domain/passage/port";
import type { ExperienceCapabilitiesV1 } from "@/domain/experience/port";
import type { TranslationWitnessListV1 } from "@/domain/translation/port";

const fixturePaths = {
  releaseChannel: "fixtures/release-channel-production.json",
  releaseManifest: "fixtures/release-manifest.json",
  passageCore: "fixtures/passage-core.json",
  passageRequest: "fixtures/passage-request.json",
  passageLocator: "fixtures/passage-locator-label.json",
  capabilities: "fixtures/experience-capabilities.json",
  translationWitnessList: "fixtures/translation-witness-list.json",
} as const;

type ReleaseChannelFixture = {
  channel: "PREVIEW" | "STAGING" | "PRODUCTION";
  researchReleaseId: string;
};

type ReleaseManifestFixture = {
  researchReleaseId: string;
  releaseLabel: string;
};

type PassageRequestFixture = {
  researchReleaseId?: string | null;
  locator: PassageLabelLocator;
};

export type CanonicalFixtureSet = {
  releasePointer: ReleasePointerV1;
  passageCore: PassageCoreV1;
  passageRequest: PassageRequestFixture;
  passageLocator: PassageLabelLocator;
  capabilities: ExperienceCapabilitiesV1;
  translationWitnessList: TranslationWitnessListV1;
};

let cached: CanonicalFixtureSet | undefined;

export function loadCanonicalFixtureSet(): CanonicalFixtureSet {
  if (cached) return cached;

  const releaseChannel = readContractJson(fixturePaths.releaseChannel);
  assertContract<ReleaseChannelFixture>("releaseChannelPointer", releaseChannel);

  const releaseManifest = readContractJson(fixturePaths.releaseManifest);
  assertContract<ReleaseManifestFixture>("releaseManifest", releaseManifest);

  const passageCore = readContractJson(fixturePaths.passageCore);
  assertContract<PassageCoreV1>("passageCore", passageCore);

  const passageRequest = readContractJson(fixturePaths.passageRequest);
  assertContract<PassageRequestFixture>("passageRequest", passageRequest);

  const passageLocator = readContractJson(fixturePaths.passageLocator);
  assertContract<PassageLabelLocator>("passageLocator", passageLocator);

  const capabilities = readContractJson(fixturePaths.capabilities);
  assertContract<ExperienceCapabilitiesV1>("experienceCapabilities", capabilities);

  const translationWitnessList = readContractJson(fixturePaths.translationWitnessList);
  assertContract<TranslationWitnessListV1>("translationWitnessList", translationWitnessList);

  if (
    releaseChannel.researchReleaseId !== releaseManifest.researchReleaseId ||
    releaseChannel.researchReleaseId !== passageCore.researchReleaseId ||
    releaseChannel.researchReleaseId !== capabilities.researchReleaseId ||
    passageRequest.researchReleaseId !== releaseChannel.researchReleaseId
  ) {
    throw new Error("Canonical fixture chain does not share one ResearchRelease.");
  }

  if (
    passageLocator.referenceSystemCode !== passageRequest.locator.referenceSystemCode ||
    passageLocator.referenceLabel !== passageRequest.locator.referenceLabel ||
    passageCore.resolvedReference?.referenceSystemCode !== passageLocator.referenceSystemCode ||
    passageCore.resolvedReference?.referenceLabel !== passageLocator.referenceLabel
  ) {
    throw new Error("Canonical fixture chain does not share one ReferenceSystem-aware locator.");
  }

  const releasePointer: ReleasePointerV1 = {
    researchReleaseId: releaseChannel.researchReleaseId,
    releaseLabel: releaseManifest.releaseLabel,
    channel: releaseChannel.channel,
  };
  assertContract<ReleasePointerV1>("releasePointer", releasePointer);

  cached = { releasePointer, passageCore, passageRequest, passageLocator, capabilities, translationWitnessList };
  return cached;
}
