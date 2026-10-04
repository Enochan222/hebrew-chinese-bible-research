import type { ReleaseReadPort, ResearchReleaseId } from "./port";

export type ReleaseSelector =
  | { kind: "CURRENT" }
  | { kind: "PINNED"; researchReleaseId: ResearchReleaseId };

export class InvalidReleaseIdError extends Error {
  readonly code = "INVALID_RELEASE_ID";
}

export class ReleaseNotFoundError extends Error {
  readonly code = "RELEASE_NOT_FOUND";
}

const UUID = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/;

export function isResearchReleaseId(value: string): boolean {
  return UUID.test(value);
}

export async function resolveRelease(
  selector: ReleaseSelector,
  releaseReader: ReleaseReadPort,
): Promise<ResearchReleaseId> {
  if (selector.kind === "CURRENT") {
    const pointer = await releaseReader.getCurrentRelease();
    return pointer.researchReleaseId;
  }

  if (!isResearchReleaseId(selector.researchReleaseId)) {
    throw new InvalidReleaseIdError("Research release identifier is not a valid UUID.");
  }

  if (!(await releaseReader.releaseExists(selector.researchReleaseId))) {
    throw new ReleaseNotFoundError("Requested research release is not available in the fixture release set.");
  }

  return selector.researchReleaseId;
}
