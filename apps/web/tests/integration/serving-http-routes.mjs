import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import http from "node:http";
import path from "node:path";

const appPort = 3125;
const restPort = 4125;
const appBase = `http://127.0.0.1:${appPort}`;
const restBase = `http://127.0.0.1:${restPort}`;
const releaseId = "71000000-0000-4000-8000-000000000005";
const nextBin = path.join(process.cwd(), "node_modules", "next", "dist", "bin", "next");

let appOutput = "";
const observed = [];

const passagePayload = {
  dataSource: "SERVING",
  researchReleaseId: releaseId,
  referenceSpanId: "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
  resolvedReference: {
    referenceSystemId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    referenceSystemCode: "OSHB_OSIS",
    referenceLabel: "Gen.1.1",
  },
  textReconstructionStatus: "OSHB_WORD_TOKENS_ONLY",
  hebrewText: "בְּרֵאשִׁית בָּרָא",
  tokens: [
    {
      analysisNodeId: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      textSegmentId: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
      surface: "בְּרֵאשִׁית",
      lemmaRaw: "7225",
      morphRaw: "HR/Ncfsa",
    },
  ],
  navigation: {
    currentBookCode: "Gen",
    currentChapter: 1,
    previousReference: null,
    nextReference: "Gen.1.2",
    books: [
      { bookCode: "Gen", firstReference: "Gen.1.1" },
      { bookCode: "Exod", firstReference: "Exod.1.1" },
    ],
    chapters: [
      { chapterNumber: 1, firstReference: "Gen.1.1" },
      { chapterNumber: 2, firstReference: "Gen.2.1" },
    ],
    passages: [
      { referenceLabel: "Gen.1.1", verseLabel: "1" },
      { referenceLabel: "Gen.1.2", verseLabel: "2" },
    ],
  },
  attribution: "Open Scriptures Hebrew Bible / Westminster Leningrad Codex; source and morphology attribution required.",
};

const restServer = http.createServer(async (req, res) => {
  observed.push({
    method: req.method,
    url: req.url,
    acceptProfile: req.headers["accept-profile"],
    contentProfile: req.headers["content-profile"],
  });

  res.setHeader("content-type", "application/json");
  if (req.method === "GET" && req.url?.startsWith("/current_release?")) {
    res.end(JSON.stringify([{
      channel_key: "PRODUCTION",
      research_release_id: releaseId,
      release_label: "wb2-oshb-serving-1",
    }]));
    return;
  }
  if (req.method === "GET" && req.url?.startsWith("/research_releases?")) {
    res.end(JSON.stringify([{ research_release_id: releaseId }]));
    return;
  }
  if (req.method === "POST" && req.url === "/rpc/read_passage_core") {
    let body = "";
    for await (const chunk of req) body += chunk;
    const parsed = JSON.parse(body);
    assert.equal(parsed.p_release_id, releaseId);
    assert.equal(parsed.p_reference_system_code, "OSHB_OSIS");
    if (parsed.p_reference_label === "Gen.1.2") {
      res.end(JSON.stringify({
        dataSource: "SERVING",
        researchReleaseId: releaseId,
        referenceSpanId: "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
      }));
      return;
    }
    assert.equal(parsed.p_reference_label, "Gen.1.1");
    res.end(JSON.stringify(passagePayload));
    return;
  }
  res.statusCode = 404;
  res.end(JSON.stringify({ message: "not found" }));
});

await new Promise((resolve) => restServer.listen(restPort, "127.0.0.1", resolve));

const app = spawn(process.execPath, [nextBin, "dev", "--hostname", "127.0.0.1", "--port", String(appPort)], {
  cwd: process.cwd(),
  env: {
    ...process.env,
    NEXT_TELEMETRY_DISABLED: "1",
    HCBIBLE_SERVING_REST_URL: restBase,
  },
  stdio: ["ignore", "pipe", "pipe"],
});
app.stdout.on("data", (chunk) => { appOutput += chunk.toString(); });
app.stderr.on("data", (chunk) => { appOutput += chunk.toString(); });

async function waitForApp() {
  const deadline = Date.now() + 120_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${appBase}/api/v1/releases/current`);
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Next dev server did not become ready.\n${appOutput}`);
}

async function json(pathname, expectedStatus = 200) {
  const response = await fetch(`${appBase}${pathname}`);
  if (response.status !== expectedStatus) {
    const body = await response.text();
    assert.fail(`${pathname} returned ${response.status}; expected ${expectedStatus}: ${body}`);
  }
  return response.json();
}

try {
  await waitForApp();

  const release = await json("/api/v1/releases/current");
  assert.equal(release.researchReleaseId, releaseId);
  assert.equal(release.channel, "PRODUCTION");

  const passage = await json("/api/v1/passages/Gen.1.1?referenceSystemCode=OSHB_OSIS");
  assert.equal(passage.dataSource, "SERVING");
  assert.equal(passage.researchReleaseId, releaseId);
  assert.equal(passage.resolvedReference.referenceLabel, "Gen.1.1");
  assert.equal(passage.textReconstructionStatus, "OSHB_WORD_TOKENS_ONLY");
  assert.equal(passage.tokens.length, 1);
  assert.equal(passage.tokens[0].morphRaw, "HR/Ncfsa");
  assert.equal(passage.navigation.nextReference, "Gen.1.2");
  assert.deepEqual(passage.navigation.books.map((item) => item.bookCode), ["Gen", "Exod"]);
  assert.deepEqual(passage.navigation.chapters.map((item) => item.chapterNumber), [1, 2]);
  assert.deepEqual(passage.navigation.passages.map((item) => item.referenceLabel), ["Gen.1.1", "Gen.1.2"]);
  assert.match(passage.attribution, /Open Scriptures Hebrew Bible/);

  const malformed = await json("/api/v1/passages/Gen.1.2?referenceSystemCode=OSHB_OSIS", 500);
  assert.equal(malformed.code, "CONTRACT_VIOLATION");
  assert.match(malformed.message, /serving contract validation failed/i);

  const page = await fetch(
    `${appBase}/releases/${releaseId}/passages/Gen.1.1?referenceSystemCode=OSHB_OSIS&mode=STUDY`,
  );
  assert.equal(page.status, 200);
  const html = await page.text();
  assert.match(html, /Published database-backed passage/);
  assert.match(html, /OSHB source tokens/);
  assert.match(html, /Word-token display only/);
  assert.match(html, /Gen\.1\.2/);
  assert.match(html, /Whole-Bible reference navigation/);
  assert.match(html, /Exod/);

  assert.ok(observed.length >= 3);
  for (const request of observed) {
    assert.equal(request.acceptProfile, "serving");
    assert.equal(request.contentProfile, "serving");
  }

  console.log("WB-3 Serving/PostgREST HTTP integration validation passed.");
} catch (error) {
  console.error(error);
  console.error(appOutput);
  process.exitCode = 1;
} finally {
  app.kill("SIGTERM");
  restServer.close();
  await new Promise((resolve) => setTimeout(resolve, 500));
}
