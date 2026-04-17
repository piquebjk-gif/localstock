/* IQ Elektronik — Canlı Arama */
(function($) {
  'use strict';

  var zamanAsimi;
  var $giris, $sonuclar;

  $(document).ready(function() {
    $giris    = $('.iq-arama-giris');
    $sonuclar = $('.iq-arama-sonuclar');
    if (!$giris.length) return;

    $giris.on('input', function() {
      clearTimeout(zamanAsimi);
      var q = $(this).val().trim();
      if (q.length < 2) { $sonuclar.empty(); return; }
      $sonuclar.html('<div class="iq-arama-yukleniyor"><i class="fas fa-spinner fa-spin"></i> Aranıyor...</div>');
      zamanAsimi = setTimeout(function() { iqArama(q); }, 280);
    });

    // Klavye navigasyonu
    $giris.on('keydown', function(e) {
      var $items = $sonuclar.find('.iq-arama-item');
      var $aktif = $items.filter('.iq-secili');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        var $sonraki = $aktif.length ? $aktif.next() : $items.first();
        $items.removeClass('iq-secili');
        $sonraki.addClass('iq-secili');
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        var $onceki = $aktif.length ? $aktif.prev() : $items.last();
        $items.removeClass('iq-secili');
        $onceki.addClass('iq-secili');
      } else if (e.key === 'Enter') {
        if ($aktif.length) { e.preventDefault(); window.location = $aktif.attr('href'); }
      }
    });
  });

  function iqArama(q) {
    $.ajax({
      url:      iqData.ajaxurl,
      data:     { action: 'iq_arama', nonce: iqData.nonce, q: q },
      dataType: 'json',
      success: function(sonuclar) {
        if (!sonuclar || !sonuclar.length) {
          $sonuclar.html('<div class="iq-arama-bos"><i class="fas fa-search"></i> "' + iqVurgula(q) + '" için sonuç bulunamadı</div>');
          return;
        }
        var html = '';
        $.each(sonuclar, function(i, u) {
          html += '<a href="' + u.url + '" class="iq-arama-item">'
            + '<img src="' + u.gorsel + '" alt="' + iqKacis(u.baslik) + '" loading="lazy">'
            + '<div>'
            + '<div class="iq-arama-baslik">' + iqVurgula(u.baslik, q) + '</div>'
            + '<div class="iq-arama-fiyat">' + u.fiyat + '</div>'
            + '</div>'
            + '</a>';
        });
        $sonuclar.html(html);
      },
      error: function() {
        $sonuclar.html('<div class="iq-arama-bos">Bir hata oluştu, lütfen tekrar deneyin.</div>');
      }
    });
  }

  function iqVurgula(metin, q) {
    if (!q) return $('<div>').text(metin).html();
    var guvli = metin.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return $('<div>').text(metin).html()
      .replace(new RegExp('(' + $('<div>').text(q).html() + ')', 'gi'), '<mark>$1</mark>');
  }

  function iqKacis(str) {
    return $('<div>').text(str).html();
  }

})(jQuery);
