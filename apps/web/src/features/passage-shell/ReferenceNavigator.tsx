"use client";

import { useRouter } from "next/navigation";
import type { ExperienceMode } from "@/domain/experience/port";
import type { PassageNavigationV1 } from "@/domain/passage/port";
import type { ResearchReleaseId } from "@/domain/release/port";

export function ReferenceNavigator(props: {
  researchReleaseId: ResearchReleaseId;
  referenceSystemCode: string;
  currentReference: string;
  mode: ExperienceMode;
  navigation: PassageNavigationV1;
}) {
  const router = useRouter();
  const books = props.navigation.books ?? [];
  const chapters = props.navigation.chapters ?? [];
  const passages = props.navigation.passages ?? [];

  const href = (reference: string) =>
    `/releases/${encodeURIComponent(props.researchReleaseId)}/passages/${encodeURIComponent(reference)}?referenceSystemCode=${encodeURIComponent(props.referenceSystemCode)}&mode=${encodeURIComponent(props.mode)}`;

  const navigate = (reference: string | undefined) => {
    if (reference) router.push(href(reference));
  };

  return (
    <nav className="reference-navigator" aria-label="Whole-Bible reference navigation" data-testid="reference-navigator">
      <label>
        <span>Book</span>
        <select
          aria-label="Book"
          value={props.navigation.currentBookCode ?? ""}
          onChange={(event) => navigate(books.find((book) => book.bookCode === event.target.value)?.firstReference)}
        >
          {books.map((book) => (
            <option key={book.bookCode} value={book.bookCode}>
              {book.bookCode}
            </option>
          ))}
        </select>
      </label>

      <label>
        <span>Chapter</span>
        <select
          aria-label="Chapter"
          value={props.navigation.currentChapter?.toString() ?? ""}
          onChange={(event) =>
            navigate(chapters.find((chapter) => chapter.chapterNumber === Number(event.target.value))?.firstReference)
          }
        >
          {chapters.map((chapter) => (
            <option key={chapter.chapterNumber} value={chapter.chapterNumber}>
              {chapter.chapterNumber}
            </option>
          ))}
        </select>
      </label>

      <label>
        <span>Passage</span>
        <select
          aria-label="Passage"
          value={props.currentReference}
          onChange={(event) => navigate(event.target.value)}
        >
          {passages.map((passage) => (
            <option key={passage.referenceLabel} value={passage.referenceLabel}>
              {passage.verseLabel ?? passage.referenceLabel}
            </option>
          ))}
        </select>
      </label>
    </nav>
  );
}
