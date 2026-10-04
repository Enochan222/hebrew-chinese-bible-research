import "server-only";

import { FixtureCapabilityReader } from "@/adapters/fixture/capability-reader.fixture.server";
import { FixturePassageReader } from "@/adapters/fixture/passage-reader.fixture.server";
import { FixtureReleaseReader } from "@/adapters/fixture/release-reader.fixture.server";

export const runtime = {
  releaseReader: new FixtureReleaseReader(),
  passageReader: new FixturePassageReader(),
  capabilityReader: new FixtureCapabilityReader(),
} as const;
