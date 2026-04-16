# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Brain (Beyin) Modülü
Med Tuning - Diyarbakır
Tüm AI kararları, bilgi tabanı ve durum yönetimi burada.
"""

import json
import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config" / "settings.json"
DB_FILE = BASE_DIR / "data" / "medajan.db"


# ─────────────────────────────────────────────────────────────────────────────
# Bilgi Tabanı  (Med Tuning ürün/hizmet kataloğu)
# ─────────────────────────────────────────────────────────────────────────────
BILGI_TABANI = {
    "urunler": {
        "ekranlar": {
            "astra_j": {
                "isim": "Opel Astra J Multimedya Ekran",
                "fiyat": "3.500 - 5.500 TL",
                "ozellikler": ["Android 10", "GPS Navigasyon", "Bluetooth", "USB", "WiFi", "Geri görüş kamerası desteği"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
            "astra_k": {
                "isim": "Opel Astra K Multimedya Ekran",
                "fiyat": "4.000 - 6.000 TL",
                "ozellikler": ["Android 11", "Carplay", "Android Auto", "GPS", "4G"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
            "insignia": {
                "isim": "Opel Insignia Multimedya Ekran",
                "fiyat": "5.000 - 8.000 TL",
                "ozellikler": ["Android 12", "Carplay", "Android Auto", "4K ekran"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
            "corsa": {
                "isim": "Opel Corsa Multimedya Ekran",
                "fiyat": "2.800 - 4.500 TL",
                "ozellikler": ["Android 10", "GPS", "Bluetooth", "USB"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
            "mokka": {
                "isim": "Opel Mokka Multimedya Ekran",
                "fiyat": "4.500 - 7.000 TL",
                "ozellikler": ["Android 11", "Carplay", "4G", "WiFi"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
            "volkswagen": {
                "isim": "Volkswagen Multimedya Ekran",
                "fiyat": "4.000 - 9.000 TL",
                "ozellikler": ["Android 12", "Carplay", "Android Auto", "DSP ses sistemi"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
            "bmw": {
                "isim": "BMW Multimedya / Navigasyon Ekran",
                "fiyat": "6.000 - 15.000 TL",
                "ozellikler": ["Android", "iDrive entegrasyonu", "Carplay wireless"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
            "toyota": {
                "isim": "Toyota Multimedya Ekran",
                "fiyat": "3.500 - 6.500 TL",
                "ozellikler": ["Android 11", "Carplay", "GPS", "Bluetooth"],
                "montaj": "Ücretsiz montaj",
                "garanti": "12 ay garanti"
            },
        },
        "ses_sistemleri": {
            "hoparlor": {
                "isim": "Araç Hoparlör Seti",
                "fiyat": "1.500 - 5.000 TL",
                "markalar": ["Pioneer", "JBL", "Hertz", "Alpine"],
                "garanti": "12 ay garanti"
            },
            "amplifikator": {
                "isim": "Amplifikatör",
                "fiyat": "2.000 - 8.000 TL",
                "markalar": ["Pioneer", "Alpine", "JBL"],
                "garanti": "12 ay garanti"
            },
            "subwoofer": {
                "isim": "Subwoofer",
                "fiyat": "2.500 - 7.000 TL",
                "markalar": ["JL Audio", "Rockford", "Pioneer"],
                "garanti": "12 ay garanti"
            }
        },
        "kamera": {
            "geri_goris": {
                "isim": "Geri Görüş Kamerası",
                "fiyat": "500 - 1.500 TL",
                "ozellikler": ["Gece görüş", "170° geniş açı", "Su geçirmez"],
                "garanti": "6 ay garanti"
            },
            "360": {
                "isim": "360° Kamera Sistemi",
                "fiyat": "3.000 - 6.000 TL",
                "ozellikler": ["4 kamera", "Kuş bakışı görünüm"],
                "garanti": "12 ay garanti"
            }
        },
        "aydinlatma": {
            "led": {
                "isim": "LED Far / Stop / İç Aydınlatma",
                "fiyat": "500 - 3.000 TL",
                "garanti": "6 ay garanti"
            }
        }
    },
    "hizmetler": {
        "montaj": "Tüm ürünlerde ücretsiz montaj",
        "garanti": "Ürüne göre 6-12 ay garanti",
        "teknik_servis": "Araç multimedya ve ses sistemi teknik servisi",
        "yazilim_guncelleme": "Multimedya yazılım güncelleme hizmeti",
        "adres": "Diyarbakır - Med Tuning",
        "calisma_saatleri": "Hafta içi 09:00 - 18:00, Cumartesi 09:00 - 15:00"
    },
    "sikca_sorulan": {
        "montaj_suresi": "Ürüne göre 1-3 saat",
        "odeme": "Nakit, havale/EFT, kredi kartı (taksit imkânı)",
        "teslimat": "Yerinde montaj yapılmaktadır, kargo seçeneği mevcuttur",
        "garanti_kapsami": "Üretim ve malzeme hatalarını kapsar"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Intent / Niyet Eşleştirmeleri
# ─────────────────────────────────────────────────────────────────────────────
INTENT_PATTERNS = {
    "fiyat_sor": [
        "fiyat", "fiyatı", "ne kadar", "kaç tl", "kaç para", "ücret", "maliyet", "tutar", "para"
    ],
    "urun_sor": [
        "var mı", "satıyor musunuz", "ürün", "model", "marka", "ekran", "hoparlör",
        "subwoofer", "amplifikatör", "kamera", "navigasyon", "multimedya"
    ],
    "adres_sor": [
        "adres", "nerede", "konum", "nasıl gelirim", "lokasyon", "nereden"
    ],
    "calisma_saati_sor": [
        "saat", "çalışma saati", "açık mısınız", "kaçta", "ne zaman", "kapatıyorsunuz"
    ],
    "montaj_sor": [
        "montaj", "takma", "kurulum", "taktırma", "monte"
    ],
    "garanti_sor": [
        "garanti", "güvence", "iade", "değişim", "bozulursa"
    ],
    "iletisim_sor": [
        "telefon", "iletişim", "ulaşmak", "aramak", "whatsapp"
    ],
    "selamlasma": [
        "merhaba", "selam", "iyi günler", "iyi akşamlar", "günaydın", "hayırlı", "hello", "hi"
    ],
    "tesekur": [
        "teşekkür", "sağ ol", "eyvallah", "tamam", "tamam anladım", "anladım"
    ]
}

ARAC_MODELLERI = {
    "astra j": "astra_j",
    "astra k": "astra_k",
    "astra": "astra_j",
    "insignia": "insignia",
    "corsa": "corsa",
    "mokka": "mokka",
    "vw": "volkswagen",
    "volkswagen": "volkswagen",
    "golf": "volkswagen",
    "passat": "volkswagen",
    "bmw": "bmw",
    "toyota": "toyota",
    "yaris": "toyota",
    "corolla": "toyota",
    "auris": "toyota",
}


class Brain:
    """
    MedAjan merkezi beyin sınıfı.
    Tüm platformlar arası koordinasyonu, bilgi tabanını ve
    AI karar mekanizmasını yönetir.
    """

    def __init__(self):
        self._kilit = threading.Lock()
        self._konusma_gecmisi: dict[str, list] = {}
        self._ayarlar: dict = {}
        self._istatistikler: dict = {
            "toplam_mesaj": 0,
            "platform_dagilimi": {},
            "cevaplanan": 0,
            "baslama_zamani": datetime.now().isoformat()
        }
        self._platform_durumu: dict = {
            "instagram": False,
            "facebook": False,
            "whatsapp": False,
            "tiktok": False
        }
        self._yukle_ayarlar()
        self._db_baslat()
        logger.info("Brain başlatıldı - Med Tuning Diyarbakır")

    # ── Ayarlar ──────────────────────────────────────────────────────────────

    def _yukle_ayarlar(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    self._ayarlar = json.load(f)
            else:
                self._ayarlar = {}
        except Exception as e:
            logger.error(f"Ayarlar yüklenemedi: {e}")
            self._ayarlar = {}

    def ayar_al(self, *anahtarlar, varsayilan=None):
        veri = self._ayarlar
        for a in anahtarlar:
            if isinstance(veri, dict) and a in veri:
                veri = veri[a]
            else:
                return varsayilan
        return veri

    def ayar_kaydet(self, deger, *anahtarlar):
        veri = self._ayarlar
        for a in anahtarlar[:-1]:
            veri = veri.setdefault(a, {})
        veri[anahtarlar[-1]] = deger
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._ayarlar, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ayar kaydedilemedi: {e}")

    # ── Veritabanı ────────────────────────────────────────────────────────────

    def _db_baslat(self):
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._db_baglanti = sqlite3.connect(str(DB_FILE), check_same_thread=False)
        self._db_baglanti.row_factory = sqlite3.Row
        cur = self._db_baglanti.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS mesajlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                kullanici_id TEXT,
                kullanici_adi TEXT,
                mesaj TEXT,
                yanit TEXT,
                tarih TEXT,
                okundu INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                kullanici_id TEXT UNIQUE,
                kullanici_adi TEXT,
                ilk_gorusme TEXT,
                son_gorusme TEXT,
                mesaj_sayisi INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS gorevler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tip TEXT,
                platform TEXT,
                veri TEXT,
                durum TEXT DEFAULT 'bekliyor',
                olusturma TEXT,
                tamamlama TEXT
            );
        """)
        self._db_baglanti.commit()

    def mesaj_kaydet(self, platform: str, kullanici_id: str,
                     kullanici_adi: str, mesaj: str, yanit: str):
        with self._kilit:
            cur = self._db_baglanti.cursor()
            cur.execute(
                "INSERT INTO mesajlar (platform, kullanici_id, kullanici_adi, mesaj, yanit, tarih) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (platform, kullanici_id, kullanici_adi, mesaj, yanit,
                 datetime.now().isoformat())
            )
            cur.execute("""
                INSERT INTO kullanicilar (platform, kullanici_id, kullanici_adi, ilk_gorusme, son_gorusme, mesaj_sayisi)
                VALUES (?, ?, ?, ?, ?, 1)
                ON CONFLICT(kullanici_id) DO UPDATE SET
                    son_gorusme=excluded.son_gorusme,
                    mesaj_sayisi=mesaj_sayisi+1
            """, (platform, kullanici_id, kullanici_adi,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            self._db_baglanti.commit()
            self._istatistikler["toplam_mesaj"] += 1
            self._istatistikler["cevaplanan"] += 1
            self._istatistikler["platform_dagilimi"][platform] = \
                self._istatistikler["platform_dagilimi"].get(platform, 0) + 1

    def son_mesajlar(self, limit: int = 50) -> list:
        cur = self._db_baglanti.cursor()
        cur.execute(
            "SELECT * FROM mesajlar ORDER BY tarih DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in cur.fetchall()]

    # ── Konuşma Geçmişi ───────────────────────────────────────────────────────

    def gecmis_ekle(self, kullanici_id: str, rol: str, icerik: str):
        with self._kilit:
            if kullanici_id not in self._konusma_gecmisi:
                self._konusma_gecmisi[kullanici_id] = []
            self._konusma_gecmisi[kullanici_id].append({
                "rol": rol, "icerik": icerik,
                "zaman": datetime.now().isoformat()
            })
            # Son 20 mesajı tut
            if len(self._konusma_gecmisi[kullanici_id]) > 20:
                self._konusma_gecmisi[kullanici_id] = \
                    self._konusma_gecmisi[kullanici_id][-20:]

    def gecmis_al(self, kullanici_id: str) -> list:
        return self._konusma_gecmisi.get(kullanici_id, [])

    # ── Platform Durumu ───────────────────────────────────────────────────────

    def platform_durumu_guncelle(self, platform: str, durum: bool):
        self._platform_durumu[platform] = durum

    def platform_durumu_al(self, platform: str) -> bool:
        return self._platform_durumu.get(platform, False)

    def tum_durum(self) -> dict:
        return {
            "platformlar": self._platform_durumu.copy(),
            "istatistikler": self._istatistikler.copy(),
            "zaman": datetime.now().isoformat()
        }

    # ── Intent Tespiti ────────────────────────────────────────────────────────

    def intent_tespit_et(self, metin: str) -> list:
        metin_kucuk = metin.lower()
        bulunan = []
        for intent, kelimeler in INTENT_PATTERNS.items():
            for kelime in kelimeler:
                if kelime in metin_kucuk:
                    bulunan.append(intent)
                    break
        return bulunan

    def arac_modeli_tespit_et(self, metin: str) -> str | None:
        metin_kucuk = metin.lower()
        for anahtar, model_kodu in ARAC_MODELLERI.items():
            if anahtar in metin_kucuk:
                return model_kodu
        return None

    def urun_kategorisi_tespit_et(self, metin: str) -> str | None:
        metin_kucuk = metin.lower()
        ekran_kelimeleri = ["ekran", "multimedya", "navigasyon", "navigation", "teyp"]
        ses_kelimeleri = ["hoparlör", "ses", "subwoofer", "amplifikatör", "bas"]
        kamera_kelimeleri = ["kamera", "kamera sistemi", "geri görüş"]

        if any(k in metin_kucuk for k in ekran_kelimeleri):
            return "ekranlar"
        if any(k in metin_kucuk for k in ses_kelimeleri):
            return "ses_sistemleri"
        if any(k in metin_kucuk for k in kamera_kelimeleri):
            return "kamera"
        return None

    # ── Yanıt Üretme (dahili bilgi tabanı) ───────────────────────────────────

    def yanit_olustur(self, metin: str, kullanici_id: str = "anonim",
                      platform: str = "test") -> str:
        intents = self.intent_tespit_et(metin)
        arac = self.arac_modeli_tespit_et(metin)
        kategori = self.urun_kategorisi_tespit_et(metin)

        # Selamlama
        if "selamlasma" in intents:
            return (
                "Merhaba! Med Tuning Diyarbakır'a hoş geldiniz 🚗\n"
                "Araç multimedya ekranları, ses sistemleri ve aksesuar konularında "
                "size nasıl yardımcı olabilirim?"
            )

        # Teşekkür
        if "tesekur" in intents:
            return (
                "Rica ederiz! Başka bir sorunuz olursa her zaman buradayız. "
                "Med Tuning olarak size yardımcı olmaktan memnuniyet duyarız 😊"
            )

        # Fiyat sorusu + araç modeli
        if "fiyat_sor" in intents and arac and kategori == "ekranlar":
            urun = BILGI_TABANI["urunler"]["ekranlar"].get(arac)
            if urun:
                ozellik_str = "\n  • ".join(urun.get("ozellikler", []))
                return (
                    f"**{urun['isim']}** fiyatlarımız:\n\n"
                    f"💰 Fiyat aralığı: **{urun['fiyat']}**\n"
                    f"🔧 {urun['montaj']}\n"
                    f"✅ {urun['garanti']}\n\n"
                    f"Özellikler:\n  • {ozellik_str}\n\n"
                    f"Detaylı bilgi ve randevu için bize ulaşabilirsiniz."
                )

        # Sadece fiyat sorusu (araç belirtilmemiş)
        if "fiyat_sor" in intents:
            if kategori == "ekranlar":
                return (
                    "Araç multimedya ekran fiyatlarımız araç modeline göre değişmektedir:\n\n"
                    "• Opel Astra J: 3.500 - 5.500 TL\n"
                    "• Opel Astra K: 4.000 - 6.000 TL\n"
                    "• Opel Insignia: 5.000 - 8.000 TL\n"
                    "• VW Golf/Passat: 4.000 - 9.000 TL\n"
                    "• BMW: 6.000 - 15.000 TL\n"
                    "• Toyota: 3.500 - 6.500 TL\n\n"
                    "Tüm fiyatlara **ücretsiz montaj** dahildir. "
                    "Araç modelinizi belirtirseniz daha net fiyat verebilirim."
                )
            elif kategori == "ses_sistemleri":
                return (
                    "Ses sistemi fiyatlarımız:\n\n"
                    "• Hoparlör Seti: 1.500 - 5.000 TL\n"
                    "• Amplifikatör: 2.000 - 8.000 TL\n"
                    "• Subwoofer: 2.500 - 7.000 TL\n\n"
                    "Pioneer, JBL, Hertz ve Alpine markalarda geniş ürün yelpazemiz mevcuttur."
                )
            else:
                return (
                    "Ürünlerimiz hakkında fiyat bilgisi almak için hangi ürünle ilgilendiğinizi belirtir misiniz?\n\n"
                    "📺 Multimedya Ekranlar\n"
                    "🔊 Ses Sistemleri (hoparlör, subwoofer, amplifikatör)\n"
                    "📷 Kamera Sistemleri\n"
                    "💡 LED Aydınlatma"
                )

        # Adres sorusu
        if "adres_sor" in intents:
            return (
                "📍 **Med Tuning - Diyarbakır**\n\n"
                f"{self.ayar_al('uygulama', 'sehir', varsayilan='Diyarbakır')}\n\n"
                "Konum bilgisi için WhatsApp veya Instagram üzerinden yazabilirsiniz, "
                "size haritamızı gönderelim."
            )

        # Çalışma saati
        if "calisma_saati_sor" in intents:
            return (
                "⏰ **Çalışma Saatlerimiz:**\n\n"
                "Pazartesi - Cuma: 09:00 - 18:00\n"
                "Cumartesi: 09:00 - 15:00\n"
                "Pazar: Kapalı\n\n"
                "Randevu için önceden haber vermenizi öneririz."
            )

        # Montaj sorusu
        if "montaj_sor" in intents:
            return (
                "🔧 **Montaj Hizmetimiz:**\n\n"
                "• Tüm ürünlerde **ücretsiz montaj** yapıyoruz\n"
                "• Ürüne göre montaj süresi 1-3 saat\n"
                "• Uzman teknisyenlerimiz tarafından yapılır\n"
                "• Montaj sonrası test ve ayar yapılır\n\n"
                "Randevu almak ister misiniz?"
            )

        # Garanti sorusu
        if "garanti_sor" in intents:
            return (
                "✅ **Garanti Kapsamımız:**\n\n"
                "• Multimedya ekranlar: 12 ay garanti\n"
                "• Ses sistemleri: 12 ay garanti\n"
                "• Kameralar: 6 ay garanti\n\n"
                "Garanti kapsamı; üretim ve malzeme hatalarını içerir. "
                "Hasar görmesi durumunda destek sağlıyoruz."
            )

        # İletişim sorusu
        if "iletisim_sor" in intents:
            tel = self.ayar_al("uygulama", "telefon", varsayilan="")
            return (
                "📞 **İletişim Bilgileri:**\n\n"
                f"Telefon/WhatsApp: {tel if tel else 'Profilimizdeki numaradan ulaşabilirsiniz'}\n"
                "Instagram: Profil sayfamızdan DM atabilirsiniz\n"
                "Konum: Diyarbakır - Med Tuning\n\n"
                "Size en kısa sürede geri dönüş yapacağız."
            )

        # Araç modeli var ama intent net değil
        if arac:
            urun = BILGI_TABANI["urunler"]["ekranlar"].get(arac)
            if urun:
                return (
                    f"{urun['isim']} konusunda yardımcı olabilirim!\n\n"
                    f"💰 Fiyat: {urun['fiyat']}\n"
                    f"🔧 {urun['montaj']}\n\n"
                    "Fiyat, özellikler veya montaj hakkında sormak istediğiniz bir şey var mı?"
                )

        # Genel yanıt
        return (
            "Med Tuning Diyarbakır olarak araç multimedya ve ses sistemleri konusunda "
            "hizmet veriyoruz.\n\n"
            "Şu konularda yardımcı olabilirim:\n"
            "• 📺 Multimedya ekran fiyatları ve özellikleri\n"
            "• 🔊 Ses sistemi (hoparlör, subwoofer, amplifikatör)\n"
            "• 📷 Kamera sistemleri\n"
            "• 🔧 Montaj ve garanti bilgileri\n"
            "• 📍 Adres ve çalışma saatleri\n\n"
            "Hangi konuda bilgi almak istersiniz?"
        )

    def bilgi_tabani_al(self) -> dict:
        return BILGI_TABANI

    def istatistik_al(self) -> dict:
        return self._istatistikler.copy()
