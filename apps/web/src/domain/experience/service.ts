import type { ExperienceCapabilityPort, ExperienceCapabilitiesV1, ExperienceMode } from "./port";
import type { ResearchReleaseId } from "../release/port";

export class InvalidModeError extends Error {
  readonly code = "INVALID_MODE";
}

export function parseExperienceMode(value: string | undefined): ExperienceMode {
  if (value === undefined || value === "") return "STUDY";
  if (value === "STUDY" || value === "RESEARCH") return value;
  throw new InvalidModeError("mode must be STUDY or RESEARCH.");
}

export async function readCapabilities(
  researchReleaseId: ResearchReleaseId,
  capabilityReader: ExperienceCapabilityPort,
): Promise<ExperienceCapabilitiesV1> {
  const capabilities = await capabilityReader.getCapabilities({ researchReleaseId });
  if (capabilities.researchReleaseId !== researchReleaseId) {
    throw new Error("Fixture capabilities resolved to a different ResearchRelease than requested.");
  }
  return capabilities;
}
