import type { ReleaseReadPort } from "../release/port";
import { resolveRelease, type ReleaseSelector } from "../release/service";
import { validatePassageLocator } from "../passage/service";
import { ReferenceNotFoundError } from "../passage/errors";
import type { PassageLabelLocator } from "../passage/port";
import type { TranslationWitnessListV1, TranslationWitnessReadPort } from "./port";

export async function readTranslationWitnesses(input: {
  selector: ReleaseSelector;
  locator: PassageLabelLocator;
  releaseReader: ReleaseReadPort;
  translationReader: TranslationWitnessReadPort;
}): Promise<TranslationWitnessListV1> {
  const locator = validatePassageLocator(input.locator);
  const researchReleaseId = await resolveRelease(input.selector, input.releaseReader);
  const witnesses = await input.translationReader.getTranslationWitnesses({ researchReleaseId, locator });
  if (!witnesses) {
    throw new ReferenceNotFoundError("Requested reference is not present in the selected ResearchRelease.");
  }
  if (witnesses.researchReleaseId !== researchReleaseId) {
    throw new Error("Translation witnesses resolved to a different ResearchRelease than requested.");
  }
  return witnesses;
}
