"use strict";

const crypto = require("crypto");
const fs = require("fs");
const http = require("http");
const path = require("path");
const { chromium } = require("playwright");
const playwrightVersion = require("playwright/package.json").version;

const laneRoot = path.resolve(__dirname, "..");
const readerRoot = path.join(laneRoot, "build", "html");
const visualRoot = path.join(laneRoot, "qa", "visual");
const reportPath = path.join(laneRoot, "qa", "FULL_READER_VISUAL_QA.json");

const pages = [
  "index.html",
  "units/01-membaca-argumen.html",
  "units/02-menelusuri-sumber.html",
  "units/03-merekonstruksi-pembuktian.html",
  "units/04-sitasi-provenance-catatan-sumber.html",
  "units/05-eksposisi-matematika.html",
  "units/06-komputasi-dapat-direproduksi.html",
  "units/07-errata-koreksi-batas-kepastian.html",
  "units/08-seminar-penelaah-tanggapan-kritik.html",
  "units/09-kontribusi-komunitas-portofolio.html",
];

const legalFiles = [
  "LICENSES.md",
  "THIRD_PARTY_NOTICES.md",
  "licenses/MIT.txt",
  "licenses/APACHE-2.0.txt",
];

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".py": "text/x-python; charset=utf-8",
  ".svg": "image/svg+xml",
  ".txt": "text/plain; charset=utf-8",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
};

function sha256File(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function readerTree() {
  const files = [];
  const visit = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const target = path.join(directory, entry.name);
      if (entry.isDirectory()) visit(target);
      else if (entry.isFile()) files.push(target);
    }
  };
  visit(readerRoot);
  files.sort((left, right) => {
    const a = path.relative(readerRoot, left).replaceAll("\\", "/").toLowerCase();
    const b = path.relative(readerRoot, right).replaceAll("\\", "/").toLowerCase();
    return a < b ? -1 : a > b ? 1 : 0;
  });
  const manifest = files.map((file) => {
    const relative = path.relative(readerRoot, file).replaceAll("\\", "/");
    return `${relative}\t${fs.statSync(file).size}\t${sha256File(file)}\n`;
  }).join("");
  return {
    files: files.length,
    bytes: files.reduce((total, file) => total + fs.statSync(file).size, 0),
    manifestSha256: crypto.createHash("sha256").update(manifest, "utf8").digest("hex"),
  };
}

function serveFile(request, response) {
  const requestUrl = new URL(request.url, "http://127.0.0.1");
  let relative = decodeURIComponent(requestUrl.pathname).replace(/^\/+/, "");
  if (!relative || relative.endsWith("/")) relative += "index.html";
  if (relative === "favicon.ico") {
    response.writeHead(204);
    response.end();
    return;
  }
  const target = path.resolve(readerRoot, relative);
  if (!target.startsWith(readerRoot + path.sep) || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    response.end("Not found");
    return;
  }
  response.writeHead(200, {
    "Content-Type": contentTypes[path.extname(target).toLowerCase()] || "application/octet-stream",
  });
  fs.createReadStream(target).pipe(response);
}

async function captureIndexTiles(page, label, viewport) {
  await page.setViewportSize(viewport);
  const documentHeight = await page.evaluate(() => Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight,
  ));
  const overlap = Math.min(120, Math.floor(viewport.height / 4));
  const step = Math.max(1, viewport.height - overlap);
  const positions = [0];
  const maximumScroll = Math.max(0, documentHeight - viewport.height);
  while (positions.at(-1) < maximumScroll) {
    const next = Math.min(maximumScroll, positions.at(-1) + step);
    if (next === positions.at(-1)) break;
    positions.push(next);
  }
  const tiles = [];
  for (let index = 0; index < positions.length; index += 1) {
    const requestedY = positions[index];
    const actualY = await page.evaluate(async (targetY) => {
      window.scrollTo(0, targetY);
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return window.scrollY;
    }, requestedY);
    if (Math.abs(actualY - requestedY) > 1) {
      throw new Error(`${label}: vertical tile landed at ${actualY}, expected ${requestedY}`);
    }
    const screenshot = path.join(
      visualRoot,
      `full-reader-index-${label}-tile-${String(index + 1).padStart(3, "0")}.png`,
    );
    await page.screenshot({ path: screenshot, animations: "disabled" });
    tiles.push({
      index: index + 1,
      requestedY,
      actualY,
      coveredStart: actualY,
      coveredEnd: Math.min(documentHeight, actualY + viewport.height),
      screenshot: path.relative(laneRoot, screenshot).replaceAll("\\", "/"),
      screenshotSha256: sha256File(screenshot),
    });
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  if (tiles[0].coveredStart !== 0 || tiles.at(-1).coveredEnd !== documentHeight) {
    throw new Error(`${label}: index tiles do not cover both document boundaries`);
  }
  for (let index = 1; index < tiles.length; index += 1) {
    if (tiles[index].coveredStart > tiles[index - 1].coveredEnd) {
      throw new Error(`${label}: index tile coverage gap`);
    }
  }
  return { documentHeight, overlap, step, tileCount: tiles.length, coverageComplete: true, tiles };
}

async function inspectPage(page, origin, relative, viewportName, viewport) {
  await page.setViewportSize(viewport);
  await page.goto(`${origin}/${relative}`, { waitUntil: "networkidle" });
  const metrics = await page.evaluate(() => {
    const main = document.querySelector("main.content");
    if (!main) throw new Error("main.content missing");
    const navTargets = [...document.querySelectorAll("nav.navbar a.nav-link")]
      .map((node) => {
        const url = new URL(node.href, location.href);
        return url.pathname.replace(/^\/+/, "") || "index.html";
      });
    const legalTargets = [...main.querySelectorAll("a")]
      .map((node) => node.getAttribute("href"))
      .filter((href) => href && (href.includes("LICENSES") || href.includes("THIRD_PARTY_NOTICES")));
    return {
      title: document.title,
      language: document.documentElement.lang,
      bodyScrollWidth: document.body.scrollWidth,
      documentScrollWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
      headingCount: main.querySelectorAll("h1, h2, h3").length,
      mathElements: main.querySelectorAll("math").length,
      imagesWithoutAlt: [...main.querySelectorAll("img")].filter(
        (node) => !node.hasAttribute("alt") || !node.getAttribute("alt").trim()
      ).length,
      skipLinks: document.querySelectorAll("a.o017-skip-link").length,
      skipTarget: document.querySelector("a.o017-skip-link")?.getAttribute("href") || null,
      navTargets,
      legalTargets,
      remoteRuntimeRequests: performance.getEntriesByType("resource")
        .map((entry) => entry.name)
        .filter((url) => !url.startsWith(location.origin + "/")),
    };
  });
  await page.evaluate(() => {
    if (document.activeElement && typeof document.activeElement.blur === "function") document.activeElement.blur();
    window.scrollTo(0, 0);
  });
  await page.keyboard.press("Tab");
  metrics.firstTab = await page.evaluate(() => ({
    tag: document.activeElement?.tagName || null,
    className: document.activeElement?.className || null,
    href: document.activeElement?.getAttribute?.("href") || null,
  }));

  const expectedNav = new Set(pages.map((item) => item === "index.html" ? "index.html" : item));
  const observedNav = new Set(metrics.navTargets.map((item) => item || "index.html"));
  if (metrics.language !== "id-ID") throw new Error(`${relative}/${viewportName}: wrong language`);
  if (metrics.bodyScrollWidth > metrics.viewportWidth + 1 || metrics.documentScrollWidth > metrics.viewportWidth + 1) {
    throw new Error(`${relative}/${viewportName}: page-level horizontal overflow`);
  }
  if (metrics.imagesWithoutAlt || metrics.skipLinks !== 1 || !metrics.skipTarget?.endsWith("#quarto-document-content")) {
    throw new Error(`${relative}/${viewportName}: accessibility surface failed`);
  }
  if (!String(metrics.firstTab.className).split(/\s+/).includes("o017-skip-link")) {
    throw new Error(`${relative}/${viewportName}: first keyboard target is not the skip link`);
  }
  if (metrics.remoteRuntimeRequests.length) throw new Error(`${relative}/${viewportName}: remote runtime request`);
  if (expectedNav.size !== observedNav.size || [...expectedNav].some((item) => !observedNav.has(item))) {
    throw new Error(`${relative}/${viewportName}: navbar does not expose the complete nine-unit route`);
  }
  if (relative !== "index.html" && metrics.mathElements < 1) {
    throw new Error(`${relative}/${viewportName}: unit lacks native MathML`);
  }
  if (relative === "index.html" && metrics.legalTargets.length !== 2) {
    throw new Error(`${relative}/${viewportName}: landing page lacks both legal links`);
  }
  return metrics;
}

async function main() {
  for (const relative of [...pages, ...legalFiles]) {
    const target = path.join(readerRoot, ...relative.split("/"));
    if (!fs.existsSync(target) || !fs.statSync(target).isFile()) throw new Error(`reader file missing: ${relative}`);
  }
  fs.mkdirSync(visualRoot, { recursive: true });
  const server = http.createServer(serveFile);
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  const origin = `http://127.0.0.1:${address.port}`;
  let browser;
  try {
    const executablePath = [
      "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
      "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    ].find((candidate) => fs.existsSync(candidate));
    if (!executablePath) throw new Error("No installed Edge or Chrome executable found");
    browser = await chromium.launch({ executablePath, headless: true, args: ["--disable-speech-api"] });
    const browserVersion = await browser.version();
    const page = await browser.newPage();
    const consoleErrors = [];
    const pageErrors = [];
    page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
    page.on("pageerror", (error) => pageErrors.push(String(error)));
    const viewports = {
      desktop: { width: 1440, height: 1000 },
      mobile: { width: 390, height: 844 },
    };
    const checks = {};
    for (const [viewportName, viewport] of Object.entries(viewports)) {
      checks[viewportName] = {};
      for (const relative of pages) {
        checks[viewportName][relative] = await inspectPage(page, origin, relative, viewportName, viewport);
      }
      await page.goto(`${origin}/index.html`, { waitUntil: "networkidle" });
      checks[viewportName].indexVisualCoverage = await captureIndexTiles(
        page,
        `${viewportName}-${viewport.width}x${viewport.height}`,
        viewport,
      );
    }
    if (consoleErrors.length || pageErrors.length) throw new Error(JSON.stringify({ consoleErrors, pageErrors }));
    const report = {
      schema: "o017-full-reader-visual-qa-v1",
      status: "PASS",
      date: "2026-08-22",
      pages,
      legal_files: legalFiles.map((relative) => ({
        path: relative,
        bytes: fs.statSync(path.join(readerRoot, ...relative.split("/"))).size,
        sha256: sha256File(path.join(readerRoot, ...relative.split("/"))),
      })),
      reader_tree: readerTree(),
      visual_qa_script_sha256: sha256File(__filename),
      toolchain: { node: process.version, playwright: playwrightVersion, browser: browserVersion },
      console_errors: consoleErrors,
      page_errors: pageErrors,
      checks,
    };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");
    process.stdout.write(JSON.stringify({
      status: report.status,
      pages: report.pages.length,
      reader_tree: report.reader_tree,
      toolchain: report.toolchain,
    }) + "\n");
  } finally {
    if (browser) await Promise.race([browser.close(), new Promise((resolve) => setTimeout(resolve, 2000))]);
    server.close();
    if (typeof server.closeAllConnections === "function") server.closeAllConnections();
  }
}

main().catch((error) => {
  process.stderr.write(String(error.stack || error) + "\n");
  process.exitCode = 1;
});
