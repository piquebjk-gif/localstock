#!/bin/bash
# İQ Elektronik — WP-CLI Kurulum Komutları
# Local by Flywheel Terminal veya cPanel SSH'da çalıştır
# =====================================================

echo "=== İQ Elektronik WP-CLI Kurulum ==="

# Site adı
wp option update blogname        "İQ Elektronik"
wp option update blogdescription "Teknolojide Akıllı Tercih"
wp option update timezone_string "Europe/Istanbul"

# Child tema yükle ve aktive et
wp theme install /path/to/iq-elektronik-child.zip --activate
# (yolu kendi bilgisayarınıza göre değiştirin)

# Gerekli eklentileri yükle
wp plugin install woocommerce                              --activate
wp plugin install contact-form-7                           --activate
wp plugin install wordpress-seo                            --activate
wp plugin install w3-total-cache                           --activate
wp plugin install wordfence                                --activate
wp plugin install updraftplus                              --activate
wp plugin install mailchimp-for-wp                         --activate
wp plugin install yith-woocommerce-wishlist                --activate
wp plugin install yith-woocommerce-compare                 --activate
wp plugin install loco-translate                           --activate
wp plugin install woocommerce-pdf-invoices-packing-slips   --activate

# PayTR (manuel yüklenecek — resmi repoda yok)
# https://www.paytr.com/magaza/woocommerce adresinden zip indirip:
# wp plugin install paytr-woocommerce.zip --activate

# WooCommerce ayarları
wp option update woocommerce_currency            TRY
wp option update woocommerce_currency_pos        right_space
wp option update woocommerce_price_decimal_sep   ","
wp option update woocommerce_price_thousand_sep  "."
wp option update woocommerce_price_num_decimals  2
wp option update woocommerce_calc_taxes          yes
wp option update woocommerce_tax_display_shop    incl
wp option update woocommerce_tax_display_cart    incl
wp option update woocommerce_manage_stock        yes
wp option update woocommerce_enable_ajax_add_to_cart yes

# Sayfaları oluştur
wp post create --post_type=page --post_title="Ana Sayfa"  --post_name=ana-sayfa --post_status=publish
wp post create --post_type=page --post_title="Mağaza"     --post_name=magaza    --post_status=publish --post_content="[woocommerce_shop]"
wp post create --post_type=page --post_title="Sepet"      --post_name=sepet     --post_status=publish --post_content="[woocommerce_cart]"
wp post create --post_type=page --post_title="Ödeme"      --post_name=odeme     --post_status=publish --post_content="[woocommerce_checkout]"
wp post create --post_type=page --post_title="Hesabım"    --post_name=hesabim   --post_status=publish --post_content="[woocommerce_my_account]"
wp post create --post_type=page --post_title="Hakkımızda" --post_name=hakkimizda --post_status=publish
wp post create --post_type=page --post_title="İletişim"   --post_name=iletisim  --post_status=publish

# WooCommerce sayfa atamaları (ID'leri yukarıdaki çıktıdan alın)
# wp option update woocommerce_shop_page_id      [MAGAZA_ID]
# wp option update woocommerce_cart_page_id      [SEPET_ID]
# wp option update woocommerce_checkout_page_id  [ODEME_ID]
# wp option update woocommerce_myaccount_page_id [HESABIM_ID]

# Statik ana sayfa (ID'yi değiştir)
# wp option update show_on_front page
# wp option update page_on_front [ANA_SAYFA_ID]

# Ürün kategorileri
wp term create product_cat "Telefon & Tablet"
wp term create product_cat "Bilgisayar & Laptop"
wp term create product_cat "Ev Elektroniği"
wp term create product_cat "Ses Sistemleri"
wp term create product_cat "Kamera & Fotoğraf"
wp term create product_cat "Aksesuarlar"
wp term create product_cat "Akıllı Saatler"
wp term create product_cat "Oyun & Konsol"

# KDV %20
wp wc tax create --rate=20 --name=KDV --country=TR --user=1

# IQ50 kuponu
wp wc shop_coupon create --code=IQ50 --discount_type=fixed_cart --amount=50 --minimum_amount=200 --usage_limit=1 --user=1

# Önbellek temizle
wp cache flush
wp rewrite flush --hard

echo "=== Kurulum Tamamlandı! ==="
