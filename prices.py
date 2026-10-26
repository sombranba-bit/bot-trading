"""Precios casi en directo: se ejecuta cada 15 min en horario de mercado (con el retraso de Yahoo).

Escribe docs/prices.json, que la página consulta cada minuto.
"""
import json
import os
from datetime import datetime, timezone

import yfinance as yf

from config import CRYPTO, UNIVERSE

TICKERS = UNIVERSE + CRYPTO


def summarize(s):
    """Último precio y variación frente al cierre del día anterior. s: serie de cierres con fecha y hora."""
    day = s.index[-1].date()
    today = s[[d == day for d in s.index.date]]
    prev = s[[d < day for d in s.index.date]]
    v = (today.iloc[-1] / prev.iloc[-1] - 1) * 100 if len(prev) else 0.0
    return {"p": round(float(today.iloc[-1]), 2), "v": round(float(v), 2)}


def main() -> None:
    df = yf.download(TICKERS, period="5d", interval="15m", progress=False, auto_adjust=True, group_by="ticker")
    out = {}
    for t in TICKERS:
        try:
            out[t] = summarize(df[t]["Close"].dropna())
        except Exception as e:  # un valor fallido no debe parar el resto
            print("sin datos:", t, e)
    os.makedirs("docs", exist_ok=True)
    with open("docs/prices.json", "w") as f:
        json.dump({"ts": datetime.now(timezone.utc).isoformat(timespec="minutes"), "p": out}, f)
    print(f"{len(out)} precios")


if __name__ == "__main__":
    main()
