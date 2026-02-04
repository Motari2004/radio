import asyncio
import logging
import os
from playwright.async_api import async_playwright
from aiohttp import web

# ───────── CONFIG ─────────
UID = "1098013"
TARGET_URL = f"https://radioearn.com/radio/1/?uid={UID}"
PORT = int(os.environ.get("PORT", 10000))

# UPDATED PROXY
PROXY_SERVER = "http://198.105.121.200:6462"
PROXY_USER = "lpwhmgzq"
PROXY_PASS = "yv5yw8mh3d36"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RadioBot")

browser_page = None

# ───────── ROUTES ─────────
async def index_handler(request):
    if os.path.exists("./static/index.html"):
        return web.FileResponse("./static/index.html")
    return web.Response(text="Dashboard missing in /static/index.html", status=404)

async def health_handler(request):
    return web.Response(text="OK")

async def screenshot_handler(request):
    global browser_page
    if not browser_page:
        return web.Response(text="Browser not ready", status=503)
    try:
        # Quality 50 is the 'sweet spot' for speed vs clarity
        img = await browser_page.screenshot(type="jpeg", quality=50)
        return web.Response(body=img, content_type="image/jpeg")
    except Exception as e:
        return web.Response(text=str(e), status=500)

async def play_handler(request):
    if browser_page:
        await browser_page.evaluate('document.getElementById("rearn").play()')
        return web.json_response({"status": "playing"})
    return web.json_response({"status": "error"}, status=503)

async def stop_handler(request):
    if browser_page:
        await browser_page.evaluate('document.getElementById("rearn").pause()')
        return web.json_response({"status": "stopped"})
    return web.json_response({"status": "error"}, status=503)

# ───────── BOT LOGIC ─────────
async def run_radio_bot():
    global browser_page
    async with async_playwright() as p:
        logger.info(f"Starting browser with proxy: {PROXY_SERVER}")
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": PROXY_SERVER, "username": PROXY_USER, "password": PROXY_PASS},
            args=["--no-sandbox", "--disable-dev-shm-usage", "--autoplay-policy=no-user-gesture-required"]
        )
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        await page.set_viewport_size({"width": 1024, "height": 768})
        browser_page = page

        while True:
            try:
                logger.info(f"Navigating to {TARGET_URL}")
                await page.goto(TARGET_URL, wait_until="load", timeout=60000)
                
                # Check for audio and attempt start
                await page.wait_for_selector("#rearn", timeout=15000)
                await page.evaluate('document.getElementById("rearn").play()')
                
                logger.info("Bot is active. Maintaining session...")
                await asyncio.sleep(600) # Stay on page 10 mins
            except Exception as e:
                logger.error(f"Bot Error: {e}")
                await asyncio.sleep(30)

# ───────── SERVER START ─────────
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
    logger.info(f"Web dashboard running on port {PORT}")

    await run_radio_bot()

if __name__ == "__main__":
    asyncio.run(main())