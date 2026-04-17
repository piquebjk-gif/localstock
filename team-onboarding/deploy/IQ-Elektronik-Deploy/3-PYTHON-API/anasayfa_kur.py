# -*- coding: utf-8 -*-
"""
IQ Elektronik — Ana Sayfa & Sayfalar Kurulumu
"""

import sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

spec = importlib.util.spec_from_file_location("iq_setup", ROOT / "iq_setup.py")
iq_setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(iq_setup)
motor_olustur = iq_setup.motor_olustur


def _hakkimizda_html():
    return """<h2>İQ Elektronik Hakkında</h2>
<p>İQ Elektronik, elektronik ürünlerde kaliteli ve güvenilir hizmet anlayışıyla
Bayrampaşa/İstanbul'da hizmet vermektedir. <strong>Teknolojide Akıllı Tercih</strong>
sloganıyla müşterilerimize en uygun fiyat ve en kaliteli ürünleri sunuyoruz.</p>
<ul>
<li>Geniş ürün yelpazesi</li><li>Rekabetçi fiyatlar</li>
<li>Güvenli alışveriş</li><li>Hızlı kargo</li><li>7/24 müşteri desteği</li>
</ul>
<p>📍 Yenidoğan, Kızılay Sokağı No:41, 34040 Bayrampaşa/İstanbul<br>
📞 0544 440 56 77</p>"""


def _iletisim_html():
    return """<div class="row">
<div class="col-md-6">
<h3>İletişim Bilgileri</h3>
<p>📍 Yenidoğan, Kızılay Sokağı No:41<br>34040 Bayrampaşa / İstanbul</p>
<p>📞 <a href="tel:05444405677">0544 440 56 77</a></p>
<p>📸 <a href="https://www.instagram.com/iqelektronik/" target="_blank">@iqelektronik</a></p>
<p>👍 <a href="https://www.facebook.com/iqelectroniks/" target="_blank">facebook.com/iqelectroniks</a></p>
</div></div>
<div class="mt-4">
<iframe src="https://www.google.com/maps?q=Yenidoğan+Kızılay+Sokağı+No:41+Bayrampaşa+İstanbul&output=embed"
width="100%" height="350" style="border:0;border-radius:8px;" loading="lazy"></iframe>
</div>"""


SAYFALAR = [
    ("Ana Sayfa",   "front-page", "<!-- Ana sayfa Electro/Elementor ile düzenlenir -->", "publish"),
    ("Mağaza",      "magaza",     "[woocommerce_shop]",       "publish"),
    ("Sepet",       "sepet",      "[woocommerce_cart]",       "publish"),
    ("Ödeme",       "odeme",      "[woocommerce_checkout]",   "publish"),
    ("Hesabım",     "hesabim",    "[woocommerce_my_account]", "publish"),
    ("Hakkımızda",  "hakkimizda", _hakkimizda_html(),         "publish"),
    ("İletişim",    "iletisim",   _iletisim_html(),           "publish"),
    ("Gizlilik",    "gizlilik",   "<p>Gizlilik politikamız yakında yayınlanacaktır.</p>", "publish"),
    ("KVKK",        "kvkk",       "<p>KVKK metnimiz yakında yayınlanacaktır.</p>",        "publish"),
]


def sayfalar_olustur():
    wp = motor_olustur()
    sonuc = wp.baglantiyi_test_et()
    if not sonuc.get("basarili"):
        print(f"✗ Bağlantı hatası: {sonuc.get('hata')}")
        return {}

    mevcut = {s["slug"]: s["id"] for s in wp.sayfalar_listele(adet=100)}
    print(f"✓ Bağlı. Mevcut sayfa: {len(mevcut)}\n")

    ids = {}
    for baslik, slug, icerik, durum in SAYFALAR:
        if slug in mevcut:
            print(f"  — '{baslik}' mevcut (id={mevcut[slug]})")
            ids[slug] = mevcut[slug]
            continue
        r = wp.sayfa_olustur(baslik, icerik, durum=durum)
        if "id" in r:
            print(f"  ✓ '{baslik}' oluşturuldu — id={r['id']}")
            ids[slug] = r["id"]
        else:
            print(f"  ✗ '{baslik}': {r.get('hata', r)}")

    # WooCommerce sayfa ID atamaları
    atamalar = {
        "woocommerce_shop_page_id":      ids.get("magaza"),
        "woocommerce_cart_page_id":      ids.get("sepet"),
        "woocommerce_checkout_page_id":  ids.get("odeme"),
        "woocommerce_myaccount_page_id": ids.get("hesabim"),
    }
    for k, v in atamalar.items():
        if v:
            try:
                wp._wc_put(f"{wp.wc}/settings/advanced/{k}", {"value": str(v)})
            except Exception:
                pass

    if ids.get("front-page"):
        wp.site_ayarlarini_guncelle({
            "show_on_front": "page",
            "page_on_front": ids["front-page"],
        })
        print(f"\n  ✓ Ana sayfa statik ayarlandı (id={ids['front-page']})")

    print("\n✓ Sayfa kurulumu tamamlandı.")
    return ids


if __name__ == "__main__":
    sayfalar_olustur()
