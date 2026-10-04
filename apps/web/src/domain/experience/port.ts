import type { ResearchReleaseId } from "../release/port";

export type ExperienceMode = "STUDY" | "RESEARCH";

export type AvailabilityReasonCode =
  | "FEATURE_NOT_ENTITLED"
  | "SOURCE_RIGHTS_RESTRICTED"
  | "NOT_IN_RESEARCH_RELEASE"
  | "NOT_YET_REVIEWED"
  | "DISCOVERY_PROVIDER_UNAVAILABLE"
  | "COVERAGE_NOT_AVAILABLE"
  | "DATA_TEMPORARILY_UNAVAILABLE";

export type ExperienceCapabilitiesV1 = {
  researchReleaseId: ResearchReleaseId;
  experienceModesAllowed: ExperienceMode[];
  featureDecisions: Record<string, "ALLOW" | "DENY">;
  reasonCodes: Record<string, AvailabilityReasonCode>;
  validUntil?: string | null;
};

export interface ExperienceCapabilityPort {
  getCapabilities(input: { researchReleaseId: ResearchReleaseId }): Promise<ExperienceCapabilitiesV1>;
}
