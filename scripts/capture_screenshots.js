const puppeteer = require("puppeteer-core");
const path = require("path");
const fs = require("fs");

const CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const OUTPUT_DIR = path.resolve(__dirname, "../assets/screenshots");

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function run() {
  console.log("Launching headless Chrome...");
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: "new",
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--window-size=390,844",
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({
    width: 390,
    height: 844,
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
  });

  console.log("Navigating to http://127.0.0.1:8765...");
  await page.goto("http://127.0.0.1:8765", { waitUntil: "networkidle0" });

  // Wait for WebSocket connection
  console.log("Waiting for app initialization...");
  await sleep(2500);

  // Helper to click bottom tab by text label
  async function clickBottomTab(label) {
    console.log(`Clicking tab: ${label}`);
    await page.evaluate((lbl) => {
      const buttons = Array.from(document.querySelectorAll("nav.tab-bar button"));
      const btn = buttons.find((b) => b.textContent.includes(lbl));
      if (btn) btn.click();
    }, label);
    await sleep(800);
  }

  // Helper to click sub-tab inside TOOLS
  async function clickSubTab(label) {
    console.log(`Clicking sub-tab: ${label}`);
    await page.evaluate((lbl) => {
      const buttons = Array.from(document.querySelectorAll("main button"));
      const btn = buttons.find((b) => b.textContent.trim() === lbl);
      if (btn) btn.click();
    }, label);
    await sleep(800);
  }

  // 1. PAD (Touchpad)
  console.log("Capturing 01-touchpad.png...");
  await clickBottomTab("PAD");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "01-touchpad.png") });

  // 2. KEYS (Keyboard)
  console.log("Capturing 02-keyboard.png...");
  await clickBottomTab("KEYS");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "02-keyboard.png") });

  // 3. STRM (Screen Stream)
  console.log("Capturing 03-stream.png...");
  await clickBottomTab("STRM");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "03-stream.png") });

  // 4. TOOLS -> APPS
  console.log("Navigating to TOOLS...");
  await clickBottomTab("TOOLS");
  await clickSubTab("APPS");
  await sleep(1000);
  console.log("Capturing 04-apps.png...");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "04-apps.png") });

  // 5. TOOLS -> MEDIA
  await clickSubTab("MEDIA");
  await sleep(800);
  console.log("Capturing 05-media.png...");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "05-media.png") });

  // 6. TOOLS -> SHELL (Terminal)
  await clickSubTab("SHELL");
  await sleep(800);
  // Type a sample command into the terminal input
  try {
    const inputSelector = "input[placeholder*='command' i], input[type='text']";
    const input = await page.$(inputSelector);
    if (input) {
      await input.type("uname -sm");
      await page.keyboard.press("Enter");
      await sleep(1200);
    }
  } catch (err) {
    console.warn("Could not type command:", err.message);
  }
  console.log("Capturing 06-terminal.png...");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "06-terminal.png") });

  // 7. TOOLS -> PROC (Process Manager)
  await clickSubTab("PROC");
  await sleep(1500); // allow psutil list to load
  console.log("Capturing 07-processes.png...");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "07-processes.png") });

  // 8. TOOLS -> FS (File Browser)
  await clickSubTab("FS");
  await sleep(1200); // allow filesystem entries to load
  console.log("Capturing 08-files.png...");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "08-files.png") });

  // 9. TOOLS -> SRCH (Google Search & Quick URLs)
  await clickSubTab("SRCH");
  await sleep(800);
  console.log("Capturing 09-search.png...");
  await page.screenshot({ path: path.join(OUTPUT_DIR, "09-search.png") });

  // 10. SYS (Power Controls)
  console.log("Capturing 10-power.png...");
  await clickBottomTab("SYS");
  await sleep(800);
  await page.screenshot({ path: path.join(OUTPUT_DIR, "10-power.png") });

  await browser.close();
  console.log("All screenshots captured successfully!");
}

run().catch((err) => {
  console.error("Error capturing screenshots:", err);
  process.exit(1);
});
