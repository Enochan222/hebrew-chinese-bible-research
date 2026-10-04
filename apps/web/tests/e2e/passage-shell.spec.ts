import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";

const fixtureRelease = "11111111-1111-4111-8111-111111111111";
const missingRelease = "22222222-2222-4222-8222-222222222222";
const visualDir = path.join(process.cwd(), "test-results", "visual");
fs.mkdirSync(visualDir, { recursive: true });

function pinned(reference = "1Sam.16.7", release = fixtureRelease, mode = "STUDY") {
  return `/releases/${release}/passages/${encodeURIComponent(reference)}?referenceSystemCode=MT_FIXTURE&mode=${mode}`;
}

test("current route pins once and Study/Research preserves release and reference", async ({ page }) => {
  await page.goto("/passages/1Sam.16.7?referenceSystemCode=MT_FIXTURE&mode=STUDY");
  await expect(page).toHaveURL(new RegExp(`/releases/${fixtureRelease}/passages/1Sam\\.16\\.7`));
  await expect(page.getByTestId("fixture-banner")).toContainText("Fixture data only");
  await expect(page.getByTestId("release-id")).toContainText(fixtureRelease);
  await expect(page.getByTestId("reference-span")).toHaveText("17171717-1717-4171-8171-171717171717");
  await expect(page.getByTestId("active-mode")).toHaveText("Study");
  await page.screenshot({ path: path.join(visualDir, "ready-study.png"), fullPage: true });

  await page.getByTestId("mode-research").click();
  await expect(page).toHaveURL(new RegExp(`/releases/${fixtureRelease}/passages/1Sam\\.16\\.7.*mode=RESEARCH`));
  await expect(page.getByTestId("release-id")).toContainText(fixtureRelease);
  await expect(page.getByTestId("active-mode")).toHaveText("Research");

  await page.getByTestId("mode-study").click();
  await expect(page).toHaveURL(new RegExp(`/releases/${fixtureRelease}/passages/1Sam\\.16\\.7.*mode=STUDY`));
  await expect(page.getByTestId("release-id")).toContainText(fixtureRelease);
});

test("invalid mode has a distinct state", async ({ page }) => {
  await page.goto(pinned("1Sam.16.7", fixtureRelease, "PRO"));
  await expect(page.getByTestId("passage-failure")).toHaveAttribute("data-error-code", "INVALID_MODE");
  await page.screenshot({ path: path.join(visualDir, "invalid-mode.png"), fullPage: true });
});

test("missing reference has a distinct state", async ({ page }) => {
  await page.goto(pinned("Gen.1.1"));
  await expect(page.getByTestId("passage-failure")).toHaveAttribute("data-error-code", "REFERENCE_NOT_FOUND");
  await page.screenshot({ path: path.join(visualDir, "missing-reference.png"), fullPage: true });
});

test("missing release has a distinct state", async ({ page }) => {
  await page.goto(pinned("1Sam.16.7", missingRelease));
  await expect(page.getByTestId("passage-failure")).toHaveAttribute("data-error-code", "RELEASE_NOT_FOUND");
  await page.screenshot({ path: path.join(visualDir, "missing-release.png"), fullPage: true });
});

test("malformed reference and release fail distinctly", async ({ page }) => {
  await page.goto(pinned("bad reference"));
  await expect(page.getByTestId("passage-failure")).toHaveAttribute("data-error-code", "INVALID_REFERENCE");

  await page.goto(pinned("1Sam.16.7", "not-a-uuid"));
  await expect(page.getByTestId("passage-failure")).toHaveAttribute("data-error-code", "INVALID_RELEASE_ID");
});
