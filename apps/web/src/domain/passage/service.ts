import type { PassageLabelLocator, PassageReadPort, PassageCoreV1 } from "./port";
import { InvalidReferenceError, MissingReferenceSystemError, ReferenceNotFoundError } from "./errors";
import type { ReleaseReadPort } from "../release/port";
import { resolveRelease, type ReleaseSelector } from "../release/service";

export function validatePassageLocator(locator: PassageLabelLocator): PassageLabelLocator {
  if (!locator.referenceSystemCode) {
    throw new MissingReferenceSystemError("referenceSystemCode is required for a human-readable passage label.");
  }
  if (!locator.referenceLabel) {
    throw new InvalidReferenceError("Passage reference must not be empty.");
  }
  return locator;
}

export async function readPassage(input: {
  selector: ReleaseSelector;
  locator: PassageLabelLocator;
  releaseReader: ReleaseReadPort;
  passageReader: PassageReadPort;
}): Promise<PassageCoreV1> {
  const locator = validatePassageLocator(input.locator);
  const researchReleaseId = await resolveRelease(input.selector, input.releaseReader);
  const passage = await input.passageReader.getPassageCore({ researchReleaseId, locator });
  if (!passage) {
    throw new ReferenceNotFoundError("Requested reference is not present in the fixture release.");
  }
  if (passage.researchReleaseId !== researchReleaseId) {
    throw new Error("Fixture passage resolved to a different ResearchRelease than requested.");
  }
  return passage;
}
