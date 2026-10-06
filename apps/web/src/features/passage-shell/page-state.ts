import { ContractViolationError } from "@/contracts/errors";
import { InvalidModeError } from "@/domain/experience/service";
import { InvalidReferenceError, MissingReferenceSystemError, ReferenceNotFoundError } from "@/domain/passage/errors";
import { InvalidReleaseIdError, ReleaseNotFoundError } from "@/domain/release/service";

export type PassagePageFailure = {
  code:
    | "INVALID_REFERENCE"
    | "REFERENCE_SYSTEM_REQUIRED"
    | "INVALID_RELEASE_ID"
    | "INVALID_MODE"
    | "REFERENCE_NOT_FOUND"
    | "RELEASE_NOT_FOUND"
    | "CONTRACT_VIOLATION"
    | "DATA_TEMPORARILY_UNAVAILABLE";
  title: string;
  message: string;
};

export function toPassagePageFailure(error: unknown): PassagePageFailure {
  if (error instanceof InvalidReferenceError) return { code: error.code, title: "Invalid reference", message: error.message };
  if (error instanceof MissingReferenceSystemError) return { code: error.code, title: "Reference system required", message: error.message };
  if (error instanceof InvalidReleaseIdError) return { code: error.code, title: "Invalid release identifier", message: error.message };
  if (error instanceof InvalidModeError) return { code: error.code, title: "Invalid experience mode", message: error.message };
  if (error instanceof ReferenceNotFoundError) return { code: error.code, title: "Reference not found", message: error.message };
  if (error instanceof ReleaseNotFoundError) return { code: error.code, title: "Release not found", message: error.message };
  if (error instanceof ContractViolationError) {
    const detail =
      process.env.NODE_ENV === "production"
        ? "Canonical serving data failed runtime validation and was not rendered."
        : `Canonical serving data failed runtime validation and was not rendered. ${error.message}`;
    return { code: error.code, title: "Serving contract violation", message: detail };
  }
  return {
    code: "DATA_TEMPORARILY_UNAVAILABLE",
    title: "Serving data unavailable",
    message: "The passage reader could not read the selected release.",
  };
}
