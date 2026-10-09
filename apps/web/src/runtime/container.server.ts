import "server-only";

import { FixtureCapabilityReader } from "@/adapters/fixture/capability-reader.fixture.server";
import { FixturePassageReader } from "@/adapters/fixture/passage-reader.fixture.server";
import { FixtureReleaseReader } from "@/adapters/fixture/release-reader.fixture.server";
import { FixtureTranslationWitnessReader } from "@/adapters/fixture/translation-reader.fixture.server";
import { ServingCapabilityReader } from "@/adapters/serving/capability-reader.serving.server";
import { PostgrestPassageReader } from "@/adapters/serving/passage-reader.postgrest.server";
import { PostgrestReleaseReader } from "@/adapters/serving/release-reader.postgrest.server";
import { PostgrestTranslationWitnessReader } from "@/adapters/serving/translation-reader.postgrest.server";
import { PostgrestServingClient } from "@/adapters/serving/postgrest-serving-client.server";

const servingUrl = process.env.HCBIBLE_SERVING_REST_URL?.trim();
const servingKey = process.env.HCBIBLE_SERVING_ANON_KEY?.trim();
const servingSchema = process.env.HCBIBLE_SERVING_REST_SCHEMA?.trim() || "serving";

const servingClient = servingUrl ? new PostgrestServingClient(servingUrl, servingKey, servingSchema) : null;

export const runtime = servingClient
  ? {
      releaseReader: new PostgrestReleaseReader(servingClient),
      passageReader: new PostgrestPassageReader(servingClient),
      capabilityReader: new ServingCapabilityReader(),
      translationReader: new PostgrestTranslationWitnessReader(servingClient),
      sourceMode: "SERVING" as const,
    }
  : {
      releaseReader: new FixtureReleaseReader(),
      passageReader: new FixturePassageReader(),
      capabilityReader: new FixtureCapabilityReader(),
      translationReader: new FixtureTranslationWitnessReader(),
      sourceMode: "FIXTURE" as const,
    };
