"""Datos del informe diario. La presentación está en page.py.

Escribe docs/index.html (GitHub Pages) y, si hay credenciales de Telegram, envía un resumen.
"""
import csv
import json
import os
from datetime import date, timedelta

import requests
import yfinance as yf
from alpaca.trading.client import TradingClient

from config import BENCHMARK, CRYPTO, MIN_VOTES, UNIVERSE
from page import render
from signals import votes

EVAL_DAYS = 90  # cada pronóstico se evalúa 90 días después
TICKERS = UNIVERSE + CRYPTO


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
            "summary": s.get("summary", ""), "web": s.get("web", "")}


def telegram(text):
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("Telegram no configurado; solo se guarda el informe.")
        return
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                  data={"chat_id": chat, "text": text[:4000]}, timeout=20)


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
    positions = [{"symbol": p.symbol, "value": float(p.market_value), "pl": float(p.unrealized_plpc)}
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
        f = {"n": n, "v": v, "precio": round(float(close.iloc[-1]), 2)}
        grid.append((t, f))
        if n >= MIN_VOTES:
            picks.append({"ticker": t, "votos": n, "precio": f["precio"], "flags": v, "info": info(t, screen)})
    append_csv("data/forecasts.csv", ["fecha", "ticker", "votos", "precio"],
               [{"fecha": today, "ticker": p["ticker"], "votos": p["votos"], "precio": p["precio"]} for p in picks])

    # 3. Evaluación de pronósticos antiguos frente al benchmark
    old_cut = (date.today() - timedelta(days=EVAL_DAYS)).isoformat()
    old = [r for r in read_csv("data/forecasts.csv") if r["fecha"] <= old_cut]
    eval_txt = "Sin pronósticos de más de 90 días todavía."
    if old:
        rets = [last_price(r["ticker"]) / float(r["precio"]) - 1 for r in old]
        avg = sum(rets) / len(rets)
        b = yf.download(BENCHMARK, start=old[0]["fecha"], progress=False, auto_adjust=True)["Close"].iloc[:, 0]
        b_ret = float(b.iloc[-1] / b.iloc[0] - 1)
        eval_txt = (f"Pronósticos de hace 90+ días ({len(old)}): rentabilidad media {avg:.1%} "
                    f"frente a {b_ret:.1%} del benchmark.")

    # 4. Salida: texto para Telegram y página HTML
    text = (f"Informe {today}\n"
            f"Simulación: {sim_ret:+.1%} desde {start['fecha']}\n"
            f"Benchmark VWCE: {bench_ret:+.1%}\n"
            f"Pronósticos hoy: {', '.join(p['ticker'] for p in picks) or 'ninguno'}\n"
            f"{eval_txt}")
    html = render({
        "today": today, "start": start["fecha"], "sim_ret": sim_ret, "bench_ret": bench_ret,
        "equity": [float(r["equity"]) for r in eq_rows], "positions": positions, "picks": picks,
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
