# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Ana AI Ajan
Tüm platformlardan gelen mesajlara yanıt üretir.
Otonom karar mekanizması ve görev yönetimi.
"""

import time
import threading
import random
from datetime import datetime
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class MedAjanAI:
    """
    MedAjan ana yapay zeka ajanı.
    brain.yanit_olustur() dahili bilgi tabanını kullanır.
    İsteğe bağlı olarak OpenAI/Anthropic API ile genişletilebilir.
    """

    def __init__(self, brain):
        self.brain = brain
        self._aktif = False
        self._gorev_kuyrugu: list = []
        self._kilit = threading.Lock()
        self._ajan_thread: threading.Thread | None = None
        logger.info("MedAjanAI başlatıldı")

    # ── Ana Yanıt Metodu ─────────────────────────────────────────────────────

    def yanit_uret(
        self,
        mesaj: str,
        kullanici_id: str = "anonim",
        platform: str = "test",
        kullanici_adi: str = ""
    ) -> str:
        """
        Gelen mesaja uygun yanıt üretir.
        Önce dahili bilgi tabanı kontrol edilir.
        Gerekirse harici AI API'ye yönlendirilebilir.
        """
        if not mesaj or not mesaj.strip():
            return ""

        mesaj = mesaj.strip()
        logger.debug(f"[{platform}] {kullanici_id}: {mesaj[:80]}")

        # Geçmişe ekle
        self.brain.gecmis_ekle(kullanici_id, "kullanici", mesaj)

        # Dahili bilgi tabanından yanıt al
        yanit = self.brain.yanit_olustur(mesaj, kullanici_id, platform)

        # Harici AI API varsa kullan (opsiyonel)
        api_key = self.brain.ayar_al("yapay_zeka", "openai_api_key", varsayilan="")
        if not yanit and api_key:
            yanit = self._openai_yanit(mesaj, kullanici_id, api_key)

        if not yanit:
            yanit = (
                "Sorunuz için teşekkür ederiz. "
                "Med Tuning ekibimiz en kısa sürede size dönüş yapacaktır."
            )

        # Geçmişe yanıtı ekle
        self.brain.gecmis_ekle(kullanici_id, "asistan", yanit)

        # Veritabanına kaydet
        self.brain.mesaj_kaydet(
            platform, kullanici_id,
            kullanici_adi or kullanici_id,
            mesaj, yanit
        )

        return yanit

    # ── Harici AI (opsiyonel) ─────────────────────────────────────────────────

    def _openai_yanit(self, mesaj: str, kullanici_id: str, api_key: str) -> str:
        try:
            import requests
            gecmis = self.brain.gecmis_al(kullanici_id)
            mesajlar = [
                {
                    "role": "system",
                    "content": (
                        "Sen Med Tuning Diyarbakır'ın müşteri hizmetleri asistanısın. "
                        "Araç multimedya ekranları, ses sistemleri ve aksesuar satışı yapıyoruz. "
                        "Türkçe, samimi ve yardımsever cevaplar ver. "
                        "Fiyat soruları için mutlaka fiyat aralığı ver."
                    )
                }
            ]
            for g in gecmis[-6:]:
                rol = "user" if g["rol"] == "kullanici" else "assistant"
                mesajlar.append({"role": rol, "content": g["icerik"]})
            mesajlar.append({"role": "user", "content": mesaj})

            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": mesajlar,
                    "max_tokens": self.brain.ayar_al("yapay_zeka", "max_token", varsayilan=500),
                    "temperature": self.brain.ayar_al("yapay_zeka", "sicaklik", varsayilan=0.7)
                },
                timeout=15
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI yanıt hatası: {e}")
        return ""

    # ── Otonom Ajan Döngüsü ───────────────────────────────────────────────────

    def baslat(self):
        """Otonom ajan döngüsünü başlat."""
        self._aktif = True
        self._ajan_thread = threading.Thread(
            target=self._otonom_dongu,
            daemon=True
        )
        self._ajan_thread.start()
        logger.info("MedAjanAI otonom döngü başlatıldı")

    def durdur(self):
        self._aktif = False
        logger.info("MedAjanAI durduruldu")

    def _otonom_dongu(self):
        """Görev kuyruğunu işler ve periyodik analizler yapar."""
        while self._aktif:
            try:
                with self._kilit:
                    if self._gorev_kuyrugu:
                        gorev = self._gorev_kuyrugu.pop(0)
                        self._gorevi_isle(gorev)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Otonom döngü hatası: {e}")
                time.sleep(5)

    def _gorevi_isle(self, gorev: dict):
        """Tek bir görevi işle."""
        tip = gorev.get("tip")
        if tip == "dm_yanit":
            platform = gorev.get("platform")
            mesaj = gorev.get("mesaj", "")
            kullanici_id = gorev.get("kullanici_id", "")
            yanit = self.yanit_uret(mesaj, kullanici_id, platform)
            if gorev.get("geri_cagri"):
                gorev["geri_cagri"](yanit)

    def gorev_ekle(self, gorev: dict):
        """Görev kuyruğuna yeni görev ekle."""
        with self._kilit:
            self._gorev_kuyrugu.append(gorev)

    # ── Toplu Mesaj Analizi ───────────────────────────────────────────────────

    def mesaj_analiz_et(self, mesajlar: list) -> dict:
        """Birden fazla mesajı analiz et ve özet çıkar."""
        if not mesajlar:
            return {}
        intents_sayac: dict = {}
        for m in mesajlar:
            intents = self.brain.intent_tespit_et(m.get("mesaj", ""))
            for i in intents:
                intents_sayac[i] = intents_sayac.get(i, 0) + 1
        return {
            "toplam": len(mesajlar),
            "en_cok_sorulan": sorted(
                intents_sayac.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "tarih": datetime.now().isoformat()
        }

    @property
    def aktif(self) -> bool:
        return self._aktif
