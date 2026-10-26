"""Datos del informe diario. La presentación está en page.py.

Escribe docs/index.html (GitHub Pages) y, si hay credenciales de Telegram, envía un resumen.
"""
import csv
import json
import os
from datetime import date, timedelta

import pandas as pd
import yfinance as yf
from alpaca.trading.client import TradingClient

from config import BENCHMARK, CRYPTO, CRYPTO_ALPACA, MIN_VOTES, UNIVERSE
from notify import telegram
from page import render
from signals import votes

ALPACA_TO_TICKER = {v.replace("/", ""): k for k, v in CRYPTO_ALPACA.items()}  # p. ej. BTCUSD -> BTC-USD

EVAL_DAYS = 90  # cada pronóstico se evalúa 90 días después
TICKERS = UNIVERSE + CRYPTO
PICKS = "data/picks.csv"  # primera aparición de cada acción por criterio (2 y 3 votos)


def excess(rows, last, bench):
    """Rentabilidad de cada pronóstico menos la del benchmark desde su fecha."""
    out = []
    for r in rows:
        b = bench[bench.index >= pd.Timestamp(r["fecha"])]
        if not b.empty:
            out.append((last[r["ticker"]] / float(r["precio"]) - 1) - (bench.iloc[-1] / b.iloc[0] - 1))
    return out


def last_price(t):
    return float(yf.download(t, period="5d", progress=False, auto_adjust=True)["Close"].iloc[:, 0].iloc[-1])


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def append_csv(path, fields, rows):
    new = not os.path.exists(path)
    os.makedirs("data", exist_ok=True)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(rows)


def info(t, screen):
    s = screen.get(t, {})  # datos del screening; si faltan, se muestra solo el ticker
    return {"name": s.get("name") or t, "sector": s.get("sector", ""), "industry": s.get("industry", ""),
            "summary": s.get("summary", ""), "web": s.get("web", ""), "pe": s.get("pe"),
            "target": s.get("target"), "upside": s.get("upside")}


def main() -> None:
    today = date.today().isoformat()
    screen = json.load(open("data/screen.json")) if os.path.exists("data/screen.json") else {}
    status = json.load(open("data/status.json")) if os.path.exists("data/status.json") else None

    # 1. Cuenta, cartera y benchmark
    trading = TradingClient(os.environ["ALPACA_API_KEY"], os.environ["ALPACA_API_SECRET"], paper=True)
    equity = float(trading.get_account().equity)
    eq_rows = read_csv("data/equity.csv")
    if not eq_rows or eq_rows[-1]["fecha"] != today:
        append_csv("data/equity.csv", ["fecha", "equity"], [{"fecha": today, "equity": equity}])
        eq_rows.append({"fecha": today, "equity": equity})
    start = eq_rows[0]
    sim_ret = equity / float(start["equity"]) - 1
    bench = yf.download(BENCHMARK, start=start["fecha"], progress=False, auto_adjust=True)["Close"].iloc[:, 0]
    bench_ret = float(bench.iloc[-1] / bench.iloc[0] - 1) if len(bench) > 1 else 0.0
    positions = [{"symbol": p.symbol, "ticker": ALPACA_TO_TICKER.get(p.symbol, p.symbol),
                  "value": float(p.market_value), "pl": float(p.unrealized_plpc)}
                 for p in trading.get_all_positions()]

    # 2. Señales de todas las acciones; pronósticos = al menos MIN_VOTES votos
    grid, picks = [], []
    for t in TICKERS:
        try:
            close = yf.download(t, period="2y", progress=False, auto_adjust=True)["Close"].iloc[:, 0]
        except Exception as e:  # un valor fallido no debe parar el informe
            print("sin datos:", t, e)
            continue
        n, v = votes(close, screen.get(t, {}).get("undervalued", False))
        f = {"n": n, "v": v, "precio": round(float(close.iloc[-1]), 2), "info": info(t, screen),
             "hist": [round(float(x), 2) for x in close.iloc[-252:]]}  # último año, para la ficha
        grid.append((t, f))
        if n >= MIN_VOTES:
            picks.append({"ticker": t, "votos": n, "precio": f["precio"], "flags": v, "info": f["info"]})
    # Cada acción se registra solo la primera vez que cumple un criterio, para no contar días repetidos
    seen = {(r["criterio"], r["ticker"]) for r in read_csv(PICKS)}
    criterios = sorted({MIN_VOTES, 3})
    append_csv(PICKS, ["fecha", "criterio", "ticker", "votos", "precio"],
               [{"fecha": today, "criterio": str(c), "ticker": p["ticker"], "votos": p["votos"], "precio": p["precio"]}
                for c in criterios for p in picks if p["votos"] >= c and (str(c), p["ticker"]) not in seen])

    # 3. Evaluación a 90 días: exceso de rentabilidad frente al benchmark, por criterio
    old_cut = (date.today() - timedelta(days=EVAL_DAYS)).isoformat()
    rows = [r for r in read_csv(PICKS) if r["fecha"] <= old_cut]
    partes = []
    if rows:
        last = {t: last_price(t) for t in {r["ticker"] for r in rows}}
        bench = yf.download(BENCHMARK, start=min(r["fecha"] for r in rows), progress=False, auto_adjust=True)["Close"].iloc[:, 0]
        for c in criterios:
            ex = excess([r for r in rows if r["criterio"] == str(c)], last, bench)
            if ex:
                partes.append(f"{c} votos: {len(ex)} pronósticos, exceso medio {sum(ex) / len(ex):+.1%} frente a VWCE")
    eval_txt = " · ".join(partes) or "Sin pronósticos de más de 90 días todavía."

    # 4. Salida: texto para Telegram y página HTML
    text = (f"Informe {today}\n"
            f"Simulación: {sim_ret:+.1%} desde {start['fecha']}\n"
            f"Benchmark VWCE: {bench_ret:+.1%}\n"
            f"Pronósticos hoy: {', '.join(p['ticker'] for p in picks) or 'ninguno'}\n"
            f"{eval_txt}")
    html = render({
        "today": today, "start": start["fecha"], "sim_ret": sim_ret, "bench_ret": bench_ret,
        "equity": [(r["fecha"], float(r["equity"])) for r in eq_rows], "positions": positions, "picks": picks,
        "grid": grid, "trades": read_csv("data/trades.csv")[-8:][::-1], "status": status, "eval_txt": eval_txt,
    })
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(html)
    open("docs/.nojekyll", "w").close()
    telegram(text)
    print(text)


if __name__ == "__main__":
    main()
