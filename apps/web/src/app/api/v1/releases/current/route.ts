import { NextResponse } from "next/server";
import { runtime as container } from "@/runtime/container.server";
import { apiErrorResponse } from "@/runtime/http-errors";

export const runtime = "nodejs";

export async function GET() {
  try {
    return NextResponse.json(await container.releaseReader.getCurrentRelease());
  } catch (error) {
    return apiErrorResponse(error);
  }
}
