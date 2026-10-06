import http from "node:http";

const port = Number(process.env.SERVING_MOCK_PORT ?? 4126);
const releaseId = "71000000-0000-4000-8000-000000000005";

function payload(referenceLabel) {
  const [bookCode, chapter = "1", verse = "1"] = referenceLabel.split(/[.]/);
  return {
    dataSource: "SERVING",
    researchReleaseId: releaseId,
    referenceSpanId: "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
    resolvedReference: {
      referenceSystemId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      referenceSystemCode: "OSHB_OSIS",
      referenceLabel,
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
      {
        analysisNodeId: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
        textSegmentId: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
        surface: "בָּרָא",
        lemmaRaw: "1254",
        morphRaw: "HVqp3ms",
      },
    ],
    navigation: {
      currentBookCode: bookCode,
      currentChapter: Number(chapter),
      previousReference: verse === "1" ? null : `${bookCode}.${chapter}.1`,
      nextReference: `${bookCode}.${chapter}.${Number(verse) + 1}`,
      books: [
        { bookCode: "Gen", firstReference: "Gen.1.1" },
        { bookCode: "Exod", firstReference: "Exod.1.1" },
      ],
      chapters: [
        { chapterNumber: 1, firstReference: `${bookCode}.1.1` },
        { chapterNumber: 2, firstReference: `${bookCode}.2.1` },
      ],
      passages: [
        { referenceLabel: `${bookCode}.${chapter}.1`, verseLabel: "1" },
        { referenceLabel: `${bookCode}.${chapter}.2`, verseLabel: "2" },
      ],
    },
    attribution: "Open Scriptures Hebrew Bible / Westminster Leningrad Codex; source and morphology attribution required.",
  };
}

const server = http.createServer(async (req, res) => {
  res.setHeader("content-type", "application/json");
  if (req.url === "/health") {
    res.end(JSON.stringify({ ok: true }));
    return;
  }
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
    res.end(JSON.stringify(payload(parsed.p_reference_label)));
    return;
  }
  res.statusCode = 404;
  res.end(JSON.stringify({ message: "not found" }));
});

server.listen(port, "127.0.0.1");
const close = () => server.close(() => process.exit(0));
process.on("SIGTERM", close);
process.on("SIGINT", close);
