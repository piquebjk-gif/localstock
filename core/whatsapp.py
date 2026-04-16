# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - WhatsApp Modülü
Playwright ile WhatsApp Web otomasyonu.
Timeout: 300 saniye, pane-side/chat-list selector desteği.
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
SESSION_DIZINI = BASE_DIR / "data" / "whatsapp_session"


class WhatsApp:
    def __init__(self, brain):
        self.brain = brain
        self._browser = None
        self._context = None
        self._page = None
        self._bagli = False
        self._dinleme_aktif = False
        self._kilit = threading.Lock()

    # ── Bağlantı ──────────────────────────────────────────────────────────────

    def baglan(self, headless: bool = False) -> bool:
        """
        WhatsApp Web'e Playwright ile bağlan.
        Timeout 300 saniye, QR kod beklenir.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright kurulu değil. WhatsApp simülasyon modu.")
            self._bagli = True
            self.brain.platform_durumu_guncelle("whatsapp", True)
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
                args=["--no-sandbox", "--disable-dev-shm-usage"],
                timeout=10000
            )

            self._page = self._browser.new_page()
            self._page.goto("https://web.whatsapp.com", timeout=30000)

            logger.info("WhatsApp Web yükleniyor, QR bekleniyor (max 300 sn)...")

            # pane-side veya chat-list selector bekle
            try:
                self._page.wait_for_selector(
                    "#pane-side, [data-testid='chat-list']",
                    timeout=300000  # 300 saniye
                )
                self._bagli = True
                self.brain.platform_durumu_guncelle("whatsapp", True)
                logger.info("WhatsApp Web bağlandı")
                return True
            except Exception:
                logger.error("WhatsApp QR tarama zaman aşımı (300 sn)")
                self.baglantiyi_kes()
                return False

        except Exception as e:
            logger.error(f"WhatsApp bağlantı hatası: {e}")
            self.brain.platform_durumu_guncelle("whatsapp", False)
            return False

    def baglantiyi_kes(self):
        self._bagli = False
        self._dinleme_aktif = False
        try:
            if self._browser:
                self._browser.close()
            if hasattr(self, "_pw") and self._pw:
                self._pw.stop()
        except Exception:
            pass
        self.brain.platform_durumu_guncelle("whatsapp", False)
        logger.info("WhatsApp bağlantısı kesildi")

    # ── Mesaj İşlemleri ───────────────────────────────────────────────────────

    def mesaj_gonder(self, telefon: str, mesaj: str) -> bool:
        """
        Telefon numarasına mesaj gönder.
        telefon: "905XXXXXXXXX" formatında
        """
        if not self._bagli:
            return False
        if not self._page:
            logger.info(f"[Sim] WhatsApp → {telefon}: {mesaj[:50]}")
            return True
        try:
            url = f"https://web.whatsapp.com/send?phone={telefon}&text={mesaj}"
            self._page.goto(url, timeout=30000)
            self._page.wait_for_selector(
                "[data-testid='conversation-compose-box-input']",
                timeout=15000
            )
            time.sleep(1)
            self._page.keyboard.press("Enter")
            time.sleep(2)
            logger.info(f"WhatsApp mesaj gönderildi → {telefon}")
            return True
        except Exception as e:
            logger.error(f"WhatsApp mesaj gönderilemedi: {e}")
            return False

    def yeni_mesajlar_al(self) -> list:
        """Açık sohbetteki okunmamış mesajları al."""
        if not self._bagli or not self._page:
            return []
        try:
            # Okunmamış sohbet sayısı
            try:
                self._page.goto("https://web.whatsapp.com", timeout=15000)
                self._page.wait_for_selector(
                    "#pane-side, [data-testid='chat-list']",
                    timeout=10000
                )
            except Exception:
                return []

            mesajlar = []
            # Okunmamış işaretli konuşmaları bul
            try:
                okunmamis = self._page.query_selector_all(
                    "[data-testid='cell-frame-container'] "
                    "[data-testid='icon-unread-count']"
                )
                for elem in okunmamis[:5]:
                    try:
                        parent = elem.evaluate_handle(
                            "el => el.closest('[data-testid=\"cell-frame-container\"]')"
                        )
                        parent.click()
                        time.sleep(1)
                        son_mesaj = self._page.query_selector_all(
                            "[data-testid='msg-container'] .copyable-text"
                        )
                        if son_mesaj:
                            metin = son_mesaj[-1].inner_text()
                            mesajlar.append({
                                "metin": metin,
                                "zaman": datetime.now().isoformat()
                            })
                    except Exception:
                        continue
            except Exception:
                pass

            return mesajlar
        except Exception as e:
            logger.error(f"WhatsApp mesaj alma hatası: {e}")
            return []

    # ── Otomasyon ─────────────────────────────────────────────────────────────

    def otomasyon_baslat(self, yanit_islevi):
        self._dinleme_aktif = True
        t = threading.Thread(
            target=self._otomasyon_dongusu,
            args=(yanit_islevi,),
            daemon=True
        )
        t.start()
        logger.info("WhatsApp otomasyon başlatıldı")

    def otomasyon_durdur(self):
        self._dinleme_aktif = False

    def _otomasyon_dongusu(self, yanit_islevi):
        while self._dinleme_aktif:
            try:
                mesajlar = self.yeni_mesajlar_al()
                for m in mesajlar:
                    yanit = yanit_islevi(
                        m["metin"],
                        kullanici_id="wa_user",
                        platform="whatsapp"
                    )
                    # Yanıt gönderme burada uygulanabilir
                interval = self.brain.ayar_al(
                    "zamanlama", "dm_kontrol_suresi", varsayilan=60
                )
                time.sleep(interval)
            except Exception as e:
                logger.error(f"WhatsApp otomasyon hatası: {e}")
                time.sleep(30)

    @property
    def bagli(self) -> bool:
        return self._bagli
