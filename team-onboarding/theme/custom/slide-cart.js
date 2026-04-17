/* IQ Elektronik — Slide Cart (AJAX) */
(function($) {
  'use strict';

  // Sepete ekleme → slide cart aç
  $(document.body).on('added_to_cart', function(e, fragments, cart_hash, $btn) {
    iqSlideCartYenile(fragments);
    $('#iqSlideCart').addClass('aktif');
    $('#iqOverlay').addClass('aktif');
    $('body').css('overflow', 'hidden');
    if (window.iqBildirim) {
      var isim = $btn.closest('.product, .woocommerce').find('.woocommerce-loop-product__title, .product_title').first().text().trim();
      iqBildirim((isim || 'Ürün') + ' sepete eklendi', 'basari');
    }
    // Header sepet badge bounce
    $('.cart-contents').addClass('iq-bounce');
    setTimeout(function() { $('.cart-contents').removeClass('iq-bounce'); }, 700);
  });

  // Fragment güncelleme → adet badge yenile
  $(document.body).on('wc_fragments_refreshed wc_fragments_loaded', function() {
    var adet = WC() ? WC().cart_contents_count : 0;
    $('.iq-nav-badge, .iq-sc-adet').text(adet || '');
  });

  // Ürün sil (AJAX)
  $(document).on('click', '.iq-sc-sil', function() {
    var $item = $(this).closest('.iq-sc-urun');
    var key = $(this).data('key');
    $item.css('opacity', 0.4);

    $.post(iqData.ajaxurl, {
      action: 'iq_sepet_kaldir',
      nonce:  iqData.nonce,
      key:    key
    }, function(res) {
      if (res.success) {
        $item.slideUp(250, function() { $(this).remove(); });
        $('.iq-sc-adet').text('(' + res.data.adet + ')');
        $('.iq-nav-badge').text(res.data.adet || '');
        if (res.data.adet === 0) {
          iqBosSepetGoster();
        }
        // WC fragment'larını zorla yenile
        $(document.body).trigger('wc_fragment_refresh');
      } else {
        $item.css('opacity', 1);
        if (window.iqBildirim) iqBildirim('Ürün kaldırılamadı', 'hata');
      }
    });
  });

  // Adet artır / azalt (AJAX)
  $(document).on('click', '.iq-qty-artir, .iq-qty-azalt', function() {
    var $btn   = $(this);
    var $urun  = $btn.closest('.iq-sc-urun');
    var key    = $urun.data('key');
    var $span  = $urun.find('.iq-sc-adet-kontrol span');
    var mevcut = parseInt($span.text()) || 1;
    var yeni   = $btn.hasClass('iq-qty-artir') ? mevcut + 1 : Math.max(1, mevcut - 1);
    $span.text(yeni);

    // Sepeti güncelle
    var veri = { action: 'woocommerce_update_order_review' };
    veri['cart[' + key + '][qty]'] = yeni;
    $.post(iqData.ajaxurl, veri, function() {
      $(document.body).trigger('wc_fragment_refresh');
    });
  });

  function iqBosSepetGoster() {
    $('.iq-sc-govde').html(
      '<div class="iq-sc-bos">'
      + '<i class="fas fa-shopping-cart"></i>'
      + '<p>Sepetiniz boş.</p>'
      + '<a href="' + iqData.shopUrl + '" class="iq-btn">Alışverişe Başla</a>'
      + '</div>'
    );
    $('.iq-sc-footer').hide();
  }

  function iqSlideCartYenile(fragments) {
    if (!fragments) return;
    // Electro fragment varsa güncelle
    $.each(fragments, function(key, val) {
      $(key).replaceWith(val);
    });
  }

})(jQuery);
