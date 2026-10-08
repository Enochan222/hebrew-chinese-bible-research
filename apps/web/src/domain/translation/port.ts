import type { ResearchReleaseId } from "../release/port";
import type { PassageLabelLocator } from "../passage/port";

export type TranslationWitnessSegmentV1 = {
  schemaVersion: "1.1";
  textSegmentId: string;
  textStreamId: string;
  referenceSpanId: string;
  segmentOrder: number;
  segmentKind: string;
  text: string;
  contentHash: string;
};

export type ProviderWitnessBindingV1 = {
  schemaVersion: "1.1";
  bindingMode: "SNAPSHOT_PINNED" | "LIVE_EXTERNAL";
  segmentStorageMode: "PERSISTED_CONTENT" | "PROVIDER_LOCATOR" | "EPHEMERAL";
  providerDistributionId: string;
  reference: string;
  providerSegmentKey?: string | null;
  providerVersion: string | null;
  observedHash: string;
  observedAt: string;
  snapshotContentHash?: string | null;
};

export type TranslationWitnessV1 = {
  schemaVersion: "1.1";
  textualWorkId: string;
  textualEditionId: string | null;
  digitalExpressionId: string;
  displayName: string;
  languageTag: string;
  coverageStatus: "COVERED" | "NOT_COVERED" | "UNKNOWN";
  deliveryStatus: "READY" | "PROVIDER_ERROR" | "STALE" | "NOT_RETRIEVED";
  displayStatus: "DISPLAYABLE" | "RIGHTS_RESTRICTED" | "METADATA_ONLY";
  binding: ProviderWitnessBindingV1;
  rightsDecisionSnapshotId: string;
  provenanceId: string;
  segments: TranslationWitnessSegmentV1[];
  attribution: string | null;
};

export type TranslationWitnessListV1 = {
  schemaVersion: "1.1";
  researchReleaseId: ResearchReleaseId;
  referenceSpanId: string;
  resolvedReference: {
    referenceSystemId: string;
    referenceSystemCode: string;
    referenceLabel: string;
  };
  witnesses: TranslationWitnessV1[];
};

export interface TranslationWitnessReadPort {
  getTranslationWitnesses(input: {
    researchReleaseId: ResearchReleaseId;
    locator: PassageLabelLocator;
  }): Promise<TranslationWitnessListV1 | null>;
}
