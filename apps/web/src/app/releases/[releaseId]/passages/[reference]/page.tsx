import { parseExperienceMode, readCapabilities } from "@/domain/experience/service";
import { readPassage } from "@/domain/passage/service";
import { PassageFailureView, PassageShell } from "@/features/passage-shell/PassageShell";
import { toPassagePageFailure } from "@/features/passage-shell/page-state";
import { runtime as container } from "@/runtime/container.server";

export const runtime = "nodejs";

type SearchParams = Record<string, string | string[] | undefined>;

function scalar(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function PinnedPassagePage(props: {
  params: Promise<{ releaseId: string; reference: string }>;
  searchParams: Promise<SearchParams>;
}) {
  try {
    const [{ releaseId, reference }, query] = await Promise.all([props.params, props.searchParams]);
    const mode = parseExperienceMode(scalar(query.mode));
    const referenceSystemCode = scalar(query.referenceSystemCode) ?? "";
    const passage = await readPassage({
      selector: { kind: "PINNED", researchReleaseId: releaseId },
      locator: { referenceSystemCode, referenceLabel: reference },
      releaseReader: container.releaseReader,
      passageReader: container.passageReader,
    });
    const capabilities = await readCapabilities(passage.researchReleaseId, container.capabilityReader);
    return <PassageShell passage={passage} capabilities={capabilities} mode={mode} />;
  } catch (error) {
    return <PassageFailureView failure={toPassagePageFailure(error)} />;
  }
}
