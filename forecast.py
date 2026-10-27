"""Registro de señales de compra y venta de la tendencia, para comprobar después si acertaron.

Cada fila es un cambio de señal: senal=1 (compra) o 0 (venta). Así el archivo crece poco, y report.py
mide cuánto se movió cada acción frente a VWCE tras cada señal.
"""
import csv
import os
from datetime import datetime, timezone

PATH = "data/senales.csv"


def record_changes(events):
    """events: lista de (ticker, senal, precio). Guarda solo las que cambian respecto a la última anotada."""
    last = {}
    if os.path.exists(PATH):
        with open(PATH) as f:
            last = {r["ticker"]: r["senal"] for r in csv.DictReader(f)}
    new = [(t, s, p) for t, s, p in events if last.get(t) != str(s)]
    if not new:
        return
    os.makedirs("data", exist_ok=True)
    fresh = not os.path.exists(PATH)
    now = datetime.now(timezone.utc)
    with open(PATH, "a", newline="") as f:
        w = csv.writer(f)
        if fresh:
            w.writerow(["fecha", "hora", "ticker", "senal", "precio"])
        for t, s, p in new:
            w.writerow([now.date().isoformat(), now.strftime("%H:%M"), t, s, round(p, 2)])
