# -*- coding: utf-8 -*-
"""
IQ Elektronik — WooCommerce & WordPress Tam Ayar Scripti
Çalıştır: python wc_ayarlar.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from team_onboarding_iq.iq_setup import motor_olustur, _cfg   # noqa


def _wp(wp):
    """WordPress genel site ayarlarını uygula."""
    cfg = _cfg()
    f = cfg["firma"]
    print("[WP] Site başlığı ve açıklaması...")
    wp.site_ayarlarini_guncelle({
        "title":       f["ad"],
        "description": f["slogan"],
        "timezone_string": "Europe/Istanbul",
        "date_format":  "d.m.Y",
        "time_format":  "H:i",
        "start_of_week": 1,
        "blogdescription": f["slogan"],
    })
    print("  ✓ WordPress site ayarları güncellendi")


def _wc(wp):
    """WooCommerce ayarlarını REST API ile güncelle."""
    print("[WC] WooCommerce ayarları...")
    ayarlar = [
        # Para birimi
        ("woocommerce_currency",                "TRY"),
        ("woocommerce_currency_pos",            "right_space"),
        ("woocommerce_price_decimal_sep",       ","),
        ("woocommerce_price_thousand_sep",      "."),
        ("woocommerce_price_num_decimals",      "2"),
        # Ölçü birimleri
        ("woocommerce_weight_unit",             "kg"),
        ("woocommerce_dimension_unit",          "cm"),
        # Mağaza adresi
        ("woocommerce_store_address",           "Yenidoğan, Kızılay Sokağı No:41"),
        ("woocommerce_store_city",              "İstanbul"),
        ("woocommerce_default_country",         "TR:34"),
        ("woocommerce_store_postcode",          "34040"),
        # Kargo
        ("woocommerce_ship_to_countries",       "all"),
        ("woocommerce_shipping_debug_mode",     "no"),
        # Vergi
        ("woocommerce_calc_taxes",              "yes"),
        ("woocommerce_tax_display_shop",        "incl"),
        ("woocommerce_tax_display_cart",        "incl"),
        # Katalog
        ("woocommerce_shop_page_display",       ""),
        ("woocommerce_category_archive_display", ""),
        ("woocommerce_default_catalog_orderby", "popularity"),
        ("woocommerce_catalog_columns",         "4"),
        ("woocommerce_catalog_rows",            "4"),
        # Sepet
        ("woocommerce_cart_redirect_after_add", "no"),
        ("woocommerce_enable_ajax_add_to_cart", "yes"),
        # Hesap
        ("woocommerce_enable_guest_checkout",   "yes"),
        ("woocommerce_enable_checkout_login_reminder", "yes"),
        ("woocommerce_enable_signup_and_login_from_checkout", "yes"),
        # E-posta
        ("woocommerce_email_from_name",         "İQ Elektronik"),
        ("woocommerce_email_from_address",      "info@iqelektronik.com"),
        # Stok
        ("woocommerce_manage_stock",            "yes"),
        ("woocommerce_notify_low_stock",        "yes"),
        ("woocommerce_notify_no_stock",         "yes"),
        ("woocommerce_notify_low_stock_amount", "5"),
    ]

    for option, value in ayarlar:
        try:
            r = wp._post(
                f"{wp.base}/wp-json/wp/v2/settings",
                {option: value}
            )
        except Exception:
            pass  # bazı option'lar Settings API'da yoksa atla

    # wp_options üzerinden doğrudan ayar (genel WP API yolu)
    # Alternatif: WooCommerce REST API /settings endpoint
    try:
        # WC General grubu
        base_wc = f"{wp.wc}/settings/general"
        # Para birimi
        wp._wc_put(f"{base_wc}/woocommerce_currency",          {"value": "TRY"})
        wp._wc_put(f"{base_wc}/woocommerce_currency_pos",       {"value": "right_space"})
        wp._wc_put(f"{base_wc}/woocommerce_price_decimal_sep",  {"value": ","})
        wp._wc_put(f"{base_wc}/woocommerce_price_thousand_sep", {"value": "."})
        wp._wc_put(f"{base_wc}/woocommerce_price_num_decimals", {"value": "2"})

        # WC Products grubu
        base_prod = f"{wp.wc}/settings/products"
        wp._wc_put(f"{base_prod}/woocommerce_weight_unit",    {"value": "kg"})
        wp._wc_put(f"{base_prod}/woocommerce_dimension_unit", {"value": "cm"})

        # WC Tax grubu
        base_tax = f"{wp.wc}/settings/tax"
        wp._wc_put(f"{base_tax}/woocommerce_calc_taxes",       {"value": "yes"})
        wp._wc_put(f"{base_tax}/woocommerce_tax_display_shop", {"value": "incl"})
        wp._wc_put(f"{base_tax}/woocommerce_tax_display_cart", {"value": "incl"})

        # WC Checkout grubu
        base_co = f"{wp.wc}/settings/checkout"
        wp._wc_put(f"{base_co}/woocommerce_enable_guest_checkout", {"value": "yes"})

        print("  ✓ WooCommerce API ayarları uygulandı")
    except Exception as e:
        print(f"  ⚠ WC API ayar hatası (bazı ayarlar atlandı): {e}")


def _kategoriler(wp):
    """Ana kategorileri oluştur."""
    cfg = _cfg()
    print("[WC] Kategoriler kontrol ediliyor...")
    mevcut = {k["name"].lower(): k["id"] for k in wp.wc_kategoriler_listele()}
    for kat in cfg["kategoriler"]:
        isim = kat["isim"]
        if isim.lower() in mevcut:
            print(f"  — '{isim}' mevcut")
            continue
        r = wp.wc_kategori_olustur(isim)
        if "id" in r:
            print(f"  ✓ '{isim}' oluşturuldu (id={r['id']})")
        else:
            print(f"  ✗ '{isim}': {r.get('hata', r)}")


def _kargo(wp):
    """Ücretsiz kargo (500₺+) ve sabit kargo zonu ekle."""
    print("[WC] Kargo bölgeleri...")
    # Türkiye bölgesi oluştur
    try:
        zone_r = wp._wc_post(f"{wp.wc}/shipping/zones", {"name": "Türkiye", "order": 0})
        zone_id = zone_r.get("id")
        if not zone_id:
            zones = wp._wc_get(f"{wp.wc}/shipping/zones") or []
            for z in zones:
                if z.get("name") == "Türkiye":
                    zone_id = z["id"]
                    break
        if zone_id:
            # Bölgeye Türkiye ekle
            wp._wc_post(f"{wp.wc}/shipping/zones/{zone_id}/locations",
                        [{"code": "TR", "type": "country"}])
            # Sabit kargo metodu
            wp._wc_post(f"{wp.wc}/shipping/zones/{zone_id}/methods", {
                "method_id": "flat_rate",
                "settings": {"title": {"value": "Standart Kargo"},
                             "cost":  {"value": "29.90"}}
            })
            # Ücretsiz kargo metodu (500₺+)
            wp._wc_post(f"{wp.wc}/shipping/zones/{zone_id}/methods", {
                "method_id": "free_shipping",
                "settings": {"title":        {"value": "Ücretsiz Kargo (500₺+)"},
                             "min_amount":   {"value": "500"},
                             "requires":     {"value": "min_amount"}}
            })
            print(f"  ✓ Kargo bölgesi (Türkiye) id={zone_id}")
    except Exception as e:
        print(f"  ⚠ Kargo bölgesi hatası: {e}")


def _vergi(wp):
    """KDV oranı (%20) ekle."""
    print("[WC] Vergi oranı...")
    try:
        r = wp._wc_post(f"{wp.wc}/taxes", {
            "country":  "TR",
            "rate":     "20.0000",
            "name":     "KDV",
            "shipping": True,
            "priority": 1,
            "compound": False,
        })
        if "id" in r:
            print(f"  ✓ KDV (%20) eklendi (id={r['id']})")
        else:
            print(f"  — KDV zaten mevcut olabilir: {r.get('hata','')}")
    except Exception as e:
        print(f"  ⚠ Vergi hatası: {e}")


def _coupon(wp):
    """İlk üyelik kuponu: IQ50 — 50₺ indirim."""
    print("[WC] Kupon...")
    try:
        r = wp._wc_post(f"{wp.wc}/coupons", {
            "code":              "IQ50",
            "discount_type":     "fixed_cart",
            "amount":            "50",
            "description":       "Yeni üye hoş geldin kuponu — 50₺ indirim",
            "usage_limit":       1,
            "usage_limit_per_user": 1,
            "minimum_amount":    "200",
        })
        if "id" in r:
            print(f"  ✓ Kupon IQ50 oluşturuldu (id={r['id']})")
        else:
            print(f"  — Kupon: {r.get('hata', r)}")
    except Exception as e:
        print(f"  ⚠ Kupon hatası: {e}")


def tam_ayar():
    wp = motor_olustur()
    sonuc = wp.baglantiyi_test_et()
    if not sonuc.get("basarili"):
        print(f"✗ Bağlantı hatası: {sonuc.get('hata')}")
        return

    print(f"✓ Bağlı: {sonuc['site_adi']} ({sonuc['url']})\n")
    _wp(wp)
    _wc(wp)
    _kategoriler(wp)
    _kargo(wp)
    _vergi(wp)
    _coupon(wp)
    print("\n✓ Tüm WooCommerce ayarları tamamlandı.")


if __name__ == "__main__":
    # path fix — scripts/ içinden import
    import importlib, sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import importlib.util, types

    # iq_setup'ı team-onboarding/ kökünden import et
    spec = importlib.util.spec_from_file_location(
        "iq_setup",
        Path(__file__).resolve().parents[1] / "iq_setup.py"
    )
    iq_setup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(iq_setup)
    motor_olustur = iq_setup.motor_olustur
    _cfg          = iq_setup._cfg

    tam_ayar()
