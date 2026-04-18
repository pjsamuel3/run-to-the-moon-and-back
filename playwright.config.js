import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: 'http://localhost:8081',
    screenshot: 'only-on-failure',
  },
});
