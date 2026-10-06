import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e-serving",
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [["list"]],
  use: {
    baseURL: "http://127.0.0.1:3126",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "node tests/support/serving-mock-server.mjs",
      url: "http://127.0.0.1:4126/health",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "npm run dev -- --hostname 127.0.0.1 --port 3126",
      url: "http://127.0.0.1:3126/api/v1/releases/current",
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        ...process.env,
        HCBIBLE_SERVING_REST_URL: "http://127.0.0.1:4126",
        NEXT_TELEMETRY_DISABLED: "1",
      },
    },
  ],
});
