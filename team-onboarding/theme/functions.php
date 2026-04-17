<?php
/**
 * İQ Elektronik Child Theme — functions.php
 * Teknolojide Akıllı Tercih
 */

defined('ABSPATH') || exit;

/* ─────────────────────────────────────────────────────────────
   1. STIL & SCRIPT YÜKLEME
───────────────────────────────────────────────────────────── */
add_action('wp_enqueue_scripts', 'iq_varliklar', 20);
function iq_varliklar() {
    // Parent tema stilini yükle
    wp_enqueue_style(
        'electro-parent-style',
        get_template_directory_uri() . '/style.css',
        [], wp_get_theme()->parent()->get('Version')
    );

    // Child tema stili
    wp_enqueue_style(
        'iq-child-style',
        get_stylesheet_uri(),
        ['electro-parent-style'],
        wp_get_theme()->get('Version')
    );

    // Google Fonts — Inter
    wp_enqueue_style(
        'iq-fonts',
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
        [], null
    );

    // Font Awesome (sosyal medya ikonları)
    wp_enqueue_style(
        'iq-fontawesome',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
        [], '6.5.1'
    );

    // Özel CSS
    wp_enqueue_style(
        'iq-custom-css',
        get_stylesheet_directory_uri() . '/custom/iq-custom.css',
        ['iq-child-style'],
        wp_get_theme()->get('Version')
    );

    // Mobil Alt Navigasyon JS
    wp_enqueue_script(
        'iq-mobile-nav',
        get_stylesheet_directory_uri() . '/custom/mobile-nav.js',
        ['jquery'], wp_get_theme()->get('Version'), true
    );

    // Slide Cart JS
    wp_enqueue_script(
        'iq-slide-cart',
        get_stylesheet_directory_uri() . '/custom/slide-cart.js',
        ['jquery', 'wc-cart-fragments'], wp_get_theme()->get('Version'), true
    );

    // Canlı Arama JS
    wp_enqueue_script(
        'iq-live-search',
        get_stylesheet_directory_uri() . '/custom/live-search.js',
        ['jquery'], wp_get_theme()->get('Version'), true
    );

    // JS'e WordPress verilerini aktar
    wp_localize_script('iq-mobile-nav', 'iqData', [
        'ajaxurl'    => admin_url('admin-ajax.php'),
        'nonce'      => wp_create_nonce('iq_nonce'),
        'cartUrl'    => wc_get_cart_url(),
        'shopUrl'    => get_permalink(wc_get_page_id('shop')),
        'homeUrl'    => home_url('/'),
        'siteAdi'    => get_bloginfo('name'),
        'telefon'    => '0544 440 56 77',
        'currency'   => get_woocommerce_currency_symbol(),
    ]);
}

/* ─────────────────────────────────────────────────────────────
   2. FİRMA BİLGİLERİ
───────────────────────────────────────────────────────────── */
define('IQ_AD',       'İQ Elektronik');
define('IQ_SLOGAN',   'Teknolojide Akıllı Tercih');
define('IQ_ADRES',    'Yenidoğan, Kızılay Sokağı No:41, 34040 Bayrampaşa/İstanbul');
define('IQ_TELEFON',  '0544 440 56 77');
define('IQ_INSTAGRAM','https://www.instagram.com/iqelektronik/');
define('IQ_FACEBOOK', 'https://www.facebook.com/iqelectroniks/');
define('IQ_RENK',     '#FDD700');

/* ─────────────────────────────────────────────────────────────
   3. TEMA DESTEĞİ
───────────────────────────────────────────────────────────── */
add_action('after_setup_theme', 'iq_tema_destegi');
function iq_tema_destegi() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('woocommerce');
    add_theme_support('wc-product-gallery-zoom');
    add_theme_support('wc-product-gallery-lightbox');
    add_theme_support('wc-product-gallery-slider');

    // Özel logo boyutu
    add_theme_support('custom-logo', [
        'height'      => 80,
        'width'       => 260,
        'flex-height' => true,
        'flex-width'  => true,
        'header-text' => ['site-title', 'site-description'],
    ]);
}

/* ─────────────────────────────────────────────────────────────
   4. TOP BAR
───────────────────────────────────────────────────────────── */
add_action('iq_topbar', 'iq_topbar_icerik');
function iq_topbar_icerik() { ?>
<div class="iq-topbar iq-desktop-only">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-md-6">
        <span><?= IQ_AD ?>'e Hoş Geldiniz! </span>
        <span class="iq-topbar-kargo">🚚 500₺ üzeri ücretsiz kargo</span>
      </div>
      <div class="col-md-6 text-end">
        <a href="tel:<?= IQ_TELEFON ?>"><i class="fas fa-phone-alt"></i> <?= IQ_TELEFON ?></a>
        &nbsp;|&nbsp;
        <a href="<?= IQ_INSTAGRAM ?>" target="_blank"><i class="fab fa-instagram"></i></a>
        &nbsp;
        <a href="<?= IQ_FACEBOOK ?>" target="_blank"><i class="fab fa-facebook-f"></i></a>
      </div>
    </div>
  </div>
</div>
<?php }

/* ─────────────────────────────────────────────────────────────
   5. MOBİL ALT NAVİGASYON
───────────────────────────────────────────────────────────── */
add_action('wp_footer', 'iq_mobil_alt_nav');
function iq_mobil_alt_nav() { ?>
<nav class="iq-mobil-nav d-lg-none" id="iqMobilNav">
  <a href="<?= home_url('/') ?>" class="iq-nav-item <?= is_front_page() ? 'aktif' : '' ?>">
    <i class="fas fa-home"></i><span>Ana Sayfa</span>
  </a>
  <a href="<?= get_permalink(wc_get_page_id('shop')) ?>" class="iq-nav-item <?= is_shop() ? 'aktif' : '' ?>">
    <i class="fas fa-th-large"></i><span>Ürünler</span>
  </a>
  <a href="#" class="iq-nav-item iq-arama-toggle">
    <i class="fas fa-search"></i><span>Ara</span>
  </a>
  <a href="<?= wc_get_cart_url() ?>" class="iq-nav-item iq-nav-sepet">
    <i class="fas fa-shopping-cart"></i>
    <span class="iq-nav-badge"><?= WC()->cart->get_cart_contents_count() ?></span>
    <span>Sepet</span>
  </a>
  <a href="<?= get_permalink(wc_get_page_id('myaccount')) ?>" class="iq-nav-item">
    <i class="fas fa-user"></i><span>Hesap</span>
  </a>
</nav>

<!-- Mobil Arama Overlay -->
<div class="iq-arama-overlay" id="iqAramaOverlay" style="display:none;">
  <div class="iq-arama-kapsam">
    <form role="search" method="get" action="<?= home_url('/') ?>">
      <input type="text" name="s" placeholder="Ürün ara..." class="iq-arama-giris" autocomplete="off">
      <input type="hidden" name="post_type" value="product">
      <button type="submit"><i class="fas fa-search"></i></button>
    </form>
    <div class="iq-arama-sonuclar"></div>
    <button class="iq-arama-kapat" onclick="document.getElementById('iqAramaOverlay').style.display='none'">
      <i class="fas fa-times"></i>
    </button>
  </div>
</div>
<?php }

/* ─────────────────────────────────────────────────────────────
   6. SLİDE CART (Mini Sepet Paneli)
───────────────────────────────────────────────────────────── */
add_action('wp_footer', 'iq_slide_cart');
function iq_slide_cart() { ?>
<div class="iq-overlay" id="iqOverlay"></div>
<div class="iq-slide-cart" id="iqSlideCart">
  <div class="iq-sc-header">
    <h5><i class="fas fa-shopping-cart"></i> Sepetim
      <span class="iq-sc-adet">(<?= WC()->cart->get_cart_contents_count() ?>)</span>
    </h5>
    <button class="iq-sc-kapat" id="iqScKapat"><i class="fas fa-times"></i></button>
  </div>
  <div class="iq-sc-govde">
    <?php if (WC()->cart->is_empty()): ?>
    <div class="iq-sc-bos">
      <i class="fas fa-shopping-cart"></i>
      <p>Sepetiniz boş.</p>
      <a href="<?= get_permalink(wc_get_page_id('shop')) ?>" class="iq-btn">Alışverişe Başla</a>
    </div>
    <?php else:
      foreach (WC()->cart->get_cart() as $key => $item):
        $urun = $item['data'];
        $gorsel = wp_get_attachment_image_url($urun->get_image_id(), 'thumbnail') ?: wc_placeholder_img_src('thumbnail');
    ?>
    <div class="iq-sc-urun" data-key="<?= esc_attr($key) ?>">
      <img src="<?= esc_url($gorsel) ?>" alt="<?= esc_attr($urun->get_name()) ?>">
      <div class="iq-sc-urun-bilgi">
        <div class="iq-sc-isim"><?= esc_html($urun->get_name()) ?></div>
        <div class="iq-sc-fiyat"><?= WC()->cart->get_product_price($urun) ?></div>
        <div class="iq-sc-adet-kontrol">
          <button class="iq-qty-btn iq-qty-azalt">−</button>
          <span><?= $item['quantity'] ?></span>
          <button class="iq-qty-btn iq-qty-artir">+</button>
        </div>
      </div>
      <button class="iq-sc-sil" data-key="<?= esc_attr($key) ?>"><i class="fas fa-trash"></i></button>
    </div>
    <?php endforeach; ?>
    <?php endif; ?>
  </div>
  <?php if (!WC()->cart->is_empty()): ?>
  <div class="iq-sc-footer">
    <div class="iq-sc-toplam">
      Toplam: <strong><?= WC()->cart->get_cart_total() ?></strong>
    </div>
    <a href="<?= wc_get_cart_url() ?>" class="iq-btn iq-btn-outline">Sepete Git</a>
    <a href="<?= wc_get_checkout_url() ?>" class="iq-btn">Ödemeye Geç</a>
  </div>
  <?php endif; ?>
</div>
<?php }

/* ─────────────────────────────────────────────────────────────
   7. FOOTER
───────────────────────────────────────────────────────────── */
add_action('iq_footer_icerik', 'iq_footer_ciz');
function iq_footer_ciz() { ?>
<footer class="iq-footer">
  <div class="iq-footer-ust">
    <div class="container">
      <div class="row">
        <div class="col-lg-4 col-md-6 mb-4">
          <div class="iq-footer-logo">
            <?php if (has_custom_logo()): the_custom_logo();
            else: ?><span class="iq-footer-marka"><?= IQ_AD ?></span><?php endif; ?>
          </div>
          <p class="iq-footer-slogan"><?= IQ_SLOGAN ?></p>
          <address class="iq-footer-adres">
            <p><i class="fas fa-map-marker-alt"></i> <?= IQ_ADRES ?></p>
            <p><i class="fas fa-phone-alt"></i> <a href="tel:<?= IQ_TELEFON ?>"><?= IQ_TELEFON ?></a></p>
          </address>
          <div class="iq-social">
            <a href="<?= IQ_INSTAGRAM ?>" target="_blank" rel="noopener" title="Instagram">
              <i class="fab fa-instagram"></i>
            </a>
            <a href="<?= IQ_FACEBOOK ?>" target="_blank" rel="noopener" title="Facebook">
              <i class="fab fa-facebook-f"></i>
            </a>
            <a href="https://wa.me/90<?= str_replace([' ','0544 '], ['','544'], IQ_TELEFON) ?>" target="_blank" title="WhatsApp">
              <i class="fab fa-whatsapp"></i>
            </a>
          </div>
        </div>

        <div class="col-lg-2 col-md-6 mb-4">
          <h5 class="iq-footer-baslik">Kategoriler</h5>
          <?php
            $kat = get_terms(['taxonomy'=>'product_cat','exclude'=>[get_option('default_product_cat')],'number'=>8,'hide_empty'=>false]);
            if ($kat && !is_wp_error($kat)):
          ?><ul class="iq-footer-menu">
            <?php foreach ($kat as $k): ?>
            <li><a href="<?= get_term_link($k) ?>"><?= esc_html($k->name) ?></a></li>
            <?php endforeach; ?>
          </ul><?php endif; ?>
        </div>

        <div class="col-lg-2 col-md-6 mb-4">
          <h5 class="iq-footer-baslik">Hizmetlerimiz</h5>
          <ul class="iq-footer-menu">
            <li><a href="#">Hakkımızda</a></li>
            <li><a href="<?= get_permalink(wc_get_page_id('shop')) ?>">Mağaza</a></li>
            <li><a href="#">İade & Değişim</a></li>
            <li><a href="#">Garanti Koşulları</a></li>
            <li><a href="#">SSS</a></li>
            <li><a href="#">İletişim</a></li>
          </ul>
        </div>

        <div class="col-lg-4 col-md-6 mb-4">
          <h5 class="iq-footer-baslik">Bülten</h5>
          <p>İlk alışverişinizde <strong>50₺ indirim</strong> için kayıt olun.</p>
          <?php if (is_plugin_active('mailchimp-for-wp/mailchimp-for-wp.php')): ?>
            <?php echo do_shortcode('[mc4wp_form id=""]'); ?>
          <?php else: ?>
          <form class="iq-bulten-form" onsubmit="iqBultenKayit(event)">
            <div class="iq-bulten-grup">
              <input type="email" placeholder="E-posta adresiniz" required>
              <button type="submit">Kayıt Ol</button>
            </div>
          </form>
          <?php endif; ?>
          <div class="iq-odeme-yontemleri mt-3">
            <img src="<?= get_stylesheet_directory_uri() ?>/images/visa.svg"       alt="Visa"       height="28">
            <img src="<?= get_stylesheet_directory_uri() ?>/images/mastercard.svg" alt="Mastercard" height="28">
            <img src="<?= get_stylesheet_directory_uri() ?>/images/troy.svg"       alt="Troy"       height="28">
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="iq-footer-alt">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-md-6">
          <p class="mb-0">&copy; <?= date('Y') ?> <?= IQ_AD ?> — Tüm hakları saklıdır.</p>
        </div>
        <div class="col-md-6 text-end">
          <a href="#">Gizlilik Politikası</a> &nbsp;|&nbsp; <a href="#">KVKK</a>
        </div>
      </div>
    </div>
  </div>
</footer>
<?php }

/* ─────────────────────────────────────────────────────────────
   8. WOOCOMMERCE AYARLAR
───────────────────────────────────────────────────────────── */
// Para birimi sembolü
add_filter('woocommerce_currency_symbol', function($s, $c) {
    return $c === 'TRY' ? '₺' : $s;
}, 10, 2);

// Fiyat formatı: 1.299,00 ₺
add_filter('woocommerce_price_format', function() { return '%2$s %1$s'; });

// Sepet bildirimi (Türkçe)
add_filter('woocommerce_add_to_cart_message_html', function($msg, $products) {
    return '<a href="' . wc_get_cart_url() . '">Sepete git</a> — ürün sepete eklendi.';
}, 10, 2);

// Ürün adeti: mini cart & checkout sayfasında göster
add_filter('woocommerce_show_cart_item_quantity', '__return_true');

// Ürün resmi hover için 2. resim
add_action('woocommerce_before_shop_loop_item_title', 'iq_urun_gorsel_hover', 11);
function iq_urun_gorsel_hover() {
    global $product;
    $gallery = $product->get_gallery_image_ids();
    if (!empty($gallery)) {
        echo '<div class="iq-gorsel-hover">';
        echo wp_get_attachment_image($gallery[0], 'woocommerce_thumbnail', false, ['class'=>'iq-ikinci-gorsel']);
        echo '</div>';
    }
}

// Ücretsiz kargo bilgilendirmesi (sepet altında)
add_action('woocommerce_after_cart_totals', 'iq_kargo_bilgi');
function iq_kargo_bilgi() {
    $hedef = 500;
    $toplam = WC()->cart->get_subtotal();
    if ($toplam < $hedef) {
        $kalan = $hedef - $toplam;
        echo '<p class="iq-kargo-bilgi">
            <strong>' . wc_price($kalan) . '</strong> daha harcayın, kargo ücretsiz!
          </p>';
    } else {
        echo '<p class="iq-kargo-bilgi iq-kargo-tamam">🎉 Ücretsiz kargo kazandınız!</p>';
    }
}

// Breadcrumb → anasayfa & mağaza
add_filter('woocommerce_breadcrumb_defaults', function($crumbs) {
    $crumbs['home'] = 'Ana Sayfa';
    return $crumbs;
});

/* ─────────────────────────────────────────────────────────────
   9. SEO — SCHEMA MARKUP
───────────────────────────────────────────────────────────── */
add_action('wp_head', 'iq_schema_local_business');
function iq_schema_local_business() {
    if (!is_front_page()) return;
    $schema = [
        '@context'  => 'https://schema.org',
        '@type'     => 'ElectronicsStore',
        'name'      => IQ_AD,
        'description' => IQ_SLOGAN,
        'url'       => home_url('/'),
        'telephone' => IQ_TELEFON,
        'address'   => [
            '@type'           => 'PostalAddress',
            'streetAddress'   => 'Yenidoğan, Kızılay Sokağı No:41',
            'addressLocality' => 'Bayrampaşa',
            'addressRegion'   => 'İstanbul',
            'postalCode'      => '34040',
            'addressCountry'  => 'TR',
        ],
        'sameAs' => [IQ_INSTAGRAM, IQ_FACEBOOK],
    ];
    echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>';
}

/* ─────────────────────────────────────────────────────────────
   10. AJAX — SEPET İŞLEMLERİ
───────────────────────────────────────────────────────────── */
add_action('wp_ajax_iq_sepet_kaldir',       'iq_ajax_kaldir');
add_action('wp_ajax_nopriv_iq_sepet_kaldir','iq_ajax_kaldir');
function iq_ajax_kaldir() {
    check_ajax_referer('iq_nonce', 'nonce');
    $key = sanitize_text_field($_POST['key'] ?? '');
    if ($key && WC()->cart->remove_cart_item($key)) {
        wp_send_json_success([
            'adet'   => WC()->cart->get_cart_contents_count(),
            'toplam' => WC()->cart->get_cart_total(),
        ]);
    }
    wp_send_json_error('Ürün kaldırılamadı');
}

add_action('wp_ajax_iq_arama',       'iq_ajax_arama');
add_action('wp_ajax_nopriv_iq_arama','iq_ajax_arama');
function iq_ajax_arama() {
    check_ajax_referer('iq_nonce', 'nonce');
    $q = sanitize_text_field($_GET['q'] ?? '');
    if (strlen($q) < 2) wp_send_json([]);

    $sorgu = new WP_Query([
        'post_type'      => 'product',
        'post_status'    => 'publish',
        's'              => $q,
        'posts_per_page' => 7,
    ]);

    $sonuclar = [];
    foreach ($sorgu->posts as $post) {
        $urun = wc_get_product($post->ID);
        $sonuclar[] = [
            'id'     => $post->ID,
            'baslik' => $post->post_title,
            'url'    => get_permalink($post->ID),
            'fiyat'  => $urun->get_price_html(),
            'gorsel' => get_the_post_thumbnail_url($post->ID, 'thumbnail') ?: wc_placeholder_img_src('thumbnail'),
        ];
    }
    wp_send_json($sonuclar);
}

/* ─────────────────────────────────────────────────────────────
   11. ÖZEL META TAGS (OG / Twitter Card)
───────────────────────────────────────────────────────────── */
add_action('wp_head', 'iq_og_tags', 5);
function iq_og_tags() {
    if (is_product()) {
        global $post;
        $urun = wc_get_product($post->ID);
        $gorsel = get_the_post_thumbnail_url($post->ID, 'large') ?: '';
        echo '<meta property="og:type"        content="product">' . "\n";
        echo '<meta property="og:title"       content="' . esc_attr(get_the_title()) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr(wp_strip_all_tags($urun->get_short_description())) . '">' . "\n";
        echo '<meta property="og:image"       content="' . esc_url($gorsel) . '">' . "\n";
        echo '<meta property="og:url"         content="' . esc_url(get_permalink()) . '">' . "\n";
        echo '<meta name="twitter:card"       content="summary_large_image">' . "\n";
    }
}

/* ─────────────────────────────────────────────────────────────
   12. PERFORMANS OPTİMİZASYONU
───────────────────────────────────────────────────────────── */
// Emoji script'lerini kaldır (gereksiz)
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('wp_print_styles', 'print_emoji_styles');

// Query string kaldır (cache dostu)
add_filter('style_loader_src',  'iq_src_temizle', 10, 2);
add_filter('script_loader_src', 'iq_src_temizle', 10, 2);
function iq_src_temizle($src, $handle) {
    if (strpos($src, 'ver=') && strpos($handle, 'iq-') === false) {
        $src = remove_query_arg('ver', $src);
    }
    return $src;
}

// Yazar sayfalarını kapat (güvenlik)
add_filter('redirect_canonical', function($url) {
    if (is_author()) { wp_redirect(home_url(), 301); exit; }
    return $url;
});

/* ─────────────────────────────────────────────────────────────
   13. ADMIN PANELI ÖZELLEŞTIRME
───────────────────────────────────────────────────────────── */
add_filter('admin_footer_text', function() {
    return 'İQ Elektronik — WordPress Yönetim Paneli | <em>Teknolojide Akıllı Tercih</em>';
});

// Login sayfası logosu
add_action('login_enqueue_scripts', 'iq_login_logo');
function iq_login_logo() { ?>
<style>
#login h1 a {
  background-image: url('<?= get_stylesheet_directory_uri() ?>/images/logo.svg') !important;
  background-size: contain !important;
  width: 200px !important;
  height: 60px !important;
}
</style>
<?php }
add_filter('login_headerurl', fn() => home_url('/'));
add_filter('login_headertext', fn() => IQ_AD);
