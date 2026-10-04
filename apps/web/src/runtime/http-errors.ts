import { NextResponse } from "next/server";
import { ContractViolationError } from "@/contracts/errors";
import { InvalidReferenceError, MissingReferenceSystemError, ReferenceNotFoundError } from "@/domain/passage/errors";
import { InvalidReleaseIdError, ReleaseNotFoundError } from "@/domain/release/service";

export type ApiErrorBody = { code: string; message: string };

export function apiErrorResponse(error: unknown): NextResponse<ApiErrorBody> {
  if (error instanceof MissingReferenceSystemError) {
    return NextResponse.json({ code: error.code, message: error.message }, { status: 400 });
  }
  if (error instanceof InvalidReferenceError) {
    return NextResponse.json({ code: error.code, message: error.message }, { status: 400 });
  }
  if (error instanceof InvalidReleaseIdError) {
    return NextResponse.json({ code: error.code, message: error.message }, { status: 400 });
  }
  if (error instanceof ReleaseNotFoundError) {
    return NextResponse.json({ code: error.code, message: error.message }, { status: 404 });
  }
  if (error instanceof ReferenceNotFoundError) {
    return NextResponse.json({ code: error.code, message: error.message }, { status: 404 });
  }
  if (error instanceof ContractViolationError) {
    return NextResponse.json({ code: error.code, message: "Canonical fixture contract validation failed." }, { status: 500 });
  }
  return NextResponse.json(
    { code: "DATA_TEMPORARILY_UNAVAILABLE", message: "Fixture serving data is temporarily unavailable." },
    { status: 503 },
  );
}
