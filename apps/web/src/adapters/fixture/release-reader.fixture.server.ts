import "server-only";

import type { ReleaseReadPort } from "@/domain/release/port";
import { loadCanonicalFixtureSet } from "./contract-fixtures.server";

export class FixtureReleaseReader implements ReleaseReadPort {
  async getCurrentRelease() {
    return loadCanonicalFixtureSet().releasePointer;
  }

  async releaseExists(researchReleaseId: string) {
    return loadCanonicalFixtureSet().releasePointer.researchReleaseId === researchReleaseId;
  }
}
