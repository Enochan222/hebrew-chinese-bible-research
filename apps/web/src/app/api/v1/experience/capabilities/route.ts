import { NextResponse } from "next/server";
import { readCapabilities } from "@/domain/experience/service";
import { resolveRelease } from "@/domain/release/service";
import { runtime as container } from "@/runtime/container.server";
import { apiErrorResponse } from "@/runtime/http-errors";

export const runtime = "nodejs";

export async function GET() {
  try {
    const researchReleaseId = await resolveRelease({ kind: "CURRENT" }, container.releaseReader);
    return NextResponse.json(await readCapabilities(researchReleaseId, container.capabilityReader));
  } catch (error) {
    return apiErrorResponse(error);
  }
}
