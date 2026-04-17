# -*- coding: utf-8 -*-
"""
IQ Elektronik Child Theme — Dağıtım Scripti
Çıktı: deploy/iq-elektronik-child.zip  (WordPress'e direkt yüklenebilir)

Kullanım: python deploy/deploy.py
"""

import zipfile
import shutil
from pathlib import Path

TEMA_KOKU = Path(__file__).resolve().parents[1] / "theme"
CIKTI     = Path(__file__).resolve().parent / "iq-elektronik-child.zip"

# Temada olması gereken dosyalar (yoksa boş oluştur)
ZORUNLU = {
    "screenshot.png": None,   # Opsiyonel — tema önizleme görseli
}


def zip_olustur():
    if not TEMA_KOKU.exists():
        print(f"✗ Tema klasörü bulunamadı: {TEMA_KOKU}")
        return

    # Önceki zip'i sil
    if CIKTI.exists():
        CIKTI.unlink()

    with zipfile.ZipFile(CIKTI, "w", zipfile.ZIP_DEFLATED) as zf:
        for dosya in sorted(TEMA_KOKU.rglob("*")):
            if dosya.is_file():
                arcname = Path("iq-elektronik-child") / dosya.relative_to(TEMA_KOKU)
                zf.write(dosya, arcname)
                print(f"  + {arcname}")

    boyut = CIKTI.stat().st_size / 1024
    print(f"\n✓ Zip oluşturuldu: {CIKTI}")
    print(f"  Boyut: {boyut:.1f} KB")
    print(f"\n  WordPress'te yüklemek için:")
    print(f"  Görünüm → Temalar → Tema Ekle → Tema Yükle → iq-elektronik-child.zip")


def wp_cli_komutlari():
    """WP-CLI ile tema aktivasyonu için komutlar."""
    print("\n─── WP-CLI Komutları (opsiyonel) ───────────────────────")
    print("wp theme install iq-elektronik-child.zip --activate")
    print("wp theme activate iq-elektronik-child")
    print("")
    print("─── Gerekli Eklentiler ──────────────────────────────────")
    eklentiler = [
        ("woocommerce",                 "WooCommerce"),
        ("electro",                     "Electro Theme (ana tema)"),
        ("slider-revolution",           "Slider Revolution"),
        ("yith-woocommerce-wishlist",   "YITH Wishlist"),
        ("yith-woocommerce-compare",    "YITH Compare"),
        ("woocommerce-quick-view",      "Quick View"),
        ("contact-form-7",              "Contact Form 7"),
        ("yoast-seo",                   "Yoast SEO"),
        ("w3-total-cache",              "W3 Total Cache"),
        ("wordfence",                   "Wordfence Security"),
        ("paytr-woocommerce",           "PayTR Ödeme (Türk)"),
        ("iyzico-woocommerce",          "iyzico Ödeme"),
        ("loco-translate",              "Loco Translate"),
        ("updraftplus",                 "UpdraftPlus Yedek"),
        ("mailchimp-for-wp",            "Mailchimp for WP"),
        ("woocommerce-pdf-invoices-packing-slips", "PDF Faturalar"),
    ]
    for slug, isim in eklentiler:
        print(f"wp plugin install {slug} --activate   # {isim}")
    print("─────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    zip_olustur()
    wp_cli_komutlari()
