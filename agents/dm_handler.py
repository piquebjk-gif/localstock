# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - DM Handler
Tüm platformlardaki DM'leri koordineli olarak yönetir.
"""

import time
import threading
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class DMHandler:
    def __init__(self, brain, ai_ajan, platformlar: dict):
        """
        platformlar: {"instagram": Instagram(), "whatsapp": WhatsApp(), ...}
        """
        self.brain = brain
        self.ai = ai_ajan
        self.platformlar = platformlar
        self._aktif = False
        self._islenen: set = set()
        self._istatistik = {
            "toplam_islenen": 0,
            "platform_dagilimi": {}
        }

    def baslat(self):
        self._aktif = True
        t = threading.Thread(target=self._ana_dongu, daemon=True)
        t.start()
        logger.info("DM Handler başlatıldı")

    def durdur(self):
        self._aktif = False

    def _ana_dongu(self):
        while self._aktif:
            try:
                self._instagram_dm_isle()
                self._whatsapp_dm_isle()
                interval = self.brain.ayar_al(
                    "zamanlama", "dm_kontrol_suresi", varsayilan=60
                )
                time.sleep(interval)
            except Exception as e:
                logger.error(f"DM Handler hata: {e}")
                time.sleep(30)

    def _instagram_dm_isle(self):
        ig = self.platformlar.get("instagram")
        if not ig or not ig.bagli:
            return
        if not self.brain.ayar_al("instagram", "dm_otomatik_yanit", varsayilan=True):
            return
        try:
            dmler = ig.dm_listesi_al(limit=10)
            for dm in dmler:
                anahtar = f"ig_{dm['thread_id']}_{dm['mesaj'][:30]}"
                if anahtar in self._islenen or not dm["mesaj"]:
                    continue
                self._islenen.add(anahtar)
                # Gecikme simülasyonu (insan gibi davranış)
                gecikme = self.brain.ayar_al(
                    "yapay_zeka", "yanit_gecikmesi", varsayilan=3
                )
                gecikme_max = self.brain.ayar_al(
                    "yapay_zeka", "yanit_gecikmesi_max", varsayilan=10
                )
                import random
                time.sleep(random.uniform(gecikme, gecikme_max))

                yanit = self.ai.yanit_uret(
                    dm["mesaj"],
                    kullanici_id=dm["kullanici"],
                    platform="instagram",
                    kullanici_adi=dm["kullanici"]
                )
                if yanit:
                    ig.dm_yanit_gonder(dm["thread_id"], yanit)
                    self._istatistik["toplam_islenen"] += 1
                    self._istatistik["platform_dagilimi"]["instagram"] = \
                        self._istatistik["platform_dagilimi"].get("instagram", 0) + 1
                    logger.info(f"Instagram DM yanıtlandı: {dm['kullanici']}")
        except Exception as e:
            logger.error(f"Instagram DM işleme hatası: {e}")

    def _whatsapp_dm_isle(self):
        wa = self.platformlar.get("whatsapp")
        if not wa or not wa.bagli:
            return
        if not self.brain.ayar_al("whatsapp", "otomatik_yanit", varsayilan=True):
            return
        # WhatsApp mesajları _otomasyon_dongusu üzerinden işlenir
        pass

    def dm_gonder(self, platform: str, kullanici_id: str, mesaj: str) -> bool:
        """Manuel DM gönder."""
        p = self.platformlar.get(platform)
        if not p or not p.bagli:
            return False
        if platform == "instagram":
            return p.dm_gonder(kullanici_id, mesaj)
        elif platform == "whatsapp":
            return p.mesaj_gonder(kullanici_id, mesaj)
        elif platform == "facebook":
            return p.dm_gonder(kullanici_id, mesaj)
        return False

    def istatistik_al(self) -> dict:
        return self._istatistik.copy()
