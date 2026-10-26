"""Informe diario: rendimiento de la simulación frente al benchmark, pronósticos y evaluación de pronósticos antiguos.

Escribe docs/index.md (GitHub Pages) y, si hay credenciales de Telegram, envía un resumen.
"""
import csv
import json
import os
from datetime import date, timedelta

import requests
import yfinance as yf
from alpaca.trading.client import TradingClient

from config import BENCHMARK, MIN_VOTES, UNIVERSE
from signals import votes

EVAL_DAYS = 90  # cada pronóstico se evalúa 90 días después


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

    # 1. Equity de la simulación y benchmark
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

    # 2. Pronósticos de hoy: acciones con al menos MIN_VOTES votos
    picks = []
    for t in UNIVERSE:
        close = yf.download(t, period="2y", progress=False, auto_adjust=True)["Close"].iloc[:, 0]
        n, _ = votes(close, screen.get(t, {}).get("undervalued", False))
        if n >= MIN_VOTES:
            picks.append({"ticker": t, "votos": n, "precio": round(float(close.iloc[-1]), 2)})
    append_csv("data/forecasts.csv", ["fecha", "ticker", "votos", "precio"],
               [{"fecha": today, **p} for p in picks])

    # 3. Evaluación de pronósticos antiguos frente al benchmark
    old_cut = (date.today() - timedelta(days=EVAL_DAYS)).isoformat()
    old = [r for r in read_csv("data/forecasts.csv") if r["fecha"] <= old_cut]
    eval_txt = "Sin pronósticos de más de 90 días todavía."
    if old:
        rets = []
        for r in old:
            now = last_price(r["ticker"])
            rets.append(now / float(r["precio"]) - 1)
        avg = sum(rets) / len(rets)
        b = yf.download(BENCHMARK, start=old[0]["fecha"], progress=False, auto_adjust=True)["Close"].iloc[:, 0]
        b_ret = float(b.iloc[-1] / b.iloc[0] - 1)
        eval_txt = (f"Pronósticos de hace 90+ días ({len(old)}): rentabilidad media {avg:.1%} "
                    f"frente a {b_ret:.1%} del benchmark.")

    # 4. Informe
    lines = [
        f"# Informe {today}",
        "",
        f"**Simulación:** {sim_ret:+.1%} desde {start['fecha']}",
        f"**Benchmark VWCE:** {bench_ret:+.1%} en el mismo periodo",
        "",
        "## Pronósticos de hoy (acciones con 2 o más votos)",
    ]
    if picks:
        lines += [f"- {p['ticker']}: {p['votos']} votos, precio {p['precio']}" for p in picks]
    else:
        lines.append("Ninguna acción cumple el criterio hoy.")
    lines += ["", "## Evaluación de pronósticos antiguos", eval_txt, ""]
    text = "\n".join(lines)

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.md", "w") as f:
        f.write(text)
    telegram(text)
    print(text)


if __name__ == "__main__":
    main()
