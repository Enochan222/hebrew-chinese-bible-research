import Link from "next/link";
import type { ExperienceMode } from "@/domain/experience/port";

export function ModeSwitch(props: {
  mode: ExperienceMode;
  releaseId: string;
  reference: string;
  referenceSystemCode: string;
}) {
  const base = `/releases/${encodeURIComponent(props.releaseId)}/passages/${encodeURIComponent(props.reference)}`;
  const href = (mode: ExperienceMode) =>
    `${base}?referenceSystemCode=${encodeURIComponent(props.referenceSystemCode)}&mode=${mode}`;

  return (
    <nav className="mode-switch" aria-label="Experience mode">
      {(["STUDY", "RESEARCH"] as const).map((mode) => (
        <Link
          key={mode}
          href={href(mode)}
          aria-current={props.mode === mode ? "page" : undefined}
          data-testid={`mode-${mode.toLowerCase()}`}
        >
          {mode === "STUDY" ? "Study" : "Research"}
        </Link>
      ))}
    </nav>
  );
}
