import {chromium} from "@playwright/test";
import {mkdir, writeFile} from "node:fs/promises";
import path from "node:path";

const baseUrl = (process.env.PREMARKET_WORKSPACE_URL ?? "http://127.0.0.1:3000").replace(/\/$/, "");
const outputDir = path.resolve(process.cwd(), "../../outputs/local/issue24-visual-qa");
const viewports = [
  {width: 1440, height: 900},
  {width: 1280, height: 900},
  {width: 1024, height: 900},
];
const report = {baseUrl, startedAt: new Date().toISOString(), checks: [], errors: []};

await mkdir(outputDir, {recursive: true});
const browser = await chromium.launch({channel: "chrome", headless: true});

try {
  for (const viewport of viewports) {
    const page = await browser.newPage({viewport});
    const prefix = `${viewport.width}x${viewport.height}`;
    page.on("console", (message) => {
      if (message.type() === "error") {
        const location = message.location();
        report.errors.push(`${prefix}:console:${location.url || "unknown"}:${location.lineNumber ?? 0}:${message.text()}`);
      }
    });
    page.on("pageerror", (error) => report.errors.push(`${prefix}:page:${error.message}`));
    page.on("requestfailed", (request) => {
      const reason = request.failure()?.errorText ?? "unknown";
      if (reason !== "net::ERR_ABORTED") report.errors.push(`${prefix}:request:${reason}:${request.url()}`);
    });
    page.on("response", (response) => {
      if (response.status() >= 400) report.errors.push(`${prefix}:http:${response.status()}:${response.url()}`);
    });

    await page.goto(`${baseUrl}/`, {waitUntil: "networkidle"});
    await page.getByRole("heading", {name: "Command Center", exact: true}).waitFor();
    await page.locator(".freshness-banner.is-blocked").waitFor();
    await page.getByText("Refresh SUCCEEDED").waitFor();
    await page.getByText("Validation PASS").waitFor();
    const layout = await inspectLayout(page);
    assert(layout.bodyOverflow <= 1, `${prefix} command center body overflow ${layout.bodyOverflow}px`);
    assert(layout.contextOverflow <= 1, `${prefix} topbar context overflow ${layout.contextOverflow}px`);
    assert(!layout.topbarTextOverlap, `${prefix} provider and mode text overlap`);
    assert(layout.mainStartsAfterSidebar, `${prefix} sidebar overlaps workspace content`);
    assert(layout.refreshOverflow <= 1, `${prefix} refresh status overflow ${layout.refreshOverflow}px`);
    await page.screenshot({path: path.join(outputDir, `${prefix}-command-center.png`), fullPage: true});
    report.checks.push({viewport: prefix, page: "command-center", layout, staleBlocked: true});

    if (viewport.width === 1440) {
      await page.goto(`${baseUrl}/portfolio`, {waitUntil: "networkidle"});
      await page.getByRole("heading", {name: "Portfolio Overview"}).waitFor();
      const canvas = await inspectCanvases(page);
      const clusterOverflow = await page.locator(".cluster-list small").evaluateAll((elements) => Math.max(0, ...elements.map((element) => element.scrollWidth - element.clientWidth)));
      assert(canvas.count > 0 && canvas.nonBlank === canvas.count, "portfolio correlation canvas is blank");
      assert(clusterOverflow <= 1, `portfolio cluster text overflow ${clusterOverflow}px`);
      await page.screenshot({path: path.join(outputDir, `${prefix}-portfolio.png`), fullPage: true});
      report.checks.push({viewport: prefix, page: "portfolio", canvas, clusterOverflow});

      await page.goto(`${baseUrl}/quant/recommendation-tiering`, {waitUntil: "networkidle"});
      await page.getByText("Issue #10: locked").waitFor();
      await page.screenshot({path: path.join(outputDir, `${prefix}-recommendation-locked.png`), fullPage: true});
      report.checks.push({viewport: prefix, page: "recommendation-tiering", lockVisible: true});
    }

    if (viewport.width === 1280) {
      await page.goto(`${baseUrl}/risk-monitor`, {waitUntil: "networkidle"});
      await page.getByRole("heading", {name: "Risk Monitor"}).waitFor();
      const canvas = await inspectCanvases(page);
      const kpiOverflow = await page.locator(".kpi-card").evaluateAll((elements) => Math.max(0, ...elements.map((element) => element.scrollWidth - element.clientWidth)));
      assert(canvas.count >= 2 && canvas.nonBlank === canvas.count, "risk monitor canvases are blank");
      assert(kpiOverflow <= 1, `risk KPI overflow ${kpiOverflow}px`);
      await page.screenshot({path: path.join(outputDir, `${prefix}-risk-monitor.png`), fullPage: true});
      report.checks.push({viewport: prefix, page: "risk-monitor", canvas, kpiOverflow});
    }

    if (viewport.width === 1024) {
      await page.goto(`${baseUrl}/stocks/000333.SZ`, {waitUntil: "networkidle"});
      await page.getByRole("heading", {name: "Midea Group"}).waitFor();
      await page.locator(".stock-price .price-down").waitFor();
      await page.getByRole("tab", {name: "Price chart"}).click();
      await page.locator(".price-volume-chart canvas").first().waitFor();
      const canvas = await inspectCanvases(page);
      assert(canvas.count >= 2 && canvas.nonBlank >= 2, `stock price or volume canvas is blank: ${JSON.stringify(canvas)}`);
      const stockLayout = await inspectLayout(page);
      assert(stockLayout.bodyOverflow <= 1, `1024 stock page body overflow ${stockLayout.bodyOverflow}px`);
      await page.screenshot({path: path.join(outputDir, `${prefix}-stock-detail.png`), fullPage: true});
      report.checks.push({viewport: prefix, page: "stock-detail", canvas, layout: stockLayout, negativePriceUsesDownColor: true});
    }
    await page.close();
  }
} catch (error) {
  report.errors.push(error instanceof Error ? error.message : String(error));
} finally {
  report.completedAt = new Date().toISOString();
  report.status = report.errors.length === 0 ? "PASS" : "FAIL";
  await writeFile(path.join(outputDir, "report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
  await browser.close();
}

if (report.status !== "PASS") {
  console.error(JSON.stringify(report, null, 2));
  process.exit(1);
}
console.log(`visual QA: PASS | screenshots=7 | report=${path.join(outputDir, "report.json")}`);

async function inspectLayout(page) {
  return page.evaluate(() => {
    const sidebar = document.querySelector(".sidebar")?.getBoundingClientRect();
    const main = document.querySelector(".workspace-main")?.getBoundingClientRect();
    const contextOverflow = Math.max(0, ...Array.from(document.querySelectorAll(".context-block")).map((element) => element.scrollWidth - element.clientWidth));
    const refreshOverflow = Math.max(0, ...Array.from(document.querySelectorAll(".refresh-status-strip > div")).map((element) => element.scrollWidth - element.clientWidth));
    const provider = textRect(document.querySelector(".context-provider strong"));
    const mode = textRect(document.querySelector(".mode-badge"));
    const contextClip = document.querySelector(".topbar-context")?.getBoundingClientRect() ?? null;
    return {
      bodyOverflow: document.documentElement.scrollWidth - window.innerWidth,
      contextOverflow,
      refreshOverflow,
      topbarTextOverlap: intersects(clip(provider, contextClip), mode),
      mainStartsAfterSidebar: Boolean(sidebar && main && main.left >= sidebar.right - 1),
      sidebarRight: sidebar?.right ?? null,
      mainLeft: main?.left ?? null,
    };

    function textRect(element) {
      if (!element) return null;
      const range = document.createRange();
      range.selectNodeContents(element);
      return range.getBoundingClientRect();
    }
    function intersects(left, right) {
      if (!left || !right) return false;
      return left.left < right.right && left.right > right.left && left.top < right.bottom && left.bottom > right.top;
    }
    function clip(rect, boundary) {
      if (!rect || !boundary) return rect;
      const visible = {left: Math.max(rect.left, boundary.left), right: Math.min(rect.right, boundary.right), top: Math.max(rect.top, boundary.top), bottom: Math.min(rect.bottom, boundary.bottom)};
      return visible.left < visible.right && visible.top < visible.bottom ? visible : null;
    }
  });
}

async function inspectCanvases(page) {
  await page.waitForTimeout(600);
  return page.locator("canvas").evaluateAll((canvases) => {
    const lengths = canvases.map((canvas) => canvas.toDataURL().length);
    return {count: canvases.length, nonBlank: lengths.filter((length) => length > 1000).length, dataUrlLengths: lengths};
  });
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}
