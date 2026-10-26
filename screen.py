"""Screening de infravaloración: P/E bajo y precio objetivo de analistas con margen de subida.

Datos de Yahoo Finance (no oficiales): pueden faltar campos. Se guarda data/screen.json.
"""
import json
import os

import yfinance as yf

from config import PE_MAX, UNIVERSE, UPSIDE_MIN


def run() -> dict:
    out = {}
    prev = json.load(open("data/screen.json")) if os.path.exists("data/screen.json") else {}
    for t in UNIVERSE:
        try:
            info = yf.Ticker(t).info
        except Exception as e:  # una acción fallida no debe parar el resto
            print("sin datos:", t, e)
            info = {}
        if "longName" not in info and t in prev:  # Yahoo falló: conservar la última copia buena
            out[t] = prev[t]
            continue
        if not info:
            continue
        pe = info.get("trailingPE")
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        target = info.get("targetMeanPrice")
        upside = (target / price - 1) if target and price else None
        undervalued = bool(pe and 0 < pe < PE_MAX and upside is not None and upside >= UPSIDE_MIN)
        out[t] = {"pe": pe, "price": price, "target": target, "upside": upside, "undervalued": undervalued,
                  "name": info.get("longName") or t, "sector": info.get("sector", ""),
                  "industry": info.get("industry", ""), "summary": (info.get("longBusinessSummary") or "")[:300],
                  "web": info.get("website", "")}

    os.makedirs("data", exist_ok=True)
    with open("data/screen.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"Screening: {sum(v['undervalued'] for v in out.values())} infravaloradas de {len(out)}")
    return out


if __name__ == "__main__":
    run()
