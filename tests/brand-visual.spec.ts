import { expect, test } from "@playwright/test";

test("approved brand lockups render without clipping", async ({
  page,
}, testInfo) => {
  await page.goto("/tests/brand-preview.html");
  await expect(page.locator("html")).toHaveAttribute(
    "data-brand-ready",
    "true",
  );

  const nameBox = await page.locator("#name-lockup").boundingBox();
  const numericBox = await page.locator("#numeric-lockup").boundingBox();
  expect(nameBox).not.toBeNull();
  expect(numericBox).not.toBeNull();
  expect(nameBox!.width).toBeLessThan(180);
  expect(numericBox!.width).toBeLessThan(240);
  expect(nameBox!.height).toBeGreaterThanOrEqual(26);
  expect(numericBox!.height).toBeGreaterThanOrEqual(52);

  await page.screenshot({
    path: testInfo.outputPath("brand-preview.png"),
    fullPage: true,
  });
});
