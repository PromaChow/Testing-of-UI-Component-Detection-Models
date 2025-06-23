const fs = require("fs").promises;
const path = require("path");
const puppeteer = require("puppeteer");
const { createServer } = require("./server");

class HtmlConverter {
  constructor(options = {}) {
    this.options = {
      inputDir: path.resolve("./input"),
      outputDir: path.resolve("./output"),
      imageFormat: "png",
      quality: 100,
      scale: 2,
      port: 3000,
      ...options,
    };
    this.server = null;
    this.browser = null;
    this.page = null;
  }

  async initialize(width, height) {
    try {
      await fs.mkdir(this.options.outputDir, { recursive: true });
      this.server = await createServer(this.options);

      this.browser = await puppeteer.launch({
        headless: "new",
        args: [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-web-security",
          "--disable-cors",
          "--disable-features=IsolateOrigins",
          "--disable-site-isolation-trials",
          "--allow-file-access-from-files",
          "--allow-file-access",
          "--allow-cross-origin-auth-prompt",
          "--disable-web-security",
          "--disable-features=IsolateOrigins,site-per-process",
          "--disable-dev-shm-usage",
        ],
      });

      this.page = await this.initializePage(width, height);
    } catch (error) {
      console.error("Initialization error:", error);
      throw error;
    }
  }

  async initializePage(width, height) {
    const page = await this.browser.newPage();
    await page.setBypassCSP(true);
    await page.setViewport({
      width,
      height,
      deviceScaleFactor: this.options.scale,
    });

    await page.setExtraHTTPHeaders({
      Accept: "*/*",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "*",
    });

    await page.setRequestInterception(true);
    this.setupPageListeners(page);

    return page;
  }

  setupPageListeners(page) {
    page.on("request", (request) => {
      const headers = request.headers();
      headers["Access-Control-Allow-Origin"] = "*";
      request.continue({ headers });
    });

    page.on("console", (msg) => console.log("Browser:", msg.text()));
    page.on("pageerror", (err) => console.error("Page error:", err));
    page.on("response", (response) => {
      if (!response.ok()) {
        console.log(`Failed to load: ${response.url()} (${response.status()})`);
      }
    });
  }

  async processFile(filePath) {
    const fileName = path.basename(filePath);
    const relativeDir = path.relative(
      this.options.inputDir,
      path.dirname(filePath)
    );
    const outputPath = path.join(
      this.options.outputDir,
      `${path.parse(fileName).name}.${this.options.imageFormat}`
    );

    try {
      const htmlContent = await this.prepareHtmlContent(filePath, relativeDir);
      const fileUrl = `file://${path.resolve(filePath)}`;
      console.log(`\nProcessing: ${fileUrl}`);

      await this.loadPage(fileUrl);
      await this.takeScreenshot(outputPath);
    } catch (error) {
      console.error(`✗ Error processing ${fileName}:`, error.message);
    }
  }

  async prepareHtmlContent(filePath, relativeDir) {
    let htmlContent = await fs.readFile(filePath, "utf-8");
    return htmlContent.replace(
      /(src|href)=(["'])((?!http|\/).+?)(["'])/g,
      (match, attr, quote, url, endQuote) => {
        const absoluteUrl = path.join("/", relativeDir, url);
        return `${attr}=${quote}${absoluteUrl}${endQuote}`;
      }
    );
  }

  async loadPage(url) {
    await this.page.goto(url, {
      waitUntil: ["load", "networkidle0"],
      timeout: 30000,
    });

    await this.page.evaluate(async () => {
      await Promise.all([
        document.fonts.ready,
        ...Array.from(document.images)
          .filter((img) => !img.complete)
          .map(
            (img) =>
              new Promise((resolve) => {
                img.onload = img.onerror = resolve;
              })
          ),
      ]);
    });
  }

  async takeScreenshot(outputPath) {
    const screenshotOptions = {
      path: outputPath,
      fullPage: true,
      type: this.options.imageFormat,
    };

    if (this.options.imageFormat === "jpeg") {
      screenshotOptions.quality = this.options.quality;
    }

    await this.page.screenshot(screenshotOptions);
    console.log(`✓ Saved screenshot: ${outputPath}`);
  }

  async processDirectory(width, height) {
    try {
      const files = await fs.readdir(this.options.inputDir);
      const htmlFiles = files.filter((file) =>
        file.toLowerCase().endsWith(".html")
      );

      if (htmlFiles.length === 0) {
        console.log("No HTML files found in input directory");
        return;
      }

      console.log(`Found ${htmlFiles.length} HTML files to process`);

      for (const file of htmlFiles) {
        const filePath = path.join(this.options.inputDir, file);
        await this.processFile(filePath);
      }
    } catch (error) {
      console.error("Error processing directory:", error);
      throw error;
    }
  }

  async close() {
    try {
      if (this.browser) await this.browser.close();
      if (this.server)
        await new Promise((resolve) => this.server.close(resolve));
    } catch (error) {
      console.error("Error closing resources:", error);
    }
  }
}

module.exports = HtmlConverter;
