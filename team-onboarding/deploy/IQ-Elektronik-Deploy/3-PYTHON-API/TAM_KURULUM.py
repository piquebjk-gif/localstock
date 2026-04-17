# -*- coding: utf-8 -*-
"""
IQ Elektronik — TAM KURULUM (TEK TUŞLA)
========================================
Sırasıyla:
  1. WordPress bağlantı testi
  2. Site başlığı / açıklaması
  3. WooCommerce + kargo + vergi + kupon ayarları
  4. Sayfalar (Ana Sayfa, Mağaza, Sepet, Ödeme, Hesabım, Hakkımızda, İletişim)
  5. Ürün kategorileri
  6. Child tema zip oluştur
  7. Özet rapor

Çalıştır:
    python TAM_KURULUM.py
    python TAM_KURULUM.py --urunler /path/to/OtoGorseller   (ürünleri de yükle)
    python TAM_KURULUM.py --kuru                             (test — gerçek değişiklik yok)
"""

import sys
import argparse
import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))


# ── Modülleri dinamik yükle ───────────────────────────────────────────────────
def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


iq_setup   = _yukle("iq_setup",   ROOT / "iq_setup.py")
motor_olustur = iq_setup.motor_olustur
_cfg          = iq_setup._cfg


# ── Yardımcı ─────────────────────────────────────────────────────────────────
def _baslik(metin):
    print(f"\n{'═'*55}")
    print(f"  {metin}")
    print(f"{'═'*55}")


def _adim(no, toplam, metin):
    print(f"\n[{no}/{toplam}] {metin}")


# ── Adımlar ───────────────────────────────────────────────────────────────────
def adim_baglanti(wp):
    sonuc = wp.baglantiyi_test_et()
    if not sonuc.get("basarili"):
        print(f"  ✗ Bağlantı BAŞARISIZ: {sonuc.get('hata')}")
        sys.exit(1)
    print(f"  ✓ {sonuc['site_adi']}  ({sonuc['url']})")
    return True


def adim_site_bilgi(wp):
    cfg = _cfg()
    f = cfg["firma"]
    r = wp.site_ayarlarini_guncelle({
        "title":            f["ad"],
        "description":      f["slogan"],
        "timezone_string":  "Europe/Istanbul",
        "date_format":      "d.m.Y",
        "time_format":      "H:i",
    })
    print(f"  ✓ '{f['ad']} — {f['slogan']}'")


def adim_wc_ayarlar(wp):
    # Para birimi
    try:
        wp._wc_put(f"{wp.wc}/settings/general/woocommerce_currency",           {"value": "TRY"})
        wp._wc_put(f"{wp.wc}/settings/general/woocommerce_currency_pos",        {"value": "right_space"})
        wp._wc_put(f"{wp.wc}/settings/general/woocommerce_price_decimal_sep",   {"value": ","})
        wp._wc_put(f"{wp.wc}/settings/general/woocommerce_price_thousand_sep",  {"value": "."})
        wp._wc_put(f"{wp.wc}/settings/general/woocommerce_price_num_decimals",  {"value": "2"})
        print("  ✓ Para birimi: ₺ (TRY), format: 1.299,00 ₺")
    except Exception as e:
        print(f"  ⚠ Para birimi: {e}")

    # Kargo bölgesi
    try:
        zone = wp._wc_post(f"{wp.wc}/shipping/zones", {"name": "Türkiye", "order": 0})
        zid  = zone.get("id")
        if not zid:
            for z in (wp._wc_get(f"{wp.wc}/shipping/zones") or []):
                if z.get("name") == "Türkiye":
                    zid = z["id"]; break
        if zid:
            wp._wc_post(f"{wp.wc}/shipping/zones/{zid}/locations",
                        [{"code": "TR", "type": "country"}])
            wp._wc_post(f"{wp.wc}/shipping/zones/{zid}/methods",
                        {"method_id": "flat_rate",
                         "settings": {"title": {"value": "Standart Kargo"},
                                      "cost":  {"value": "29.90"}}})
            wp._wc_post(f"{wp.wc}/shipping/zones/{zid}/methods",
                        {"method_id": "free_shipping",
                         "settings": {"title":      {"value": "Ücretsiz Kargo (500₺+)"},
                                      "min_amount": {"value": "500"},
                                      "requires":   {"value": "min_amount"}}})
            print(f"  ✓ Kargo: Standart 29,90₺ + Ücretsiz (500₺+)")
    except Exception as e:
        print(f"  ⚠ Kargo: {e}")

    # KDV
    try:
        wp._wc_put(f"{wp.wc}/settings/tax/woocommerce_calc_taxes",        {"value": "yes"})
        wp._wc_put(f"{wp.wc}/settings/tax/woocommerce_tax_display_shop",  {"value": "incl"})
        wp._wc_put(f"{wp.wc}/settings/tax/woocommerce_tax_display_cart",  {"value": "incl"})
        r = wp._wc_post(f"{wp.wc}/taxes",
                        {"country": "TR", "rate": "20.0000", "name": "KDV",
                         "shipping": True, "priority": 1})
        print(f"  ✓ Vergi: KDV %20 ({'eklendi' if 'id' in r else 'mevcut'})")
    except Exception as e:
        print(f"  ⚠ Vergi: {e}")

    # Kupon
    try:
        r = wp._wc_post(f"{wp.wc}/coupons",
                        {"code": "IQ50", "discount_type": "fixed_cart",
                         "amount": "50", "minimum_amount": "200",
                         "usage_limit": 1, "usage_limit_per_user": 1,
                         "description": "Yeni üye 50₺ indirim"})
        print(f"  ✓ Kupon: IQ50 (50₺, min 200₺, tek kullanım)")
    except Exception as e:
        print(f"  ⚠ Kupon: {e}")


def adim_sayfalar(wp):
    mevcut = {s["slug"]: s["id"] for s in wp.sayfalar_listele(adet=100)}
    sayfalik = [
        ("Ana Sayfa",   "front-page",   "<!-- Ana sayfa Electro/Elementor ile düzenlenir -->", "publish"),
        ("Mağaza",      "magaza",       "[woocommerce_shop]",        "publish"),
        ("Sepet",       "sepet",        "[woocommerce_cart]",        "publish"),
        ("Ödeme",       "odeme",        "[woocommerce_checkout]",    "publish"),
        ("Hesabım",     "hesabim",      "[woocommerce_my_account]",  "publish"),
        ("Hakkımızda",  "hakkimizda",   "<h2>İQ Elektronik</h2><p>Bayrampaşa İstanbul'da elektronik ürünlerde güvenilir adres.</p>", "publish"),
        ("İletişim",    "iletisim",     "<p>📍 Yenidoğan, Kızılay Sk. No:41 Bayrampaşa/İstanbul<br>📞 0544 440 56 77</p>", "publish"),
    ]
    ids = {}
    for baslik, slug, icerik, durum in sayfalik:
        if slug in mevcut:
            print(f"  — '{baslik}' mevcut"); ids[slug] = mevcut[slug]; continue
        r = wp.sayfa_olustur(baslik, icerik, durum=durum)
        if "id" in r:
            print(f"  ✓ '{baslik}' oluşturuldu (id={r['id']})")
            ids[slug] = r["id"]
        else:
            print(f"  ✗ '{baslik}': {r.get('hata','')}")

    # WC sayfa atamalarını güncelle
    atamalar = {
        "woocommerce_shop_page_id":      ids.get("magaza"),
        "woocommerce_cart_page_id":      ids.get("sepet"),
        "woocommerce_checkout_page_id":  ids.get("odeme"),
        "woocommerce_myaccount_page_id": ids.get("hesabim"),
    }
    for k, v in atamalar.items():
        if v:
            try: wp._wc_put(f"{wp.wc}/settings/advanced/{k}", {"value": str(v)})
            except Exception: pass

    # Statik ön sayfa
    if ids.get("front-page"):
        wp.site_ayarlarini_guncelle({
            "show_on_front": "page",
            "page_on_front": ids["front-page"],
        })
        print(f"  ✓ Ana sayfa statik olarak ayarlandı")


def adim_kategoriler(wp):
    cfg = _cfg()
    mevcut = {k["name"].lower(): k["id"] for k in wp.wc_kategoriler_listele()}
    for kat in cfg["kategoriler"]:
        isim = kat["isim"]
        if isim.lower() in mevcut:
            print(f"  — '{isim}' mevcut"); continue
        r = wp.wc_kategori_olustur(isim)
        print(f"  {'✓' if 'id' in r else '✗'} '{isim}'" + (f" (id={r['id']})" if "id" in r else f": {r.get('hata','')}"))


def adim_zip(kuru):
    deploy_py = ROOT / "deploy" / "deploy.py"
    if not deploy_py.exists():
        print("  ⚠ deploy.py bulunamadı"); return
    if kuru:
        print("  — [KURU] Zip oluşturulmadı"); return
    r = subprocess.run([sys.executable, str(deploy_py)], capture_output=True, text=True)
    if r.returncode == 0:
        zip_yolu = ROOT / "deploy" / "iq-elektronik-child.zip"
        print(f"  ✓ {zip_yolu}")
    else:
        print(f"  ⚠ Zip hatası: {r.stderr[:200]}")


def adim_urunler(wp, klasor, kuru):
    urun_py = ROOT / "urun_yukle.py"
    if not urun_py.exists():
        print("  ⚠ urun_yukle.py bulunamadı"); return
    if kuru:
        print(f"  — [KURU] Ürün yükleme atlandı ({klasor})"); return
    r = subprocess.run(
        [sys.executable, str(urun_py), klasor] + (["--kuru"] if kuru else []),
        capture_output=False, text=True
    )


# ── Ana Akış ─────────────────────────────────────────────────────────────────
def tam_kurulum(urunler_klasoru=None, kuru=False):
    _baslik(f"İQ Elektronik — {'[KURU ÇALIŞTIRMA] ' if kuru else ''}TAM KURULUM")

    wp     = motor_olustur()
    toplam = 6 + (1 if urunler_klasoru else 0)

    _adim(1, toplam, "Bağlantı testi");       adim_baglanti(wp)
    _adim(2, toplam, "Site bilgileri");        adim_site_bilgi(wp)   if not kuru else print("  — atlandı")
    _adim(3, toplam, "WooCommerce ayarları"); adim_wc_ayarlar(wp)   if not kuru else print("  — atlandı")
    _adim(4, toplam, "Sayfalar");             adim_sayfalar(wp)     if not kuru else print("  — atlandı")
    _adim(5, toplam, "Kategoriler");          adim_kategoriler(wp)  if not kuru else print("  — atlandı")
    _adim(6, toplam, "Child tema zip");       adim_zip(kuru)

    if urunler_klasoru:
        _adim(7, toplam, f"Ürün yükleme ({urunler_klasoru})")
        adim_urunler(wp, urunler_klasoru, kuru)

    # Özet
    _baslik("ÖZET RAPOR")
    try:
        ozet = wp.site_ozeti_al()
        for k, v in ozet.items():
            print(f"  {k}: {v}")
    except Exception:
        pass

    print(f"\n✅ Kurulum {'simülasyonu' if kuru else 'tamamlandı'}!")
    print(f"\nSonraki adımlar:")
    print(f"  1. deploy/iq-elektronik-child.zip → WP Görünüm → Temalar → Yükle")
    print(f"  2. Gerekli eklentileri kur (deploy.py listesine bak)")
    print(f"  3. Electro Demo içeriği import et → kendi içeriğinle değiştir")
    print(f"  4. Slider Revolution → hero slider ekle")
    print(f"  5. Ana sayfa widget'larını Elementor ile düzenle\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IQ Elektronik Tam Kurulum")
    parser.add_argument("--urunler", metavar="KLASOR", help="OtoGorseller klasör yolu")
    parser.add_argument("--kuru",    action="store_true", help="Test modu")
    args = parser.parse_args()
    tam_kurulum(urunler_klasoru=args.urunler, kuru=args.kuru)
