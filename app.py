import asyncio
import logging
from playwright.async_api import async_playwright
from aiohttp import web
import os

# ───────── CONFIG ─────────
UID = "1098013"
TARGET_URL = f"https://radioearn.com/radio/1/?uid={UID}"
PORT = int(os.environ.get("PORT", 10000))

# PROXY CREDENTIALS
PROXY_SERVER = "http://107.172.163.27:6543"
PROXY_USER = "lpwhmgzq"
PROXY_PASS = "yv5yw8mh3d36"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RadioListener")

browser_page = None

# ───────── HELPERS ─────────
async def click_if_exists(selector):
    global browser_page
    if not browser_page: return False
    try:
        el = await browser_page.query_selector(selector)
        if el:
            await el.click()
            return True
    except Exception as e:
        logger.error(f"Click error: {e}")
    return False

# ───────── API ROUTES ─────────
async def health_handler(request):
    return web.Response(text="OK")

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
    if os.path.exists("./static/index.html"):
        return web.FileResponse("./static/index.html")
    return web.Response(text="Frontend file missing", status=404)

# ───────── PLAYWRIGHT BOT ─────────
async def main_bot():
    global browser_page
    async with async_playwright() as p:
        logger.info("Launching Chromium with Proxy...")
        browser = await p.chromium.launch(
            headless=True,
            proxy={
                "server": PROXY_SERVER,
                "username": PROXY_USER,
                "password": PROXY_PASS
            },
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        
        # Use a real user agent to avoid bot detection
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        browser_page = page

        while True:
            try:
                logger.info(f"Navigating to {TARGET_URL}")
                await page.goto(TARGET_URL, timeout=60000, wait_until="load")
                
                # Check for the play button after loading
                await asyncio.sleep(10) 
                await click_if_exists("#rearn .play, .play")
                
                logger.info("Page loaded. Staying active...")
                await asyncio.sleep(300) # Wait 5 minutes before checking again
            except Exception as e:
                logger.error(f"Bot Loop Error: {e}")
                await asyncio.sleep(20)

# ───────── MAIN ─────────
async def main():
    app = web.Application()
    app.add_routes([
        web.get("/", index_handler),
        web.get("/health", health_handler),
        web.get("/screenshot", screenshot_handler),
        web.post("/play", play_handler),
        web.post("/stop", stop_handler),
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Server running on port {PORT}")

    await main_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass