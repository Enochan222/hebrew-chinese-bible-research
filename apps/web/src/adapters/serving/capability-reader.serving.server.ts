import "server-only";

import type { ExperienceCapabilityPort } from "@/domain/experience/port";

export class ServingCapabilityReader implements ExperienceCapabilityPort {
  async getCapabilities({ researchReleaseId }: Parameters<ExperienceCapabilityPort["getCapabilities"]>[0]) {
    return {
      researchReleaseId,
      experienceModesAllowed: ["STUDY", "RESEARCH"] as const,
      featureDecisions: {
        PASSAGE_STUDY: "ALLOW" as const,
        PASSAGE_RESEARCH: "ALLOW" as const,
        HEBREW_TEXT: "ALLOW" as const,
        TRANSLATION_WITNESSES: "DENY" as const,
      },
      reasonCodes: {
        TRANSLATION_WITNESSES: "NOT_IN_RESEARCH_RELEASE" as const,
      },
      validUntil: null,
    };
  }
}
