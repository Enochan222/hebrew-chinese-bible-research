import { redirect } from "next/navigation";
import { parseExperienceMode } from "@/domain/experience/service";
import { validatePassageLocator } from "@/domain/passage/service";
import { resolveRelease } from "@/domain/release/service";
import { PassageFailureView } from "@/features/passage-shell/PassageShell";
import { toPassagePageFailure } from "@/features/passage-shell/page-state";
import { runtime as container } from "@/runtime/container.server";

export const runtime = "nodejs";

type SearchParams = Record<string, string | string[] | undefined>;

function scalar(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function CurrentPassagePage(props: {
  params: Promise<{ reference: string }>;
  searchParams: Promise<SearchParams>;
}) {
  try {
    const [{ reference }, query] = await Promise.all([props.params, props.searchParams]);
    const mode = parseExperienceMode(scalar(query.mode));
    const referenceSystemCode = scalar(query.referenceSystemCode) ?? "";
    validatePassageLocator({ referenceSystemCode, referenceLabel: reference });

    const researchReleaseId = await resolveRelease({ kind: "CURRENT" }, container.releaseReader);
    const pinned = `/releases/${encodeURIComponent(researchReleaseId)}/passages/${encodeURIComponent(reference)}`;
    redirect(
      `${pinned}?referenceSystemCode=${encodeURIComponent(referenceSystemCode)}&mode=${encodeURIComponent(mode)}`,
    );
  } catch (error) {
    if (typeof error === "object" && error !== null && "digest" in error) throw error;
    return <PassageFailureView failure={toPassagePageFailure(error)} />;
  }
}
