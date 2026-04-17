# -*- coding: utf-8 -*-
"""
IQ Elektronik — OtoGorseller Klasöründen Toplu Ürün Yükleme
Kullanım: python urun_yukle.py [klasor_yolu]
"""

import sys
import json
import re
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(ROOT))

from webforge.core.wp_engine import WPEngine
from iq_setup import motor_olustur, _cfg

GORSEL_UZANTILARI = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

KATEGORI_OZELLIKLERI = {
    "Telefon & Tablet": [
        "Yüksek çözünürlüklü kamera", "Hızlı şarj desteği",
        "5G bağlantı desteği", "AMOLED ekran teknolojisi",
        "Gelişmiş işlemci", "Su geçirmez tasarım",
    ],
    "Bilgisayar & Laptop": [
        "SSD depolama", "Gelişmiş grafik kartı",
        "RGB aydınlatmalı klavye", "Hızlı RAM", "Çoklu port desteği",
        "Soğutma sistemi",
    ],
    "Ev Elektroniği": [
        "Enerji tasarrufu", "Akıllı kontrol", "Sessiz çalışma",
        "Dayanıklı tasarım", "Uzaktan kumanda", "LED ekran",
    ],
    "default": [
        "Kaliteli malzeme", "Garantili ürün", "Hızlı kargo",
        "Kolay kurulum", "Teknik destek",
    ],
}

FIYAT_ARALIKLARI = {
    "Telefon & Tablet":   (2000, 80000),
    "Bilgisayar & Laptop": (5000, 50000),
    "Ev Elektroniği":     (500, 25000),
    "default":            (100, 5000),
}


def dosya_adi_temizle(dosya_adi: str) -> str:
    """Dosya adını okunabilir ürün başlığına çevir."""
    isim = Path(dosya_adi).stem
    isim = re.sub(r"[-_]+", " ", isim)
    isim = re.sub(r"\s+", " ", isim).strip()
    return isim.title()


def slug_olustur(baslik: str) -> str:
    tr_map = str.maketrans("ğüşıöçĞÜŞİÖÇ", "gusiocGUSIOC")
    slug = baslik.lower().translate(tr_map)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug


def rastgele_fiyat(kategori: str) -> tuple[str, str | None]:
    aralik = FIYAT_ARALIKLARI.get(kategori, FIYAT_ARALIKLARI["default"])
    taban = random.randint(*aralik)
    indirimli = random.random() > 0.65
    if indirimli:
        oran = random.uniform(0.10, 0.30)
        indirimli_fiyat = int(taban * (1 - oran))
        return str(indirimli_fiyat), str(taban)
    return str(taban), None


def ozellikler_listele(kategori: str) -> list[str]:
    havuz = KATEGORI_OZELLIKLERI.get(kategori, KATEGORI_OZELLIKLERI["default"])
    sayi = random.randint(3, min(5, len(havuz)))
    return random.sample(havuz, sayi)


def gorseller_tara(klasor: Path) -> dict[str, list[Path]]:
    """Alt klasörleri kategori olarak kullanarak görselleri topla."""
    sonuc: dict[str, list[Path]] = {}
    for alt in sorted(klasor.iterdir()):
        if alt.is_dir():
            gorseller = [
                f for f in sorted(alt.iterdir())
                if f.suffix.lower() in GORSEL_UZANTILARI
            ]
            if gorseller:
                sonuc[alt.name] = gorseller
    if not sonuc:
        # Düz klasör — kategori yok
        gorseller = [
            f for f in sorted(klasor.iterdir())
            if f.suffix.lower() in GORSEL_UZANTILARI
        ]
        if gorseller:
            sonuc["Genel"] = gorseller
    return sonuc


def urun_verisi_olustur(
    wp: WPEngine,
    gorsel_yolu: Path,
    baslik: str,
    kategori_adi: str,
    kategori_id: int,
) -> dict:
    """Görseli yükle ve ürün verisini hazırla."""
    print(f"    → Görsel yükleniyor: {gorsel_yolu.name}")
    medya = wp.gorsel_yukle(str(gorsel_yolu), baslik=baslik, alt_metin=baslik)
    gorsel_url = medya.get("source_url", "")

    fiyat, eski_fiyat = rastgele_fiyat(kategori_adi)
    ozellikler = ozellikler_listele(kategori_adi)
    aciklama_html = "<ul>" + "".join(f"<li>{o}</li>" for o in ozellikler) + "</ul>"

    veri: dict = {
        "name": baslik,
        "slug": slug_olustur(baslik),
        "type": "simple",
        "status": "publish",
        "regular_price": eski_fiyat or fiyat,
        "description": aciklama_html,
        "short_description": f"İQ Elektronik'ten {kategori_adi} kategorisinde kaliteli ürün.",
        "categories": [{"id": kategori_id}],
        "manage_stock": True,
        "stock_quantity": random.randint(1, 50),
        "sku": f"IQ{random.randint(100000, 999999)}",
    }
    if eski_fiyat:
        veri["sale_price"] = fiyat
    if gorsel_url:
        veri["images"] = [{"src": gorsel_url, "alt": baslik}]

    return veri


def yukle(klasor_yolu: str | None = None, kuru_calistir: bool = False):
    """
    Görselleri OtoGorseller klasöründen WooCommerce'e yükle.

    :param klasor_yolu: Klasör yolu (None → config'den al)
    :param kuru_calistir: True ise yükleme yapmaz, sadece listeler
    """
    cfg = _cfg()
    klasor = Path(klasor_yolu or cfg.get("gorseller_klasoru", ""))
    if not klasor.exists():
        print(f"✗ Klasör bulunamadı: {klasor}")
        return

    wp = motor_olustur()

    # Mevcut WC kategorileri
    wc_katlar = {k["name"].lower(): k["id"] for k in wp.wc_kategoriler_listele()}

    icerik = gorseller_tara(klasor)
    if not icerik:
        print("Klasörde görsel bulunamadı.")
        return

    toplam = sum(len(v) for v in icerik.values())
    print(f"\n{'[KURU ÇALIŞTIRMA] ' if kuru_calistir else ''}Toplam {toplam} görsel — {len(icerik)} kategori\n")

    basarili = hata = 0

    for kat_klasoru, gorseller in icerik.items():
        # Alt klasör adını WC kategorisiyle eşleştir (en yakın)
        kat_id = wc_katlar.get(kat_klasoru.lower())
        kat_adi = kat_klasoru
        if kat_id is None:
            # Bilinen kategorilere göre tahmin
            for bilinen in cfg["kategoriler"]:
                if any(w in kat_klasoru.lower() for w in bilinen["slug"].split("-")):
                    kat_adi = bilinen["isim"]
                    kat_id = wc_katlar.get(kat_adi.lower())
                    break
        if kat_id is None:
            kat_adi = "Genel"
            kat_id = wc_katlar.get("genel", 0)

        print(f"[{kat_adi}] — {len(gorseller)} ürün")

        for gorsel in gorseller:
            baslik = dosya_adi_temizle(gorsel.name)
            if kuru_calistir:
                print(f"  • {baslik}")
                continue
            try:
                veri = urun_verisi_olustur(wp, gorsel, baslik, kat_adi, kat_id)
                sonuc = wp.urun_olustur(veri)
                if "id" in sonuc:
                    print(f"  ✓ [{sonuc['id']}] {baslik} — {veri['regular_price']}₺")
                    basarili += 1
                else:
                    print(f"  ✗ {baslik}: {sonuc.get('hata', sonuc)}")
                    hata += 1
            except Exception as e:
                print(f"  ✗ {baslik}: {e}")
                hata += 1

    if not kuru_calistir:
        print(f"\n✓ {basarili} ürün yüklendi, {hata} hata")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IQ Elektronik — Ürün Yükleyici")
    parser.add_argument("klasor", nargs="?", help="Görsel klasörü yolu")
    parser.add_argument("--kuru", action="store_true", help="Gerçek yükleme yapma")
    args = parser.parse_args()
    yukle(args.klasor, kuru_calistir=args.kuru)
