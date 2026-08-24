"use strict";

const crypto = require("crypto");
const fs = require("fs");
const http = require("http");
const path = require("path");
const { chromium } = require("playwright");

const configs = {
  "O017-U01": {
    html: "units/01-membaca-argumen.html",
    report: "UNIT_01_VISUAL_QA.json",
    slug: "unit-01",
    labelPattern: "O017-U01",
    exercisePrefix: "X",
    minHeadings: 12,
    minMath: 60,
  },
  "O017-U02": {
    html: "units/02-menelusuri-sumber.html",
    report: "UNIT_02_VISUAL_QA.json",
    slug: "unit-02",
    labelPattern: "O017-U02",
    minHeadings: 14,
    minMath: 12,
  },
  "O017-U03": {
    html: "units/03-merekonstruksi-pembuktian.html",
    report: "UNIT_03_VISUAL_QA.json",
    slug: "unit-03",
    labelPattern: "O017-U03",
    minHeadings: 30,
    minMath: 30,
  },
  "O017-U04": {
    html: "units/04-sitasi-provenance-catatan-sumber.html",
    report: "UNIT_04_VISUAL_QA.json",
    slug: "unit-04",
    labelPattern: "O017-U04",
    exercisePrefix: "E",
    minHeadings: 28,
    minMath: 14,
  },
  "O017-U05": {
    html: "units/05-eksposisi-matematika.html",
    report: "UNIT_05_VISUAL_QA.json",
    slug: "unit-05",
    labelPattern: "O017-U05",
    exercisePrefix: "E",
    minHeadings: 25,
    minMath: 20,
  },
  "O017-U06": {
    html: "units/06-komputasi-dapat-direproduksi.html",
    report: "UNIT_06_VISUAL_QA.json",
    slug: "unit-06",
    labelPattern: "O017-U06",
    exercisePrefix: "EX",
    minHeadings: 30,
    minMath: 20,
  },
  "O017-U07": {
    html: "units/07-errata-koreksi-batas-kepastian.html",
    report: "UNIT_07_VISUAL_QA.json",
    slug: "unit-07",
    labelPattern: "O017-U07",
    exercisePrefix: "X",
    minHeadings: 30,
    minMath: 20,
  },
  "O017-U08": {
    html: "units/08-seminar-penelaah-tanggapan-kritik.html",
    report: "UNIT_08_VISUAL_QA.json",
    slug: "unit-08",
    labelPattern: "O017-U08",
    exercisePrefix: "E",
    minHeadings: 30,
    minMath: 20,
  },
  "O017-U09": {
    html: "units/09-kontribusi-komunitas-portofolio.html",
    report: "UNIT_09_VISUAL_QA.json",
    slug: "unit-09",
    labelPattern: "O017-U09",
    exercisePrefix: "E",
    minHeadings: 28,
    minMath: 20,
  },
};

const unitId = process.argv[2];
const config = configs[unitId];
if (!config) {
  throw new Error(`unsupported unit ID: ${unitId || "(missing)"}`);
}

const laneRoot = path.resolve(__dirname, "..");
const readerRoot = path.join(laneRoot, "build", "html");
const unitHtml = path.join(readerRoot, ...config.html.split("/"));
const visualRoot = path.join(laneRoot, "qa", "visual");
const reportPath = path.join(laneRoot, "qa", config.report);

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

async function captureViewportTiles(page, label, viewport) {
  const documentHeight = await page.evaluate(() => Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight,
  ));
  const overlap = Math.min(120, Math.floor(viewport.height / 5));
  const step = Math.max(1, viewport.height - overlap);
  const maximumScroll = Math.max(0, documentHeight - viewport.height);
  const requestedPositions = [0];
  while (requestedPositions.at(-1) < maximumScroll) {
    const next = Math.min(maximumScroll, requestedPositions.at(-1) + step);
    if (next === requestedPositions.at(-1)) break;
    requestedPositions.push(next);
  }

  const prefix = `${config.slug}-${label}`;
  for (const name of fs.readdirSync(visualRoot)) {
    if (name === `${prefix}.png` || new RegExp(`^${prefix}-tile-\\d{3}\\.png$`).test(name)) {
      fs.unlinkSync(path.join(visualRoot, name));
    }
  }

  const tiles = [];
  for (let index = 0; index < requestedPositions.length; index += 1) {
    const requestedY = requestedPositions[index];
    const actualY = await page.evaluate(async (targetY) => {
      window.scrollTo(0, targetY);
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return window.scrollY;
    }, requestedY);
    if (Math.abs(actualY - requestedY) > 1) {
      throw new Error(`${label}: scroll tile ${index + 1} landed at ${actualY}, expected ${requestedY}`);
    }
    const witness = await page.evaluate(() => {
      const nodes = [...document.querySelectorAll("main.content h2, main.content h3, main.content p, main.content li")];
      const visible = nodes.find((node) => {
        const rect = node.getBoundingClientRect();
        return rect.bottom > 0 && rect.top < window.innerHeight;
      });
      return (visible?.textContent || "").trim().replace(/\s+/g, " ").slice(0, 160);
    });
    const suffix = index === 0 ? "" : `-tile-${String(index + 1).padStart(3, "0")}`;
    const screenshot = path.join(visualRoot, `${prefix}${suffix}.png`);
    await page.screenshot({ path: screenshot, fullPage: false, captureBeyondViewport: false });
    tiles.push({
      index: index + 1,
      requestedY,
      actualY,
      coveredStart: actualY,
      coveredEnd: Math.min(documentHeight, actualY + viewport.height),
      witness,
      screenshot: path.relative(laneRoot, screenshot).replaceAll("\\", "/"),
      screenshotSha256: sha256File(screenshot),
    });
  }

  if (tiles[0].coveredStart !== 0 || tiles.at(-1).coveredEnd !== documentHeight) {
    throw new Error(`${label}: tiled screenshots do not cover both document boundaries`);
  }
  for (let index = 1; index < tiles.length; index += 1) {
    if (tiles[index].coveredStart > tiles[index - 1].coveredEnd) {
      throw new Error(`${label}: visual-evidence gap before tile ${index + 1}`);
    }
  }
  if (new Set(tiles.map((tile) => tile.screenshotSha256)).size !== tiles.length) {
    throw new Error(`${label}: duplicate viewport tile bytes detected`);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  return {
    documentHeight,
    viewportHeight: viewport.height,
    overlap,
    step,
    tileCount: tiles.length,
    coverageComplete: true,
    tiles,
  };
}

async function captureHorizontalRegions(page, label) {
  const prefix = `${config.slug}-${label}-horizontal`;
  for (const name of fs.readdirSync(visualRoot)) {
    if (new RegExp(`^${prefix}-(?:table|math)-\\d{3}-tile-\\d{3}\\.png$`).test(name)) {
      fs.unlinkSync(path.join(visualRoot, name));
    }
  }

  const handles = await page.$$("main.content .o017-table-scroll, main.content .o017-math-scroll");
  const evidence = [];
  for (const handle of handles) {
    const metadata = await handle.evaluate((node) => {
      const regionKind = node.classList.contains("o017-table-scroll") ? "table" : "math";
      const selector = regionKind === "table" ? ".o017-table-scroll" : ".o017-math-scroll";
      const peers = [...document.querySelectorAll(`main.content ${selector}`)];
      return {
        regionKind,
        regionIndex: peers.indexOf(node) + 1,
        ariaLabel: node.getAttribute("aria-label"),
        clientWidth: node.clientWidth,
        scrollWidth: node.scrollWidth,
      };
    });
    if (metadata.scrollWidth <= metadata.clientWidth + 1) continue;

    const overlap = Math.min(80, Math.floor(metadata.clientWidth / 4));
    const step = Math.max(1, metadata.clientWidth - overlap);
    const maximumScroll = metadata.scrollWidth - metadata.clientWidth;
    const requestedPositions = [0];
    while (requestedPositions.at(-1) < maximumScroll) {
      const next = Math.min(maximumScroll, requestedPositions.at(-1) + step);
      if (next === requestedPositions.at(-1)) break;
      requestedPositions.push(next);
    }

    const tiles = [];
    for (let index = 0; index < requestedPositions.length; index += 1) {
      const requestedX = requestedPositions[index];
      const actualX = await handle.evaluate(async (node, targetX) => {
        node.scrollLeft = targetX;
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        return node.scrollLeft;
      }, requestedX);
      if (Math.abs(actualX - requestedX) > 1) {
        throw new Error(`${label}: horizontal tile landed at ${actualX}, expected ${requestedX}`);
      }
      const screenshot = path.join(
        visualRoot,
        `${prefix}-${metadata.regionKind}-${String(metadata.regionIndex).padStart(3, "0")}`
          + `-tile-${String(index + 1).padStart(3, "0")}.png`,
      );
      await handle.screenshot({ path: screenshot, animations: "disabled" });
      tiles.push({
        index: index + 1,
        requestedX,
        actualX,
        coveredStart: actualX,
        coveredEnd: Math.min(metadata.scrollWidth, actualX + metadata.clientWidth),
        screenshot: path.relative(laneRoot, screenshot).replaceAll("\\", "/"),
        screenshotSha256: sha256File(screenshot),
      });
    }
    await handle.evaluate((node) => { node.scrollLeft = 0; });
    if (tiles[0].coveredStart !== 0 || tiles.at(-1).coveredEnd !== metadata.scrollWidth) {
      throw new Error(`${label}: horizontal tiles do not cover both region boundaries`);
    }
    for (let index = 1; index < tiles.length; index += 1) {
      if (tiles[index].coveredStart > tiles[index - 1].coveredEnd) {
        throw new Error(`${label}: horizontal evidence gap before tile ${index + 1}`);
      }
    }
    if (new Set(tiles.map((tile) => tile.screenshotSha256)).size !== tiles.length) {
      throw new Error(`${label}: duplicate horizontal tile bytes detected`);
    }
    evidence.push({
      ...metadata,
      overlap,
      step,
      tileCount: tiles.length,
      coverageComplete: true,
      tiles,
    });
  }
  return evidence;
}

async function inspect(page, origin, label, viewport) {
  await page.setViewportSize(viewport);
  await page.goto(`${origin}/${config.html}`, { waitUntil: "networkidle" });
  const metrics = await page.evaluate(({ prefix, exercisePrefix }) => {
    const main = document.querySelector("main.content");
    if (!main) throw new Error("main.content missing");
    const rect = main.getBoundingClientRect();
    const escaped = prefix.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const exerciseIdPattern = new RegExp(`^${escaped}-${exercisePrefix}\\d{2}$`, "i");
    const guidanceIdPattern = new RegExp(`^${escaped}-H\\d{2}$`, "i");
    return {
      title: document.title,
      language: document.documentElement.lang,
      viewportWidth: window.innerWidth,
      bodyScrollWidth: document.body.scrollWidth,
      documentScrollWidth: document.documentElement.scrollWidth,
      mainLeft: Number(rect.left.toFixed(2)),
      mainWidth: Number(rect.width.toFixed(2)),
      mainRight: Number(rect.right.toFixed(2)),
      headingCount: main.querySelectorAll("h2, h3").length,
      exerciseCount: [...main.querySelectorAll("[id]")].filter((node) => exerciseIdPattern.test(node.id)).length,
      guidanceCount: [...main.querySelectorAll("[id]")].filter((node) => guidanceIdPattern.test(node.id)).length,
      imagesWithoutAlt: [...main.querySelectorAll("img")].filter(
        (node) => !node.hasAttribute("alt") || !node.getAttribute("alt").trim()
      ).length,
      skipLinks: document.querySelectorAll("a.o017-skip-link").length,
      skipTarget: (() => {
        const href = document.querySelector("a.o017-skip-link")?.getAttribute("href");
        if (!href) return null;
        const target = new URL(href, location.href);
        return `${target.pathname}${target.hash}`;
      })(),
      mathElements: main.querySelectorAll("math").length,
      invalidNavbarMenuRoles: document.querySelectorAll('button.navbar-toggler[role="menu"]').length,
      tocTitleElement: document.querySelector("#toc-title")?.tagName || null,
      tables: main.querySelectorAll("table").length,
      tableScrolls: [...main.querySelectorAll(".o017-table-scroll")].map((node, index) => ({
        regionKind: "table",
        regionIndex: index + 1,
        clientWidth: node.clientWidth,
        scrollWidth: node.scrollWidth,
        overflowX: getComputedStyle(node).overflowX,
        display: getComputedStyle(node).display,
        ariaLabel: node.getAttribute("aria-label"),
        role: node.getAttribute("role"),
        tabIndex: node.getAttribute("tabindex"),
        tableAriaLabel: node.querySelector("table")?.getAttribute("aria-label") || null,
      })),
      mathScrolls: [...main.querySelectorAll(".o017-math-scroll")].map((node, index) => ({
        regionKind: "math",
        regionIndex: index + 1,
        clientWidth: node.clientWidth,
        scrollWidth: node.scrollWidth,
        overflowX: getComputedStyle(node).overflowX,
        ariaLabel: node.getAttribute("aria-label"),
        role: node.getAttribute("role"),
        tabIndex: node.getAttribute("tabindex"),
      })),
      overflowingElements: [...document.querySelectorAll("body *")]
        .map((node) => {
          const rect = node.getBoundingClientRect();
          return {
            tag: node.tagName,
            id: node.id || null,
            className: typeof node.className === "string" ? node.className : null,
            left: Number(rect.left.toFixed(1)),
            right: Number(rect.right.toFixed(1)),
            scrollWidth: node.scrollWidth,
            clientWidth: node.clientWidth,
            text: (node.textContent || "").trim().slice(0, 90),
          };
        })
        .filter((item) => item.right > window.innerWidth + 1 || item.left < -1)
        .slice(0, 20),
      uncontainedOverflowElements: [...document.querySelectorAll("body *")]
        .filter((node) => !node.closest(".o017-table-scroll, .o017-math-scroll"))
        .map((node) => {
          const rect = node.getBoundingClientRect();
          return { tag: node.tagName, id: node.id || null, left: rect.left, right: rect.right };
        })
        .filter((item) => item.right > window.innerWidth + 1 || item.left < -1)
        .slice(0, 20),
      remoteRuntimeRequests: performance.getEntriesByType("resource")
        .map((entry) => entry.name)
        .filter((url) => !url.startsWith(location.origin + "/")),
    };
  }, { prefix: config.labelPattern, exercisePrefix: config.exercisePrefix || "X" });

  metrics.pageHorizontalScrollAfterAttempt = await page.evaluate(() => {
    window.scrollTo(99999, 0);
    const value = window.scrollX;
    window.scrollTo(0, 0);
    return value;
  });

  if (metrics.language !== "id-ID") throw new Error(`${label}: language is not id-ID`);
  if (metrics.pageHorizontalScrollAfterAttempt > 1 || metrics.uncontainedOverflowElements.length) {
    throw new Error(`${label}: uncontained page overflow ${JSON.stringify({ scrollX: metrics.pageHorizontalScrollAfterAttempt, elements: metrics.uncontainedOverflowElements })}`);
  }
  if (metrics.tableScrolls.some((table) =>
    table.overflowX !== "auto" || table.tabIndex !== "0" || !table.ariaLabel ||
    table.role !== "region" || table.tableAriaLabel !== table.ariaLabel
  )) {
    throw new Error(`${label}: table lacks an accessible named scroll region`);
  }
  if (metrics.mathScrolls.some((region) =>
    region.overflowX !== "auto" || region.tabIndex !== "0" || !region.ariaLabel ||
    region.role !== "region"
  )) {
    throw new Error(`${label}: formula lacks an accessible named scroll region`);
  }
  if (metrics.headingCount < config.minHeadings) throw new Error(`${label}: heading surface incomplete`);
  if (metrics.exerciseCount !== 6 || metrics.guidanceCount !== 6) {
    throw new Error(`${label}: exercise/guidance is ${metrics.exerciseCount}/${metrics.guidanceCount}`);
  }
  if (metrics.imagesWithoutAlt !== 0) throw new Error(`${label}: image without alt`);
  if (metrics.skipLinks !== 1 || !metrics.skipTarget.endsWith("#quarto-document-content")) {
    throw new Error(`${label}: invalid skip link`);
  }
  if (metrics.mathElements < config.minMath) throw new Error(`${label}: MathML surface incomplete`);
  if (metrics.invalidNavbarMenuRoles !== 0) throw new Error(`${label}: invalid navbar menu role`);
  if (metrics.tocTitleElement && metrics.tocTitleElement !== "DIV") throw new Error(`${label}: TOC title is heading`);
  if (metrics.remoteRuntimeRequests.length) throw new Error(`${label}: remote runtime requests`);

  const horizontalScrollEvidence = await captureHorizontalRegions(page, label);
  const visualCoverage = await captureViewportTiles(page, label, viewport);
  const firstTile = visualCoverage.tiles[0];
  return {
    ...metrics,
    screenshot: firstTile.screenshot,
    screenshotSha256: firstTile.screenshotSha256,
    horizontalScrollEvidence,
    visualCoverage,
  };
}

async function main() {
  if (!fs.existsSync(unitHtml)) throw new Error(`reader unit missing: ${unitHtml}`);
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
    const installed = [
      "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
      "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    ].find((candidate) => fs.existsSync(candidate));
    if (!installed) throw new Error("No installed Edge or Chrome executable found");
    browser = await chromium.launch({ executablePath: installed, headless: true, args: ["--disable-speech-api"] });
    const page = await browser.newPage();
    const consoleErrors = [];
    const pageErrors = [];
    page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
    page.on("pageerror", (error) => pageErrors.push(String(error)));
    const desktop = await inspect(page, origin, "desktop-1440x1000", { width: 1440, height: 1000 });
    const mobile = await inspect(page, origin, "mobile-390x844", { width: 390, height: 844 });
    if (consoleErrors.length || pageErrors.length) throw new Error(JSON.stringify({ consoleErrors, pageErrors }));
    const report = {
      schema: "o017-unit-visual-qa-v2",
      status: "PASS",
      date: "2026-08-24",
      unit_id: unitId,
      audio_widgets_exercised: false,
      unit_html_sha256: sha256File(unitHtml),
      reader_tree: readerTree(),
      visual_qa_script_sha256: sha256File(__filename),
      console_errors: consoleErrors,
      page_errors: pageErrors,
      desktop,
      mobile,
    };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");
    process.stdout.write(JSON.stringify(report) + "\n");
  } finally {
    if (browser) await Promise.race([browser.close(), new Promise((resolve) => setTimeout(resolve, 2000))]);
    server.close();
    if (typeof server.closeAllConnections === "function") server.closeAllConnections();
  }
  process.exit(0);
}

main().catch((error) => {
  process.stderr.write(String(error.stack || error) + "\n");
  process.exitCode = 1;
});
