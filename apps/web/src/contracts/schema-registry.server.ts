import fs from "node:fs";
import path from "node:path";

export const contractPaths = {
  releasePointer: "contracts/v1.1/json-schema/release-pointer.schema.json",
  releaseChannelPointer: "contracts/v1.1/json-schema/release-channel-pointer.schema.json",
  releaseManifest: "contracts/v1.1/json-schema/release-manifest.schema.json",
  passageCore: "contracts/v1.1/json-schema/passage-core.schema.json",
  passageRequest: "contracts/v1.1/json-schema/passage-request.schema.json",
  passageLocator: "contracts/v1.1/json-schema/passage-locator.schema.json",
  experienceCapabilities: "contracts/v1.1/json-schema/experience-capabilities.schema.json",
} as const;

export type ContractSchemaKey = keyof typeof contractPaths;

export function repoRoot(): string {
  const root = path.resolve(process.cwd(), "../..");
  if (!fs.existsSync(path.join(root, "contracts", "v1.1"))) {
    throw new Error("Repository root could not be resolved from apps/web.");
  }
  return root;
}

export function readContractJson(relativePath: string): unknown {
  return JSON.parse(fs.readFileSync(path.join(repoRoot(), relativePath), "utf8")) as unknown;
}
