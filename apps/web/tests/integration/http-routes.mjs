import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import path from "node:path";

const port = 3124;
const base = `http://127.0.0.1:${port}`;
const fixtureRelease = "11111111-1111-4111-8111-111111111111";
const missingRelease = "22222222-2222-4222-8222-222222222222";
const nextBin = path.join(process.cwd(), "node_modules", "next", "dist", "bin", "next");
let output = "";
const server = spawn(process.execPath, [nextBin, "dev", "--hostname", "127.0.0.1", "--port", String(port)], {
  cwd: process.cwd(),
  env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" },
  stdio: ["ignore", "pipe", "pipe"],
});
server.stdout.on("data", (chunk) => { output += chunk.toString(); });
server.stderr.on("data", (chunk) => { output += chunk.toString(); });

async function waitForServer() {
  const deadline = Date.now() + 120_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${base}/api/v1/releases/current`);
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Next dev server did not become ready.\n${output}`);
}

async function json(pathname, expectedStatus) {
  const response = await fetch(`${base}${pathname}`);
  if (response.status !== expectedStatus) {
    const body = await response.text();
    assert.fail(`${pathname} returned ${response.status}; expected ${expectedStatus}: ${body}`);
  }
  return response.json();
}

try {
  await waitForServer();

  const release = await json("/api/v1/releases/current", 200);
  assert.equal(release.researchReleaseId, fixtureRelease);
  assert.equal(release.channel, "PRODUCTION");

  const current = await json("/api/v1/passages/1Sam.16.7?referenceSystemCode=MT_FIXTURE", 200);
  assert.equal(current.researchReleaseId, fixtureRelease);
  assert.equal(current.referenceSpanId, "17171717-1717-4171-8171-171717171717");

  const pinned = await json(
    `/api/v1/releases/${fixtureRelease}/passages/1Sam.16.7?referenceSystemCode=MT_FIXTURE`,
    200,
  );
  assert.deepEqual(pinned, current);

  assert.equal(
    (await json("/api/v1/passages/1Sam.16.7", 400)).code,
    "REFERENCE_SYSTEM_REQUIRED",
  );
  assert.equal(
    (await json("/api/v1/passages/bad%20reference?referenceSystemCode=MT_FIXTURE", 400)).code,
    "INVALID_REFERENCE",
  );
  assert.equal(
    (await json("/api/v1/passages/Gen.1.1?referenceSystemCode=MT_FIXTURE", 404)).code,
    "REFERENCE_NOT_FOUND",
  );
  assert.equal(
    (await json("/api/v1/releases/not-a-uuid/passages/1Sam.16.7?referenceSystemCode=MT_FIXTURE", 400)).code,
    "INVALID_RELEASE_ID",
  );
  assert.equal(
    (await json(`/api/v1/releases/${missingRelease}/passages/1Sam.16.7?referenceSystemCode=MT_FIXTURE`, 404)).code,
    "RELEASE_NOT_FOUND",
  );

  const capabilities = await json("/api/v1/experience/capabilities", 200);
  assert.equal(capabilities.researchReleaseId, fixtureRelease);

  const redirectResponse = await fetch(
    `${base}/passages/1Sam.16.7?referenceSystemCode=MT_FIXTURE&mode=STUDY`,
    { redirect: "manual" },
  );
  assert.ok([307, 308].includes(redirectResponse.status));
  const location = redirectResponse.headers.get("location") ?? "";
  assert.match(location, new RegExp(`/releases/${fixtureRelease}/passages/1Sam\\.16\\.7`));
  assert.match(location, /referenceSystemCode=MT_FIXTURE/);
  assert.match(location, /mode=STUDY/);

  const invalidMode = await fetch(
    `${base}/releases/${fixtureRelease}/passages/1Sam.16.7?referenceSystemCode=MT_FIXTURE&mode=PRO`,
  );
  assert.equal(invalidMode.status, 200);
  assert.match(await invalidMode.text(), /INVALID_MODE/);

  console.log("P1-VS-001 HTTP integration validation passed.");
} catch (error) {
  console.error(error);
  console.error(output);
  process.exitCode = 1;
} finally {
  server.kill("SIGTERM");
  await new Promise((resolve) => setTimeout(resolve, 500));
}
