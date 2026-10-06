import "server-only";

import { ContractViolationError } from "@/contracts/errors";
import { assertContract } from "@/contracts/validate.server";
import type { ReleaseReadPort, ReleasePointerV1 } from "@/domain/release/port";
import { PostgrestServingClient } from "./postgrest-serving-client.server";

function singleRow(value: unknown, context: string): Record<string, unknown> | null {
  if (!Array.isArray(value) || value.length > 1) {
    throw new ContractViolationError(`${context} must return zero or one row.`);
  }
  if (value.length === 0) return null;
  const row = value[0];
  if (typeof row !== "object" || row === null || Array.isArray(row)) {
    throw new ContractViolationError(`${context} returned a malformed row.`);
  }
  return row as Record<string, unknown>;
}

export class PostgrestReleaseReader implements ReleaseReadPort {
  constructor(private readonly client: PostgrestServingClient) {}

  async getCurrentRelease(): Promise<ReleasePointerV1> {
    const raw = await this.client.json<unknown>(
      "/current_release?channel_key=eq.PRODUCTION&select=channel_key,research_release_id,release_label&limit=1",
    );
    const row = singleRow(raw, "Current release query");
    if (!row) throw new Error("No published PRODUCTION ResearchRelease is available.");
    const pointer: unknown = {
      researchReleaseId: row.research_release_id,
      releaseLabel: row.release_label,
      channel: row.channel_key,
    };
    assertContract<ReleasePointerV1>("releasePointer", pointer);
    return pointer;
  }

  async releaseExists(researchReleaseId: string): Promise<boolean> {
    const id = encodeURIComponent(researchReleaseId);
    const raw = await this.client.json<unknown>(
      `/research_releases?research_release_id=eq.${id}&select=research_release_id&limit=1`,
    );
    const row = singleRow(raw, "Pinned release query");
    if (!row) return false;
    if (row.research_release_id !== researchReleaseId) {
      throw new ContractViolationError("Pinned release query returned a different ResearchRelease.");
    }
    return true;
  }
}
