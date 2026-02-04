import asyncio
import logging
import os
from playwright.async_api import async_playwright
from aiohttp import web

# ───────── CONFIG ─────────
UID = "1098013"
TARGET_URL = f"https://radioearn.com/radio/1/?uid={UID}"
PORT = int(os.environ.get("PORT", 10000))

# ───────── UPDATED PROXY ─────────
PROXY_SERVER = "http://198.105.121.200:6462"
PROXY_USER = "lpwhmgzq"
PROXY_PASS = "yv5yw8mh3d36"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RadioListener")

browser_page = None

# ───────── HELPERS ─────────
async def control_audio(action):
    global browser_page
    if not browser_page:
        return False
    try:
        if action == "play":
            # Direct JS execution to bypass autoplay blocks
            await browser_page.evaluate('document.getElementById("rearn").play()')
        else:
            await browser_page.evaluate('document.getElementById("rearn").pause()')
        return True
    except Exception as e:
        logger.error(f"Audio control error ({action}): {e}")
        return False

# ───────── API ROUTES ─────────
async def index_handler(request):
    # Serves the dashboard
    if os.path.exists("./static/index.html"):
        return web.FileResponse("./static/index.html")
    return web.Response(text="Frontend missing in /static/index.html", status=404)

async def health_handler(request):
    return web.Response(text="OK")

async def screenshot_handler(request):
    if not browser_page:
        return web.Response(text="Browser not ready", status=503)
    img = await browser_page.screenshot()
    return web.Response(body=img, content_type="image/png")

async def play_handler(request):
    success = await control_audio("play")
    return web.json_response({"status": "playing" if success else "error"})

async def stop_handler(request):
    success = await control_audio("stop")
    return web.json_response({"status": "stopped" if success else "error"})

# ───────── PLAYWRIGHT BOT ─────────
async def main_bot():
    global browser_page
    async with async_playwright() as p:
        logger.info(f"Launching browser with Proxy: {PROXY_SERVER}")
        
        browser = await p.chromium.launch(
            headless=True,
            proxy={
                "server": PROXY_SERVER,
                "username": PROXY_USER,
                "password": PROXY_PASS
            },
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--autoplay-policy=no-user-gesture-required" # Critical for auto-play
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        await page.set_viewport_size({"width": 1024, "height": 768})
        browser_page = page

        while True:
            try:
                logger.info(f"Opening {TARGET_URL}")
                await page.goto(TARGET_URL, timeout=60000, wait_until="networkidle")
                
                # Wait for audio element and attempt auto-play
                await page.wait_for_selector("#rearn", timeout=10000)
                await control_audio("play")
                
                logger.info("Bot is active and playing.")
                await asyncio.sleep(600) # Stay on page for 10 mins
            except Exception as e:
                logger.error(f"Loop Error: {e}")
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
    logger.info(f"Web Server active on port {PORT}")

    await main_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass