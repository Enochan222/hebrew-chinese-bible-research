import "server-only";

import { assertContract } from "@/contracts/validate.server";
import type { TranslationWitnessListV1, TranslationWitnessReadPort } from "@/domain/translation/port";
import { PostgrestServingClient } from "./postgrest-serving-client.server";

export class PostgrestTranslationWitnessReader implements TranslationWitnessReadPort {
  constructor(private readonly client: PostgrestServingClient) {}

  async getTranslationWitnesses(
    input: Parameters<TranslationWitnessReadPort["getTranslationWitnesses"]>[0],
  ): Promise<TranslationWitnessListV1 | null> {
    const payload = await this.client.json<unknown>("/rpc/read_translation_witnesses", {
      method: "POST",
      body: JSON.stringify({
        p_release_id: input.researchReleaseId,
        p_reference_system_code: input.locator.referenceSystemCode,
        p_reference_label: input.locator.referenceLabel,
      }),
    });
    if (payload === null) return null;
    assertContract<TranslationWitnessListV1>("translationWitnessList", payload);
    return payload;
  }
}
