import type { ResearchReleaseId } from "../release/port";

export type PassageLabelLocator = {
  referenceSystemCode: string;
  referenceLabel: string;
};

export type PassageCoreV1 = {
  researchReleaseId: ResearchReleaseId;
  referenceSpanId: string;
  resolvedReference?:
    | {
        referenceSystemId: string;
        referenceSystemCode: string;
        referenceLabel: string;
      }
    | null;
  [key: string]: unknown;
};

export interface PassageReadPort {
  getPassageCore(input: {
    researchReleaseId: ResearchReleaseId;
    locator: PassageLabelLocator;
  }): Promise<PassageCoreV1 | null>;
}
