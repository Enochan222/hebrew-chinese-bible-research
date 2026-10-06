import "server-only";

import type { PassageReadPort } from "@/domain/passage/port";
import { loadCanonicalFixtureSet } from "./contract-fixtures.server";

export class FixturePassageReader implements PassageReadPort {
  async getPassageCore(input: Parameters<PassageReadPort["getPassageCore"]>[0]) {
    const fixture = loadCanonicalFixtureSet();
    if (input.researchReleaseId !== fixture.releasePointer.researchReleaseId) return null;
    if (
      input.locator.referenceSystemCode !== fixture.passageLocator.referenceSystemCode ||
      input.locator.referenceLabel !== fixture.passageLocator.referenceLabel
    ) {
      return null;
    }
    return { ...fixture.passageCore, dataSource: "FIXTURE" as const };
  }
}
