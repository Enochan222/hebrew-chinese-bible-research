import type { ResearchReleaseId } from "../release/port";

export type PassageLabelLocator = {
  referenceSystemCode: string;
  referenceLabel: string;
};

export type PassageTokenV1 = {
  analysisNodeId: string;
  textSegmentId: string;
  surface: string;
  lemmaRaw?: string | null;
  morphRaw?: string | null;
};

export type PassageNavigationV1 = {
  currentBookCode?: string;
  currentChapter?: number | null;
  previousReference?: string | null;
  nextReference?: string | null;
  books?: Array<{ bookCode: string; firstReference: string }>;
  chapters?: Array<{ chapterNumber: number; firstReference: string }>;
  passages?: Array<{ referenceLabel: string; verseLabel?: string | null }>;
};

export type PassageCoreV1 = {
  researchReleaseId: ResearchReleaseId;
  referenceSpanId: string;
  dataSource?: "FIXTURE" | "SERVING";
  resolvedReference?:
    | {
        referenceSystemId: string;
        referenceSystemCode: string;
        referenceLabel: string;
      }
    | null;
  textReconstructionStatus?: "OSHB_WORD_TOKENS_ONLY";
  hebrewText?: string;
  tokens?: PassageTokenV1[];
  navigation?: PassageNavigationV1;
  attribution?: string;
  [key: string]: unknown;
};

export interface PassageReadPort {
  getPassageCore(input: {
    researchReleaseId: ResearchReleaseId;
    locator: PassageLabelLocator;
  }): Promise<PassageCoreV1 | null>;
}
