export class InvalidReferenceError extends Error {
  readonly code = "INVALID_REFERENCE";
}

export class MissingReferenceSystemError extends Error {
  readonly code = "REFERENCE_SYSTEM_REQUIRED";
}

export class ReferenceNotFoundError extends Error {
  readonly code = "REFERENCE_NOT_FOUND";
}
