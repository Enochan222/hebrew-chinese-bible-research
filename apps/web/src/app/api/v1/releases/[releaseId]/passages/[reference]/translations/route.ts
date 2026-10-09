import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { readTranslationWitnesses } from "@/domain/translation/service";
import { runtime as container } from "@/runtime/container.server";
import { apiErrorResponse } from "@/runtime/http-errors";

export const runtime = "nodejs";

type Context = { params: Promise<{ releaseId: string; reference: string }> };

export async function GET(request: NextRequest, context: Context) {
  try {
    const { releaseId, reference } = await context.params;
    const witnesses = await readTranslationWitnesses({
      selector: { kind: "PINNED", researchReleaseId: releaseId },
      locator: {
        referenceSystemCode: request.nextUrl.searchParams.get("referenceSystemCode") ?? "",
        referenceLabel: reference,
      },
      releaseReader: container.releaseReader,
      translationReader: container.translationReader,
    });
    return NextResponse.json(witnesses);
  } catch (error) {
    return apiErrorResponse(error);
  }
}
