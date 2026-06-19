import asyncio
import atexit
import os
import re
import signal
from typing import Optional

from playwright.async_api import async_playwright, Browser, Playwright
from nonebot import get_driver
from .basic_method import file_path

_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None
_lock = asyncio.Lock()
_shutting_down = False


async def init_browser():
    global _playwright, _browser
    async with _lock:
        if _browser is not None:
            return
        _playwright = await async_playwright().start()
        _browser = await _playwright.firefox.launch(
        headless=True,
        firefox_user_prefs={
            'javascript.options.mem.max': 256,  # 限制JS内存为256MB[reference:14]
            'dom.ipc.processCount': 1,          # 减少进程数[reference:15]
        }
    )


async def shutdown_browser():
    global _playwright, _browser, _shutting_down
    if _shutting_down:
        return
    _shutting_down = True
    try:
        async with _lock:
            if _browser:
                try:
                    await _browser.close()
                except Exception as e:
                    # 连接已关闭或浏览器不可用，忽略
                    pass
                _browser = None
            if _playwright:
                try:
                    await _playwright.stop()
                except Exception as e:
                    pass
                _playwright = None
    finally:
        _shutting_down = False


async def html_to_png(html: str, width: int = 800, height: int = 600) -> bytes:
    if os.path.exists(file_path/html):
        with open(file_path/html, 'r', encoding='utf-8') as f:
            html = f.read()
    elif os.path.exists(html):
        with open(html, 'r', encoding='utf-8') as f:
            html = f.read()

    url_pattern = re.compile(r'^https?://', re.IGNORECASE)
    is_url = bool(url_pattern.match(html.strip()))
    if _browser is None:
        raise RuntimeError("Browser not initialized")
    page = await _browser.new_page(viewport={"width": width, "height": height})
    try:
        if is_url:
            try:
                await page.goto(html, wait_until="networkidle",timeout=3000)
            except:
                try:
                    await page.goto(html,wait_until="load",timeout=3000)
                except:
                    await page.goto(html,wait_until="domcontentloaded")
        else:
            await page.set_content(html, wait_until="networkidle")
        return await page.screenshot(full_page=True, type="png")
    finally:
        await page.close()


# ----- NoneBot 生命周期钩子 -----
driver = get_driver()

@driver.on_startup
async def _startup():
    await init_browser()
    # 信号处理器：解决 reload 强制杀进程问题
    def _sigterm_handler():
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(shutdown_browser())
        else:
            loop.run_until_complete(shutdown_browser())
        import sys
        sys.exit(0)
    signal.signal(signal.SIGTERM, lambda s, f: _sigterm_handler())

@driver.on_shutdown
async def _shutdown():
    await shutdown_browser()


# ----- atexit 保底清理 -----
def _atexit_cleanup():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(shutdown_browser())
    except Exception:
        pass

atexit.register(_atexit_cleanup)