import assert from "node:assert/strict";
import test from "node:test";
import { InvalidModeError, parseExperienceMode } from "../../src/domain/experience/service.ts";
import { InvalidReferenceError, MissingReferenceSystemError } from "../../src/domain/passage/errors.ts";
import { validatePassageLocator } from "../../src/domain/passage/service.ts";

test("mode defaults to STUDY and rejects unknown values", () => {
  assert.equal(parseExperienceMode(undefined), "STUDY");
  assert.equal(parseExperienceMode("RESEARCH"), "RESEARCH");
  assert.throws(() => parseExperienceMode("PRO"), InvalidModeError);
});

test("human passage labels require an explicit reference system", () => {
  assert.throws(
    () => validatePassageLocator({ referenceSystemCode: "", referenceLabel: "1Sam.16.7" }),
    MissingReferenceSystemError,
  );
});

test("malformed references fail before lookup", () => {
  assert.throws(
    () => validatePassageLocator({ referenceSystemCode: "MT_FIXTURE", referenceLabel: "bad reference" }),
    InvalidReferenceError,
  );
});
