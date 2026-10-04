export type ResearchReleaseId = string;

export type ReleasePointerV1 = {
  researchReleaseId: ResearchReleaseId;
  releaseLabel: string;
  channel: "PREVIEW" | "STAGING" | "PRODUCTION";
};

export interface ReleaseReadPort {
  getCurrentRelease(): Promise<ReleasePointerV1>;
  releaseExists(researchReleaseId: ResearchReleaseId): Promise<boolean>;
}
