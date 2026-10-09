import fs from "node:fs";
import path from "node:path";
import type { AnySchema } from "ajv/dist/2020";

export const contractPaths = {
  releasePointer: "json-schema/release-pointer.schema.json",
  releaseChannelPointer: "json-schema/release-channel-pointer.schema.json",
  releaseManifest: "json-schema/release-manifest.schema.json",
  passageCore: "json-schema/passage-core.schema.json",
  passageRequest: "json-schema/passage-request.schema.json",
  passageLocator: "json-schema/passage-locator.schema.json",
  experienceCapabilities: "json-schema/experience-capabilities.schema.json",
  providerWitnessBinding: "json-schema/provider-witness-binding.schema.json",
  translationWitnessSegment: "json-schema/translation-witness-segment.schema.json",
  translationWitness: "json-schema/translation-witness.schema.json",
  translationWitnessList: "json-schema/translation-witness-list.schema.json",
} as const;

export type ContractSchemaKey = keyof typeof contractPaths;

export function contractRoot(): string {
  const root = path.resolve(process.cwd(), "../..", "contracts", "v1.1");
  if (!fs.existsSync(root)) {
    throw new Error("Repository root could not be resolved from apps/web.");
  }
  return root;
}

export function readContractJson(relativePath: string): AnySchema {
  return JSON.parse(fs.readFileSync(path.join(contractRoot(), relativePath), "utf8")) as AnySchema;
}
