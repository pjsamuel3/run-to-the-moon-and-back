import { test, expect } from '@playwright/test';

const jsErrors = [];

test.beforeEach(async ({ page }) => {
  page.on('pageerror', err => jsErrors.push(err.message));
  await page.goto('/');
  await page.waitForSelector('#app', { state: 'visible', timeout: 10000 });
});

test('no JS errors on load', async ({ page }) => {
  expect(jsErrors).toEqual([]);
});

test('total km counter is visible and non-zero', async ({ page }) => {
  const km = page.locator('#totalKm');
  await expect(km).toBeVisible();
  // wait for the counter animation (120ms delay + ~1100ms roll-up) to finish
  await page.waitForFunction(
    () => parseInt(document.getElementById('totalKm').textContent.replace(/,/g, ''), 10) > 0,
    { timeout: 3000 }
  );
  const value = await km.textContent();
  expect(parseInt(value.replace(/,/g, ''), 10)).toBeGreaterThan(0);
});

test('progress bar and rocket are visible', async ({ page }) => {
  await expect(page.locator('#rocketMarker')).toBeVisible();
  await expect(page.locator('#progressFill')).toBeVisible();
});

test('next milestone label is shown', async ({ page }) => {
  await expect(page.locator('#nextMilestone')).toContainText('Next:');
});

test('leaderboard renders runner cards', async ({ page }) => {
  await page.locator('#leaderboard').scrollIntoViewIfNeeded();
  const cards = page.locator('.runner-card');
  await expect(cards.first()).toBeVisible();
  expect(await cards.count()).toBeGreaterThan(0);
});

test('journey milestones render all 7 items', async ({ page }) => {
  await page.locator('#milestones').scrollIntoViewIfNeeded();
  const items = page.locator('.milestone-item');
  await expect(items.first()).toBeVisible();
  expect(await items.count()).toBe(7);
});

test('feed renders activity items', async ({ page }) => {
  await page.locator('#feed').scrollIntoViewIfNeeded();
  const items = page.locator('.feed-item');
  await expect(items.first()).toBeVisible();
  expect(await items.count()).toBeGreaterThan(0);
});

test('mobile: bottom nav visible, top nav hidden', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');
  await page.waitForSelector('#app', { state: 'visible' });
  await expect(page.locator('.bottom-nav')).toBeVisible();
  await expect(page.locator('.top-nav')).toBeHidden();
});

test('desktop: top nav visible, bottom nav hidden', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto('/');
  await page.waitForSelector('#app', { state: 'visible' });
  await expect(page.locator('.top-nav')).toBeVisible();
  await expect(page.locator('.bottom-nav')).toBeHidden();
});
