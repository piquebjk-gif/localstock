# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - PyQt5 Masaüstü GUI
Qt::AA_EnableHighDpiScaling QApplication'dan ÖNCE set edilir.
"""

import sys
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTabWidget, QTextEdit, QLineEdit,
        QGroupBox, QGridLayout, QSplitter, QScrollArea, QFrame,
        QSizePolicy, QMessageBox, QSystemTrayIcon, QMenu, QAction
    )
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl
    from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
    PYQT5_MEVCUT = True
except ImportError:
    PYQT5_MEVCUT = False

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# ── Koyu Tema Paleti ──────────────────────────────────────────────────────────
KOYU_STIL = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QTabWidget::pane {
    border: 1px solid #30363d;
    background: #161b22;
    border-radius: 8px;
}
QTabBar::tab {
    background: #21262d;
    color: #8b949e;
    padding: 8px 18px;
    border: 1px solid #30363d;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #161b22; color: #58a6ff; border-bottom: 2px solid #58a6ff; }
QTabBar::tab:hover { background: #30363d; color: #e6edf3; }
QGroupBox {
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
    color: #8b949e;
    font-size: 11px;
    text-transform: uppercase;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QPushButton {
    background: #238636;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover { background: #2ea043; }
QPushButton:pressed { background: #1a7f37; }
QPushButton#btnDanger { background: #da3633; }
QPushButton#btnDanger:hover { background: #f85149; }
QPushButton#btnBlue { background: #1f6feb; }
QPushButton#btnBlue:hover { background: #388bfd; }
QPushButton#btnGray { background: #21262d; border: 1px solid #30363d; }
QPushButton#btnGray:hover { background: #30363d; }
QLineEdit, QTextEdit {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    padding: 6px 10px;
    font-size: 13px;
}
QLineEdit:focus, QTextEdit:focus { border-color: #58a6ff; }
QLabel { color: #e6edf3; }
QLabel#labelSub { color: #8b949e; font-size: 12px; }
QLabel#labelGreen { color: #3fb950; font-weight: bold; }
QLabel#labelRed { color: #f85149; font-weight: bold; }
QLabel#labelBlue { color: #58a6ff; font-weight: bold; }
QLabel#labelBig { font-size: 28px; font-weight: bold; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #161b22; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #30363d; border-radius: 4px; }
QFrame#separator { background: #30363d; }
"""


# ── Arka Plan Güncelleme Thread'i ─────────────────────────────────────────────
class GuncelleyiciThread(QThread):
    durum_guncellendi = pyqtSignal(dict)

    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self._calis = True

    def run(self):
        import time
        while self._calis:
            try:
                durum = self.brain.tum_durum()
                durum["mesajlar"] = self.brain.son_mesajlar(limit=20)
                self.durum_guncellendi.emit(durum)
            except Exception:
                pass
            time.sleep(3)

    def durdur(self):
        self._calis = False


# ── Ana Pencere ───────────────────────────────────────────────────────────────
class AnaPencere(QMainWindow):
    def __init__(self, brain, ai_ajan, platformlar: dict = None):
        super().__init__()
        self.brain = brain
        self.ai = ai_ajan
        self.platformlar = platformlar or {}

        self.setWindowTitle("MedAjan v21.00 — Med Tuning Diyarbakır")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        self._widget_olustur()
        self._guncelleme_baslat()

    # ── Widget Kurulumu ───────────────────────────────────────────────────────

    def _widget_olustur(self):
        merkez = QWidget()
        self.setCentralWidget(merkez)
        ana_layout = QVBoxLayout(merkez)
        ana_layout.setSpacing(0)
        ana_layout.setContentsMargins(0, 0, 0, 0)

        # Üst başlık
        ana_layout.addWidget(self._baslik_olustur())

        # Sekmeler
        self.sekmeler = QTabWidget()
        self.sekmeler.setDocumentMode(True)
        ana_layout.addWidget(self.sekmeler)

        self.sekmeler.addTab(self._panel_sekme(), "📊  Panel")
        self.sekmeler.addTab(self._mesajlar_sekme(), "💬  Mesajlar")
        self.sekmeler.addTab(self._test_sekme(), "🧪  Test AI")
        self.sekmeler.addTab(self._platformlar_sekme(), "🔌  Platformlar")
        self.sekmeler.addTab(self._ayarlar_sekme(), "⚙️  Ayarlar")

    def _baslik_olustur(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(56)
        w.setStyleSheet("background:#161b22;border-bottom:1px solid #30363d;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(20, 0, 20, 0)

        ico = QLabel("🤖")
        ico.setFont(QFont("Segoe UI", 22))
        lay.addWidget(ico)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        baslik_lbl = QLabel("MedAjan v21.00")
        baslik_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sub_lbl = QLabel("Med Tuning · Diyarbakır")
        sub_lbl.setObjectName("labelSub")
        vbox.addWidget(baslik_lbl)
        vbox.addWidget(sub_lbl)
        lay.addLayout(vbox)
        lay.addStretch()

        self.durum_lbl = QLabel("● Başlatılıyor...")
        self.durum_lbl.setObjectName("labelSub")
        lay.addWidget(self.durum_lbl)

        web_btn = QPushButton("🌐 Web Panel Aç")
        web_btn.setObjectName("btnBlue")
        web_btn.clicked.connect(self._web_ac)
        lay.addWidget(web_btn)
        return w

    # ── Panel Sekmesi ─────────────────────────────────────────────────────────

    def _panel_sekme(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        # İstatistik kartları
        kart_lay = QHBoxLayout()
        self.stat_toplam = self._istatistik_karti("Toplam Mesaj", "0", "#e6edf3")
        self.stat_cevap  = self._istatistik_karti("Yanıtlanan", "0", "#3fb950")
        self.stat_plat   = self._istatistik_karti("Aktif Platform", "0", "#58a6ff")
        kart_lay.addWidget(self.stat_toplam)
        kart_lay.addWidget(self.stat_cevap)
        kart_lay.addWidget(self.stat_plat)
        lay.addLayout(kart_lay)

        # Platform durumları
        plat_grup = QGroupBox("Platform Durumları")
        plat_ilay = QGridLayout(plat_grup)
        plat_ilay.setSpacing(8)
        self._plat_etiketleri = {}
        self._plat_butonlari = {}
        platformlar_listesi = [
            ("instagram", "📸 Instagram"),
            ("whatsapp",  "💚 WhatsApp"),
            ("facebook",  "📘 Facebook"),
            ("tiktok",    "🎵 TikTok"),
        ]
        for i, (pid, padi) in enumerate(platformlar_listesi):
            lbl_ad = QLabel(padi)
            lbl_ad.setFont(QFont("Segoe UI", 12, QFont.Bold))
            lbl_durum = QLabel("● Bağlı değil")
            lbl_durum.setObjectName("labelRed")
            btn_baglan = QPushButton("Bağlan")
            btn_baglan.setFixedWidth(90)
            btn_baglan.clicked.connect(lambda _, p=pid: self._platform_baglan(p))
            btn_kes = QPushButton("Kes")
            btn_kes.setObjectName("btnDanger")
            btn_kes.setFixedWidth(60)
            btn_kes.clicked.connect(lambda _, p=pid: self._platform_kes(p))

            self._plat_etiketleri[pid] = lbl_durum
            self._plat_butonlari[pid] = btn_baglan

            plat_ilay.addWidget(lbl_ad, i, 0)
            plat_ilay.addWidget(lbl_durum, i, 1)
            plat_ilay.addWidget(btn_baglan, i, 2)
            plat_ilay.addWidget(btn_kes, i, 3)
        lay.addWidget(plat_grup)

        # Son mesajlar
        msg_grup = QGroupBox("Son Mesajlar")
        msg_ilay = QVBoxLayout(msg_grup)
        self.mesaj_kutusu = QTextEdit()
        self.mesaj_kutusu.setReadOnly(True)
        self.mesaj_kutusu.setMinimumHeight(200)
        self.mesaj_kutusu.setStyleSheet(
            "QTextEdit { background:#161b22; border:1px solid #30363d; "
            "border-radius:8px; font-family:'Consolas','Courier New'; font-size:12px; }"
        )
        msg_ilay.addWidget(self.mesaj_kutusu)
        lay.addWidget(msg_grup)
        return w

    def _istatistik_karti(self, baslik: str, deger: str, renk: str) -> QGroupBox:
        g = QGroupBox(baslik)
        lay = QVBoxLayout(g)
        lbl = QLabel(deger)
        lbl.setObjectName("labelBig")
        lbl.setStyleSheet(f"color:{renk};font-size:32px;font-weight:bold;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        g._deger_lbl = lbl
        return g

    # ── Mesajlar Sekmesi ──────────────────────────────────────────────────────

    def _mesajlar_sekme(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        self.tum_mesajlar_kutu = QTextEdit()
        self.tum_mesajlar_kutu.setReadOnly(True)
        self.tum_mesajlar_kutu.setStyleSheet(
            "QTextEdit { background:#161b22; border:1px solid #30363d; "
            "border-radius:8px; font-family:'Consolas','Courier New'; font-size:12px; }"
        )
        yenile_btn = QPushButton("🔄 Yenile")
        yenile_btn.clicked.connect(self._mesajlari_yenile)
        lay.addWidget(yenile_btn)
        lay.addWidget(self.tum_mesajlar_kutu)
        return w

    # ── Test AI Sekmesi ───────────────────────────────────────────────────────

    def _test_sekme(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        grup = QGroupBox("AI Asistan Test — Med Tuning")
        glay = QVBoxLayout(grup)

        self.chat_kutu = QTextEdit()
        self.chat_kutu.setReadOnly(True)
        self.chat_kutu.setMinimumHeight(340)
        self.chat_kutu.setStyleSheet(
            "QTextEdit { background:#0d1117; border:1px solid #30363d; "
            "border-radius:8px; font-size:13px; }"
        )
        self.chat_kutu.setHtml(
            "<p style='color:#3fb950'>🤖 <b>MedAjan:</b> Merhaba! Med Tuning Diyarbakır AI asistanıyım. "
            "Araç multimedya ekranları, ses sistemleri ve aksesuar konularında yardımcı olabilirim.</p>"
        )
        glay.addWidget(self.chat_kutu)

        giris_lay = QHBoxLayout()
        self.chat_girdi = QLineEdit()
        self.chat_girdi.setPlaceholderText("Mesajınızı yazın... (örn: Astra J ekran fiyatı?)")
        self.chat_girdi.returnPressed.connect(self._test_mesaj_gonder)
        self.chat_girdi.setMinimumHeight(38)
        gonder_btn = QPushButton("Gönder ➤")
        gonder_btn.setObjectName("btnBlue")
        gonder_btn.setMinimumHeight(38)
        gonder_btn.clicked.connect(self._test_mesaj_gonder)
        giris_lay.addWidget(self.chat_girdi)
        giris_lay.addWidget(gonder_btn)
        glay.addLayout(giris_lay)

        lay.addWidget(grup)
        return w

    # ── Platformlar Sekmesi ───────────────────────────────────────────────────

    def _platformlar_sekme(self) -> QWidget:
        w = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        ic = QWidget()
        lay = QVBoxLayout(ic)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Instagram
        ig_grup = QGroupBox("📸 Instagram Ayarları")
        ig_lay = QGridLayout(ig_grup)
        ig_lay.addWidget(QLabel("Kullanıcı Adı:"), 0, 0)
        self.ig_user = QLineEdit()
        self.ig_user.setPlaceholderText("@kullanici_adi")
        ig_lay.addWidget(self.ig_user, 0, 1)
        ig_lay.addWidget(QLabel("Şifre:"), 1, 0)
        self.ig_pass = QLineEdit()
        self.ig_pass.setEchoMode(QLineEdit.Password)
        self.ig_pass.setPlaceholderText("••••••")
        ig_lay.addWidget(self.ig_pass, 1, 1)
        ig_lay.addWidget(QLabel("Proxy (opsiyonel):"), 2, 0)
        self.ig_proxy = QLineEdit()
        self.ig_proxy.setPlaceholderText("http://user:pass@ip:port")
        ig_lay.addWidget(self.ig_proxy, 2, 1)
        ig_btn_lay = QHBoxLayout()
        ig_kaydet_btn = QPushButton("💾 Kaydet & Bağlan")
        ig_kaydet_btn.clicked.connect(self._ig_kaydet_baglan)
        ig_kes_btn = QPushButton("Bağlantıyı Kes")
        ig_kes_btn.setObjectName("btnDanger")
        ig_kes_btn.clicked.connect(lambda: self._platform_kes("instagram"))
        ig_btn_lay.addWidget(ig_kaydet_btn)
        ig_btn_lay.addWidget(ig_kes_btn)
        ig_btn_lay.addStretch()
        ig_lay.addLayout(ig_btn_lay, 3, 0, 1, 2)
        lay.addWidget(ig_grup)

        # WhatsApp
        wa_grup = QGroupBox("💚 WhatsApp Ayarları")
        wa_lay = QVBoxLayout(wa_grup)
        wa_lbl = QLabel(
            "WhatsApp Web bağlantısı için QR kod tarama gereklidir.\n"
            "Bağlan butonuna tıkladığınızda Chromium açılacak, QR kodu telefonunuzla tarayın."
        )
        wa_lbl.setObjectName("labelSub")
        wa_lbl.setWordWrap(True)
        wa_lay.addWidget(wa_lbl)
        wa_btn = QPushButton("📱 QR ile Bağlan")
        wa_btn.setObjectName("btnBlue")
        wa_btn.clicked.connect(lambda: self._platform_baglan("whatsapp"))
        wa_lay.addWidget(wa_btn)
        lay.addWidget(wa_grup)

        # Facebook
        fb_grup = QGroupBox("📘 Facebook Ayarları")
        fb_lay = QGridLayout(fb_grup)
        fb_lay.addWidget(QLabel("Page ID:"), 0, 0)
        self.fb_page = QLineEdit()
        self.fb_page.setPlaceholderText("sayfa id numarası")
        fb_lay.addWidget(self.fb_page, 0, 1)
        fb_lay.addWidget(QLabel("Access Token:"), 1, 0)
        self.fb_token = QLineEdit()
        self.fb_token.setPlaceholderText("EAABxx...")
        fb_lay.addWidget(self.fb_token, 1, 1)
        fb_btn = QPushButton("💾 Kaydet & Bağlan")
        fb_btn.clicked.connect(self._fb_kaydet_baglan)
        fb_lay.addLayout(QHBoxLayout(), 2, 0, 1, 2)
        fb_lay.addWidget(fb_btn, 2, 0, 1, 2)
        lay.addWidget(fb_grup)

        lay.addStretch()
        scroll.setWidget(ic)
        outer = QVBoxLayout(w)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        return w

    # ── Ayarlar Sekmesi ───────────────────────────────────────────────────────

    def _ayarlar_sekme(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        isletme_grup = QGroupBox("İşletme Bilgileri")
        ig_lay = QGridLayout(isletme_grup)
        ig_lay.addWidget(QLabel("İşletme Adı:"), 0, 0)
        self.ay_isletme = QLineEdit("Med Tuning")
        ig_lay.addWidget(self.ay_isletme, 0, 1)
        ig_lay.addWidget(QLabel("Şehir:"), 1, 0)
        self.ay_sehir = QLineEdit("Diyarbakır")
        ig_lay.addWidget(self.ay_sehir, 1, 1)
        ig_lay.addWidget(QLabel("Telefon:"), 2, 0)
        self.ay_tel = QLineEdit()
        self.ay_tel.setPlaceholderText("05XX XXX XX XX")
        ig_lay.addWidget(self.ay_tel, 2, 1)
        lay.addWidget(isletme_grup)

        ai_grup = QGroupBox("Yapay Zeka")
        ai_lay = QGridLayout(ai_grup)
        ai_lay.addWidget(QLabel("OpenAI API Key (opsiyonel):"), 0, 0)
        self.ay_oai = QLineEdit()
        self.ay_oai.setEchoMode(QLineEdit.Password)
        self.ay_oai.setPlaceholderText("sk-... (boş bırakılabilir)")
        ai_lay.addWidget(self.ay_oai, 0, 1)
        ai_lay.addWidget(QLabel("Yanıt Gecikmesi (sn):"), 1, 0)
        self.ay_gecikme = QLineEdit("3")
        ai_lay.addWidget(self.ay_gecikme, 1, 1)
        lay.addWidget(ai_grup)

        kaydet_btn = QPushButton("💾 Ayarları Kaydet")
        kaydet_btn.clicked.connect(self._ayarlari_kaydet)
        lay.addWidget(kaydet_btn)
        lay.addStretch()
        return w

    # ── İşlevler ──────────────────────────────────────────────────────────────

    def _guncelleme_baslat(self):
        self._guncelleme = GuncelleyiciThread(self.brain)
        self._guncelleme.durum_guncellendi.connect(self._arayuzu_guncelle)
        self._guncelleme.start()

    def _arayuzu_guncelle(self, durum: dict):
        stat = durum.get("istatistikler", {})
        plat = durum.get("platformlar", {})
        mesajlar = durum.get("mesajlar", [])

        self.stat_toplam._deger_lbl.setText(str(stat.get("toplam_mesaj", 0)))
        self.stat_cevap._deger_lbl.setText(str(stat.get("cevaplanan", 0)))

        aktif = sum(1 for v in plat.values() if v)
        self.stat_plat._deger_lbl.setText(str(aktif))

        for pid, etiket in self._plat_etiketleri.items():
            if plat.get(pid):
                etiket.setText("● Bağlı")
                etiket.setObjectName("labelGreen")
            else:
                etiket.setText("● Bağlı değil")
                etiket.setObjectName("labelRed")
            etiket.style().unpolish(etiket)
            etiket.style().polish(etiket)

        self.durum_lbl.setText(f"● {aktif} platform aktif")

        if mesajlar:
            html = ""
            for m in mesajlar[:8]:
                plat_adi = (m.get("platform") or "").upper()
                kul = m.get("kullanici_adi") or m.get("kullanici_id") or "?"
                msg = (m.get("mesaj") or "")[:80]
                yanit = (m.get("yanit") or "")[:80]
                html += (
                    f"<p><span style='color:#58a6ff'>[{plat_adi}]</span> "
                    f"<b style='color:#e6edf3'>@{kul}</b>: "
                    f"<span style='color:#8b949e'>{self._html_kac(msg)}</span><br>"
                    f"<span style='color:#3fb950'>🤖 {self._html_kac(yanit)}</span></p><hr style='border-color:#30363d'>"
                )
            self.mesaj_kutusu.setHtml(html or "<p style='color:#8b949e'>Henüz mesaj yok.</p>")

    def _html_kac(self, s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _test_mesaj_gonder(self):
        metin = self.chat_girdi.text().strip()
        if not metin:
            return
        self.chat_girdi.clear()
        self.chat_kutu.append(
            f"<p style='text-align:right'>"
            f"<span style='background:#1f6feb;color:#fff;padding:4px 10px;border-radius:8px'>"
            f"{self._html_kac(metin)}</span></p>"
        )

        def _yanit_al():
            yanit = self.ai.yanit_uret(metin, kullanici_id="gui_test", platform="gui")
            self._test_yaniti_goster(yanit)

        threading.Thread(target=_yanit_al, daemon=True).start()

    def _test_yaniti_goster(self, yanit: str):
        self.chat_kutu.append(
            f"<p><span style='color:#3fb950'>🤖 <b>MedAjan:</b></span> "
            f"<span style='color:#e6edf3'>{self._html_kac(yanit)}</span></p>"
        )
        sb = self.chat_kutu.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _platform_baglan(self, platform: str):
        p = self.platformlar.get(platform)
        if not p:
            logger.warning(f"{platform} modülü yüklü değil")
            return
        def _baglan():
            sonuc = p.baglan()
            logger.info(f"{platform} bağlantı: {'OK' if sonuc else 'HATA'}")
        threading.Thread(target=_baglan, daemon=True).start()

    def _platform_kes(self, platform: str):
        p = self.platformlar.get(platform)
        if p:
            p.baglantiyi_kes()

    def _ig_kaydet_baglan(self):
        kullanici_adi = self.ig_user.text().strip()
        sifre = self.ig_pass.text().strip()
        proxy = self.ig_proxy.text().strip()
        if not kullanici_adi or not sifre:
            QMessageBox.warning(self, "Eksik Bilgi", "Kullanıcı adı ve şifre gerekli!")
            return
        self.brain.ayar_kaydet(kullanici_adi, "instagram", "kullanici_adi")
        self.brain.ayar_kaydet(sifre, "instagram", "sifre")
        if proxy:
            self.brain.ayar_kaydet(proxy, "instagram", "proxy")
        self._platform_baglan("instagram")

    def _fb_kaydet_baglan(self):
        page_id = self.fb_page.text().strip()
        token = self.fb_token.text().strip()
        if not page_id or not token:
            QMessageBox.warning(self, "Eksik Bilgi", "Page ID ve Access Token gerekli!")
            return
        self.brain.ayar_kaydet(page_id, "facebook", "page_id")
        self.brain.ayar_kaydet(token, "facebook", "access_token")
        self._platform_baglan("facebook")

    def _ayarlari_kaydet(self):
        self.brain.ayar_kaydet(self.ay_isletme.text(), "uygulama", "isletme_adi")
        self.brain.ayar_kaydet(self.ay_sehir.text(), "uygulama", "sehir")
        self.brain.ayar_kaydet(self.ay_tel.text(), "uygulama", "telefon")
        self.brain.ayar_kaydet(self.ay_oai.text(), "yapay_zeka", "openai_api_key")
        try:
            self.brain.ayar_kaydet(int(self.ay_gecikme.text()), "yapay_zeka", "yanit_gecikmesi")
        except ValueError:
            pass
        QMessageBox.information(self, "Kaydedildi", "Ayarlar başarıyla kaydedildi!")

    def _mesajlari_yenile(self):
        mesajlar = self.brain.son_mesajlar(limit=100)
        html = ""
        for m in mesajlar:
            plat = (m.get("platform") or "").upper()
            kul = m.get("kullanici_adi") or m.get("kullanici_id") or "?"
            msg = self._html_kac(m.get("mesaj") or "")
            yanit = self._html_kac((m.get("yanit") or "")[:120])
            html += (
                f"<p><span style='color:#58a6ff'>[{plat}]</span> "
                f"<b>@{kul}</b>: <span style='color:#8b949e'>{msg}</span><br>"
                f"<span style='color:#3fb950'>🤖 {yanit}</span></p>"
                f"<hr style='border-color:#30363d'>"
            )
        self.tum_mesajlar_kutu.setHtml(
            html or "<p style='color:#8b949e'>Henüz mesaj yok.</p>"
        )

    def _web_ac(self):
        import webbrowser
        port = self.brain.ayar_al("uygulama", "web_port", varsayilan=8000)
        webbrowser.open(f"http://localhost:{port}")

    def closeEvent(self, event):
        if hasattr(self, "_guncelleme"):
            self._guncelleme.durdur()
        event.accept()


# ── Başlatıcı ─────────────────────────────────────────────────────────────────

def gui_baslat(brain, ai_ajan, platformlar: dict = None):
    if not PYQT5_MEVCUT:
        logger.error("PyQt5 kurulu değil. GUI başlatılamıyor.")
        return

    # !! Bu satırlar QApplication'dan ÖNCE gelmeli !!
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(KOYU_STIL)

    pencere = AnaPencere(brain, ai_ajan, platformlar)
    pencere.show()
    return app, pencere
