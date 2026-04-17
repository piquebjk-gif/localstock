# -*- coding: utf-8 -*-
"""
IQ Elektronik — Sipariş & Müşteri Takip
"""

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(ROOT))

from iq_setup import motor_olustur


def siparisler(adet: int = 20):
    wp = motor_olustur()
    liste = wp.siparisler_listele(adet=adet)
    print(f"\n── Son {len(liste)} Sipariş ──────────────────────")
    for s in liste:
        toplam = s.get("total", "?")
        durum = s.get("status", "?")
        tarih = s.get("date_created", "?")[:10]
        ad = f"{s.get('billing', {}).get('first_name', '')} {s.get('billing', {}).get('last_name', '')}".strip()
        print(f"  #{s['id']} | {tarih} | {ad} | {durum} | {toplam}₺")
    print("─────────────────────────────────────────────\n")
    return liste


def musteriler(adet: int = 20):
    wp = motor_olustur()
    liste = wp.musteri_listele(adet=adet)
    print(f"\n── Müşteriler ({len(liste)}) ─────────────────────")
    for m in liste:
        ad = f"{m.get('first_name', '')} {m.get('last_name', '')}".strip()
        email = m.get("email", "")
        siparis = m.get("orders_count", 0)
        print(f"  [{m['id']}] {ad} | {email} | {siparis} sipariş")
    print("─────────────────────────────────────────────\n")
    return liste


def urun_sil(urun_id: int):
    wp = motor_olustur()
    sonuc = wp.urun_sil(urun_id)
    if sonuc.get("id"):
        print(f"✓ Ürün #{urun_id} silindi")
    else:
        print(f"✗ Silinemedi: {sonuc}")
    return sonuc


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IQ Elektronik — Sipariş & Müşteri")
    parser.add_argument("komut", choices=["siparisler", "musteriler"])
    parser.add_argument("--adet", type=int, default=20)
    args = parser.parse_args()
    {"siparisler": siparisler, "musteriler": musteriler}[args.komut](args.adet)
