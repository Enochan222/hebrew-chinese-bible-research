import "server-only";

import { assertContract } from "@/contracts/validate.server";
import type { ExperienceCapabilityPort, ExperienceCapabilitiesV1 } from "@/domain/experience/port";

export class ServingCapabilityReader implements ExperienceCapabilityPort {
  async getCapabilities(
    { researchReleaseId }: Parameters<ExperienceCapabilityPort["getCapabilities"]>[0],
  ): Promise<ExperienceCapabilitiesV1> {
    const capabilities: unknown = {
      researchReleaseId,
      experienceModesAllowed: ["STUDY", "RESEARCH"],
      featureDecisions: {
        PASSAGE_STUDY: "ALLOW",
        PASSAGE_RESEARCH: "ALLOW",
        HEBREW_TEXT: "ALLOW",
        TRANSLATION_WITNESSES: "DENY",
      },
      reasonCodes: {
        TRANSLATION_WITNESSES: "NOT_IN_RESEARCH_RELEASE",
      },
      validUntil: null,
    };
    assertContract<ExperienceCapabilitiesV1>("experienceCapabilities", capabilities);
    return capabilities;
  }
}
