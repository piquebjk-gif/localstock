# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Retargeting Agent
Müşteri segmentasyonu ve yeniden hedefleme kampanyaları.
"""

import time
import threading
from datetime import datetime, timedelta

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class RetargetingAgent:
    """
    Konuşma geçmişine göre müşteri segmentleri oluşturur
    ve hedefli takip mesajları gönderir.
    """

    SEGMENTLER = {
        "ekran_ilgili": {
            "anahtar_kelimeler": ["ekran", "multimedya", "navigasyon", "teyp"],
            "mesaj": (
                "Merhaba! Geçen sefer multimedya ekran hakkında bilgi almıştınız. "
                "Yeni modellerimiz geldi, ilgilenir misiniz? 🚗"
            )
        },
        "ses_ilgili": {
            "anahtar_kelimeler": ["hoparlör", "ses", "subwoofer", "müzik"],
            "mesaj": (
                "Merhaba! Araç ses sistemi hakkında merak ettikleriniz için "
                "yeni kampanyamıza göz atabilirsiniz 🎵"
            )
        },
        "fiyat_arastiran": {
            "anahtar_kelimeler": ["fiyat", "ne kadar", "kaç tl"],
            "mesaj": (
                "Merhaba! Fiyat araştırıyordunuz. "
                "Bu ay özel indirimlerimiz var, bilgi almak ister misiniz? 💰"
            )
        }
    }

    def __init__(self, brain, ai_ajan, platformlar: dict):
        self.brain = brain
        self.ai = ai_ajan
        self.platformlar = platformlar
        self._aktif = False
        self._gonderilen: set = set()

    def baslat(self):
        self._aktif = True
        t = threading.Thread(target=self._dongu, daemon=True)
        t.start()
        logger.info("Retargeting Agent başlatıldı")

    def durdur(self):
        self._aktif = False

    def _dongu(self):
        while self._aktif:
            try:
                self._segmentleri_isle()
                # 24 saatte bir çalış
                time.sleep(86400)
            except Exception as e:
                logger.error(f"Retargeting hatası: {e}")
                time.sleep(3600)

    def _segmentleri_isle(self):
        """Son 3 günde mesaj göndermiş ama satın almamış kullanıcıları hedefle."""
        mesajlar = self.brain.son_mesajlar(limit=200)
        uc_gun_once = (datetime.now() - timedelta(days=3)).isoformat()

        kullanici_segment: dict = {}
        for m in mesajlar:
            if m.get("tarih", "") < uc_gun_once:
                continue
            uid = m.get("kullanici_id", "")
            platform = m.get("platform", "")
            mesaj_metni = m.get("mesaj", "").lower()

            for segment_adi, segment in self.SEGMENTLER.items():
                if any(k in mesaj_metni for k in segment["anahtar_kelimeler"]):
                    anahtar = f"{platform}_{uid}"
                    kullanici_segment[anahtar] = {
                        "platform": platform,
                        "uid": uid,
                        "segment": segment_adi,
                        "mesaj": segment["mesaj"]
                    }

        for anahtar, bilgi in kullanici_segment.items():
            if anahtar in self._gonderilen:
                continue
            # Retargeting mesajını gönder
            platform = bilgi["platform"]
            if platform == "instagram":
                ig = self.platformlar.get("instagram")
                if ig and ig.bagli:
                    basarili = ig.dm_gonder(bilgi["uid"], bilgi["mesaj"])
                    if basarili:
                        self._gonderilen.add(anahtar)
                        logger.info(
                            f"Retargeting mesajı gönderildi: {platform}/{bilgi['uid']}"
                        )

    def segment_analiz_et(self) -> dict:
        """Tüm konuşmaları analiz edip segment dağılımını döndür."""
        mesajlar = self.brain.son_mesajlar(limit=500)
        dagilim: dict = {}
        for m in mesajlar:
            metni = m.get("mesaj", "").lower()
            for seg_adi, seg in self.SEGMENTLER.items():
                if any(k in metni for k in seg["anahtar_kelimeler"]):
                    dagilim[seg_adi] = dagilim.get(seg_adi, 0) + 1
        return dagilim
