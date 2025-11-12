import os
import pathlib
import ssl
import tempfile
import urllib.request
import asyncio
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchWindowException,
    InvalidSessionIdException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from nadf.crawler.http_client.crawler_client import CrawlerClient
from nadf.exception.ssl_invalid_exception import SSLInvalidException
from dotenv import load_dotenv

load_dotenv()

# ----- SSL 설정 (기존 유지) -----
try:
    import certifi
    _cafile = certifi.where()
    _ctx = ssl.create_default_context(cafile=_cafile)
    _opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_ctx))
    urllib.request.install_opener(_opener)
except Exception:
    raise SSLInvalidException()


def _detect_chrome_binary() -> str:
    """컨테이너 내 Chrome 바이너리 경로 자동 감지(문자열 반환)."""
    candidates = [
        os.getenv("GOOGLE_CHROME_BIN"),
        os.getenv("CHROME_BIN"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(c)
    raise RuntimeError(
        "Chrome binary not found. Set $GOOGLE_CHROME_BIN or install google-chrome-stable."
    )


def _detect_version_main(chrome_bin: str) -> Optional[int]:
    """설치된 Chrome 메이저 버전 추출 실패 시 None."""
    # 환경변수로 강제 지정 가능: CHROME_VERSION_MAIN=139
    env_val = os.getenv("CHROME_VERSION_MAIN")
    if env_val and env_val.isdigit():
        return int(env_val)

    try:
        out = subprocess.check_output([chrome_bin, "--version"], text=True).strip()
        # 예) "Google Chrome 139.0.6487.62"
        import re
        m = re.search(r"(\d+)\.", out)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def _detect_chromedriver_path() -> Optional[str]:
    """시스템에 설치된 chromedriver 경로 감지 (ARM 환경용)."""
    # 환경변수로 강제 지정 가능: CHROMEDRIVER_PATH=/usr/bin/chromedriver
    env_path = os.getenv("CHROMEDRIVER_PATH")
    if env_path and Path(env_path).exists():
        return str(env_path)

    candidates = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
    ]

    for c in candidates:
        if Path(c).exists():
            return str(c)

    return None


def _is_arm_architecture() -> bool:
    """ARM 아키텍처 여부 확인."""
    machine = platform.machine().lower()
    return "arm" in machine or "aarch64" in machine


class SeleniumClient(CrawlerClient):
    def __init__(self):
        self._exec = ThreadPoolExecutor(max_workers=1)
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            # 코루틴 밖에서 생성되면 기존 정책대로 loop를 생성/획득
            self._loop = asyncio.get_event_loop()

        self._lock = asyncio.Lock()

        def _new_driver():
            opts = uc.ChromeOptions()

            try:
                chrome_bin = _detect_chrome_binary()
            except RuntimeError as e:
                raise RuntimeError(
                    f"Chrome 바이너리를 찾을 수 없습니다: {e}\n"
                    "해결방법:\n"
                    "1. Chrome을 설치하거나\n"
                    "2. GOOGLE_CHROME_BIN 환경변수를 설정하세요."
                )
            opts.binary_location = chrome_bin

            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--disable-software-rasterizer")
            opts.add_argument("--disable-extensions")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--no-first-run")
            opts.add_argument("--no-default-browser-check")
            opts.add_argument("--remote-debugging-port=0")  # 0 = 자동으로 사용 가능한 포트 선택

            user_data_dir = tempfile.mkdtemp(prefix="uc-")
            pathlib.Path(user_data_dir).mkdir(parents=True, exist_ok=True)
            opts.add_argument(f"--user-data-dir={user_data_dir}")

            version_main = _detect_version_main(chrome_bin)
            if not version_main:
                version_main = 142  # fallback (현재 chrome 142.x)

            if _is_arm_architecture():
                driver_path = _detect_chromedriver_path()
                if driver_path:
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=opts,
                        version_main=version_main,
                    )
                else:
                    # ARM 환경에서 chromedriver가 없으면 자동 다운로드 시도
                    driver = uc.Chrome(options=opts, version_main=version_main)
            else:
                driver = uc.Chrome(options=opts, version_main=version_main)

            driver.set_page_load_timeout(40)
            driver.set_script_timeout(40)

            return driver

        self._new_driver = _new_driver
        # 최초 드라이버 비동기 생성
        self._driver_fut = self._loop.run_in_executor(self._exec, self._new_driver)

    async def _run(self, fn):
        driver = await self._driver_fut
        return await self._loop.run_in_executor(self._exec, lambda: fn(driver))

    async def _recreate_driver(self):
        def _quit_and_create(old):
            try:
                old.quit()
            except Exception:
                pass
            return self._new_driver()

        old = await self._driver_fut
        self._driver_fut = self._loop.run_in_executor(self._exec, lambda: _quit_and_create(old))
        return await self._driver_fut

    async def _ensure_alive(self):
        def _check(drv):
            try:
                _ = drv.current_window_handle
                return True
            except Exception:
                return False

        drv = await self._driver_fut
        alive = await self._loop.run_in_executor(self._exec, lambda: _check(drv))
        if not alive:
            await self._recreate_driver()

    # override
    async def get(self, url: str):
        async with self._lock:
            await self._ensure_alive()

            def _fetch(driver):
                try:
                    driver.get(url)
                except TimeoutException:
                    try:
                        driver.execute_script("window.stop();")  # 페이지 중단 후
                    except Exception:
                        pass

                html = driver.page_source
                return BeautifulSoup(html, "html.parser")

            try:
                return await self._run(_fetch)

            except (NoSuchWindowException, InvalidSessionIdException, WebDriverException):
                # 드라이버 재생성 후 한 번 재시도
                await self._recreate_driver()
                return await self._run(_fetch)

    async def close(self):
        try:
            d = await self._driver_fut
            await self._loop.run_in_executor(self._exec, d.quit)
        finally:
            self._exec.shutdown(wait=False)


if __name__ == "__main__":
    async def main():
        client = SeleniumClient()
        try:
            print("나루토 크롤링")
            soup = await client.get("https://namu.wiki/w/나루토")
            print(soup.title.text if soup.title else "(no title)")
            print(soup.text)
        finally:
            await client.close()

    asyncio.run(main())
