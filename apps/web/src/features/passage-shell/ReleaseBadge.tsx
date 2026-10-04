export function ReleaseBadge({ researchReleaseId }: { researchReleaseId: string }) {
  return (
    <div className="release-badge" data-testid="release-id">
      <span>ResearchRelease</span>
      <code>{researchReleaseId}</code>
    </div>
  );
}
