"""Datos del informe diario. La presentación está en page.py.

Escribe docs/index.html (GitHub Pages) y, si hay credenciales de Telegram, envía un resumen.
"""
import csv
import json
import os
from datetime import date, timedelta
from html import escape

import pandas as pd
import yfinance as yf
from alpaca.trading.client import TradingClient

from config import BENCHMARK, COST, CRYPTO, CRYPTO_ALPACA, MIN_SAMPLE, MIN_VOTES, UNIVERSE
from notify import photo, telegram
from page import render
from signals import votes

ALPACA_TO_TICKER = {v.replace("/", ""): k for k, v in CRYPTO_ALPACA.items()}  # p. ej. BTCUSD -> BTC-USD
SECTOR_ICON = {"Technology": "💻", "Financial Services": "🏦", "Healthcare": "💊", "Consumer Defensive": "🛒",
               "Consumer Cyclical": "🛍️", "Energy": "⛽", "Communication Services": "📡", "Industrials": "🏭",
               "Utilities": "💡", "Real Estate": "🏢", "Basic Materials": "🧱"}


SECTOR_ES = {"Technology": "Tecnología", "Financial Services": "Financiero", "Healthcare": "Salud",
             "Consumer Defensive": "Consumo básico", "Consumer Cyclical": "Consumo discrecional",
             "Energy": "Energía", "Communication Services": "Comunicación", "Industrials": "Industria",
             "Utilities": "Suministros", "Real Estate": "Inmobiliario", "Basic Materials": "Materiales"}


def pick_line(p):
    icon = "₿" if p["ticker"] in CRYPTO else SECTOR_ICON.get(p["info"]["sector"], "📦")  # icono por sector
    return f'{icon} <b>{escape(p["ticker"])}</b> · {escape(p["info"]["name"])} · {p["votos"]}/3'

EVAL_DAYS = 90  # cada pronóstico se evalúa 90 días después
TICKERS = UNIVERSE + CRYPTO
PICKS = "data/picks.csv"  # primera aparición de cada acción por criterio (2 y 3 votos)


def excess(rows, last, bench):
    """Rentabilidad de cada pronóstico menos la del benchmark desde su fecha."""
    out = []
    for r in rows:
        b = bench[bench.index >= pd.Timestamp(r["fecha"])]
        if not b.empty:
            out.append((last[r["ticker"]] / float(r["precio"]) - 1) - COST - (bench.iloc[-1] / b.iloc[0] - 1))
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


def chart(eq_rows, bench, positions, screen, path):
    """Imagen para Telegram: rentabilidad frente a VWCE y reparto de la cartera por sector."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [2, 1]})
    vals = [float(r["equity"]) for r in eq_rows]
    ax.plot(pd.to_datetime([r["fecha"] for r in eq_rows]), [(v / vals[0] - 1) * 100 for v in vals],
            color="#58a6ff", lw=2.5, label="Simulación")
    if len(bench) > 1:
        ax.plot(bench.index, (bench / bench.iloc[0] - 1) * 100, color="#8b98a5", lw=1.5, ls="--", label="VWCE")
    ax.axhline(0, color="#30363d", lw=1)
    ax.set_title("Rentabilidad desde el inicio (%)")
    ax.legend(frameon=False)
    ax.tick_params(axis="x", labelrotation=30)

    sectors = {}
    for p in positions:
        s = "Cripto" if p["ticker"] in CRYPTO else (screen.get(p["ticker"], {}).get("sector") or "Otros")
        s = SECTOR_ES.get(s, s)
        sectors[s] = sectors.get(s, 0) + p["value"]
    if sectors:
        names, amounts = zip(*sorted(sectors.items(), key=lambda x: x[1]))
        bx.barh(names, amounts, color="#3fb950")
    bx.set_title("Cartera por sector (USD)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def weekly(eq_rows, trades, grid, today):
    since = (date.fromisoformat(today) - timedelta(days=7)).isoformat()
    before = [r for r in eq_rows if r["fecha"] <= since]
    ret = float(eq_rows[-1]["equity"]) / float((before or eq_rows)[-1]["equity"]) - 1
    ops = [t for t in trades if t["fecha"][:10] > since]
    top = sorted(grid, key=lambda g: -g[1]["n"])[:3]
    return "\n".join([
        f"🗓️ <b>Resumen semanal · {today}</b>", "",
        f"💼 <b>Semana</b>  {ret:+.1%}",
        f"🔁 <b>Operaciones</b>  {len(ops)}", "",
        "🔥 <b>Acciones con más señales</b>",
        *[f"{SECTOR_ICON.get(f['info']['sector'], '📦')} <b>{escape(t)}</b> · {f['n']}/3" for t, f in top], "",
        '🔗 <a href="https://sombranba-bit.github.io/bot-trading/">Ver el panel completo</a>',
    ])


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
    os.makedirs("docs", exist_ok=True)
    chart(eq_rows, bench, positions, screen, "docs/informe.png")

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
    picks.sort(key=lambda p: (-p["votos"], -(p["info"]["upside"] or 0)))  # más señales y más potencial, primero
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
                aviso = "" if len(ex) >= MIN_SAMPLE else f" (muestra pequeña: menos de {MIN_SAMPLE}, no concluyente)"
                partes.append(f"{c} votos: {len(ex)} pronósticos, exceso medio {sum(ex) / len(ex):+.1%} frente a VWCE{aviso}")
    eval_txt = " · ".join(partes) or "Sin pronósticos de más de 90 días todavía."

    # 4. Salida: texto para Telegram y página HTML
    text = "\n".join([
        f"📊 <b>Informe diario · {today}</b>", "",
        f"💼 <b>Simulación</b>  {sim_ret:+.1%} desde {start['fecha']}",
        f"📈 <b>Benchmark VWCE</b>  {bench_ret:+.1%}", "",
        f"🎯 <b>Pronósticos de hoy</b> ({len(picks)})",
        *[pick_line(p) for p in picks[:12]],
        *([f"… y {len(picks) - 12} más"] if len(picks) > 12 else []),
        *([] if picks else ["Ninguno hoy"]), "",
        f"🧪 <b>Evaluación</b>", escape(eval_txt), "",
        '🔗 <a href="https://sombranba-bit.github.io/bot-trading/">Ver el panel completo</a>',
    ])
    html = render({
        "today": today, "start": start["fecha"], "sim_ret": sim_ret, "bench_ret": bench_ret,
        "equity": [(r["fecha"], float(r["equity"])) for r in eq_rows], "positions": positions, "picks": picks,
        "grid": grid, "trades": read_csv("data/trades.csv")[-8:][::-1], "status": status, "eval_txt": eval_txt,
        "backtest": read_csv("data/backtest.csv"),
    })
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(html)
    open("docs/.nojekyll", "w").close()
    telegram(text)
    photo("docs/informe.png", "📉 Curva de la simulación frente a VWCE y reparto por sector")
    if date.fromisoformat(today).weekday() == 4:  # viernes
        telegram(weekly(eq_rows, read_csv("data/trades.csv"), grid, today))
    print(text)


if __name__ == "__main__":
    main()
