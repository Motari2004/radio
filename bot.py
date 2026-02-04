import asyncio
import logging
from playwright.async_api import async_playwright
from aiohttp import web
import os

# ───────── CONFIG ─────────
UID = "1098013"
TARGET_URL = f"https://radioearn.com/radio/1/?uid={UID}"
SCREENSHOT_DELAY = 10  # seconds
PORT = int(os.environ.get("PORT", 10000))

# ───────── LOGGING SETUP ─────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("radio_listener.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RadioListener")

# ───────── GLOBAL PAGE OBJECT ─────────
browser_page = None

# ───────── HTTP ENDPOINTS ─────────
async def health_handler(request):
    return web.Response(text="OK", status=200)

async def screenshot_handler(request):
    if not browser_page:
        return web.Response(text="Browser not ready", status=503)
    try:
        screenshot_bytes = await browser_page.screenshot()
        return web.Response(body=screenshot_bytes, content_type="image/png")
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return web.Response(text="Error taking screenshot", status=500)

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
                await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=90000)

                await page.wait_for_selector("#rearn", timeout=30000)
                logger.info("Radio player detected, heartbeat active")

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

            except Exception as e:
                logger.error(f"Error: {str(e)[:50]} → retrying in 10s")
                await asyncio.sleep(10)
                try:
                    await page.reload(wait_until="domcontentloaded")
                except:
                    logger.error("Reload failed, restarting browser...")
                    await browser.close()
                    return await main_bot()

# ───────── RUN BOTH BOT + HTTP SERVER ─────────
async def main():
    app = web.Application()
    app.add_routes([
        web.get("/", health_handler),
        web.get("/health", health_handler),
        web.get("/screenshot", screenshot_handler)
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info(f"HTTP server running on port {PORT}")
    await main_bot()

if __name__ == "__main__":
    asyncio.run(main())