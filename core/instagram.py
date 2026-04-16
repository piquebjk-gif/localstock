# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Instagram Modülü
Cookie tabanlı giriş, DM okuma/gönderme, yorum yönetimi, story.
"""

import json
import time
import random
import threading
from pathlib import Path
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired
    INSTAGRAPI_MEVCUT = True
except ImportError:
    INSTAGRAPI_MEVCUT = False
    logger.warning("instagrapi kurulu değil. Simülasyon modunda çalışıyor.")

BASE_DIR = Path(__file__).parent.parent
COOKIE_DOSYASI = BASE_DIR / "data" / "instagram_cookies.json"
SESSION_DOSYASI = BASE_DIR / "data" / "instagram_session.json"


class Instagram:
    def __init__(self, brain):
        self.brain = brain
        self._client = None
        self._bagli = False
        self._kilit = threading.Lock()
        self._kullanici_adi = ""
        self._dinleme_aktif = False

    # ── Bağlantı ──────────────────────────────────────────────────────────────

    def baglan(self, kullanici_adi: str = "", sifre: str = "") -> bool:
        """
        Cookie tabanlı giriş öncelikli, yoksa kullanıcı adı/şifre ile giriş.
        """
        if not INSTAGRAPI_MEVCUT:
            logger.warning("Instagram: instagrapi yok, simülasyon modu")
            self._bagli = True
            self.brain.platform_durumu_guncelle("instagram", True)
            return True

        # Ayarlardan al
        if not kullanici_adi:
            kullanici_adi = self.brain.ayar_al("instagram", "kullanici_adi", varsayilan="")
        if not sifre:
            sifre = self.brain.ayar_al("instagram", "sifre", varsayilan="")

        self._kullanici_adi = kullanici_adi

        try:
            self._client = Client()
            self._client.delay_range = [2, 5]

            # Proxy ayarı
            proxy = self.brain.ayar_al("instagram", "proxy", varsayilan="")
            if proxy:
                self._client.set_proxy(proxy)

            # Önce session dosyasından dene
            if SESSION_DOSYASI.exists():
                try:
                    self._client.load_settings(str(SESSION_DOSYASI))
                    self._client.login(kullanici_adi, sifre)
                    self._bagli = True
                    logger.info(f"Instagram: Session ile giriş yapıldı - {kullanici_adi}")
                    self.brain.platform_durumu_guncelle("instagram", True)
                    return True
                except Exception as e:
                    logger.warning(f"Instagram: Session geçersiz, yeniden giriş: {e}")

            # Normal giriş
            self._client.login(kullanici_adi, sifre)
            self._client.dump_settings(str(SESSION_DOSYASI))
            self._bagli = True
            logger.info(f"Instagram: Giriş başarılı - {kullanici_adi}")
            self.brain.platform_durumu_guncelle("instagram", True)
            return True

        except TwoFactorRequired:
            logger.error("Instagram: 2FA gerekli")
            return False
        except ChallengeRequired:
            logger.error("Instagram: Challenge gerekli (IP kara liste olabilir)")
            return False
        except Exception as e:
            logger.error(f"Instagram bağlantı hatası: {e}")
            self.brain.platform_durumu_guncelle("instagram", False)
            return False

    def tarayici_ile_cookie_kaydet(self):
        """
        Playwright ile Instagram'a giriş yapıp cookie kaydet.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("Playwright kurulu değil")
            return False

        import os
        browser_path = os.environ.get(
            "PLAYWRIGHT_BROWSERS_PATH",
            str(BASE_DIR / "playwright_browsers")
        )
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path

        kullanici_adi = self.brain.ayar_al("instagram", "kullanici_adi", varsayilan="")
        sifre = self.brain.ayar_al("instagram", "sifre", varsayilan="")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                page.goto("https://www.instagram.com/accounts/login/")
                page.wait_for_selector("input[name='username']", timeout=15000)
                page.fill("input[name='username']", kullanici_adi)
                page.fill("input[name='password']", sifre)
                page.click("button[type='submit']")
                page.wait_for_url("https://www.instagram.com/", timeout=30000)

                cookies = context.cookies()
                COOKIE_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
                with open(COOKIE_DOSYASI, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)

                browser.close()
                logger.info("Instagram: Cookie kaydedildi")
                return True
        except Exception as e:
            logger.error(f"Cookie kaydetme hatası: {e}")
            return False

    def baglantiyi_kes(self):
        self._bagli = False
        self._dinleme_aktif = False
        self.brain.platform_durumu_guncelle("instagram", False)
        logger.info("Instagram bağlantısı kesildi")

    # ── DM İşlemleri ─────────────────────────────────────────────────────────

    def dm_listesi_al(self, limit: int = 20) -> list:
        if not self._bagli:
            return []
        if not INSTAGRAPI_MEVCUT or not self._client:
            return self._ornek_dm_listesi()
        try:
            threads = self._client.direct_threads(amount=limit)
            result = []
            for t in threads:
                for m in t.messages[:1]:
                    result.append({
                        "thread_id": str(t.id),
                        "kullanici": t.users[0].username if t.users else "?",
                        "mesaj": m.text or "",
                        "zaman": m.timestamp.isoformat() if m.timestamp else "",
                        "okundu": not t.unread_count
                    })
            return result
        except Exception as e:
            logger.error(f"DM listesi alınamadı: {e}")
            return []

    def dm_gonder(self, kullanici_id: str, mesaj: str) -> bool:
        if not self._bagli:
            return False
        if not INSTAGRAPI_MEVCUT or not self._client:
            logger.info(f"[Sim] Instagram DM → {kullanici_id}: {mesaj[:50]}")
            return True
        try:
            gecikme = random.uniform(2, 8)
            time.sleep(gecikme)
            self._client.direct_send(mesaj, user_ids=[int(kullanici_id)])
            logger.info(f"Instagram DM gönderildi → {kullanici_id}")
            return True
        except Exception as e:
            logger.error(f"DM gönderilemedi: {e}")
            return False

    def dm_yanit_gonder(self, thread_id: str, mesaj: str) -> bool:
        if not self._bagli:
            return False
        if not INSTAGRAPI_MEVCUT or not self._client:
            logger.info(f"[Sim] Instagram thread yanıt → {thread_id}: {mesaj[:50]}")
            return True
        try:
            gecikme = random.uniform(2, 8)
            time.sleep(gecikme)
            self._client.direct_answer(thread_id, mesaj)
            logger.info(f"Instagram DM yanıtlandı → thread:{thread_id}")
            return True
        except Exception as e:
            logger.error(f"DM yanıtlanamadı: {e}")
            return False

    # ── Yorum İşlemleri ───────────────────────────────────────────────────────

    def yorumlar_al(self, post_id: str, limit: int = 50) -> list:
        if not self._bagli:
            return []
        if not INSTAGRAPI_MEVCUT or not self._client:
            return []
        try:
            yorumlar = self._client.media_comments(post_id, amount=limit)
            return [
                {
                    "id": str(y.pk),
                    "kullanici": y.user.username,
                    "metin": y.text,
                    "zaman": y.created_at_utc.isoformat() if y.created_at_utc else ""
                }
                for y in yorumlar
            ]
        except Exception as e:
            logger.error(f"Yorumlar alınamadı: {e}")
            return []

    def yorum_yanit_gonder(self, media_id: str, yorum_id: str, metin: str) -> bool:
        if not self._bagli:
            return False
        if not INSTAGRAPI_MEVCUT or not self._client:
            logger.info(f"[Sim] Instagram yorum yanıtı → {yorum_id}: {metin[:50]}")
            return True
        try:
            gecikme = random.uniform(3, 10)
            time.sleep(gecikme)
            self._client.media_comment(media_id, f"@{yorum_id} {metin}")
            return True
        except Exception as e:
            logger.error(f"Yorum yanıtlanamadı: {e}")
            return False

    def gonderi_listesi_al(self, limit: int = 12) -> list:
        if not self._bagli or not INSTAGRAPI_MEVCUT or not self._client:
            return []
        try:
            medyalar = self._client.user_medias(
                self._client.user_id, amount=limit
            )
            return [
                {
                    "id": str(m.pk),
                    "tip": str(m.media_type),
                    "begeni": m.like_count,
                    "yorum": m.comment_count,
                    "zaman": m.taken_at.isoformat() if m.taken_at else ""
                }
                for m in medyalar
            ]
        except Exception as e:
            logger.error(f"Gonderi listesi alınamadı: {e}")
            return []

    # ── Otomasyon Döngüsü ─────────────────────────────────────────────────────

    def otomasyon_baslat(self, yanit_islevi):
        """Arka planda DM'leri kontrol edip otomatik yanıtla."""
        self._dinleme_aktif = True
        t = threading.Thread(
            target=self._otomasyon_dongusu,
            args=(yanit_islevi,),
            daemon=True
        )
        t.start()
        logger.info("Instagram otomasyon başlatıldı")

    def otomasyon_durdur(self):
        self._dinleme_aktif = False

    def _otomasyon_dongusu(self, yanit_islevi):
        islenen = set()
        while self._dinleme_aktif:
            try:
                dmler = self.dm_listesi_al(limit=10)
                for dm in dmler:
                    anahtar = f"{dm['thread_id']}_{dm['mesaj'][:20]}"
                    if anahtar not in islenen and dm["mesaj"]:
                        islenen.add(anahtar)
                        yanit = yanit_islevi(
                            dm["mesaj"],
                            kullanici_id=dm["kullanici"],
                            platform="instagram"
                        )
                        if yanit:
                            self.dm_yanit_gonder(dm["thread_id"], yanit)
                interval = self.brain.ayar_al(
                    "zamanlama", "dm_kontrol_suresi", varsayilan=60
                )
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Instagram otomasyon hatası: {e}")
                time.sleep(30)

    # ── Yardımcı ─────────────────────────────────────────────────────────────

    def _ornek_dm_listesi(self) -> list:
        return [
            {
                "thread_id": "sim_001",
                "kullanici": "demo_kullanici",
                "mesaj": "Astra J ekran fiyatı nedir?",
                "zaman": datetime.now().isoformat(),
                "okundu": False
            }
        ]

    @property
    def bagli(self) -> bool:
        return self._bagli
