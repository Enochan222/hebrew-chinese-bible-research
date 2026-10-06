import "server-only";

import { assertContract } from "@/contracts/validate.server";
import type { PassageCoreV1, PassageReadPort } from "@/domain/passage/port";
import { PostgrestServingClient } from "./postgrest-serving-client.server";

export class PostgrestPassageReader implements PassageReadPort {
  constructor(private readonly client: PostgrestServingClient) {}

  async getPassageCore(
    input: Parameters<PassageReadPort["getPassageCore"]>[0],
  ): Promise<PassageCoreV1 | null> {
    const payload = await this.client.json<unknown>("/rpc/read_passage_core", {
      method: "POST",
      body: JSON.stringify({
        p_release_id: input.researchReleaseId,
        p_reference_system_code: input.locator.referenceSystemCode,
        p_reference_label: input.locator.referenceLabel,
      }),
    });
    if (payload === null) return null;
    assertContract<PassageCoreV1>("passageCore", payload);
    return payload;
  }
}
