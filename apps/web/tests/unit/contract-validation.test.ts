import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { ContractViolationError } from "../../src/contracts/errors.ts";
import { assertContract } from "../../src/contracts/validate.server.ts";

test("canonical passage fixture validates and a corrupted copy fails closed", () => {
  const root = path.resolve(process.cwd(), "../..");
  const fixture = JSON.parse(
    fs.readFileSync(path.join(root, "contracts/v1.1/fixtures/passage-core.json"), "utf8"),
  ) as Record<string, unknown>;

  assert.doesNotThrow(() => assertContract("passageCore", fixture));
  assert.throws(
    () => assertContract("passageCore", { ...fixture, researchReleaseId: "not-a-uuid" }),
    ContractViolationError,
  );
});
