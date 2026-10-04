import assert from "node:assert/strict";
import test from "node:test";
import type { ReleaseReadPort, ReleasePointerV1 } from "../../src/domain/release/port.ts";
import { InvalidReleaseIdError, ReleaseNotFoundError, resolveRelease } from "../../src/domain/release/service.ts";

const fixtureId = "11111111-1111-4111-8111-111111111111";
const missingId = "22222222-2222-4222-8222-222222222222";

class CountingReleaseReader implements ReleaseReadPort {
  currentCalls = 0;
  existsCalls = 0;
  pointer: ReleasePointerV1 = { researchReleaseId: fixtureId, releaseLabel: "fixture", channel: "PRODUCTION" };

  async getCurrentRelease() {
    this.currentCalls += 1;
    return this.pointer;
  }

  async releaseExists(researchReleaseId: string) {
    this.existsCalls += 1;
    return researchReleaseId === fixtureId;
  }
}

test("CURRENT resolves the current release exactly once", async () => {
  const reader = new CountingReleaseReader();
  assert.equal(await resolveRelease({ kind: "CURRENT" }, reader), fixtureId);
  assert.equal(reader.currentCalls, 1);
  assert.equal(reader.existsCalls, 0);
});

test("PINNED never resolves current", async () => {
  const reader = new CountingReleaseReader();
  assert.equal(await resolveRelease({ kind: "PINNED", researchReleaseId: fixtureId }, reader), fixtureId);
  assert.equal(reader.currentCalls, 0);
  assert.equal(reader.existsCalls, 1);
});

test("invalid and missing pinned releases are distinct", async () => {
  const reader = new CountingReleaseReader();
  await assert.rejects(() => resolveRelease({ kind: "PINNED", researchReleaseId: "bad" }, reader), InvalidReleaseIdError);
  await assert.rejects(() => resolveRelease({ kind: "PINNED", researchReleaseId: missingId }, reader), ReleaseNotFoundError);
  assert.equal(reader.currentCalls, 0);
});
