"""Página del informe para GitHub Pages: pantalla completa, con logos, descripciones y estado del bot."""
from html import escape
from urllib.parse import urlparse

NAMES = ["Tendencia", "Momentum", "Valor"]


def logo(t, info):
    # Iniciales siempre visibles; el favicon de la web de la empresa se pone encima si carga
    dom = urlparse(info.get("web") or "").netloc.replace("www.", "")
    img = (f'<img src="https://www.google.com/s2/favicons?domain={escape(dom)}&amp;sz=128" alt="" '
           f'onerror="this.remove()">') if dom else ""
    return f'<div class="logo"><span>{escape(t.split("-")[0][:4])}</span>{img}</div>'


def desc(info):
    return escape(info.get("summary") or f"Sin descripción disponible en Yahoo Finance. Sector: {info.get('sector') or 'n/d'}.")


def pct(x):
    return f"{x:+.1%}"


def cls(x):
    return "pos" if x >= 0 else "neg"


def equity_svg(vals):
    if len(vals) < 2:
        return '<div class="empty">Primer día de seguimiento. La curva aparecerá cuando haya más datos.</div>'
    w, h = 800, 240
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pts = " ".join(f"{i * w / (len(vals) - 1):.1f},{h - (v - lo) / span * (h - 30) - 15:.1f}"
                   for i, v in enumerate(vals))
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" class="chart">'
            f'<polyline points="{pts}" fill="none" stroke="var(--acc)" stroke-width="3" '
            f'vector-effect="non-scaling-stroke"/></svg>')


def pick_card(p):
    c = p["info"]
    chips = "".join(f'<span class="chip{" on" if on else ""}">{nm}</span>'
                    for nm, on in zip(NAMES, p["flags"]))
    meta = escape(c["sector"]) + (f" · {escape(c['industry'])}" if c["industry"] else "")
    return (f'<article class="pick">{logo(p["ticker"], c)}<div class="pb">'
            f'<div class="ttl"><strong>{escape(c["name"])}</strong><span class="tk">{escape(p["ticker"])}</span></div>'
            f'<div class="meta">{meta} · {p["precio"]} USD</div>'
            f'<p>{desc(c)}</p><div class="chips">{chips}</div></div></article>')


def heat_cell(t, f):
    return f'<div class="cell v{f["n"]}"><b>{escape(t)}</b><span>{f["n"]}/3</span></div>'


def kpi(label, value, c=""):
    return f'<div class="kpi"><span>{label}</span><strong class="{c}">{value}</strong></div>'


def render(ctx) -> str:
    st = ctx["status"]
    if st is None:
        pill = '<span class="pill off">Sin datos del bot todavía</span>'
    elif st.get("parado"):
        pill = '<span class="pill off">Bot parado (KILL_SWITCH)</span>'
    else:
        mercado = "Bolsa EE. UU. abierta" if st["mercado_abierto"] else "Bolsa EE. UU. cerrada (solo cripto)"
        pill = (f'<span class="pill ok"><i></i> Bot activo · último ciclo <b id="ago" data-ts="{st["ts"]}">'
                f'{st["ts"]}</b></span><span class="pill">{mercado}</span>')

    positions = "".join(
        f'<div class="row"><b>{escape(p["symbol"])}</b><span>{p["value"]:,.0f} USD</span>'
        f'<span class="{cls(p["pl"])}">{pct(p["pl"])}</span></div>' for p in ctx["positions"]
    ) or '<p class="muted">Sin posiciones abiertas.</p>'

    trades = "".join(
        f'<div class="row"><span class="muted">{escape(r["fecha"][:16].replace("T", " "))}</span>'
        f'<b>{escape(r["simbolo"])}</b><span class="{"pos" if r["accion"] == "COMPRA" else "neg"}">'
        f'{escape(r["accion"])}</span></div>' for r in ctx["trades"]
    ) or '<p class="muted">Todavía no ha habido operaciones.</p>'

    picks = "".join(pick_card(p) for p in ctx["picks"]) or \
        '<p class="muted">Ninguna acción cumple el criterio hoy.</p>'

    heat = "".join(heat_cell(t, f) for t, f in ctx["grid"])
    eq = ctx["equity"]
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bot de trading · {ctx["today"]}</title>
<style>
:root{{--bg:#070b10;--card:#0f1620;--line:#1d2836;--txt:#e6edf3;--muted:#8b98a5;--pos:#3fb950;--neg:#f85149;--acc:#58a6ff;--warn:#d29922}}
@media (prefers-color-scheme: light){{:root{{--bg:#f3f5f8;--card:#fff;--line:#d8dee6;--txt:#1f2328;--muted:#5f6b7a;--pos:#1a7f37;--neg:#cf222e;--acc:#0969da}}}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
.wrap{{padding:24px 32px;max-width:none}}
.top{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;margin-bottom:20px}}
h1{{margin:0;font-size:1.6rem}} .sub{{margin:2px 0 0;color:var(--muted)}}
.pill{{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;border:1px solid var(--line);font-size:.85rem;margin-left:6px}}
.pill.ok{{border-color:var(--pos);color:var(--pos)}} .pill.off{{border-color:var(--warn);color:var(--warn)}}
.pill i{{width:8px;height:8px;border-radius:50%;background:var(--pos);animation:pulse 1.6s infinite}}
@keyframes pulse{{0%{{opacity:1}}50%{{opacity:.25}}100%{{opacity:1}}}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px}}
.kpi,.panel{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
.kpi span{{color:var(--muted);font-size:.85rem}} .kpi strong{{display:block;font-size:1.8rem;margin-top:4px}}
.grid{{display:grid;grid-template-columns:2fr 1fr;gap:16px}}
.panel.big{{grid-column:span 1}}
h2{{margin:0 0 12px;font-size:1rem;color:var(--acc)}}
.chart{{width:100%;height:240px;display:block}} .empty,.muted{{color:var(--muted)}} .empty{{padding:40px 0;text-align:center}}
.pos{{color:var(--pos)}} .neg{{color:var(--neg)}}
.row{{display:grid;grid-template-columns:1.2fr 1fr .8fr;gap:8px;padding:9px 0;border-bottom:1px solid var(--line);font-size:.92rem}}
.row:last-child{{border:0}} .row span:last-child{{text-align:right}}
.pick{{display:flex;gap:14px;padding:14px 0;border-bottom:1px solid var(--line)}} .pick:last-child{{border:0}}
.pb{{min-width:0}} .pick p{{margin:6px 0;font-size:.92rem}}
.ttl{{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline}} .tk{{color:var(--acc);font-size:.85rem;font-weight:600}}
.meta{{color:var(--muted);font-size:.85rem}}
.logo{{position:relative;width:52px;height:52px;flex:none;border-radius:12px;background:var(--line);display:grid;place-items:center}}
.logo span{{font-weight:700;font-size:.75rem}}
.logo img{{position:absolute;inset:0;width:100%;height:100%;border-radius:12px;background:#fff;object-fit:contain;padding:8px}}
.chips{{display:flex;gap:6px;flex-wrap:wrap}}
.chip{{font-size:.75rem;padding:3px 9px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}}
.chip.on{{border-color:var(--pos);color:var(--pos)}}
.heat{{display:grid;grid-template-columns:repeat(auto-fill,minmax(88px,1fr));gap:8px}}
.cell{{border-radius:10px;padding:8px;font-size:.78rem;display:flex;flex-direction:column;gap:2px}}
.cell b{{font-size:.85rem}} .cell span{{opacity:.8}}
.v0{{background:var(--line);color:var(--muted)}} .v1{{background:#1f3a2a;color:#9ee6ad}}
.v2{{background:#1f6f3a;color:#fff}} .v3{{background:var(--pos);color:#06210d}}
.legend{{font-size:.8rem;margin-top:10px}}
footer{{margin-top:20px;color:var(--muted);font-size:.8rem}}
@media (max-width:1000px){{.grid{{grid-template-columns:1fr}} .kpis{{grid-template-columns:repeat(2,1fr)}}}}
@media (max-width:560px){{.wrap{{padding:16px}} .kpi strong{{font-size:1.4rem}}}}
</style></head>
<body><div class="wrap">
<header class="top"><div><h1>Bot de trading</h1><p class="sub">Paper trading · informe del {ctx["today"]}</p></div>
<div>{pill}</div></header>

<section class="kpis">
{kpi("Simulación desde " + ctx["start"], pct(ctx["sim_ret"]), cls(ctx["sim_ret"]))}
{kpi("Benchmark VWCE", pct(ctx["bench_ret"]), cls(ctx["bench_ret"]))}
{kpi("Posiciones abiertas", len(ctx["positions"]))}
{kpi("Pronósticos hoy", len(ctx["picks"]))}
</section>

<section class="grid">
  <div class="panel big"><h2>Evolución de la simulación</h2>{equity_svg(eq)}</div>
  <div class="panel"><h2>Cartera</h2>{positions}</div>

  <div class="panel big"><h2>Pronósticos de hoy</h2>{picks}</div>
  <div class="panel"><h2>Señales por activo</h2><div class="heat">{heat}</div>
    <p class="legend muted">Número de señales a favor (de 3). Con 2 o más, el bot compra.</p></div>

  <div class="panel big"><h2>Actividad reciente</h2>{trades}</div>
  <div class="panel"><h2>Evaluación de pronósticos</h2><p>{escape(ctx["eval_txt"])}</p></div>
</section>

<footer>Simulación, no asesoramiento financiero. Datos de Yahoo Finance y Alpaca.</footer>
</div>
<script>
const el=document.getElementById('ago');
if(el){{const m=Math.round((Date.now()-Date.parse(el.dataset.ts))/60000);
el.textContent=m<60?'hace '+m+' min':'hace '+Math.round(m/60)+' h';}}
</script>
</body></html>
"""
