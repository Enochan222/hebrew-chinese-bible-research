import "server-only";

import type { ExperienceCapabilityPort } from "@/domain/experience/port";
import { loadCanonicalFixtureSet } from "./contract-fixtures.server";

export class FixtureCapabilityReader implements ExperienceCapabilityPort {
  async getCapabilities({ researchReleaseId }: Parameters<ExperienceCapabilityPort["getCapabilities"]>[0]) {
    const fixture = loadCanonicalFixtureSet();
    if (researchReleaseId !== fixture.capabilities.researchReleaseId) {
      throw new Error("Capabilities requested for a release outside the canonical fixture set.");
    }
    return fixture.capabilities;
  }
}
