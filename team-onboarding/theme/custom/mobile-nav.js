/* IQ Elektronik — Mobil Alt Navigasyon */
(function($) {
  'use strict';

  // Sepet adeti badge güncelle
  function iqBadgeGuncelle(adet) {
    var badge = $('.iq-nav-badge');
    badge.text(adet > 0 ? adet : '');
    if (adet > 0) badge.show(); else badge.hide();
  }

  // WooCommerce fragment güncellemesi gelince badge'i yenile
  $(document.body).on('wc_fragments_refreshed wc_fragments_loaded', function() {
    var adet = parseInt($('.cart-contents .count, .iq-cart-count').first().text()) || 0;
    iqBadgeGuncelle(adet);
  });

  // Aktif sayfa nav item'ını işaretle
  var mevcut = window.location.href;
  $('.iq-nav-item').each(function() {
    var href = $(this).attr('href');
    if (href && href !== '#' && mevcut.indexOf(href) !== -1) {
      $('.iq-nav-item').removeClass('aktif');
      $(this).addClass('aktif');
    }
  });

  // Arama toggle
  $(document).on('click', '.iq-arama-toggle', function(e) {
    e.preventDefault();
    var overlay = $('#iqAramaOverlay');
    overlay.fadeIn(180);
    setTimeout(function() { $('.iq-arama-giris').focus(); }, 200);
  });

  // Overlay kapatma
  $(document).on('click', '#iqAramaOverlay', function(e) {
    if ($(e.target).is('#iqAramaOverlay')) {
      $(this).fadeOut(180);
    }
  });

  // ESC kapatır
  $(document).on('keyup', function(e) {
    if (e.key === 'Escape') {
      $('#iqAramaOverlay').fadeOut(180);
      $('#iqSlideCart').removeClass('aktif');
      $('#iqOverlay').removeClass('aktif');
      $('body').css('overflow', '');
    }
  });

  // Slide Cart toggle — header sepet ikonuna tıklama
  $(document).on('click', '.cart-contents, .iq-header-sepet', function(e) {
    e.preventDefault();
    $('#iqSlideCart').addClass('aktif');
    $('#iqOverlay').addClass('aktif');
    $('body').css('overflow', 'hidden');
  });

  // Slide Cart kapat
  $(document).on('click', '#iqScKapat, #iqOverlay', function() {
    $('#iqSlideCart').removeClass('aktif');
    $('#iqOverlay').removeClass('aktif');
    $('body').css('overflow', '');
  });

  // Toast bildirimi göster
  window.iqBildirim = function(mesaj, tip) {
    tip = tip || 'basari';
    var ikonlar = { basari: 'fa-check-circle', hata: 'fa-times-circle', bilgi: 'fa-info-circle' };
    var el = $('<div class="iq-bildirim ' + (tip === 'hata' ? 'hata' : tip === 'bilgi' ? 'bilgi' : '') + '">'
      + '<i class="fas ' + (ikonlar[tip] || ikonlar.basari) + '"></i>'
      + '<span>' + mesaj + '</span>'
      + '</div>');
    $('body').append(el);
    setTimeout(function() { el.addClass('goster'); }, 30);
    setTimeout(function() { el.removeClass('goster'); setTimeout(function() { el.remove(); }, 320); }, 3500);
  };

  // Bülten form
  window.iqBultenKayit = function(e) {
    e.preventDefault();
    var email = $(e.target).find('input[type="email"]').val();
    if (!email) return;
    iqBildirim('Teşekkürler! ' + email + ' adresiniz kaydedildi.', 'basari');
    $(e.target).find('input[type="email"]').val('');
  };

})(jQuery);
