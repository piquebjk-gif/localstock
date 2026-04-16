# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Story & Reels Manager
Instagram story ve reels zamanlama/yönetim ajanı.
"""

import time
import threading
import json
from pathlib import Path
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
ZAMANLAMA_DOSYASI = BASE_DIR / "data" / "story_zamanlama.json"


class StoryReelsManager:
    def __init__(self, brain, platformlar: dict):
        self.brain = brain
        self.platformlar = platformlar
        self._aktif = False
        self._zamanlama: list = []
        self._zamanlama_yukle()

    def _zamanlama_yukle(self):
        if ZAMANLAMA_DOSYASI.exists():
            try:
                with open(ZAMANLAMA_DOSYASI, encoding="utf-8") as f:
                    self._zamanlama = json.load(f)
            except Exception:
                self._zamanlama = []

    def _zamanlama_kaydet(self):
        ZAMANLAMA_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
        with open(ZAMANLAMA_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(self._zamanlama, f, ensure_ascii=False, indent=2)

    # ── Zamanlama Yönetimi ────────────────────────────────────────────────────

    def story_ekle(self, dosya_yolu: str, yayin_saati: str,
                   baslik: str = "", platform: str = "instagram") -> bool:
        """
        yayin_saati: "2024-12-01 14:30" formatında
        """
        gorev = {
            "tip": "story",
            "platform": platform,
            "dosya": dosya_yolu,
            "yayin_saati": yayin_saati,
            "baslik": baslik,
            "durum": "bekliyor",
            "olusturma": datetime.now().isoformat()
        }
        self._zamanlama.append(gorev)
        self._zamanlama_kaydet()
        logger.info(f"Story eklendi: {platform} @ {yayin_saati}")
        return True

    def reels_ekle(self, dosya_yolu: str, yayin_saati: str,
                   aciklama: str = "", platform: str = "instagram") -> bool:
        gorev = {
            "tip": "reels",
            "platform": platform,
            "dosya": dosya_yolu,
            "yayin_saati": yayin_saati,
            "aciklama": aciklama,
            "durum": "bekliyor",
            "olusturma": datetime.now().isoformat()
        }
        self._zamanlama.append(gorev)
        self._zamanlama_kaydet()
        logger.info(f"Reels eklendi: {platform} @ {yayin_saati}")
        return True

    def zamanlama_listesi(self) -> list:
        return sorted(
            [g for g in self._zamanlama if g["durum"] == "bekliyor"],
            key=lambda x: x["yayin_saati"]
        )

    # ── Otomasyon ─────────────────────────────────────────────────────────────

    def baslat(self):
        self._aktif = True
        t = threading.Thread(target=self._dongu, daemon=True)
        t.start()
        logger.info("Story/Reels Manager başlatıldı")

    def durdur(self):
        self._aktif = False

    def _dongu(self):
        while self._aktif:
            try:
                simdi = datetime.now().strftime("%Y-%m-%d %H:%M")
                for gorev in self._zamanlama:
                    if gorev["durum"] != "bekliyor":
                        continue
                    if gorev["yayin_saati"][:16] <= simdi:
                        self._gorevi_yayinla(gorev)
                time.sleep(60)
            except Exception as e:
                logger.error(f"Story Manager hata: {e}")
                time.sleep(60)

    def _gorevi_yayinla(self, gorev: dict):
        platform = gorev.get("platform", "instagram")
        tip = gorev.get("tip", "story")
        dosya = gorev.get("dosya", "")

        if not Path(dosya).exists():
            logger.warning(f"Dosya bulunamadı: {dosya}")
            gorev["durum"] = "hata"
            self._zamanlama_kaydet()
            return

        ig = self.platformlar.get("instagram")
        if not ig or not ig.bagli:
            logger.warning("Instagram bağlı değil, story yayınlanamadı")
            return

        try:
            if not hasattr(ig, "_client") or not ig._client:
                logger.info(f"[Sim] {tip.upper()} yayınlandı: {dosya}")
                gorev["durum"] = "tamamlandi"
                self._zamanlama_kaydet()
                return

            if tip == "story":
                from pathlib import Path as P
                if dosya.lower().endswith((".jpg", ".jpeg", ".png")):
                    ig._client.photo_upload_to_story(P(dosya))
                else:
                    ig._client.video_upload_to_story(P(dosya))
            elif tip == "reels":
                aciklama = gorev.get("aciklama", "")
                ig._client.video_upload(P(dosya), caption=aciklama)

            gorev["durum"] = "tamamlandi"
            gorev["tamamlama"] = datetime.now().isoformat()
            self._zamanlama_kaydet()
            logger.info(f"{tip.upper()} başarıyla yayınlandı: {dosya}")
        except Exception as e:
            logger.error(f"{tip} yayınlama hatası: {e}")
            gorev["durum"] = "hata"
            self._zamanlama_kaydet()
