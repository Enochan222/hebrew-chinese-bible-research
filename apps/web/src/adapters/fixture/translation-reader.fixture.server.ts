import "server-only";

import type { TranslationWitnessListV1, TranslationWitnessReadPort } from "@/domain/translation/port";
import { loadCanonicalFixtureSet } from "./contract-fixtures.server";

export class FixtureTranslationWitnessReader implements TranslationWitnessReadPort {
  async getTranslationWitnesses(
    input: Parameters<TranslationWitnessReadPort["getTranslationWitnesses"]>[0],
  ): Promise<TranslationWitnessListV1 | null> {
    const fixture = loadCanonicalFixtureSet().translationWitnessList as TranslationWitnessListV1;
    if (
      fixture.researchReleaseId !== input.researchReleaseId ||
      fixture.resolvedReference.referenceSystemCode !== input.locator.referenceSystemCode ||
      fixture.resolvedReference.referenceLabel !== input.locator.referenceLabel
    ) {
      return null;
    }
    return fixture;
  }
}
