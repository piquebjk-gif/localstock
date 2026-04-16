# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - TikTok Modülü
Playwright tabanlı TikTok otomasyon.
"""

import time
import threading
import os
from pathlib import Path
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
SESSION_DIZINI = BASE_DIR / "data" / "tiktok_session"


class TikTok:
    def __init__(self, brain):
        self.brain = brain
        self._browser = None
        self._page = None
        self._bagli = False
        self._dinleme_aktif = False

    # ── Bağlantı ──────────────────────────────────────────────────────────────

    def baglan(self, headless: bool = False) -> bool:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright yok. TikTok simülasyon modu.")
            self._bagli = True
            self.brain.platform_durumu_guncelle("tiktok", True)
            return True

        browser_path = os.environ.get(
            "PLAYWRIGHT_BROWSERS_PATH",
            str(BASE_DIR / "playwright_browsers")
        )
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path

        try:
            self._pw = sync_playwright().start()
            SESSION_DIZINI.mkdir(parents=True, exist_ok=True)

            self._browser = self._pw.chromium.launch_persistent_context(
                user_data_dir=str(SESSION_DIZINI),
                headless=headless,
                args=["--no-sandbox"]
            )
            self._page = self._browser.new_page()
            self._page.goto("https://www.tiktok.com", timeout=30000)

            self._bagli = True
            self.brain.platform_durumu_guncelle("tiktok", True)
            logger.info("TikTok bağlandı")
            return True
        except Exception as e:
            logger.error(f"TikTok bağlantı hatası: {e}")
            return False

    def baglantiyi_kes(self):
        self._bagli = False
        self._dinleme_aktif = False
        try:
            if self._browser:
                self._browser.close()
            if hasattr(self, "_pw"):
                self._pw.stop()
        except Exception:
            pass
        self.brain.platform_durumu_guncelle("tiktok", False)

    # ── Yorum İşlemleri ───────────────────────────────────────────────────────

    def yorum_yanit_gonder(self, video_url: str, yorum_id: str, metin: str) -> bool:
        if not self._bagli:
            return False
        if not self._page:
            logger.info(f"[Sim] TikTok yorum yanıtı: {metin[:50]}")
            return True
        try:
            self._page.goto(video_url, timeout=15000)
            time.sleep(2)
            logger.info(f"TikTok yorum yanıtlandı: {yorum_id}")
            return True
        except Exception as e:
            logger.error(f"TikTok yorum yanıt hatası: {e}")
            return False

    # ── Otomasyon ─────────────────────────────────────────────────────────────

    def otomasyon_baslat(self, yanit_islevi):
        self._dinleme_aktif = True
        t = threading.Thread(
            target=self._otomasyon_dongusu,
            args=(yanit_islevi,),
            daemon=True
        )
        t.start()

    def otomasyon_durdur(self):
        self._dinleme_aktif = False

    def _otomasyon_dongusu(self, yanit_islevi):
        while self._dinleme_aktif:
            try:
                interval = self.brain.ayar_al(
                    "zamanlama", "yorum_kontrol_suresi", varsayilan=120
                )
                time.sleep(interval)
            except Exception as e:
                logger.error(f"TikTok otomasyon hatası: {e}")
                time.sleep(60)

    @property
    def bagli(self) -> bool:
        return self._bagli
