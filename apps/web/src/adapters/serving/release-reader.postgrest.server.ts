import "server-only";

import type { ReleaseReadPort, ReleasePointerV1 } from "@/domain/release/port";
import { PostgrestServingClient } from "./postgrest-serving-client.server";

type CurrentReleaseRow = {
  channel_key: "PRODUCTION";
  research_release_id: string;
  release_label: string;
};

export class PostgrestReleaseReader implements ReleaseReadPort {
  constructor(private readonly client: PostgrestServingClient) {}

  async getCurrentRelease(): Promise<ReleasePointerV1> {
    const rows = await this.client.json<CurrentReleaseRow[]>(
      "/current_release?channel_key=eq.PRODUCTION&select=channel_key,research_release_id,release_label&limit=1",
    );
    const row = rows[0];
    if (!row) throw new Error("No published PRODUCTION ResearchRelease is available.");
    return {
      researchReleaseId: row.research_release_id,
      releaseLabel: row.release_label,
      channel: row.channel_key,
    };
  }

  async releaseExists(researchReleaseId: string): Promise<boolean> {
    const id = encodeURIComponent(researchReleaseId);
    const rows = await this.client.json<Array<{ research_release_id: string }>>(
      `/research_releases?research_release_id=eq.${id}&select=research_release_id&limit=1`,
    );
    return rows.length === 1;
  }
}
