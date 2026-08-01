#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";

const ROUTES = [
  "/",
  "/book-appointment/",
  "/dr-cheena-langer/",
  "/locations/karan-nagar/",
  "/treatments/acne-scar-treatment/",
  "/blog/",
];

const SCENARIOS = [
  {
    name: "desktop-light",
    viewport: { width: 1440, height: 1000 },
    colorScheme: "light",
  },
  {
    name: "mobile-dark",
    viewport: { width: 390, height: 844 },
    colorScheme: "dark",
    isMobile: true,
    hasTouch: true,
  },
];

const WCAG_TAGS = [
  "wcag2a",
  "wcag2aa",
  "wcag21a",
  "wcag21aa",
  "wcag22aa",
];
const BLOCKING_TAGS = new Set(WCAG_TAGS);

function parseArguments(argv) {
  const values = {
    baseUrl: "http://127.0.0.1:8000",
    output: "audit-artifacts/accessibility",
  };

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--base-url") {
      values.baseUrl = argv[index + 1];
      index += 1;
    } else if (argument === "--output") {
      values.output = argv[index + 1];
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${argument}`);
    }
  }

  values.baseUrl = values.baseUrl.replace(/\/$/, "");
  return values;
}

function safeName(route) {
  if (route === "/") return "home";
  return route.replace(/^\//, "").replace(/\/$/, "").replace(/[^a-z0-9]+/gi, "-");
}

function isBlockingViolation(violation) {
  return violation.tags.some((tag) => BLOCKING_TAGS.has(tag));
}

function compactViolation(violation) {
  return {
    id: violation.id,
    impact: violation.impact,
    help: violation.help,
    helpUrl: violation.helpUrl,
    tags: violation.tags,
    nodes: violation.nodes.map((node) => ({
      target: node.target,
      html: node.html,
      failureSummary: node.failureSummary,
    })),
  };
}

function buildMarkdown(results, baseUrl) {
  const passing = results.filter((result) => result.blockingViolations.length === 0 && !result.error).length;
  const lines = [
    "# Accessibility audit",
    "",
    `- Base URL: ${baseUrl}`,
    `- Checks: ${results.length}`,
    `- Passing: ${passing}`,
    `- Blocking standard: WCAG 2.0/2.1/2.2 A and AA`,
    "",
    "| Route | Scenario | Blocking violations | Advisory findings | Result |",
    "|---|---|---:|---:|---|",
  ];

  for (const result of results) {
    const failed = result.blockingViolations.length > 0 || Boolean(result.error);
    lines.push(
      `| \`${result.route}\` | ${result.scenario} | ${result.blockingViolations.length} | ${result.advisoryViolations.length} | ${failed ? "FAIL" : "PASS"} |`,
    );

    if (result.error) {
      lines.push("", `- \`${result.route}\` / ${result.scenario}: audit crashed: ${result.error}`);
    }

    for (const violation of result.blockingViolations) {
      lines.push(
        "",
        `## ${result.route} — ${result.scenario} — ${violation.id}`,
        "",
        `- Impact: ${violation.impact || "unknown"}`,
        `- Rule: ${violation.help}`,
        `- Nodes: ${violation.nodes.length}`,
        `- Guidance: ${violation.helpUrl}`,
      );
      for (const node of violation.nodes.slice(0, 8)) {
        lines.push(`  - Target: \`${node.target.join(" ")}\``);
        if (node.failureSummary) {
          lines.push(`    ${node.failureSummary.replace(/\s+/g, " ").trim()}`);
        }
      }
    }
  }

  lines.push("");
  return lines.join("\n");
}

async function main() {
  const args = parseArguments(process.argv.slice(2));
  await fs.mkdir(args.output, { recursive: true });

  const browser = await chromium.launch();
  const results = [];

  try {
    for (const scenario of SCENARIOS) {
      const context = await browser.newContext({
        viewport: scenario.viewport,
        colorScheme: scenario.colorScheme,
        isMobile: scenario.isMobile || false,
        hasTouch: scenario.hasTouch || false,
        reducedMotion: "reduce",
      });

      try {
        for (const route of ROUTES) {
          const page = await context.newPage();
          const record = {
            route,
            scenario: scenario.name,
            url: `${args.baseUrl}${route}`,
            title: "",
            blockingViolations: [],
            advisoryViolations: [],
            error: "",
          };

          try {
            const response = await page.goto(record.url, {
              waitUntil: "networkidle",
              timeout: 90_000,
            });
            if (!response || !response.ok()) {
              throw new Error(`HTTP ${response ? response.status() : "no response"}`);
            }

            await page.waitForSelector("main#main-content", { timeout: 30_000 });
            await page.waitForTimeout(500);
            record.title = await page.title();

            const audit = await new AxeBuilder({ page })
              .withTags([...WCAG_TAGS, "best-practice"])
              .analyze();

            record.blockingViolations = audit.violations
              .filter(isBlockingViolation)
              .map(compactViolation);
            record.advisoryViolations = audit.violations
              .filter((violation) => !isBlockingViolation(violation))
              .map(compactViolation);

            if (record.blockingViolations.length > 0) {
              await page.screenshot({
                path: path.join(args.output, `${scenario.name}-${safeName(route)}.png`),
                fullPage: true,
              });
            }
          } catch (error) {
            record.error = error instanceof Error ? error.stack || error.message : String(error);
          } finally {
            results.push(record);
            await page.close();
          }
        }
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }

  await fs.writeFile(
    path.join(args.output, "results.json"),
    `${JSON.stringify({ baseUrl: args.baseUrl, results }, null, 2)}\n`,
    "utf8",
  );
  const summary = buildMarkdown(results, args.baseUrl);
  await fs.writeFile(path.join(args.output, "summary.md"), summary, "utf8");
  process.stdout.write(`${summary}\n`);

  const failures = results.filter(
    (result) => result.error || result.blockingViolations.length > 0,
  );
  process.exitCode = failures.length > 0 ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
