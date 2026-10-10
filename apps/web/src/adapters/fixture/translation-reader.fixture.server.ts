import "server-only";

import { assertContract } from "@/contracts/validate.server";
import { readContractJson } from "@/contracts/schema-registry.server";
import type { TranslationWitnessListV1, TranslationWitnessReadPort } from "@/domain/translation/port";

export class FixtureTranslationWitnessReader implements TranslationWitnessReadPort {
  async getTranslationWitnesses(
    input: Parameters<TranslationWitnessReadPort["getTranslationWitnesses"]>[0],
  ): Promise<TranslationWitnessListV1 | null> {
    const fixture = readContractJson("fixtures/translation-witness-list.json");
    assertContract<TranslationWitnessListV1>("translationWitnessList", fixture);
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
