# -*- coding: utf-8 -*-
"""
IQ Elektronik — WooCommerce Kurulum & Yönetim
Kategori oluşturma, ürün yükleme, site ayarları.
"""

import sys
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(ROOT))

from webforge.core.wp_engine import WPEngine


def _cfg() -> dict:
    with open(BASE / "config.json", encoding="utf-8") as f:
        return json.load(f)


def motor_olustur() -> WPEngine:
    cfg = _cfg()
    wp = WPEngine(
        site_url=cfg["site"]["url"],
        kullanici=cfg["site"]["kullanici"],
        uygulama_sifresi=cfg["site"]["uygulama_sifresi"],
    )
    wp.wc_kimlik_ayarla(
        key=cfg["woocommerce"]["consumer_key"],
        secret=cfg["woocommerce"]["consumer_secret"],
    )
    return wp


def baglanti_test():
    """WordPress bağlantısını doğrula."""
    wp = motor_olustur()
    sonuc = wp.baglantiyi_test_et()
    if sonuc.get("basarili"):
        print(f"✓ Bağlantı başarılı — {sonuc['site_adi']}")
    else:
        print(f"✗ Bağlantı hatası: {sonuc.get('hata')}")
    return sonuc


def kategorileri_kur():
    """Tanımlı kategorileri WooCommerce'de oluştur."""
    wp = motor_olustur()
    cfg = _cfg()

    mevcut = {k["name"].lower(): k["id"] for k in wp.wc_kategoriler_listele()}
    olusturulan = []

    for kat in cfg["kategoriler"]:
        isim = kat["isim"]
        if isim.lower() in mevcut:
            print(f"  — '{isim}' zaten mevcut (id={mevcut[isim.lower()]})")
            continue
        sonuc = wp.wc_kategori_olustur(isim)
        if "id" in sonuc:
            print(f"  ✓ '{isim}' oluşturuldu (id={sonuc['id']})")
            olusturulan.append(sonuc)
        else:
            print(f"  ✗ '{isim}' hatası: {sonuc.get('hata')}")

    return olusturulan


def site_bilgilerini_guncelle():
    """Site başlığı ve açıklamasını IQ Elektronik olarak ayarla."""
    wp = motor_olustur()
    cfg = _cfg()
    firma = cfg["firma"]

    sonuc = wp.site_ayarlarini_guncelle({
        "title": firma["ad"],
        "description": firma["slogan"],
    })
    if "title" in sonuc:
        print(f"✓ Site bilgileri güncellendi: {firma['ad']} — {firma['slogan']}")
    else:
        print(f"✗ Güncelleme hatası: {sonuc}")
    return sonuc


def site_ozeti():
    """WooCommerce site özetini göster."""
    wp = motor_olustur()
    ozet = wp.site_ozeti_al()
    print("\n── Site Özeti ──────────────────────────")
    for k, v in ozet.items():
        print(f"  {k}: {v}")
    print("────────────────────────────────────────\n")
    return ozet


def urunleri_listele(adet: int = 10):
    """WooCommerce'deki ilk ürünleri listele."""
    wp = motor_olustur()
    urunler = wp.urunler_listele(adet=adet)
    print(f"\n── Ürünler ({len(urunler)}) ──────────────────────")
    for u in urunler:
        fiyat = u.get("regular_price", "?")
        print(f"  [{u['id']}] {u['name']} — {fiyat}₺")
    print("────────────────────────────────────────\n")
    return urunler


def tam_kurulum():
    """Tüm kurulum adımlarını sırayla çalıştır."""
    print("=" * 50)
    print("İQ Elektronik — WooCommerce Tam Kurulum")
    print("=" * 50)

    print("\n[1/3] Bağlantı testi...")
    sonuc = baglanti_test()
    if not sonuc.get("basarili"):
        print("Bağlantı kurulamadı. Kurulum durduruldu.")
        return

    print("\n[2/3] Site bilgileri güncelleniyor...")
    site_bilgilerini_guncelle()

    print("\n[3/3] Kategoriler oluşturuluyor...")
    kategorileri_kur()

    print("\n✓ Kurulum tamamlandı!")
    site_ozeti()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IQ Elektronik WooCommerce Kurulum")
    parser.add_argument("komut", nargs="?", default="tam_kurulum",
                        choices=["tam_kurulum", "baglanti", "kategoriler",
                                 "site_bilgi", "ozet", "urunler"])
    args = parser.parse_args()

    komutlar = {
        "tam_kurulum":  tam_kurulum,
        "baglanti":     baglanti_test,
        "kategoriler":  kategorileri_kur,
        "site_bilgi":   site_bilgilerini_guncelle,
        "ozet":         site_ozeti,
        "urunler":      urunleri_listele,
    }
    komutlar[args.komut]()
