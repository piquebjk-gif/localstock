# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Comment Handler
Instagram ve Facebook yorumlarını otomatik yönetir.
"""

import time
import threading
import random

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class CommentHandler:
    def __init__(self, brain, ai_ajan, platformlar: dict):
        self.brain = brain
        self.ai = ai_ajan
        self.platformlar = platformlar
        self._aktif = False
        self._islenen_yorumlar: set = set()
        self._istatistik = {"toplam_yanit": 0}

    def baslat(self):
        self._aktif = True
        t = threading.Thread(target=self._dongu, daemon=True)
        t.start()
        logger.info("Comment Handler başlatıldı")

    def durdur(self):
        self._aktif = False

    def _dongu(self):
        while self._aktif:
            try:
                self._instagram_yorumlar_isle()
                self._facebook_yorumlar_isle()
                interval = self.brain.ayar_al(
                    "zamanlama", "yorum_kontrol_suresi", varsayilan=120
                )
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Comment Handler hata: {e}")
                time.sleep(60)

    def _instagram_yorumlar_isle(self):
        ig = self.platformlar.get("instagram")
        if not ig or not ig.bagli:
            return
        if not self.brain.ayar_al("instagram", "yorum_otomatik_yanit", varsayilan=True):
            return
        try:
            gonderiler = ig.gonderi_listesi_al(limit=5)
            for gonderi in gonderiler:
                yorumlar = ig.yorumlar_al(gonderi["id"], limit=20)
                for yorum in yorumlar:
                    yorum_id = yorum["id"]
                    if yorum_id in self._islenen_yorumlar:
                        continue
                    self._islenen_yorumlar.add(yorum_id)

                    # Soru içeren yorumlara yanıt ver
                    metin = yorum["metin"]
                    if any(k in metin.lower() for k in [
                        "fiyat", "ne kadar", "var mı", "kaç", "bilgi", "?", "nasıl"
                    ]):
                        time.sleep(random.uniform(5, 15))
                        yanit = self.ai.yanit_uret(
                            metin,
                            kullanici_id=yorum["kullanici"],
                            platform="instagram"
                        )
                        if yanit:
                            ig.yorum_yanit_gonder(
                                gonderi["id"], yorum["kullanici"], yanit
                            )
                            self._istatistik["toplam_yanit"] += 1
        except Exception as e:
            logger.error(f"Instagram yorum işleme hatası: {e}")

    def _facebook_yorumlar_isle(self):
        fb = self.platformlar.get("facebook")
        if not fb or not fb.bagli:
            return
        if not self.brain.ayar_al("facebook", "yorum_otomatik_yanit", varsayilan=True):
            return
        # Facebook yorum işleme (post_id listesi gerekir)

    def istatistik_al(self) -> dict:
        return self._istatistik.copy()
