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

test("passage request validation resolves the canonical passage-locator schema", () => {
  const root = path.resolve(process.cwd(), "../..");
  const fixture = JSON.parse(
    fs.readFileSync(path.join(root, "contracts/v1.1/fixtures/passage-request.json"), "utf8"),
  ) as Record<string, unknown>;

  assert.doesNotThrow(() => assertContract("passageRequest", fixture));
});


test("SERVING passage projections require the complete runtime payload", () => {
  const validServing = {
    researchReleaseId: "71000000-0000-4000-8000-000000000005",
    referenceSpanId: "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
    dataSource: "SERVING",
    resolvedReference: {
      referenceSystemId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      referenceSystemCode: "OSHB_OSIS",
      referenceLabel: "Gen.1.1",
    },
    textReconstructionStatus: "OSHB_WORD_TOKENS_ONLY",
    hebrewText: "בְּרֵאשִׁית",
    tokens: [{
      analysisNodeId: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      textSegmentId: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
      surface: "בְּרֵאשִׁית",
      lemmaRaw: "7225",
      morphRaw: "HR/Ncfsa",
    }],
    navigation: {
      currentBookCode: "Gen",
      currentChapter: 1,
      previousReference: null,
      nextReference: "Gen.1.2",
      books: [{ bookCode: "Gen", firstReference: "Gen.1.1" }],
      chapters: [{ chapterNumber: 1, firstReference: "Gen.1.1" }],
      passages: [{ referenceLabel: "Gen.1.1", verseLabel: "1" }],
    },
    attribution: "Open Scriptures Hebrew Bible attribution",
  };
  assert.doesNotThrow(() => assertContract("passageCore", validServing));
  const { attribution: _attribution, ...missingAttribution } = validServing;
  assert.throws(() => assertContract("passageCore", missingAttribution), ContractViolationError);
  assert.throws(() => assertContract("passageCore", { ...validServing, tokens: [] }), ContractViolationError);
  assert.throws(
    () => assertContract("passageCore", { ...validServing, navigation: { previousReference: null, nextReference: "Gen.1.2" } }),
    ContractViolationError,
  );
});
