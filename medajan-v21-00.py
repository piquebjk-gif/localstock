# -*- coding: utf-8 -*-
"""
MedAjan v21.00 — Ana Giriş Noktası
Med Tuning · Diyarbakır

Kullanım:
    python medajan-v21-00.py          → GUI + Web birlikte
    python medajan-v21-00.py --web    → Sadece web
    python medajan-v21-00.py --nogui  → Sadece web (GUI olmadan)
"""

import sys
import os
import threading
import time
import argparse
from pathlib import Path

# ── Proje kök dizinini path'e ekle ───────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# ── Log sistemi ───────────────────────────────────────────────────────────────
try:
    from loguru import logger
    LOG_DOSYASI = BASE_DIR / "logs" / "medajan.log"
    LOG_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(LOG_DOSYASI),
        rotation="10 MB",
        retention=5,
        encoding="utf-8",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# ── Core ──────────────────────────────────────────────────────────────────────
from core.brain import Brain
from core.instagram import Instagram
from core.facebook import Facebook
from core.whatsapp import WhatsApp
from core.tiktok import TikTok

# ── Agents ───────────────────────────────────────────────────────────────────
from agents.medajan_ai import MedAjanAI
from agents.dm_handler import DMHandler
from agents.comment_handler import CommentHandler
from agents.retargeting import RetargetingAgent
from agents.story_reels_manager import StoryReelsManager

# ── Web ───────────────────────────────────────────────────────────────────────
from web.dashboard import WebDashboard


def baslat(gui: bool = True, web: bool = True):
    """
    Tüm sistemi başlat.
    1. Brain (merkezi beyin)
    2. Platform modülleri
    3. AI ajan
    4. Handler ajanları
    5. Web dashboard
    6. GUI (opsiyonel)
    """

    logger.info("=" * 60)
    logger.info("MedAjan v21.00 başlatılıyor...")
    logger.info("Med Tuning · Diyarbakır")
    logger.info("=" * 60)

    # ── 1. Brain ──────────────────────────────────────────────────────────────
    brain = Brain()

    # ── 2. Platform Modülleri ─────────────────────────────────────────────────
    instagram = Instagram(brain)
    facebook  = Facebook(brain)
    whatsapp  = WhatsApp(brain)
    tiktok    = TikTok(brain)

    platformlar = {
        "instagram": instagram,
        "facebook":  facebook,
        "whatsapp":  whatsapp,
        "tiktok":    tiktok,
    }

    # ── 3. Ana AI Ajan ────────────────────────────────────────────────────────
    ai = MedAjanAI(brain)
    ai.baslat()

    # ── 4. Handler Ajanları ───────────────────────────────────────────────────
    dm_handler = DMHandler(brain, ai, platformlar)
    dm_handler.baslat()

    comment_handler = CommentHandler(brain, ai, platformlar)
    comment_handler.baslat()

    retargeting = RetargetingAgent(brain, ai, platformlar)
    retargeting.baslat()

    story_mgr = StoryReelsManager(brain, platformlar)
    story_mgr.baslat()

    # ── 5. Web Dashboard ──────────────────────────────────────────────────────
    web_dashboard = None
    if web:
        web_dashboard = WebDashboard(brain, ai, platformlar)
        port = brain.ayar_al("uygulama", "web_port", varsayilan=8000)
        web_dashboard.baslat(port=port)
        logger.info(f"Web panel: http://localhost:{port}")

    # ── 6. GUI ────────────────────────────────────────────────────────────────
    if gui:
        try:
            from gui.app import gui_baslat
            sonuc = gui_baslat(brain, ai, platformlar)
            if sonuc:
                app, pencere = sonuc
                logger.info("GUI başlatıldı")
                # GUI'nin event loop'u burada bloklar
                sys.exit(app.exec_())
            else:
                logger.warning("GUI başlatılamadı, web modunda devam ediliyor")
                _bekle()
        except Exception as e:
            logger.error(f"GUI başlatma hatası: {e}")
            if web:
                logger.info("Web paneli çalışıyor: http://localhost:8000")
                _bekle()
    else:
        logger.info("GUI devre dışı. Web panel aktif.")
        _bekle()


def _bekle():
    """Ctrl+C ile durdurulana kadar bekle."""
    logger.info("Çalışıyor... Durdurmak için Ctrl+C")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("MedAjan durduruldu.")


# ── Argüman Ayrıştırma ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="MedAjan v21.00 — Med Tuning")
    parser.add_argument("--nogui", action="store_true", help="GUI olmadan çalıştır")
    parser.add_argument("--web",   action="store_true", help="Sadece web panel")
    parser.add_argument("--noweb", action="store_true", help="Web olmadan çalıştır")
    args = parser.parse_args()

    gui_aktif = not (args.nogui or args.web)
    web_aktif = not args.noweb

    baslat(gui=gui_aktif, web=web_aktif)


if __name__ == "__main__":
    main()
