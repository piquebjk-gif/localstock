<?php
/**
 * İQ Elektronik — Tek Dosya Kurulum Aracı
 * =========================================
 * KULLANIM:
 *   1. Bu dosyayı WordPress kök klasörüne yükle (wp-config.php ile aynı yere)
 *   2. Tarayıcıdan aç: http://[siteniz]/iq-installer.php?secret=iq2024
 *   3. Bitince bu dosyayı SİL (güvenlik için)
 *
 * Local by Flywheel için yol örneği:
 *   C:\Users\[kullanici]\Local Sites\[site-adi]\app\public\iq-installer.php
 */

define('IQ_SECRET', 'iq2024');

// Güvenlik kontrolü
if (($_GET['secret'] ?? '') !== IQ_SECRET) {
    http_response_code(403);
    die('<h2 style="color:red">Erişim reddedildi. ?secret=iq2024 parametresi gerekli.</h2>');
}

// WordPress çekirdek yükle
if (!defined('ABSPATH')) {
    $wp_load = __DIR__ . '/wp-load.php';
    if (!file_exists($wp_load)) {
        die('<h2>wp-load.php bulunamadı. Bu dosyayı WordPress kök dizinine yükleyin.</h2>');
    }
    require_once $wp_load;
}

// Yönetici yetkisi iste
if (!current_user_can('manage_options')) {
    auth_redirect();
}

$adim = $_GET['adim'] ?? 'menu';
$log  = [];

function iq_log($msg, $tip = 'ok') {
    global $log;
    $log[] = ['msg' => $msg, 'tip' => $tip];
}

/* ═══════════════════════════════════════════════════════════════
   ADIMLAR
═══════════════════════════════════════════════════════════════ */

function iq_adim_site_bilgi() {
    update_option('blogname',        'İQ Elektronik');
    update_option('blogdescription', 'Teknolojide Akıllı Tercih');
    update_option('timezone_string', 'Europe/Istanbul');
    update_option('date_format',     'd.m.Y');
    update_option('time_format',     'H:i');
    update_option('start_of_week',   1);
    update_option('woocommerce_email_from_name',    'İQ Elektronik');
    update_option('woocommerce_email_from_address', 'info@iqelektronik.com');
    iq_log('Site adı: İQ Elektronik — Teknolojide Akıllı Tercih');
    iq_log('Saat dilimi: Europe/Istanbul');
}

function iq_adim_wc_ayarlar() {
    $ayarlar = [
        'woocommerce_currency'               => 'TRY',
        'woocommerce_currency_pos'           => 'right_space',
        'woocommerce_price_decimal_sep'      => ',',
        'woocommerce_price_thousand_sep'     => '.',
        'woocommerce_price_num_decimals'     => '2',
        'woocommerce_weight_unit'            => 'kg',
        'woocommerce_dimension_unit'         => 'cm',
        'woocommerce_store_address'          => 'Yenidoğan, Kızılay Sokağı No:41',
        'woocommerce_store_city'             => 'İstanbul',
        'woocommerce_default_country'        => 'TR:34',
        'woocommerce_store_postcode'         => '34040',
        'woocommerce_calc_taxes'             => 'yes',
        'woocommerce_tax_display_shop'       => 'incl',
        'woocommerce_tax_display_cart'       => 'incl',
        'woocommerce_prices_include_tax'     => 'yes',
        'woocommerce_enable_ajax_add_to_cart'=> 'yes',
        'woocommerce_cart_redirect_after_add'=> 'no',
        'woocommerce_enable_guest_checkout'  => 'yes',
        'woocommerce_enable_checkout_login_reminder' => 'yes',
        'woocommerce_manage_stock'           => 'yes',
        'woocommerce_notify_low_stock'       => 'yes',
        'woocommerce_notify_no_stock'        => 'yes',
        'woocommerce_notify_low_stock_amount'=> 5,
        'woocommerce_catalog_columns'        => 4,
        'woocommerce_catalog_rows'           => 4,
        'woocommerce_default_catalog_orderby'=> 'popularity',
        'woocommerce_shop_page_display'      => '',
        'woocommerce_category_archive_display' => '',
    ];
    foreach ($ayarlar as $k => $v) {
        update_option($k, $v);
    }
    iq_log('WooCommerce: ₺ TRY, KDV dahil, AJAX sepet aktif');
    iq_log('Mağaza adresi: Bayrampaşa / İstanbul');
}

function iq_adim_sayfalar() {
    $sayfalar = [
        'Ana Sayfa'   => ['slug' => 'ana-sayfa',   'icerik' => '<!-- Electro ana sayfa -->'],
        'Mağaza'      => ['slug' => 'magaza',       'icerik' => '[woocommerce_shop]'],
        'Sepet'       => ['slug' => 'sepet',        'icerik' => '[woocommerce_cart]'],
        'Ödeme'       => ['slug' => 'odeme',        'icerik' => '[woocommerce_checkout]'],
        'Hesabım'     => ['slug' => 'hesabim',      'icerik' => '[woocommerce_my_account]'],
        'Hakkımızda'  => ['slug' => 'hakkimizda',   'icerik' => '<h2>İQ Elektronik</h2><p>Bayrampaşa İstanbul\'da elektronik ürünlerde güvenilir adres. Teknolojide Akıllı Tercih.</p><p>📞 0544 440 56 77</p>'],
        'İletişim'    => ['slug' => 'iletisim',     'icerik' => '<p>📍 Yenidoğan, Kızılay Sokağı No:41, 34040 Bayrampaşa/İstanbul</p><p>📞 <a href="tel:05444405677">0544 440 56 77</a></p>'],
        'Gizlilik'    => ['slug' => 'gizlilik',     'icerik' => '<p>Gizlilik politikamız.</p>'],
        'KVKK'        => ['slug' => 'kvkk',         'icerik' => '<p>KVKK aydınlatma metni.</p>'],
    ];

    $ids = [];
    foreach ($sayfalar as $baslik => $s) {
        $mevcut = get_page_by_path($s['slug']);
        if ($mevcut) {
            $ids[$s['slug']] = $mevcut->ID;
            iq_log("'$baslik' sayfası zaten mevcut (id={$mevcut->ID})");
            continue;
        }
        $id = wp_insert_post([
            'post_title'   => $baslik,
            'post_name'    => $s['slug'],
            'post_content' => $s['icerik'],
            'post_status'  => 'publish',
            'post_type'    => 'page',
        ]);
        if ($id && !is_wp_error($id)) {
            $ids[$s['slug']] = $id;
            iq_log("'$baslik' sayfası oluşturuldu (id=$id)");
        }
    }

    // WooCommerce sayfalarını ata
    if (!empty($ids['magaza']))   update_option('woocommerce_shop_page_id',      $ids['magaza']);
    if (!empty($ids['sepet']))    update_option('woocommerce_cart_page_id',      $ids['sepet']);
    if (!empty($ids['odeme']))    update_option('woocommerce_checkout_page_id',  $ids['odeme']);
    if (!empty($ids['hesabim']))  update_option('woocommerce_myaccount_page_id', $ids['hesabim']);

    // Statik ön sayfa
    if (!empty($ids['ana-sayfa'])) {
        update_option('show_on_front',  'page');
        update_option('page_on_front',  $ids['ana-sayfa']);
        update_option('page_for_posts', 0);
        iq_log('Ana sayfa statik olarak ayarlandı');
    }

    return $ids;
}

function iq_adim_kategoriler() {
    $kategoriler = [
        'Telefon & Tablet',
        'Bilgisayar & Laptop',
        'Ev Elektroniği',
        'Ses Sistemleri',
        'Kamera & Fotoğraf',
        'Aksesuarlar',
        'Akıllı Saatler',
        'Oyun & Konsol',
    ];
    foreach ($kategoriler as $isim) {
        if (term_exists($isim, 'product_cat')) {
            iq_log("'$isim' kategorisi mevcut");
            continue;
        }
        $r = wp_insert_term($isim, 'product_cat');
        if (!is_wp_error($r)) {
            iq_log("'$isim' kategorisi oluşturuldu (id={$r['term_id']})");
        } else {
            iq_log("'$isim' hatası: " . $r->get_error_message(), 'warn');
        }
    }
}

function iq_adim_kargo() {
    global $wpdb;
    // Türkiye kargo zonu
    $mevcut = $wpdb->get_var("SELECT zone_id FROM {$wpdb->prefix}woocommerce_shipping_zones WHERE zone_name='Türkiye' LIMIT 1");
    if ($mevcut) {
        iq_log("Kargo bölgesi 'Türkiye' mevcut (id=$mevcut)");
        return;
    }
    $wpdb->insert("{$wpdb->prefix}woocommerce_shipping_zones", [
        'zone_name'  => 'Türkiye',
        'zone_order' => 0,
    ]);
    $zone_id = $wpdb->insert_id;

    // Türkiye konumu
    $wpdb->insert("{$wpdb->prefix}woocommerce_shipping_zone_locations", [
        'zone_id'       => $zone_id,
        'location_code' => 'TR',
        'location_type' => 'country',
    ]);

    // Sabit kargo (29.90₺)
    $wpdb->insert("{$wpdb->prefix}woocommerce_shipping_zone_methods", [
        'zone_id'      => $zone_id,
        'method_id'    => 'flat_rate',
        'method_order' => 1,
        'is_enabled'   => 1,
    ]);
    $flat_id = $wpdb->insert_id;
    update_option("woocommerce_flat_rate_{$flat_id}_settings", [
        'title'   => 'Standart Kargo',
        'cost'    => '29.90',
        'enabled' => 'yes',
    ]);

    // Ücretsiz kargo (500₺+)
    $wpdb->insert("{$wpdb->prefix}woocommerce_shipping_zone_methods", [
        'zone_id'      => $zone_id,
        'method_id'    => 'free_shipping',
        'method_order' => 2,
        'is_enabled'   => 1,
    ]);
    $free_id = $wpdb->insert_id;
    update_option("woocommerce_free_shipping_{$free_id}_settings", [
        'title'      => 'Ücretsiz Kargo (500₺ ve üzeri)',
        'requires'   => 'min_amount',
        'min_amount' => '500',
        'enabled'    => 'yes',
    ]);

    iq_log("Kargo bölgesi 'Türkiye' oluşturuldu (id=$zone_id)");
    iq_log('Kargo: Standart 29,90₺ + Ücretsiz (500₺+)');
}

function iq_adim_vergi() {
    global $wpdb;
    $mevcut = $wpdb->get_var("SELECT tax_rate_id FROM {$wpdb->prefix}woocommerce_tax_rates WHERE tax_rate_name='KDV' LIMIT 1");
    if ($mevcut) {
        iq_log("KDV vergi oranı zaten mevcut (id=$mevcut)");
        return;
    }
    $wpdb->insert("{$wpdb->prefix}woocommerce_tax_rates", [
        'tax_rate_country'  => 'TR',
        'tax_rate_state'    => '',
        'tax_rate'          => '20.0000',
        'tax_rate_name'     => 'KDV',
        'tax_rate_priority' => 1,
        'tax_rate_compound' => 0,
        'tax_rate_shipping' => 1,
        'tax_rate_order'    => 0,
        'tax_rate_class'    => '',
    ]);
    iq_log('KDV %20 eklendi');
}

function iq_adim_kupon() {
    $mevcut = get_page_by_title('IQ50', OBJECT, 'shop_coupon');
    if ($mevcut) {
        iq_log("IQ50 kuponu zaten mevcut (id={$mevcut->ID})");
        return;
    }
    $id = wp_insert_post([
        'post_title'   => 'IQ50',
        'post_name'    => 'iq50',
        'post_content' => '',
        'post_status'  => 'publish',
        'post_type'    => 'shop_coupon',
    ]);
    if ($id && !is_wp_error($id)) {
        update_post_meta($id, 'discount_type',        'fixed_cart');
        update_post_meta($id, 'coupon_amount',        '50');
        update_post_meta($id, 'minimum_amount',       '200');
        update_post_meta($id, 'usage_limit',          '1');
        update_post_meta($id, 'usage_limit_per_user', '1');
        update_post_meta($id, 'individual_use',       'yes');
        update_post_meta($id, 'usage_count',          '0');
        iq_log("IQ50 kuponu oluşturuldu (50₺, min 200₺, tek kullanım) — id=$id");
    }
}

function iq_adim_tema() {
    $zip_yolu = __DIR__ . '/iq-elektronik-child.zip';
    if (!file_exists($zip_yolu)) {
        iq_log("iq-elektronik-child.zip bulunamadı — temayı WP admin'den manuel yükleyin", 'warn');
        return;
    }
    require_once ABSPATH . 'wp-admin/includes/file.php';
    require_once ABSPATH . 'wp-admin/includes/misc.php';
    require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
    require_once ABSPATH . 'wp-admin/includes/theme.php';

    WP_Filesystem();
    $sonuc = unzip_file($zip_yolu, get_theme_root());
    if (is_wp_error($sonuc)) {
        iq_log('Tema zip açma hatası: ' . $sonuc->get_error_message(), 'warn');
    } else {
        switch_theme('iq-elektronik-child');
        iq_log('İQ Elektronik child tema aktive edildi');
    }
}

function iq_adim_menu() {
    // Ana menü
    $menu_id = wp_create_nav_menu('Ana Menü');
    if (!is_wp_error($menu_id)) {
        $sayfalar_slug = ['magaza','hakkimizda','iletisim'];
        $sira = 1;
        foreach ($sayfalar_slug as $slug) {
            $sayfa = get_page_by_path($slug);
            if ($sayfa) {
                wp_update_nav_menu_item($menu_id, 0, [
                    'menu-item-title'     => $sayfa->post_title,
                    'menu-item-object-id' => $sayfa->ID,
                    'menu-item-object'    => 'page',
                    'menu-item-type'      => 'post_type',
                    'menu-item-status'    => 'publish',
                    'menu-item-position'  => $sira++,
                ]);
            }
        }
        $lokasyon = get_registered_nav_menus();
        $atamalar = get_theme_mod('nav_menu_locations', []);
        foreach (array_keys($lokasyon) as $loc) {
            $atamalar[$loc] = $menu_id;
        }
        set_theme_mod('nav_menu_locations', $atamalar);
        iq_log("Ana Menü oluşturuldu ve tüm lokasyonlara atandı (id=$menu_id)");
    } else {
        iq_log('Menü oluşturma: ' . $menu_id->get_error_message(), 'warn');
    }
}

function iq_adim_yoast() {
    // Yoast SEO varsa temel ayarlar
    if (!defined('WPSEO_VERSION')) {
        iq_log('Yoast SEO aktif değil — atlandı', 'warn');
        return;
    }
    $opts = get_option('wpseo_social', []);
    $opts['facebook_site']  = 'https://www.facebook.com/iqelectroniks/';
    $opts['instagram_url']  = 'https://www.instagram.com/iqelektronik/';
    update_option('wpseo_social', $opts);

    $general = get_option('wpseo', []);
    $general['website_name'] = 'İQ Elektronik';
    update_option('wpseo', $general);
    iq_log('Yoast SEO: sosyal medya bilgileri güncellendi');
}

function iq_adim_temizle() {
    // Gereksiz örnek içerik sil
    $ornek = get_page_by_path('sample-page');
    if ($ornek) { wp_delete_post($ornek->ID, true); iq_log('Örnek sayfa silindi'); }

    $hello = get_post_by_title_and_type('Hello world!', 'post');
    if (!$hello) {
        $query = new WP_Query(['post_type'=>'post','title'=>'Hello world!','post_status'=>'any']);
        $hello = $query->posts[0] ?? null;
    }
    if ($hello) { wp_delete_post($hello->ID, true); iq_log('Hello World yazısı silindi'); }

    // Önbellek temizle
    if (function_exists('w3tc_flush_all'))      w3tc_flush_all();
    if (function_exists('wp_cache_flush'))       wp_cache_flush();
    if (function_exists('rocket_clean_domain'))  rocket_clean_domain();
    iq_log('Önbellek temizlendi');
}

/* ═══════════════════════════════════════════════════════════════
   TAM KURULUM
═══════════════════════════════════════════════════════════════ */
function iq_tam_kurulum() {
    iq_adim_site_bilgi();
    iq_adim_wc_ayarlar();
    iq_adim_sayfalar();
    iq_adim_kategoriler();
    iq_adim_kargo();
    iq_adim_vergi();
    iq_adim_kupon();
    iq_adim_tema();
    iq_adim_menu();
    iq_adim_yoast();
    iq_adim_temizle();
}

/* ═══════════════════════════════════════════════════════════════
   ARAYÜZ
═══════════════════════════════════════════════════════════════ */
if ($adim === 'kur') {
    iq_tam_kurulum();
}
?>
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>İQ Elektronik — Kurulum</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
  .kart{background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.12);width:100%;max-width:680px;overflow:hidden}
  .header{background:#333E48;color:#fff;padding:28px 32px;display:flex;align-items:center;gap:14px}
  .header-iq{background:#FDD700;color:#333E48;font-weight:900;font-size:22px;padding:6px 14px;border-radius:6px}
  .header h1{font-size:1.3rem;font-weight:600}
  .header p{font-size:12px;color:#aaa;margin-top:4px}
  .govde{padding:32px}
  .govde p{color:#555;line-height:1.7;margin-bottom:20px}
  .adimlar{background:#f8f9fa;border-radius:8px;padding:20px;margin-bottom:24px}
  .adimlar h3{font-size:.9rem;font-weight:700;color:#333E48;margin-bottom:12px;text-transform:uppercase;letter-spacing:.5px}
  .adim-liste{list-style:none}
  .adim-liste li{display:flex;align-items:center;gap:10px;padding:6px 0;font-size:13px;color:#444;border-bottom:1px solid #eee}
  .adim-liste li:last-child{border-bottom:none}
  .adim-liste .ico{width:20px;height:20px;border-radius:50%;background:#FDD700;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0}
  .btn{display:inline-block;background:#FDD700;color:#333E48;font-weight:700;font-size:15px;padding:14px 36px;border-radius:8px;border:none;cursor:pointer;text-decoration:none;transition:all .2s;width:100%;text-align:center}
  .btn:hover{background:#EFCA00;transform:translateY(-1px)}
  .btn-tehlike{background:#DC3545;color:#fff;margin-top:10px;font-size:13px;padding:10px}
  .btn-tehlike:hover{background:#c82333}
  .uyari{background:#FFF3CD;border:1px solid #FDD700;border-radius:8px;padding:14px 18px;font-size:13px;color:#856404;margin-bottom:20px}
  .sonuc{margin-top:24px}
  .log-item{display:flex;gap:10px;align-items:flex-start;padding:8px 12px;border-radius:6px;margin-bottom:6px;font-size:13px}
  .log-ok{background:#D4EDDA;color:#155724}
  .log-warn{background:#FFF3CD;color:#856404}
  .log-err{background:#F8D7DA;color:#721C24}
  .log-item .ico{flex-shrink:0;font-size:14px}
  .basarili-banner{background:#D4EDDA;border:2px solid #28A745;border-radius:10px;padding:20px;text-align:center;margin-bottom:20px}
  .basarili-banner h2{color:#155724;font-size:1.3rem}
  .basarili-banner p{color:#155724;margin-top:8px;font-size:13px}
  .linkler{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}
  .link-btn{background:#333E48;color:#FDD700;padding:10px;border-radius:6px;text-align:center;text-decoration:none;font-size:13px;font-weight:600}
  .link-btn:hover{background:#2C3E50;color:#FDD700}
</style>
</head>
<body>
<div class="kart">
  <div class="header">
    <div class="header-iq">İQ</div>
    <div>
      <h1>Elektronik — Kurulum Aracı</h1>
      <p>Teknolojide Akıllı Tercih &nbsp;|&nbsp; WordPress + WooCommerce Tam Kurulum</p>
    </div>
  </div>
  <div class="govde">

<?php if ($adim === 'kur'): ?>

  <?php $hata_var = count(array_filter($log, fn($l) => $l['tip'] === 'err')) > 0; ?>
  <div class="basarili-banner">
    <h2><?= $hata_var ? '⚠ Kurulum tamamlandı (bazı uyarılar var)' : '✅ Kurulum başarıyla tamamlandı!' ?></h2>
    <p>İQ Elektronik WordPress siteniz yapılandırıldı.</p>
  </div>

  <div class="sonuc">
    <?php foreach ($log as $l): ?>
    <div class="log-item log-<?= $l['tip'] ?>">
      <span class="ico"><?= $l['tip']==='ok' ? '✓' : ($l['tip']==='warn' ? '⚠' : '✗') ?></span>
      <span><?= htmlspecialchars($l['msg']) ?></span>
    </div>
    <?php endforeach; ?>
  </div>

  <div class="linkler">
    <a href="<?= admin_url() ?>" class="link-btn">🏠 WP Admin Panel</a>
    <a href="<?= admin_url('themes.php') ?>" class="link-btn">🎨 Temalar</a>
    <a href="<?= admin_url('admin.php?page=wc-settings') ?>" class="link-btn">🛒 WooCommerce</a>
    <a href="<?= home_url('/') ?>" class="link-btn" target="_blank">🌐 Siteyi Gör</a>
    <a href="<?= admin_url('nav-menus.php') ?>" class="link-btn">📋 Menüler</a>
    <a href="<?= admin_url('upload.php') ?>" class="link-btn">🖼 Medya</a>
  </div>

  <div style="margin-top:20px;padding:14px;background:#f8f9fa;border-radius:8px;font-size:12px;color:#666">
    <strong>⚠ ÖNEMLİ:</strong> Kurulum tamamlandı. <strong>Bu dosyayı (iq-installer.php) sunucudan SİLİN!</strong><br>
    Local: <code>...app/public/iq-installer.php</code> dosyasını silin.
  </div>

  <a href="?secret=<?= IQ_SECRET ?>&adim=sil" class="btn btn-tehlike"
     onclick="return confirm('Yükleyici dosyasını silmek istediğinizden emin misiniz?')">
    🗑 Bu Dosyayı Şimdi Sil (Güvenlik)
  </a>

<?php elseif ($adim === 'sil'): ?>
  <?php if (@unlink(__FILE__)): ?>
    <div class="basarili-banner"><h2>✅ Yükleyici silindi</h2><p>Güvenlik sağlandı.</p></div>
    <a href="<?= admin_url() ?>" class="btn">WP Admin'e Git</a>
  <?php else: ?>
    <div class="uyari">⚠ Dosya silinemedi. Lütfen manuel olarak silin: <code>iq-installer.php</code></div>
    <a href="<?= admin_url() ?>" class="btn">WP Admin'e Git</a>
  <?php endif; ?>

<?php else: /* MENU */ ?>

  <div class="uyari">
    <strong>📋 Bu araç ne yapar?</strong> Tek tıkla aşağıdaki her şeyi otomatik olarak kurar.
  </div>

  <div class="adimlar">
    <h3>Kurulum Adımları</h3>
    <ul class="adim-liste">
      <li><span class="ico">1</span> Site adı: İQ Elektronik — Teknolojide Akıllı Tercih</li>
      <li><span class="ico">2</span> WooCommerce: ₺ TRY, KDV %20 dahil, AJAX sepet</li>
      <li><span class="ico">3</span> Sayfalar: Ana Sayfa, Mağaza, Sepet, Ödeme, Hesabım, Hakkımızda, İletişim, Gizlilik, KVKK</li>
      <li><span class="ico">4</span> Ürün kategorileri: Telefon, Laptop, Ev Elektroniği, Ses, Kamera, Aksesuar…</li>
      <li><span class="ico">5</span> Kargo: Standart 29,90₺ + Ücretsiz (500₺+) — Türkiye bölgesi</li>
      <li><span class="ico">6</span> Vergi: KDV %20 (Türkiye)</li>
      <li><span class="ico">7</span> Kupon: IQ50 — 50₺ indirim (min 200₺, tek kullanım)</li>
      <li><span class="ico">8</span> Child tema: iq-elektronik-child zip varsa otomatik yükle & aktive et</li>
      <li><span class="ico">9</span> Ana menü oluştur ve sayfalara ata</li>
      <li><span class="ico">10</span> Yoast SEO sosyal medya ayarları</li>
      <li><span class="ico">11</span> Örnek içerik temizle, önbellek sıfırla</li>
    </ul>
  </div>

  <div class="uyari">
    <strong>Child tema için:</strong> <code>iq-elektronik-child.zip</code> dosyasını da
    bu PHP ile aynı klasöre (<code>...app/public/</code>) kopyalayın.
    Zip bulunamazsa tema adımı atlanır — daha sonra WP Admin &gt; Temalar'dan yükleyebilirsiniz.
  </div>

  <a href="?secret=<?= IQ_SECRET ?>&adim=kur" class="btn"
     onclick="this.textContent='⏳ Kuruluyor...'; this.style.opacity='.7'">
    🚀 TAM KURULUMU BAŞLAT
  </a>

<?php endif; ?>

  </div><!-- /govde -->
</div><!-- /kart -->
</body>
</html>
