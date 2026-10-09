import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";

const releaseId = "71000000-0000-4000-8000-000000000005";
const visualDir = path.join(process.cwd(), "test-results", "visual");
fs.mkdirSync(visualDir, { recursive: true });

test("published Serving reader renders data-driven navigation and rights disclosure", async ({ page }) => {
  await page.goto(
    `/releases/${releaseId}/passages/Gen.1.1?referenceSystemCode=OSHB_OSIS&mode=STUDY`,
  );

  await expect(page.getByTestId("passage-shell")).toHaveAttribute("data-source-mode", "SERVING");
  await expect(page.getByTestId("serving-banner")).toContainText("Published database-backed passage");
  await expect(page.getByTestId("reference-navigator")).toBeVisible();
  await expect(page.getByLabel("Book")).toHaveValue("Gen");
  await expect(page.getByLabel("Book").locator("option")).toHaveCount(2);
  await expect(page.getByLabel("Chapter")).toHaveValue("1");
  await expect(page.getByLabel("Passage selector")).toHaveValue("Gen.1.1");
  await expect(page.getByTestId("hebrew-text")).toContainText("בְּרֵאשִׁית");
  await expect(page.getByText("Word-token display only.")).toBeVisible();
  await expect(page.getByTestId("passage-attribution")).toContainText("Open Scriptures Hebrew Bible");
  await expect(page.getByTestId("translation-witnesses")).toBeVisible();
  await expect(page.getByText("Synthetic Chinese Test Witness")).toBeVisible();
  await expect(page.getByTestId("translation-witness-text")).toContainText("合成測試譯文");
  await expect(page.getByText("1 rights-approved release-pinned witness available above.")).toBeVisible();
  await expect(page.getByText("Published module availability")).toBeVisible();

  await page.screenshot({ path: path.join(visualDir, "serving-genesis-1-1.png"), fullPage: true });
});
