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

const translationPayload = {
  schemaVersion: "1.1",
  researchReleaseId: releaseId,
  referenceSpanId: "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
  resolvedReference: {
    referenceSystemId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    referenceSystemCode: "OSHB_OSIS",
    referenceLabel: "Gen.1.1",
  },
  witnesses: [
    {
      schemaVersion: "1.1",
      textualWorkId: "20202020-2020-4020-8020-202020202020",
      textualEditionId: null,
      digitalExpressionId: "22000000-0000-4000-8000-000000000002",
      displayName: "Synthetic Chinese Test Witness",
      languageTag: "zh-Hant",
      coverageStatus: "COVERED",
      deliveryStatus: "READY",
      displayStatus: "DISPLAYABLE",
      binding: {
        schemaVersion: "1.1",
        bindingMode: "SNAPSHOT_PINNED",
        segmentStorageMode: "PERSISTED_CONTENT",
        providerDistributionId: "41414141-4141-4414-8414-414141414141",
        reference: "Gen.1.1",
        providerSegmentKey: "fixture-segment",
        providerVersion: "fixture-v1",
        observedHash: "8888888888888888888888888888888888888888888888888888888888888888",
        observedAt: "2026-10-03T00:00:00Z",
        snapshotContentHash: "9999999999999999999999999999999999999999999999999999999999999999",
      },
      rightsDecisionSnapshotId: "30303030-3030-4030-8030-303030303030",
      provenanceId: "40404040-4040-4040-8040-404040404040",
      segments: [
        {
          schemaVersion: "1.1",
          textSegmentId: "50505050-5050-4050-8050-505050505050",
          textStreamId: "60606060-6060-4060-8060-606060606060",
          referenceSpanId: "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
          segmentOrder: 0,
          segmentKind: "VERSE",
          text: "合成測試譯文",
          contentHash: "7777777777777777777777777777777777777777777777777777777777777777",
        },
      ],
      attribution: "Synthetic fixture only",
    },
  ],
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
    assert.ok(["Gen.1.1", "Gen.1.2"].includes(parsed.p_reference_label));
    res.end(JSON.stringify({
      ...passagePayload,
      resolvedReference: {
        ...passagePayload.resolvedReference,
        referenceLabel: parsed.p_reference_label,
      },
      navigation: {
        ...passagePayload.navigation,
        previousReference: parsed.p_reference_label === "Gen.1.1" ? null : "Gen.1.1",
        nextReference: parsed.p_reference_label === "Gen.1.1" ? "Gen.1.2" : "Gen.1.3",
      },
    }));
    return;
  }
  if (req.method === "POST" && req.url === "/rpc/read_translation_witnesses") {
    let body = "";
    for await (const chunk of req) body += chunk;
    const parsed = JSON.parse(body);
    if (parsed.p_reference_label === "Gen.1.99") {
      res.end(JSON.stringify({
        ...translationPayload,
        resolvedReference: { ...translationPayload.resolvedReference, referenceLabel: "Gen.1.99" },
        witnesses: [{ ...translationPayload.witnesses[0], segments: [] }],
      }));
      return;
    }
    if (parsed.p_reference_label === "Gen.1.2") {
      // Schema-valid response for the wrong canonical passage: the reader must
      // reject it rather than displaying a misplaced Chinese translation.
      res.end(JSON.stringify({
        ...translationPayload,
        referenceSpanId: "13000000-0000-4000-8000-000000000002",
        resolvedReference: { ...translationPayload.resolvedReference, referenceLabel: "Gen.1.2" },
      }));
      return;
    }
    res.end(JSON.stringify({
      ...translationPayload,
      resolvedReference: {
        ...translationPayload.resolvedReference,
        referenceLabel: parsed.p_reference_label,
      },
      witnesses: translationPayload.witnesses.map((witness) => ({
        ...witness,
        binding: { ...witness.binding, reference: parsed.p_reference_label },
      })),
    }));
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

  const translations = await json("/api/v1/passages/Gen.1.1/translations?referenceSystemCode=OSHB_OSIS");
  assert.equal(translations.researchReleaseId, releaseId);
  assert.equal(translations.referenceSpanId, passage.referenceSpanId);
  assert.equal(translations.witnesses.length, 1);
  assert.equal(translations.witnesses[0].displayStatus, "DISPLAYABLE");
  assert.equal(translations.witnesses[0].digitalExpressionId, "22000000-0000-4000-8000-000000000002");
  assert.equal(translations.witnesses[0].segments[0].text, "合成測試譯文");
  assert.equal(translations.witnesses[0].binding.providerDistributionId, "41414141-4141-4414-8414-414141414141");

  const pinnedTranslations = await json(
    `/api/v1/releases/${releaseId}/passages/Gen.1.1/translations?referenceSystemCode=OSHB_OSIS`,
  );
  assert.deepEqual(pinnedTranslations, translations);

  const malformedTranslations = await json(
    "/api/v1/passages/Gen.1.99/translations?referenceSystemCode=OSHB_OSIS",
    500,
  );
  assert.equal(malformedTranslations.code, "CONTRACT_VIOLATION");

  const adjacent = await json("/api/v1/passages/Gen.1.2?referenceSystemCode=OSHB_OSIS");
  assert.equal(adjacent.dataSource, "SERVING");
  assert.equal(adjacent.resolvedReference.referenceLabel, "Gen.1.2");
  assert.equal(adjacent.navigation.previousReference, "Gen.1.1");
  assert.equal(adjacent.navigation.nextReference, "Gen.1.3");

  const mismatchedPassagePage = await fetch(
    `${appBase}/releases/${releaseId}/passages/Gen.1.2?referenceSystemCode=OSHB_OSIS&mode=STUDY`,
  );
  assert.equal(mismatchedPassagePage.status, 200);
  const mismatchedHtml = await mismatchedPassagePage.text();
  assert.match(mismatchedHtml, /Serving contract violation/);
  assert.doesNotMatch(mismatchedHtml, /合成測試譯文/);

  const directRelease = await fetch(
    `${restBase}/research_releases?research_release_id=eq.${releaseId}&select=research_release_id&limit=1`,
    { headers: { "Accept-Profile": "serving", "Content-Profile": "serving" } },
  );
  assert.equal(directRelease.status, 200);
  assert.deepEqual(await directRelease.json(), [{ research_release_id: releaseId }]);

  const directPassage = await fetch(`${restBase}/rpc/read_passage_core`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept-Profile": "serving",
      "Content-Profile": "serving",
    },
    body: JSON.stringify({
      p_release_id: releaseId,
      p_reference_system_code: "OSHB_OSIS",
      p_reference_label: "Gen.1.1",
    }),
  });
  assert.equal(directPassage.status, 200);
  assert.equal((await directPassage.json()).resolvedReference.referenceLabel, "Gen.1.1");

  const directTranslations = await fetch(`${restBase}/rpc/read_translation_witnesses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept-Profile": "serving",
      "Content-Profile": "serving",
    },
    body: JSON.stringify({
      p_release_id: releaseId,
      p_reference_system_code: "OSHB_OSIS",
      p_reference_label: "Gen.1.1",
    }),
  });
  assert.equal(directTranslations.status, 200);
  assert.equal((await directTranslations.json()).witnesses[0].segments[0].text, "合成測試譯文");

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
  assert.match(html, /Release-pinned comparison witnesses/);
  assert.match(html, /Synthetic Chinese Test Witness/);
  assert.match(html, /合成測試譯文/);
  assert.match(html, /1 rights-approved release-pinned witness available above/);

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
