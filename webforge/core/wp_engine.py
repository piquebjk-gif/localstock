# -*- coding: utf-8 -*-
"""
WebForge AI Engine — WordPress REST API Engine
WordPress'in taa dibine tam erişim:
Posts, Pages, Media, Products (WooCommerce), Users,
Plugins, Themes, Settings, Menus, Custom Post Types.
"""

import base64
import json
import mimetypes
from pathlib import Path
from typing import Optional

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    requests = None

try:
    from loguru import logger
except ImportError:
    import logging; logger = logging.getLogger(__name__)


class WPEngine:
    """
    WordPress REST API v2 tam erişim motoru.
    Application Password ile kimlik doğrulama (en güvenli yöntem).
    """

    def __init__(self, site_url: str, kullanici: str, uygulama_sifresi: str):
        self.base = site_url.rstrip("/")
        self.api  = f"{self.base}/wp-json/wp/v2"
        self.wc   = f"{self.base}/wp-json/wc/v3"
        self.auth = HTTPBasicAuth(kullanici, uygulama_sifresi.replace(" ", ""))
        self.ses  = requests.Session() if requests else None
        if self.ses:
            self.ses.auth = self.auth
            self.ses.headers.update({
                "Content-Type": "application/json",
                "User-Agent": "WebForge-AI-Engine/1.0"
            })
        self._wc_key    = ""
        self._wc_secret = ""

    def wc_kimlik_ayarla(self, key: str, secret: str):
        """WooCommerce API key ayarla."""
        self._wc_key    = key
        self._wc_secret = secret

    # ── Bağlantı Testi ────────────────────────────────────────────────────────

    def baglantiyi_test_et(self) -> dict:
        try:
            r = self.ses.get(f"{self.base}/wp-json", timeout=10)
            if r.status_code == 200:
                d = r.json()
                return {"basarili": True, "site_adi": d.get("name", ""), "url": self.base, "wp_versiyon": d.get("description", "")}
            return {"basarili": False, "hata": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"basarili": False, "hata": str(e)}

    # ── Genel CRUD Yardımcısı ─────────────────────────────────────────────────

    def _get(self, endpoint: str, params: dict = None) -> dict | list:
        try:
            r = self.ses.get(endpoint, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"WP GET {endpoint}: {e}")
            return {}

    def _post(self, endpoint: str, veri: dict = None, dosyalar=None) -> dict:
        try:
            if dosyalar:
                r = self.ses.post(endpoint, files=dosyalar, timeout=30)
            else:
                r = self.ses.post(endpoint, json=veri, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"WP POST {endpoint}: {e}")
            return {"hata": str(e)}

    def _put(self, endpoint: str, veri: dict) -> dict:
        try:
            r = self.ses.put(endpoint, json=veri, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"WP PUT {endpoint}: {e}")
            return {"hata": str(e)}

    def _delete(self, endpoint: str, force: bool = True) -> dict:
        try:
            r = self.ses.delete(endpoint, params={"force": force}, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"WP DELETE {endpoint}: {e}")
            return {"hata": str(e)}

    # ══════════════════════════════════════════════════════════════════════════
    # POSTS
    # ══════════════════════════════════════════════════════════════════════════

    def yazilar_listele(self, sayfa: int = 1, adet: int = 20,
                        durum: str = "any", arama: str = "") -> list:
        params = {"page": sayfa, "per_page": adet, "status": durum}
        if arama:
            params["search"] = arama
        return self._get(f"{self.api}/posts", params) or []

    def yazi_al(self, post_id: int) -> dict:
        return self._get(f"{self.api}/posts/{post_id}") or {}

    def yazi_olustur(self, baslik: str, icerik: str, durum: str = "draft",
                     kategori_idler: list = None, etiket_idler: list = None,
                     featured_media: int = None, meta: dict = None) -> dict:
        veri = {"title": baslik, "content": icerik, "status": durum}
        if kategori_idler:  veri["categories"] = kategori_idler
        if etiket_idler:    veri["tags"] = etiket_idler
        if featured_media:  veri["featured_media"] = featured_media
        if meta:            veri["meta"] = meta
        return self._post(f"{self.api}/posts", veri)

    def yazi_guncelle(self, post_id: int, veri: dict) -> dict:
        return self._put(f"{self.api}/posts/{post_id}", veri)

    def yazi_sil(self, post_id: int) -> dict:
        return self._delete(f"{self.api}/posts/{post_id}")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGES
    # ══════════════════════════════════════════════════════════════════════════

    def sayfalar_listele(self, adet: int = 50) -> list:
        return self._get(f"{self.api}/pages", {"per_page": adet}) or []

    def sayfa_olustur(self, baslik: str, icerik: str, durum: str = "draft",
                      ust_sayfa: int = 0, sablonlar: str = "") -> dict:
        veri = {"title": baslik, "content": icerik, "status": durum}
        if ust_sayfa:  veri["parent"] = ust_sayfa
        if sablonlar:  veri["template"] = sablonlar
        return self._post(f"{self.api}/pages", veri)

    def sayfa_guncelle(self, page_id: int, veri: dict) -> dict:
        return self._put(f"{self.api}/pages/{page_id}", veri)

    def sayfa_sil(self, page_id: int) -> dict:
        return self._delete(f"{self.api}/pages/{page_id}")

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIA (Görsel Yönetimi)
    # ══════════════════════════════════════════════════════════════════════════

    def medya_listele(self, adet: int = 20, tip: str = "image") -> list:
        return self._get(f"{self.api}/media", {"per_page": adet, "media_type": tip}) or []

    def gorsel_yukle(self, dosya_yolu: str, baslik: str = "",
                     alt_metin: str = "") -> dict:
        """Yerel dosyayı WordPress'e yükle."""
        dosya = Path(dosya_yolu)
        if not dosya.exists():
            return {"hata": f"Dosya bulunamadı: {dosya_yolu}"}
        mime = mimetypes.guess_type(dosya_yolu)[0] or "image/jpeg"
        headers_old = self.ses.headers.copy()
        self.ses.headers.pop("Content-Type", None)
        try:
            with open(dosya_yolu, "rb") as f:
                r = self.ses.post(
                    f"{self.api}/media",
                    headers={"Content-Disposition": f'attachment; filename="{dosya.name}"',
                             "Content-Type": mime},
                    data=f,
                    timeout=60
                )
            r.raise_for_status()
            sonuc = r.json()
            if baslik or alt_metin:
                guncelle = {}
                if baslik:    guncelle["title"] = {"raw": baslik}
                if alt_metin: guncelle["alt_text"] = alt_metin
                self._put(f"{self.api}/media/{sonuc['id']}", guncelle)
            return sonuc
        except Exception as e:
            return {"hata": str(e)}
        finally:
            self.ses.headers.update(headers_old)

    def gorsel_url_yukle(self, url: str, dosya_adi: str = "") -> dict:
        """URL'den görseli indirip WordPress'e yükle."""
        try:
            r = requests.get(url, timeout=20, stream=True)
            r.raise_for_status()
            if not dosya_adi:
                dosya_adi = url.split("/")[-1].split("?")[0] or "image.jpg"
            gecici = Path("/tmp") / dosya_adi
            with open(gecici, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return self.gorsel_yukle(str(gecici))
        except Exception as e:
            return {"hata": str(e)}

    def medya_sil(self, media_id: int) -> dict:
        return self._delete(f"{self.api}/media/{media_id}")

    # ══════════════════════════════════════════════════════════════════════════
    # KATEGORİLER & ETİKETLER
    # ══════════════════════════════════════════════════════════════════════════

    def kategoriler_listele(self, adet: int = 100) -> list:
        return self._get(f"{self.api}/categories", {"per_page": adet}) or []

    def kategori_olustur(self, isim: str, ust: int = 0, aciklama: str = "") -> dict:
        return self._post(f"{self.api}/categories",
                          {"name": isim, "parent": ust, "description": aciklama})

    def etiketler_listele(self, adet: int = 100) -> list:
        return self._get(f"{self.api}/tags", {"per_page": adet}) or []

    def etiket_olustur(self, isim: str) -> dict:
        return self._post(f"{self.api}/tags", {"name": isim})

    # ══════════════════════════════════════════════════════════════════════════
    # KULLANICILAR
    # ══════════════════════════════════════════════════════════════════════════

    def kullanicilar_listele(self) -> list:
        return self._get(f"{self.api}/users", {"per_page": 100}) or []

    def kullanici_olustur(self, kullanici_adi: str, email: str,
                          sifre: str, rol: str = "editor") -> dict:
        return self._post(f"{self.api}/users",
                          {"username": kullanici_adi, "email": email,
                           "password": sifre, "roles": [rol]})

    def kullanici_guncelle(self, user_id: int, veri: dict) -> dict:
        return self._put(f"{self.api}/users/{user_id}", veri)

    def kullanici_sil(self, user_id: int, yeniden_atama: int = 1) -> dict:
        try:
            r = self.ses.delete(f"{self.api}/users/{user_id}",
                                params={"force": True, "reassign": yeniden_atama})
            return r.json()
        except Exception as e:
            return {"hata": str(e)}

    # ══════════════════════════════════════════════════════════════════════════
    # WOOCOMMERCE ÜRÜNLER
    # ══════════════════════════════════════════════════════════════════════════

    def _wc_get(self, endpoint: str, params: dict = None) -> list | dict:
        try:
            r = requests.get(endpoint, auth=(self._wc_key, self._wc_secret),
                             params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"WC GET {endpoint}: {e}")
            return []

    def _wc_post(self, endpoint: str, veri: dict) -> dict:
        try:
            r = requests.post(endpoint, auth=(self._wc_key, self._wc_secret),
                              json=veri, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"hata": str(e)}

    def _wc_put(self, endpoint: str, veri: dict) -> dict:
        try:
            r = requests.put(endpoint, auth=(self._wc_key, self._wc_secret),
                             json=veri, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"hata": str(e)}

    def _wc_delete(self, endpoint: str) -> dict:
        try:
            r = requests.delete(endpoint, auth=(self._wc_key, self._wc_secret),
                                params={"force": True}, timeout=15)
            return r.json()
        except Exception as e:
            return {"hata": str(e)}

    def urunler_listele(self, sayfa: int = 1, adet: int = 20,
                        kategori: int = None, arama: str = "") -> list:
        params = {"page": sayfa, "per_page": adet}
        if kategori: params["category"] = kategori
        if arama:    params["search"] = arama
        return self._wc_get(f"{self.wc}/products", params) or []

    def urun_al(self, urun_id: int) -> dict:
        return self._wc_get(f"{self.wc}/products/{urun_id}") or {}

    def urun_olustur(self, veri: dict) -> dict:
        """
        veri örneği:
        {
          "name": "Ürün Adı",
          "type": "simple",
          "regular_price": "100.00",
          "description": "...",
          "short_description": "...",
          "categories": [{"id": 1}],
          "images": [{"src": "https://..."}],
          "manage_stock": True,
          "stock_quantity": 10
        }
        """
        return self._wc_post(f"{self.wc}/products", veri)

    def urun_guncelle(self, urun_id: int, veri: dict) -> dict:
        return self._wc_put(f"{self.wc}/products/{urun_id}", veri)

    def urun_sil(self, urun_id: int) -> dict:
        return self._wc_delete(f"{self.wc}/products/{urun_id}")

    def toplu_urun_olustur(self, urunler: list) -> dict:
        """Tek seferde çoklu ürün oluştur (WooCommerce Batch API)."""
        return self._wc_post(f"{self.wc}/products/batch", {"create": urunler})

    def toplu_urun_guncelle(self, urunler: list) -> dict:
        return self._wc_post(f"{self.wc}/products/batch", {"update": urunler})

    def toplu_urun_sil(self, urun_idler: list) -> dict:
        return self._wc_post(f"{self.wc}/products/batch",
                             {"delete": urun_idler})

    def wc_kategoriler_listele(self, adet: int = 100) -> list:
        return self._wc_get(f"{self.wc}/products/categories", {"per_page": adet}) or []

    def wc_kategori_olustur(self, isim: str, ust: int = 0) -> dict:
        return self._wc_post(f"{self.wc}/products/categories",
                             {"name": isim, "parent": ust})

    def siparisler_listele(self, adet: int = 20) -> list:
        return self._wc_get(f"{self.wc}/orders", {"per_page": adet}) or []

    def musteri_listele(self, adet: int = 50) -> list:
        return self._wc_get(f"{self.wc}/customers", {"per_page": adet}) or []

    # ══════════════════════════════════════════════════════════════════════════
    # EKLENTILER & TEMALAR
    # ══════════════════════════════════════════════════════════════════════════

    def eklentiler_listele(self) -> list:
        return self._get(f"{self.base}/wp-json/wp/v2/plugins") or []

    def eklenti_aktif_et(self, eklenti: str) -> dict:
        return self._put(f"{self.base}/wp-json/wp/v2/plugins/{eklenti}",
                         {"status": "active"})

    def eklenti_pasif_et(self, eklenti: str) -> dict:
        return self._put(f"{self.base}/wp-json/wp/v2/plugins/{eklenti}",
                         {"status": "inactive"})

    def temalar_listele(self) -> list:
        return self._get(f"{self.base}/wp-json/wp/v2/themes") or []

    def tema_aktif_et(self, tema: str) -> dict:
        return self._put(f"{self.base}/wp-json/wp/v2/themes/{tema}",
                         {"status": "active"})

    # ══════════════════════════════════════════════════════════════════════════
    # AYARLAR
    # ══════════════════════════════════════════════════════════════════════════

    def site_ayarlarini_al(self) -> dict:
        return self._get(f"{self.base}/wp-json/wp/v2/settings") or {}

    def site_ayarlarini_guncelle(self, ayarlar: dict) -> dict:
        return self._put(f"{self.base}/wp-json/wp/v2/settings", ayarlar)

    # ══════════════════════════════════════════════════════════════════════════
    # MENÜLER
    # ══════════════════════════════════════════════════════════════════════════

    def menular_listele(self) -> list:
        return self._get(f"{self.base}/wp-json/wp/v2/menus") or []

    # ══════════════════════════════════════════════════════════════════════════
    # ÖZEL POST TİPLERİ
    # ══════════════════════════════════════════════════════════════════════════

    def post_tipleri_listele(self) -> dict:
        return self._get(f"{self.api}/types") or {}

    def ozel_post_listele(self, post_tipi: str, adet: int = 20) -> list:
        return self._get(f"{self.api}/{post_tipi}", {"per_page": adet}) or []

    # ══════════════════════════════════════════════════════════════════════════
    # YORUMLAR
    # ══════════════════════════════════════════════════════════════════════════

    def yorumlar_listele(self, post_id: int = None, adet: int = 20) -> list:
        params = {"per_page": adet}
        if post_id: params["post"] = post_id
        return self._get(f"{self.api}/comments", params) or []

    def yorum_onayla(self, yorum_id: int) -> dict:
        return self._put(f"{self.api}/comments/{yorum_id}", {"status": "approved"})

    def yorum_sil(self, yorum_id: int) -> dict:
        return self._delete(f"{self.api}/comments/{yorum_id}")

    # ══════════════════════════════════════════════════════════════════════════
    # SEO (Yoast SEO eklentisi varsa)
    # ══════════════════════════════════════════════════════════════════════════

    def yoast_meta_guncelle(self, post_id: int, seo_baslik: str,
                             seo_aciklama: str) -> dict:
        return self._put(f"{self.api}/posts/{post_id}", {
            "yoast_head_json": {
                "title": seo_baslik,
                "description": seo_aciklama
            }
        })

    # ══════════════════════════════════════════════════════════════════════════
    # SITE BİLGİSİ ÖZETİ
    # ══════════════════════════════════════════════════════════════════════════

    def site_ozeti_al(self) -> dict:
        try:
            ayarlar = self.site_ayarlarini_al()

            def _toplam_say(endpoint: str) -> int:
                try:
                    r = self.ses.get(endpoint, params={"per_page": 1}, timeout=10)
                    return int(r.headers.get("X-WP-Total", 0))
                except Exception:
                    return 0

            return {
                "site_adi":       ayarlar.get("title", ""),
                "site_url":       self.base,
                "yazi_sayisi":    _toplam_say(f"{self.api}/posts"),
                "sayfa_sayisi":   _toplam_say(f"{self.api}/pages"),
                "medya_sayisi":   _toplam_say(f"{self.api}/media"),
                "kategori_sayisi": _toplam_say(f"{self.api}/categories"),
            }
        except Exception as e:
            return {"hata": str(e)}
