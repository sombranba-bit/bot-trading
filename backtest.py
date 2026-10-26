"""Backtest de la estrategia frente a comprar y mantener un ETF global (benchmark).

Uso: python backtest.py
Descarga datos históricos diarios con yfinance (solo funciona donde haya acceso a Yahoo, p. ej. GitHub Actions).
"""
import numpy as np
import pandas as pd
import yfinance as yf

from strategy import signal

UNIVERSE = ["SPY", "QQQ", "AAPL", "MSFT", "BTC-USD"]  # acciones, ETFs y cripto líquidos
BENCHMARK = "VWCE.DE"  # ETF global acumulativo (MSCI ACWI), referencia de comprar y mantener
START = "2018-01-01"
FEE = 0.001  # 0,1 % por cambio de posición, para no ser optimistas


def run(ticker: str) -> dict:
    close = yf.download(ticker, start=START, progress=False, auto_adjust=True)["Close"].squeeze()
    ret = close.pct_change().fillna(0)
    pos = signal(close)
    trades = pos.diff().abs().fillna(0)
    strat = pos * ret - trades * FEE
    return {
        "ticker": ticker,
        "strategy": (1 + strat).prod() - 1,
        "buy_hold": (1 + ret).prod() - 1,
        "trades": int(trades.sum()),
    }


def main() -> None:
    df = pd.DataFrame([run(t) for t in UNIVERSE])
    bench = run(BENCHMARK)
    for col in ("strategy", "buy_hold"):
        df[col] = df[col].map("{:.1%}".format)
    print(df.to_string(index=False))
    print(f"\nBenchmark {BENCHMARK} comprar y mantener: {bench['buy_hold']:.1%}")


if __name__ == "__main__":
    main()
