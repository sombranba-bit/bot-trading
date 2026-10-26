"""Informe diario: rendimiento de la simulación frente al benchmark, pronósticos y evaluación de pronósticos antiguos.

Escribe docs/index.html (GitHub Pages) y, si hay credenciales de Telegram, envía un resumen.
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

    # 4. Informe: texto para Telegram y página HTML para GitHub Pages
    text = (f"Informe {today}\n"
            f"Simulación: {sim_ret:+.1%} desde {start['fecha']}\n"
            f"Benchmark VWCE: {bench_ret:+.1%}\n"
            f"Pronósticos hoy: {', '.join(p['ticker'] for p in picks) or 'ninguno'}\n"
            f"{eval_txt}")
    cards = "".join(f'<div class="card"><span>{k}</span><strong class="{c}">{v}</strong></div>'
                    for k, v, c in [("Simulación", f"{sim_ret:+.1%}", "pos" if sim_ret >= 0 else "neg"),
                                    ("Benchmark VWCE", f"{bench_ret:+.1%}", "pos" if bench_ret >= 0 else "neg")])
    rows = "".join(f"<tr><td>{p['ticker']}</td><td>{p['votos']}/3</td><td>{p['precio']}</td></tr>" for p in picks)
    table = (f"<table><tr><th>Activo</th><th>Votos</th><th>Precio</th></tr>{rows}</table>" if picks
             else "<p class='muted'>Ninguna acción cumple el criterio hoy.</p>")
    html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bot de trading · {today}</title>
<style>
:root{{--bg:#0b0f14;--card:#141b24;--line:#1f2a37;--txt:#e6edf3;--muted:#8b98a5;--pos:#3fb950;--neg:#f85149;--acc:#58a6ff}}
@media (prefers-color-scheme: light){{:root{{--bg:#f6f8fa;--card:#fff;--line:#d0d7de;--txt:#1f2328;--muted:#656d76;--pos:#1a7f37;--neg:#cf222e;--acc:#0969da}}}}
body{{margin:0;background:var(--bg);color:var(--txt);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:720px;margin:0 auto;padding:24px 16px}}
h1{{font-size:1.5rem;margin:0 0 4px}} .sub{{color:var(--muted);margin:0 0 24px}}
.cards{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px}}
.card,.box{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}}
.card span{{display:block;color:var(--muted);font-size:.85rem}}
.card strong{{font-size:1.6rem}} .pos{{color:var(--pos)}} .neg{{color:var(--neg)}}
h2{{font-size:1.05rem;margin:24px 0 8px;color:var(--acc)}}
table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:8px;border-bottom:1px solid var(--line)}}
th{{color:var(--muted);font-weight:500;font-size:.85rem}}
.muted{{color:var(--muted)}} footer{{margin-top:32px;color:var(--muted);font-size:.8rem}}
@media (max-width:480px){{.cards{{grid-template-columns:1fr}}}}
</style></head>
<body><main>
<h1>Bot de trading</h1>
<p class="sub">Simulación en paper trading · actualizado {today}</p>
<div class="cards">{cards}</div>
<div class="box"><h2>Pronósticos de hoy</h2>{table}</div>
<div class="box"><h2>Evaluación de pronósticos antiguos</h2><p>{eval_txt}</p></div>
<footer>Simulación, no asesoramiento financiero. Datos de Yahoo Finance y Alpaca.</footer>
</main></body></html>
"""

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(html)
    open("docs/.nojekyll", "w").close()
    telegram(text)
    print(text)


if __name__ == "__main__":
    main()
