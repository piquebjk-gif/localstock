# -*- coding: utf-8 -*-
"""
MedAjan v21.00 - Web Dashboard
FastAPI tabanlı web arayüzü.
Port: 8000  →  http://localhost:8000
"""

import asyncio
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
    FASTAPI_MEVCUT = True
except ImportError:
    FASTAPI_MEVCUT = False

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"


class WebDashboard:
    def __init__(self, brain, ai_ajan, platformlar: dict = None):
        self.brain = brain
        self.ai = ai_ajan
        self.platformlar = platformlar or {}
        self._app = None
        self._server_thread = None
        self._ws_baglantilar: list = []

        if FASTAPI_MEVCUT:
            self._app = self._olustur_app()

    def _olustur_app(self):
        app = FastAPI(
            title="MedAjan v21.00",
            description="Med Tuning Diyarbakır - Otonom AI Ajan Paneli"
        )

        # Static dosyalar
        if STATIC_DIR.exists():
            app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

        # Templates
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

        # ── Sayfalar ──────────────────────────────────────────────────────────

        @app.get("/", response_class=HTMLResponse)
        async def ana_sayfa(request: Request):
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "baslik": "MedAjan v21.00 - Med Tuning"}
            )

        # ── API Endpointleri ──────────────────────────────────────────────────

        @app.get("/api/durum")
        async def durum_al():
            durum = self.brain.tum_durum()
            durum["mesajlar"] = self.brain.son_mesajlar(limit=10)
            return JSONResponse(durum)

        @app.get("/api/mesajlar")
        async def mesajlar_al(limit: int = 50):
            return JSONResponse({"mesajlar": self.brain.son_mesajlar(limit=limit)})

        @app.get("/api/istatistik")
        async def istatistik_al():
            return JSONResponse(self.brain.istatistik_al())

        @app.post("/api/mesaj-gonder")
        async def mesaj_gonder(
            platform: str = Form(...),
            kullanici_id: str = Form(...),
            mesaj: str = Form(...)
        ):
            yanit = self.ai.yanit_uret(mesaj, kullanici_id, platform)
            return JSONResponse({"yanit": yanit, "basarili": True})

        @app.post("/api/test-mesaj")
        async def test_mesaj(request: Request):
            veri = await request.json()
            mesaj = veri.get("mesaj", "")
            kullanici_id = veri.get("kullanici_id", "web_test")
            platform = veri.get("platform", "web")
            yanit = self.ai.yanit_uret(mesaj, kullanici_id, platform)
            return JSONResponse({"yanit": yanit})

        @app.get("/api/ayarlar")
        async def ayarlar_al():
            ayarlar = {}
            for bolum in ["uygulama", "yapay_zeka", "instagram", "facebook",
                          "whatsapp", "tiktok", "zamanlama"]:
                ayarlar[bolum] = self.brain.ayar_al(bolum, varsayilan={})
            return JSONResponse(ayarlar)

        @app.post("/api/ayarlar")
        async def ayarlar_kaydet(request: Request):
            veri = await request.json()
            for bolum, degerler in veri.items():
                if isinstance(degerler, dict):
                    for anahtar, deger in degerler.items():
                        self.brain.ayar_kaydet(deger, bolum, anahtar)
            return JSONResponse({"basarili": True})

        @app.post("/api/platform-baglan")
        async def platform_baglan(request: Request):
            veri = await request.json()
            platform = veri.get("platform", "")
            sonuc = False
            p = self.platformlar.get(platform)
            if p:
                sonuc = p.baglan()
            return JSONResponse({"basarili": sonuc, "platform": platform})

        @app.post("/api/platform-kes")
        async def platform_kes(request: Request):
            veri = await request.json()
            platform = veri.get("platform", "")
            p = self.platformlar.get(platform)
            if p:
                p.baglantiyi_kes()
            return JSONResponse({"basarili": True})

        # ── WebSocket ──────────────────────────────────────────────────────────

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self._ws_baglantilar.append(websocket)
            try:
                while True:
                    # Her 3 saniyede canlı durum gönder
                    await asyncio.sleep(3)
                    durum = self.brain.tum_durum()
                    await websocket.send_json(durum)
            except WebSocketDisconnect:
                self._ws_baglantilar.remove(websocket)
            except Exception:
                try:
                    self._ws_baglantilar.remove(websocket)
                except ValueError:
                    pass

        return app

    async def _ws_yayinla(self, veri: dict):
        for ws in self._ws_baglantilar[:]:
            try:
                await ws.send_json(veri)
            except Exception:
                try:
                    self._ws_baglantilar.remove(ws)
                except ValueError:
                    pass

    # ── Sunucu Başlatma ───────────────────────────────────────────────────────

    def baslat(self, port: int = None, host: str = "0.0.0.0"):
        if not FASTAPI_MEVCUT:
            logger.error("FastAPI/uvicorn kurulu değil")
            return
        if port is None:
            port = self.brain.ayar_al("uygulama", "web_port", varsayilan=8000)

        def _calistir():
            uvicorn.run(
                self._app,
                host=host,
                port=port,
                log_level="warning"
            )

        self._server_thread = threading.Thread(target=_calistir, daemon=True)
        self._server_thread.start()
        logger.info(f"Web dashboard başlatıldı: http://localhost:{port}")

    def durdur(self):
        logger.info("Web dashboard durduruldu")


# ── Tek başına çalıştırma ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(BASE_DIR))
    from core.brain import Brain
    from agents.medajan_ai import MedAjanAI

    brain = Brain()
    ai = MedAjanAI(brain)
    dashboard = WebDashboard(brain, ai)
    dashboard.baslat(port=8000)

    # Sunucuyu çalışır tut
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
