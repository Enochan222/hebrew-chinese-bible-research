import "server-only";

import type { PassageCoreV1, PassageReadPort } from "@/domain/passage/port";
import { PostgrestServingClient } from "./postgrest-serving-client.server";

export class PostgrestPassageReader implements PassageReadPort {
  constructor(private readonly client: PostgrestServingClient) {}

  async getPassageCore(
    input: Parameters<PassageReadPort["getPassageCore"]>[0],
  ): Promise<PassageCoreV1 | null> {
    const payload = await this.client.json<PassageCoreV1 | null>("/rpc/read_passage_core", {
      method: "POST",
      body: JSON.stringify({
        p_release_id: input.researchReleaseId,
        p_reference_system_code: input.locator.referenceSystemCode,
        p_reference_label: input.locator.referenceLabel,
      }),
    });
    return payload;
  }
}
