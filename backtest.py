"""Backtest de la cartera del bot (config.CORE) frente a VWCE, en el mismo periodo:

1. Tendencia: entra o sale según la media de 20/100 días (como en el bot).
2. Comprar y mantener: sin vender nunca.
3. VWCE comprar y mantener: referencia global.

Limitación: solo cubre la señal de tendencia. El criterio de infravaloración necesita históricos de
P/E y precios objetivo que Yahoo no ofrece de forma fiable, así que no se puede backtestear.
Sesgo: el cesto son las acciones de hoy, lo que favorece a los escenarios que las mantienen.

Uso: python backtest.py (necesita acceso a Yahoo: se ejecuta en GitHub Actions).
"""
import os

import pandas as pd
import yfinance as yf

from config import BENCHMARK, CORE
from strategy import signal

START = "2018-01-01"
FEE = 0.001  # 0,1 % por cambio de posición, para no ser optimistas


def metrics(r):
    """Rentabilidad total, anual y caída máxima de una serie de retornos diarios."""
    eq = (1 + r).cumprod()
    return {"total": eq.iloc[-1] - 1, "anual": eq.iloc[-1] ** (252 / len(r)) - 1,
            "max_caida": (eq / eq.cummax() - 1).min()}


def main() -> None:
    close = yf.download(CORE + [BENCHMARK], start=START, progress=False, auto_adjust=True)["Close"]
    bench = close.pop(BENCHMARK).dropna()
    close = close.loc[bench.index[0]:].ffill().dropna(axis=1, how="all")  # periodo común: desde que existe VWCE

    ret = close.pct_change().fillna(0)
    pos = close.apply(signal)
    trades = pos.diff().abs().fillna(0)
    scenarios = {
        "Tendencia": (pos * ret - trades * FEE).mean(axis=1),
        "Comprar y mantener": ret.mean(axis=1),
        "VWCE comprar y mantener": bench.pct_change().fillna(0).reindex(close.index).fillna(0),
    }

    rows = []
    trades_by = {"Tendencia": trades}
    for name, r in scenarios.items():
        n_ops = int(trades_by[name].sum().sum()) if name in trades_by else 0
        rows.append({"escenario": name, **metrics(r), "operaciones": n_ops})
    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/backtest.csv", index=False)  # el flujo lo guarda en el repositorio

    show = df.copy()
    for col in ("total", "anual", "max_caida"):
        show[col] = show[col].map("{:.1%}".format)
    print(f"Periodo: {close.index[0].date()} a {close.index[-1].date()} · {close.shape[1]} activos")
    print(show.to_string(index=False))


if __name__ == "__main__":
    main()
