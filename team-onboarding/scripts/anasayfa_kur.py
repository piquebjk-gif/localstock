# -*- coding: utf-8 -*-
"""
IQ Elektronik — Ana Sayfa & Sayfalar Kurulumu
WooCommerce sayfaları + Ana sayfa widget içeriği oluşturur.
"""

import sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

spec = importlib.util.spec_from_file_location("iq_setup", ROOT / "iq_setup.py")
iq_setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(iq_setup)
motor_olustur = iq_setup.motor_olustur

SAYFALAR = {
    "Ana Sayfa":       ("front-page",    "<!-- Ana sayfa Elementor/Electro ile düzenlenir -->"),
    "Mağaza":          ("shop",          "<!-- WooCommerce mağaza sayfası -->"),
    "Sepet":           ("cart",          "[woocommerce_cart]"),
    "Ödeme":           ("checkout",      "[woocommerce_checkout]"),
    "Hesabım":         ("my-account",    "[woocommerce_my_account]"),
    "Hakkımızda":      ("hakkimizda",    _hakkimizda_html()),
    "İletişim":        ("iletisim",      _iletisim_html()),
    "Gizlilik":        ("gizlilik",      "<p>Gizlilik politikamız yakında yayınlanacaktır.</p>"),
    "KVKK":            ("kvkk",          "<p>KVKK metnimiz yakında yayınlanacaktır.</p>"),
}


def _hakkimizda_html():
    return """
<h2>İQ Elektronik Hakkında</h2>
<p>İQ Elektronik, elektronik ürünlerde kaliteli ve güvenilir hizmet anlayışıyla
Bayrampaşa/İstanbul'da hizmet vermektedir. <strong>Teknolojide Akıllı Tercih</strong>
sloganıyla müşterilerimize en uygun fiyat ve en kaliteli ürünleri sunuyoruz.</p>
<ul>
  <li>Geniş ürün yelpazesi</li>
  <li>Rekabetçi fiyatlar</li>
  <li>Güvenli alışveriş</li>
  <li>Hızlı kargo</li>
  <li>7/24 müşteri desteği</li>
</ul>
<h3>İletişim</h3>
<p>📍 Yenidoğan, Kızılay Sokağı No:41, 34040 Bayrampaşa/İstanbul<br>
📞 0544 440 56 77</p>
"""


def _iletisim_html():
    return """
<div class="row">
  <div class="col-md-6">
    <h3>İletişim Bilgileri</h3>
    <p>📍 Yenidoğan, Kızılay Sokağı No:41<br>34040 Bayrampaşa / İstanbul</p>
    <p>📞 <a href="tel:05444405677">0544 440 56 77</a></p>
    <p>📸 <a href="https://www.instagram.com/iqelektronik/" target="_blank">@iqelektronik</a></p>
    <p>👍 <a href="https://www.facebook.com/iqelectroniks/" target="_blank">facebook.com/iqelectroniks</a></p>
  </div>
  <div class="col-md-6">
    [contact-form-7 id="" title="İletişim Formu"]
  </div>
</div>
<div class="mt-4">
  <iframe
    src="https://www.google.com/maps?q=Yenidoğan,+Kızılay+Sokağı+No:41,+34040+Bayrampaşa/İstanbul&output=embed"
    width="100%" height="350" style="border:0;border-radius:8px;" loading="lazy">
  </iframe>
</div>
"""


def sayfalar_olustur():
    wp = motor_olustur()
    sonuc = wp.baglantiyi_test_et()
    if not sonuc.get("basarili"):
        print(f"✗ Bağlantı hatası: {sonuc.get('hata')}")
        return

    mevcut = {s["slug"]: s["id"] for s in wp.sayfalar_listele(adet=100)}
    print(f"✓ Bağlı. Mevcut sayfa sayısı: {len(mevcut)}\n")

    olusturulan = {}

    for baslik, (slug, icerik) in SAYFALAR.items():
        if slug in mevcut:
            print(f"  — '{baslik}' (/{slug}) zaten mevcut")
            olusturulan[slug] = mevcut[slug]
            continue
        r = wp.sayfa_olustur(baslik, icerik, durum="publish")
        if "id" in r:
            print(f"  ✓ '{baslik}' oluşturuldu — id={r['id']}, slug=/{r.get('slug','')}")
            olusturulan[slug] = r["id"]
        else:
            print(f"  ✗ '{baslik}': {r.get('hata', r)}")

    # WooCommerce sayfa ID'lerini ayarla
    wc_sayfalar = {
        "woocommerce_shop_page_id":       olusturulan.get("shop"),
        "woocommerce_cart_page_id":       olusturulan.get("cart"),
        "woocommerce_checkout_page_id":   olusturulan.get("checkout"),
        "woocommerce_myaccount_page_id":  olusturulan.get("my-account"),
    }
    for key, pid in wc_sayfalar.items():
        if pid:
            try:
                wp._wc_put(f"{wp.wc}/settings/advanced/{key}", {"value": str(pid)})
            except Exception:
                pass

    # Statik ön sayfa
    front_id = olusturulan.get("front-page")
    if front_id:
        wp.site_ayarlarini_guncelle({
            "show_on_front":  "page",
            "page_on_front":  front_id,
            "page_for_posts": 0,
        })
        print(f"\n  ✓ Ana sayfa ayarlandı (id={front_id})")

    print("\n✓ Sayfa kurulumu tamamlandı.")
    return olusturulan


if __name__ == "__main__":
    sayfalar_olustur()
