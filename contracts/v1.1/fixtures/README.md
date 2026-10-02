# v1.1 Contract Fixtures

These fixtures are contract/regression data only.

They are deliberately not scholarly conclusions about 1 Samuel 16:7.

## Dry Run 001

The CorpusQuery fixture represents the structural request:

```text
ראה
+
prefixed ל
+
BODY_PART
+
same clause
```

It demonstrates that a query can pin:

- a Hebrew digital expression;
- a corpus release;
- an independent morpheme-segmentation layer;
- an independent morphology layer;
- an independent clause layer;
- a semantic-set version;
- formal morpheme-host and clause relations.

Expected architectural behaviour:

1. schema validation passes;
2. semantic validation confirms every node reference exists;
3. each framework-scoped relation uses a compatible annotation layer;
4. semantic-set membership is resolved from the pinned set version;
5. no LLM decides match membership;
6. HTTP and Product MCP use the identical normalized query;
7. any compiled ConstructionInstance records its compilation dependencies.

## Rights fixture

The rights fixture intentionally demonstrates a DENY decision for persistent public storage.

The expected downstream behaviour is to select PROVIDER_LOCATOR or refuse publication, not to persist restricted text.

## Release fixture

The release manifest is a payload fixture. The manifest hash itself is stored outside the payload and is computed using RFC 8785 canonical JSON + SHA-256.

## Published analysis fixture

The published-analysis fixture proves that evidence is attached to an assertion rather than only to a prose blob or private authoring packet.
