"""Tres señales independientes. Cada una aporta un voto a favor (1) o en contra (0)."""
from strategy import signal as trend_signal


def trend(close):
    # Medias móviles: la corta por encima de la larga
    return bool(trend_signal(close).iloc[-1])


def momentum(close):
    # Subida en los últimos 12 meses y precio por encima de la media de 200 días
    if len(close) < 252:
        return False
    return bool(close.iloc[-1] > close.iloc[-252] and close.iloc[-1] > close.rolling(200).mean().iloc[-1])


def votes(close, undervalued):
    v = [trend(close), momentum(close), bool(undervalued)]
    return sum(v), v
