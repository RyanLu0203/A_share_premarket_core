import {chromium} from "@playwright/test";
import {mkdir, writeFile} from "node:fs/promises";
import path from "node:path";

const baseUrl = (process.env.PREMARKET_WORKSPACE_URL ?? "http://127.0.0.1:3000").replace(/\/$/, "");
const outputDir = path.resolve(process.cwd(), "../../outputs/local/global-refactor01-visual-qa");
const viewports = [{width: 1440, height: 900}, {width: 1280, height: 900}, {width: 1024, height: 900}];
const report = {baseUrl, startedAt: new Date().toISOString(), checks: [], screenshots: [], errors: []};

await mkdir(outputDir, {recursive: true});
const browser = await chromium.launch({channel: "chrome", headless: true});

try {
  for (const viewport of viewports) {
    const page = await browser.newPage({viewport});
    observeErrors(page, `${viewport.width}x${viewport.height}`);
    await openChart(page, "000333.SZ");
    const layout = await inspectChart(page);
    assert(layout.bodyOverflow <= 1, `${viewport.width}px chart body overflow ${layout.bodyOverflow}px`);
    assert(layout.tooltipOverflow <= 1, `${viewport.width}px tooltip overflow ${layout.tooltipOverflow}px`);
    assert(layout.nonBlankCanvasCount >= 2, `${viewport.width}px candlestick or volume canvas is blank`);
    assert(layout.distinctCanvasTops >= 2, `${viewport.width}px volume is not in a distinct pane`);
    assert(layout.hasForbiddenActionText === false, `${viewport.width}px chart contains action language`);
    const screenshot = `${viewport.width}x${viewport.height}-stock-chart.png`;
    await page.locator(".stock-tabs [role=tabpanel][data-state=active] .panel").screenshot({path: path.join(outputDir, screenshot)});
    report.screenshots.push(screenshot);
    report.checks.push({viewport: `${viewport.width}x${viewport.height}`, page: "stock-chart", ...layout});

    if (viewport.width === 1440) await runDesktopMatrix(page);
    await page.close();
  }

  await captureUnavailableState();
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
console.log(`visual QA: PASS | screenshots=${report.screenshots.length} | report=${path.join(outputDir, "report.json")}`);

async function runDesktopMatrix(page) {
  await page.goto(`${baseUrl}/watchlist`, {waitUntil: "networkidle"});
  await page.getByRole("link", {name: "Open chart for 000333.SZ"}).click();
  await page.waitForURL("**/stocks/000333.SZ/chart");
  await page.locator(".price-volume-chart canvas").first().waitFor();
  report.checks.push({viewport: "1440x900", flow: "watchlist-to-chart", status: "PASS"});

  await openChart(page, "000157.SZ");
  await page.goto(`${baseUrl}/stocks`, {waitUntil: "networkidle"});
  await page.getByText("Selected", {exact: true}).waitFor();
  const selectedHref = await page.locator('.sidebar a:has-text("Stock Detail")').getAttribute("href");
  assert(selectedHref === "/stocks/000157.SZ", `selected symbol did not persist: ${selectedHref}`);
  const explorerScreenshot = "1440x900-stock-explorer-selected.png";
  await page.screenshot({path: path.join(outputDir, explorerScreenshot), fullPage: true});
  report.screenshots.push(explorerScreenshot);
  report.checks.push({viewport: "1440x900", flow: "explorer-selected-symbol", selectedSymbol: "000157.SZ", selectedHref});

  await page.getByRole("link", {name: "Open chart for 000157.SZ"}).click();
  await page.waitForURL("**/stocks/000157.SZ/chart");
  await page.locator(".price-volume-chart canvas").first().waitFor();
  report.checks.push({viewport: "1440x900", flow: "explorer-to-chart", status: "PASS"});

  await openChart(page, "000333.SZ");
  for (const range of ["20D", "250D", "ALL"]) {
    await page.getByRole("button", {name: range, exact: true}).click();
    const expected = range === "20D" ? "20 of 20 committed sessions available" : range === "250D" ? "120 of 250 committed sessions available" : "120 of 120 committed sessions available";
    await page.getByText(expected, {exact: true}).waitFor();
    const screenshot = `1440x900-stock-chart-${range.toLowerCase()}.png`;
    await page.locator(".stock-tabs [role=tabpanel][data-state=active] .panel").screenshot({path: path.join(outputDir, screenshot)});
    report.screenshots.push(screenshot);
    report.checks.push({viewport: "1440x900", range, availability: expected});
  }

  const selectedBefore = await selectedDate(page);
  const chart = await page.locator(".price-volume-chart").boundingBox();
  assert(chart, "chart has no bounding box for crosshair interaction");
  await page.mouse.move(chart.x + chart.width * 0.22, chart.y + chart.height * 0.28);
  await page.waitForTimeout(250);
  const selectedAfter = await selectedDate(page);
  assert(selectedAfter !== "UNAVAILABLE", "crosshair tooltip did not expose a selected date");
  const tooltipScreenshot = "1440x900-stock-chart-crosshair.png";
  await page.locator(".stock-tabs [role=tabpanel][data-state=active] .panel").screenshot({path: path.join(outputDir, tooltipScreenshot)});
  report.screenshots.push(tooltipScreenshot);
  report.checks.push({viewport: "1440x900", interaction: "crosshair", selectedBefore, selectedAfter});

  await page.getByRole("button", {name: "Deterministic replay"}).click();
  await page.getByText("DETERMINISTIC REPLAY", {exact: true}).waitFor();
  await page.getByText("DETERMINISTIC REPLAY SNAPSHOT", {exact: true}).waitFor();
  const replayScreenshot = "1440x900-stock-chart-replay.png";
  await page.locator(".stock-tabs [role=tabpanel][data-state=active] .panel").screenshot({path: path.join(outputDir, replayScreenshot)});
  report.screenshots.push(replayScreenshot);
  report.checks.push({viewport: "1440x900", state: "replay", status: "PASS"});

  await page.goto(`${baseUrl}/quant/recommendation-tiering`, {waitUntil: "networkidle"});
  await page.getByText("Issue #10: locked").waitFor();
  const quantScreenshot = "1440x900-quant-locked.png";
  await page.screenshot({path: path.join(outputDir, quantScreenshot), fullPage: true});
  report.screenshots.push(quantScreenshot);
  report.checks.push({viewport: "1440x900", page: "recommendation-tiering", lockVisible: true});
}

async function captureUnavailableState() {
  const page = await browser.newPage({viewport: {width: 1280, height: 900}});
  observeErrors(page, "1280x900-unavailable");
  await page.route("**/api/stocks/000333.SZ/market*", async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    await route.fulfill({response, json: {...body, candles: []}});
  });
  await page.goto(`${baseUrl}/stocks/000333.SZ/chart`, {waitUntil: "networkidle"});
  await page.getByText("No committed candlestick evidence for this symbol.", {exact: true}).waitFor();
  const screenshot = "1280x900-stock-chart-unavailable.png";
  await page.locator(".stock-tabs [role=tabpanel][data-state=active] .panel").screenshot({path: path.join(outputDir, screenshot)});
  report.screenshots.push(screenshot);
  report.checks.push({viewport: "1280x900", state: "unavailable", status: "PASS"});
  await page.close();
}

async function openChart(page, symbol) {
  await page.goto(`${baseUrl}/stocks/${symbol}/chart`, {waitUntil: "networkidle"});
  await page.locator(".price-volume-chart canvas").first().waitFor();
  await page.getByText("NOT A LIVE QUOTE", {exact: true}).waitFor();
  await page.locator(".page-header p").filter({hasText: symbol}).waitFor();
}

async function selectedDate(page) {
  return page.locator(".chart-tooltip > div").first().locator("strong").innerText();
}

async function inspectChart(page) {
  await page.waitForTimeout(500);
  return page.evaluate(() => {
    const tooltipOverflow = Math.max(0, ...Array.from(document.querySelectorAll(".chart-tooltip > div")).map((element) => element.scrollWidth - element.clientWidth));
    const canvases = Array.from(document.querySelectorAll(".price-volume-chart canvas"));
    const dataUrlLengths = canvases.map((canvas) => canvas.toDataURL().length);
    const canvasTops = [...new Set(canvases.map((canvas) => Math.round(canvas.getBoundingClientRect().top)))];
    const text = document.querySelector(".stock-tabs [role=tabpanel][data-state=active]")?.textContent ?? "";
    return {
      bodyOverflow: document.documentElement.scrollWidth - window.innerWidth,
      tooltipOverflow,
      canvasCount: canvases.length,
      nonBlankCanvasCount: dataUrlLengths.filter((length) => length > 1000).length,
      distinctCanvasTops: canvasTops.length,
      dataUrlLengths,
      hasForbiddenActionText: /\b(?:BUY|SELL|HOLD)\b/.test(text),
    };
  });
}

function observeErrors(page, prefix) {
  page.on("console", (message) => {if (message.type() === "error") report.errors.push(`${prefix}:console:${message.text()}`);});
  page.on("pageerror", (error) => report.errors.push(`${prefix}:page:${error.message}`));
  page.on("requestfailed", (request) => {if (request.failure()?.errorText !== "net::ERR_ABORTED") report.errors.push(`${prefix}:request:${request.failure()?.errorText}:${request.url()}`);});
  page.on("response", (response) => {if (response.status() >= 400) report.errors.push(`${prefix}:http:${response.status()}:${response.url()}`);});
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}
