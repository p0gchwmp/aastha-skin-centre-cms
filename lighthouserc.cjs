const baseUrl = (process.env.LHCI_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const formFactor = process.env.LHCI_FORM_FACTOR === "desktop" ? "desktop" : "mobile";
const routes = [
  "/",
  "/book-appointment/",
  "/dr-cheena-langer/",
  "/locations/karan-nagar/",
  "/treatments/acne-scar-treatment/",
  "/blog/",
];

module.exports = {
  ci: {
    collect: {
      url: routes.map((route) => `${baseUrl}${route}`),
      numberOfRuns: 1,
      settings: {
        chromeFlags: "--headless --no-sandbox --disable-dev-shm-usage",
        throttlingMethod: "simulate",
        ...(formFactor === "desktop" ? { preset: "desktop" } : {}),
      },
    },
    assert: {
      assertions: {
        "categories:performance": ["error", { minScore: 0.95 }],
        "categories:accessibility": ["error", { minScore: 1 }],
        "categories:best-practices": ["error", { minScore: 1 }],
        "categories:seo": ["error", { minScore: 1 }],
        "first-contentful-paint": ["error", { maxNumericValue: 2500 }],
        "largest-contentful-paint": ["error", { maxNumericValue: 3000 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.1 }],
        "total-blocking-time": ["error", { maxNumericValue: 300 }],
        "uses-responsive-images": "warn",
        "uses-optimized-images": "warn",
        "unused-css-rules": "warn",
        "unused-javascript": "warn",
      },
    },
    upload: {
      target: "filesystem",
      outputDir: `audit-artifacts/lighthouse-${formFactor}`,
    },
  },
};
