# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Facebook Modülü
Graph API ile sayfa yönetimi, DM ve yorum otomasyonu.
"""

import time
import threading
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_MEVCUT = True
except ImportError:
    REQUESTS_MEVCUT = False


class Facebook:
    GRAPH_API = "https://graph.facebook.com/v18.0"

    def __init__(self, brain):
        self.brain = brain
        self._bagli = False
        self._page_id = ""
        self._access_token = ""
        self._dinleme_aktif = False

    # ── Bağlantı ──────────────────────────────────────────────────────────────

    def baglan(self, page_id: str = "", access_token: str = "") -> bool:
        if not page_id:
            page_id = self.brain.ayar_al("facebook", "page_id", varsayilan="")
        if not access_token:
            access_token = self.brain.ayar_al("facebook", "access_token", varsayilan="")

        if not page_id or not access_token:
            logger.warning("Facebook: page_id veya access_token eksik, simülasyon modu")
            self._bagli = True
            self.brain.platform_durumu_guncelle("facebook", True)
            return True

        self._page_id = page_id
        self._access_token = access_token

        try:
            if REQUESTS_MEVCUT:
                r = requests.get(
                    f"{self.GRAPH_API}/me",
                    params={"access_token": access_token},
                    timeout=10
                )
                if r.status_code == 200:
                    self._bagli = True
                    self.brain.platform_durumu_guncelle("facebook", True)
                    logger.info(f"Facebook bağlandı - Page: {page_id}")
                    return True
                else:
                    logger.error(f"Facebook token geçersiz: {r.text}")
                    return False
            else:
                self._bagli = True
                self.brain.platform_durumu_guncelle("facebook", True)
                return True
        except Exception as e:
            logger.error(f"Facebook bağlantı hatası: {e}")
            return False

    def baglantiyi_kes(self):
        self._bagli = False
        self._dinleme_aktif = False
        self.brain.platform_durumu_guncelle("facebook", False)

    # ── API İstekleri ─────────────────────────────────────────────────────────

    def _api_get(self, endpoint: str, params: dict = None) -> dict:
        if not REQUESTS_MEVCUT:
            return {}
        p = {"access_token": self._access_token}
        if params:
            p.update(params)
        try:
            r = requests.get(f"{self.GRAPH_API}/{endpoint}", params=p, timeout=10)
            return r.json()
        except Exception as e:
            logger.error(f"Facebook API GET hatası: {e}")
            return {}

    def _api_post(self, endpoint: str, veri: dict = None) -> dict:
        if not REQUESTS_MEVCUT:
            return {}
        p = {"access_token": self._access_token}
        try:
            r = requests.post(
                f"{self.GRAPH_API}/{endpoint}", params=p, json=veri, timeout=10
            )
            return r.json()
        except Exception as e:
            logger.error(f"Facebook API POST hatası: {e}")
            return {}

    # ── Gönderi İşlemleri ─────────────────────────────────────────────────────

    def gonderi_yap(self, metin: str, resim_url: str = "") -> bool:
        if not self._bagli:
            return False
        if not self._access_token:
            logger.info(f"[Sim] Facebook gönderi: {metin[:50]}")
            return True
        veri = {"message": metin}
        if resim_url:
            veri["link"] = resim_url
        sonuc = self._api_post(f"{self._page_id}/feed", veri)
        return "id" in sonuc

    def yorumlar_al(self, post_id: str) -> list:
        if not self._bagli:
            return []
        if not self._access_token:
            return []
        veri = self._api_get(f"{post_id}/comments", {"fields": "id,from,message,created_time"})
        return veri.get("data", [])

    def yorum_yanit_gonder(self, yorum_id: str, metin: str) -> bool:
        if not self._bagli:
            return False
        if not self._access_token:
            logger.info(f"[Sim] Facebook yorum yanıtı → {yorum_id}: {metin[:50]}")
            return True
        sonuc = self._api_post(f"{yorum_id}/comments", {"message": metin})
        return "id" in sonuc

    def dm_gonder(self, psid: str, metin: str) -> bool:
        """Facebook Messenger DM gönder (PSID ile)."""
        if not self._bagli:
            return False
        if not self._access_token:
            logger.info(f"[Sim] Facebook DM → {psid}: {metin[:50]}")
            return True
        veri = {
            "recipient": {"id": psid},
            "message": {"text": metin}
        }
        sonuc = self._api_post("me/messages", veri)
        return "message_id" in sonuc

    # ── Sayfa Bilgileri ───────────────────────────────────────────────────────

    def sayfa_istatistik_al(self) -> dict:
        if not self._bagli or not self._access_token:
            return {"takipci": 0, "begeni": 0}
        veri = self._api_get(
            self._page_id,
            {"fields": "fan_count,followers_count,name"}
        )
        return {
            "ad": veri.get("name", ""),
            "takipci": veri.get("followers_count", 0),
            "begeni": veri.get("fan_count", 0)
        }

    # ── Otomasyon ─────────────────────────────────────────────────────────────

    def otomasyon_baslat(self, yanit_islevi):
        self._dinleme_aktif = True
        t = threading.Thread(
            target=self._otomasyon_dongusu,
            args=(yanit_islevi,),
            daemon=True
        )
        t.start()
        logger.info("Facebook otomasyon başlatıldı")

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
                logger.error(f"Facebook otomasyon hatası: {e}")
                time.sleep(60)

    @property
    def bagli(self) -> bool:
        return self._bagli
