"""Pruebas rápidas, sin red: conversión de barras de Alpaca y aviso del screening."""
import os
import sys
import tempfile
from unittest import mock

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot
import screen
from config import UNIVERSE


def test_bars_to_series():
    idx = pd.MultiIndex.from_tuples(
        [("VT", pd.Timestamp("2026-01-02", tz="UTC")), ("VT", pd.Timestamp("2026-01-05", tz="UTC"))],
        names=["symbol", "timestamp"])
    df = pd.DataFrame({"close": [100.0, 101.5]}, index=idx)
    s = bot.bars_to_series(df)
    assert list(s) == [100.0, 101.5]
    assert s.index[0] == pd.Timestamp("2026-01-02") and s.index.tz is None


def test_screen_alerta_si_yahoo_falla():
    avisos = []
    with tempfile.TemporaryDirectory() as d, mock.patch.object(screen, "telegram", avisos.append), \
            mock.patch.object(screen.yf, "Ticker", side_effect=RuntimeError("caído")):
        cwd = os.getcwd(); os.chdir(d)
        try:
            screen.run()
        finally:
            os.chdir(cwd)
    assert len(avisos) == 1 and "Yahoo" in avisos[0], avisos


def test_screen_sin_alerta_con_datos():
    avisos = []
    info = {"longName": "X", "trailingPE": 10, "currentPrice": 100, "targetMeanPrice": 150}
    with tempfile.TemporaryDirectory() as d, mock.patch.object(screen, "telegram", avisos.append), \
            mock.patch.object(screen.yf, "Ticker", return_value=mock.Mock(info=info)):
        cwd = os.getcwd(); os.chdir(d)
        try:
            out = screen.run()
        finally:
            os.chdir(cwd)
    assert avisos == [] and len(out) == len(UNIVERSE)


if __name__ == "__main__":
    test_bars_to_series(); test_screen_alerta_si_yahoo_falla(); test_screen_sin_alerta_con_datos()
    print("OK: 3 pruebas")
