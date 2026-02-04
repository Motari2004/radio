import asyncio
import logging
from playwright.async_api import async_playwright
from aiohttp import web
import os

# ───────── CONFIG ─────────
UID = "1098013"
TARGET_URL = f"https://radioearn.com/radio/1/?uid={UID}"
SCREENSHOT_DELAY = 10
PORT = int(os.environ.get("PORT", 10000))

# ───────── LOGGING ─────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("RadioListener")

browser_page = None

<<<<<<< HEAD
# ───────── HELPERS ─────────
async def click_if_exists(selector):
    if not browser_page:
        return False
    el = await browser_page.query_selector(selector)
    if el:
        await el.click()
        return True
    return False

# ───────── API ROUTES ─────────
async def health_handler(request):
    return web.Response(text="OK")
=======
<<<<<<< HEAD
# ───────── HTTP ENDPOINTS ─────────
async def health_handler(request):
    return web.Response(text="OK", status=200)
=======
# ───────── HELPERS ─────────
async def click_if_exists(selector):
    if not browser_page:
        return False
    el = await browser_page.query_selector(selector)
    if el:
        await el.click()
        return True
    return False

# ───────── API ROUTES ─────────
async def health_handler(request):
    return web.Response(text="OK")
>>>>>>> a2d07a1 (Describe what you changed here)
>>>>>>> 509aebd (Describe what you changed here)

async def screenshot_handler(request):
    if not browser_page:
        return web.Response(text="Browser not ready", status=503)
    img = await browser_page.screenshot()
    return web.Response(body=img, content_type="image/png")

async def play_handler(request):
    success = await click_if_exists("#rearn .play, .play")
    return web.json_response({"status": "playing" if success else "not-found"})

async def stop_handler(request):
    success = await click_if_exists("#rearn .pause, .pause")
    return web.json_response({"status": "stopped" if success else "not-found"})

async def index_handler(request):
    return web.FileResponse("./static/index.html")

# ───────── PLAYWRIGHT BOT ─────────
async def main_bot():
    global browser_page
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 820, "height": 720})
        browser_page = page

        while True:
            try:
                logger.info("Opening RadioEarn page...")
<<<<<<< HEAD
                await page.goto(TARGET_URL, timeout=90000)
                await page.wait_for_selector("#rearn", timeout=30000)

                logger.info("Radio player detected")
                await asyncio.sleep(60)
=======
<<<<<<< HEAD
                await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=90000)

=======
                await page.goto(TARGET_URL, timeout=90000)
>>>>>>> a2d07a1 (Describe what you changed here)
                await page.wait_for_selector("#rearn", timeout=30000)

<<<<<<< HEAD
                await asyncio.sleep(SCREENSHOT_DELAY)
                screenshot_bytes = await page.screenshot()
                with open("latest_screenshot.png", "wb") as f:
                    f.write(screenshot_bytes)
                logger.info("Screenshot saved after 10s")

                while True:
                    exists = await page.query_selector("#rearn")
                    if not exists:
                        logger.warning("Radio player missing, reloading page...")
                        break
                    logger.info("Still alive, waiting 60s...")
                    await asyncio.sleep(60)
=======
                logger.info("Radio player detected")
                await asyncio.sleep(60)
>>>>>>> a2d07a1 (Describe what you changed here)
>>>>>>> 509aebd (Describe what you changed here)

            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(10)

# ───────── MAIN ─────────
async def main():
    app = web.Application()
    app.add_routes([
<<<<<<< HEAD
        web.get("/", index_handler),
        web.get("/health", health_handler),
        web.get("/screenshot", screenshot_handler),
        web.post("/play", play_handler),
        web.post("/stop", stop_handler),
=======
<<<<<<< HEAD
        web.get("/", health_handler),
        web.get("/health", health_handler),
        web.get("/screenshot", screenshot_handler)
=======
        web.get("/", index_handler),
        web.get("/health", health_handler),
        web.get("/screenshot", screenshot_handler),
        web.post("/play", play_handler),
        web.post("/stop", stop_handler),
>>>>>>> a2d07a1 (Describe what you changed here)
>>>>>>> 509aebd (Describe what you changed here)
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

<<<<<<< HEAD
    logger.info(f"Server running on http://localhost:{PORT}")
=======
<<<<<<< HEAD
    logger.info(f"HTTP server running on port {PORT}")
=======
    logger.info(f"Server running on http://localhost:{PORT}")
>>>>>>> a2d07a1 (Describe what you changed here)
>>>>>>> 509aebd (Describe what you changed here)
    await main_bot()

if __name__ == "__main__":
    asyncio.run(main())
