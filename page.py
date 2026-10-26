"""Página del informe para GitHub Pages: pestañas, fichas por acción, precios que se actualizan solos."""
from html import escape
from urllib.parse import urlparse

NAMES = ["Tendencia", "Momentum", "Valor"]
TABS = [("resumen", "Resumen"), ("pronosticos", "Pronósticos"), ("cartera", "Cartera"),
        ("senales", "Señales"), ("actividad", "Actividad"), ("evaluacion", "Evaluación")]


def logo(t, info, size=""):
    # Iniciales siempre visibles; el favicon de la web de la empresa se pone encima si carga
    dom = urlparse(info.get("web") or "").netloc.replace("www.", "")
    img = (f'<img src="https://www.google.com/s2/favicons?domain={escape(dom)}&amp;sz=128" alt="" '
           f'onerror="this.remove()">') if dom else ""
    return f'<div class="logo {size}"><span>{escape(t.split("-")[0][:4])}</span>{img}</div>'


def desc(info):
    return escape(info.get("summary") or f"Sin descripción disponible en Yahoo Finance. Sector: {info.get('sector') or 'n/d'}.")


def pct(x):
    return f"{x:+.1%}"


def cls(x):
    return "pos" if x >= 0 else "neg"


def spark(vals, h=240):
    if len(vals) < 2:
        return '<div class="empty">Sin datos suficientes todavía.</div>'
    w = 800
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pts = " ".join(f"{i * w / (len(vals) - 1):.1f},{h - (v - lo) / span * (h - 30) - 15:.1f}"
                   for i, v in enumerate(vals))
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" class="chart" style="height:{h}px">'
            f'<polyline points="{pts}" pathLength="1" class="draw" fill="none" stroke="var(--acc)" stroke-width="3" '
            f'vector-effect="non-scaling-stroke"/></svg>')


def open_js(t):
    return f"document.getElementById('d-{t}').showModal()"


def pick_card(p):
    c = p["info"]
    chips = "".join(f'<span class="chip{" on" if on else ""}">{nm}</span>'
                    for nm, on in zip(NAMES, p["flags"]))
    meta = escape(c["sector"]) + (f" · {escape(c['industry'])}" if c["industry"] else "")
    return (f'<article class="pick" role="button" onclick="{open_js(p["ticker"])}">{logo(p["ticker"], c)}<div class="pb">'
            f'<div class="ttl"><strong>{escape(c["name"])}</strong><span class="tk">{escape(p["ticker"])}</span></div>'
            f'<div class="meta">{meta} · {p["precio"]} USD <span class="px" data-p="{escape(p["ticker"])}"></span></div>'
            f'<p>{desc(c)}</p><div class="chips">{chips}</div></div></article>')


def mini_pick(p):
    return (f'<div class="mini">{logo(p["ticker"], p["info"], "sm")}<div><b>{escape(p["info"]["name"])}</b>'
            f'<div class="meta">{escape(p["ticker"])} · {p["votos"]}/3 señales '
            f'<span class="px" data-p="{escape(p["ticker"])}"></span></div></div></div>')


def heat_cell(t, f):
    return (f'<div class="cell v{f["n"]}" role="button" onclick="{open_js(t)}"><b>{escape(t)}</b>'
            f'<span>{f["n"]}/3 señales</span><em class="px" data-p="{escape(t)}"></em></div>')


def dialog(t, f):
    c = f["info"]
    chips = "".join(f'<span class="chip{" on" if on else ""}">{nm}</span>' for nm, on in zip(NAMES, f["v"]))
    pe = f"{c['pe']:.1f}" if c.get("pe") else "n/d"
    target = f"{c['target']:.2f} USD" if c.get("target") else "n/d"
    upside = pct(c["upside"]) if c.get("upside") is not None else "n/d"
    meta = escape(c["sector"]) + (f" · {escape(c['industry'])}" if c["industry"] else "")
    return (f'<dialog id="d-{escape(t)}" class="dlg">'
            f'<div class="dh">{logo(t, c)}<div><strong>{escape(c["name"])}</strong>'
            f'<div class="meta">{escape(t)} · {meta}</div></div>'
            f'<button class="x" onclick="this.closest(\'dialog\').close()" aria-label="Cerrar">✕</button></div>'
            f'<div class="big-px"><span class="px" data-p="{escape(t)}"></span></div>'
            f'{spark(f["hist"], 140)}<p class="meta">Último año · cierre diario</p>'
            f'<p>{desc(c)}</p><div class="chips">{chips}</div>'
            f'<div class="stats"><div><span>P/E</span><b>{pe}</b></div>'
            f'<div><span>Precio objetivo</span><b>{target}</b></div>'
            f'<div><span>Potencial</span><b>{upside}</b></div>'
            f'<div><span>Señales</span><b>{f["n"]}/3</b></div></div></dialog>')


def kpi(label, value, c="", num=None, suf=""):
    data = f' data-n="{num}" data-s="{suf}"' if num is not None else ""  # num: cifra que la página anima al cargar
    return f'<div class="kpi"><span>{label}</span><strong class="{c}"{data}>{value}</strong></div>'


def render(ctx) -> str:
    st = ctx["status"]
    if st is None:
        pill = '<span class="pill off">Sin datos del bot todavía</span>'
    elif st.get("parado"):
        pill = '<span class="pill off">Bot parado (KILL_SWITCH)</span>'
    else:
        mercado = "Bolsa EE. UU. abierta" if st["mercado_abierto"] else "Bolsa EE. UU. cerrada (solo cripto)"
        pill = (f'<span class="pill ok"><i></i> Bot activo · último ciclo <b class="ago" data-ts="{st["ts"]}">'
                f'{st["ts"]}</b></span><span class="pill">{mercado}</span>')

    eq = ctx["equity"]
    eq_vals = [v for _, v in eq]
    axis = (f'<div class="axis"><span>{eq[0][0]} · {eq[0][1]:,.0f} USD</span>'
            f'<span>{eq[-1][0]} · {eq[-1][1]:,.0f} USD</span></div>') if eq else ""

    positions = "".join(
        f'<div class="row"><b>{escape(p["symbol"])} <span class="px" data-p="{escape(p["ticker"])}"></span></b>'
        f'<span>{p["value"]:,.0f} USD</span><span class="{cls(p["pl"])}">{pct(p["pl"])}</span></div>'
        for p in ctx["positions"]
    ) or '<p class="muted">Sin posiciones abiertas.</p>'

    trades = "".join(
        f'<div class="row"><span class="muted">{escape(r["fecha"][:16].replace("T", " "))}</span>'
        f'<b>{escape(r["simbolo"])}</b><span class="{"pos" if r["accion"] == "COMPRA" else "neg"}">'
        f'{escape(r["accion"])}</span></div>' for r in ctx["trades"]
    ) or '<p class="muted">Todavía no ha habido operaciones.</p>'

    bt = "".join(
        f'<div class="row bt"><b>{escape(r["escenario"])}</b><span>{pct(float(r["anual"]))} al año</span>'
        f'<span class="neg">{pct(float(r["max_caida"]))}</span><span class="{cls(float(r["total"]))}">{pct(float(r["total"]))}</span></div>'
        for r in ctx["backtest"]
    ) or '<p class="muted">Sin resultados del backtest todavía.</p>'

    no_picks = '<p class="muted">Ninguna acción cumple el criterio hoy.</p>'
    picks = "".join(pick_card(p) for p in ctx["picks"]) or no_picks
    minis = "".join(mini_pick(p) for p in ctx["picks"][:6]) or no_picks
    heat = "".join(heat_cell(t, f) for t, f in ctx["grid"])
    dialogs = "".join(dialog(t, f) for t, f in ctx["grid"])
    nav = "".join(f'<button data-t="{k}">{v}</button>' for k, v in TABS)
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bot de trading · {ctx["today"]}</title>
<style>
:root{{--bg:#070b10;--card:#0f1620;--line:#1d2836;--txt:#e6edf3;--muted:#8b98a5;--pos:#3fb950;--neg:#f85149;--acc:#58a6ff;--warn:#d29922}}
@media (prefers-color-scheme: light){{:root{{--bg:#f3f5f8;--card:#fff;--line:#d8dee6;--txt:#1f2328;--muted:#5f6b7a;--pos:#1a7f37;--neg:#cf222e;--acc:#0969da}}}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
.wrap{{padding:24px 32px}}
.top{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}}
h1{{margin:0;font-size:1.6rem}} .sub{{margin:2px 0 0;color:var(--muted)}}
.pill{{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;border:1px solid var(--line);font-size:.85rem;margin-left:6px}}
.pill.ok{{border-color:var(--pos);color:var(--pos)}} .pill.off{{border-color:var(--warn);color:var(--warn)}}
.pill i{{width:8px;height:8px;border-radius:50%;background:var(--pos);animation:pulse 1.6s infinite}}
@keyframes pulse{{0%{{opacity:1}}50%{{opacity:.25}}100%{{opacity:1}}}}
@keyframes in{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes pop{{from{{opacity:0;transform:scale(.96)}}to{{opacity:1;transform:none}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes flash{{0%{{background:rgba(88,166,255,.35)}}100%{{background:transparent}}}}
.draw{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.2s ease-out forwards}}
.tick{{animation:flash .9s ease-out;border-radius:4px}}
.cell{{transition:transform .2s ease,outline-color .2s}} .cell:hover{{transform:translateY(-2px)}}
.pick{{transition:background .2s ease}} .pick:hover{{background:rgba(88,166,255,.06)}}
.dlg[open]{{animation:pop .3s cubic-bezier(.2,.8,.2,1) both}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
.dlg::backdrop{{animation:fade .3s ease both}}
.tabs button{{transition:color .25s ease,border-color .25s ease,transform .15s ease}} .tabs button:active{{transform:scale(.96)}}
.tab.on .pick,.tab.on .cell,.tab.on .row,.tab.on .mini{{animation:in .45s cubic-bezier(.2,.8,.2,1) backwards;animation-delay:calc(var(--i,0)*45ms)}}
.kpi{{transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s ease}} .kpi:hover{{transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.25)}}
.panel{{transition:box-shadow .25s ease}} .panel:hover{{box-shadow:0 6px 20px rgba(0,0,0,.18)}}
button:focus-visible,[role=button]:focus-visible{{outline:2px solid var(--acc);outline-offset:2px}}
@media (prefers-reduced-motion: reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}
.tabs{{display:flex;gap:4px;overflow-x:auto;border-bottom:1px solid var(--line);margin-bottom:20px}}
.tabs button{{background:none;border:0;border-bottom:2px solid transparent;color:var(--muted);padding:10px 14px;font:inherit;cursor:pointer;white-space:nowrap}}
.tabs button.on{{color:var(--txt);border-color:var(--acc)}}
.tab{{display:none}} .tab.on{{display:block;animation:in .35s ease both}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px}}
.kpi,.panel,.dlg{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
.kpi span{{color:var(--muted);font-size:.85rem}} .kpi strong{{display:block;font-size:1.8rem;margin-top:4px}}
.grid{{display:grid;grid-template-columns:2fr 1fr;gap:16px}}
h2{{margin:0 0 12px;font-size:1rem;color:var(--acc)}}
.chart{{width:100%;display:block}} .axis{{display:flex;justify-content:space-between;color:var(--muted);font-size:.8rem;margin-top:6px}}
.empty,.muted{{color:var(--muted)}} .empty{{padding:40px 0;text-align:center}}
.pos{{color:var(--pos)}} .neg{{color:var(--neg)}}
.px{{font-variant-numeric:tabular-nums;font-weight:600;margin-left:6px;font-size:.85rem;color:var(--muted)}}
.px.pos{{color:var(--pos)}} .px.neg{{color:var(--neg)}}
.row{{display:grid;grid-template-columns:1.4fr 1fr .8fr;gap:8px;padding:9px 0;border-bottom:1px solid var(--line);font-size:.92rem}}
.row:last-child{{border:0}} .row span:last-child{{text-align:right}}
.bt{{grid-template-columns:2fr 1.2fr 1fr 1fr}} .bt span+span{{text-align:right}} .bt.head{{color:var(--muted);font-size:.8rem;border-bottom:1px solid var(--line)}}
.pick{{display:flex;gap:14px;padding:14px 0;border-bottom:1px solid var(--line);cursor:pointer}} .pick:last-child{{border:0}}
.mini{{display:flex;gap:12px;align-items:center;padding:9px 0;border-bottom:1px solid var(--line)}} .mini:last-child{{border:0}}
.pb{{min-width:0}} .pick p{{margin:6px 0;font-size:.92rem}}
.ttl{{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline}} .tk{{color:var(--acc);font-size:.85rem;font-weight:600}}
.meta{{color:var(--muted);font-size:.85rem}}
.logo{{position:relative;width:52px;height:52px;flex:none;border-radius:12px;background:var(--line);display:grid;place-items:center}}
.logo.sm{{width:36px;height:36px}} .logo span{{font-weight:700;font-size:.75rem}} .logo.sm span{{font-size:.6rem}}
.logo img{{position:absolute;inset:0;width:100%;height:100%;border-radius:12px;background:#fff;object-fit:contain;padding:8px}}
.chips{{display:flex;gap:6px;flex-wrap:wrap}}
.chip{{font-size:.75rem;padding:3px 9px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}}
.chip.on{{border-color:var(--pos);color:var(--pos)}}
.heat{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}}
.cell{{border-radius:10px;padding:10px;font-size:.8rem;display:flex;flex-direction:column;gap:2px;cursor:pointer}}
.cell:hover{{outline:1px solid var(--acc)}}
.cell b{{font-size:.9rem}} .cell span{{opacity:.8}} .cell em{{font-style:normal}}
.v0{{background:var(--line);color:var(--muted)}} .v1{{background:#1f3a2a;color:#9ee6ad}}
.v2{{background:#1f6f3a;color:#fff}} .v3{{background:var(--pos);color:#06210d}}
.v2 .px,.v3 .px,.v1 .px{{color:inherit}}
.legend{{font-size:.8rem;margin-top:12px}}
.dlg{{width:min(560px,92vw);color:var(--txt)}} .dlg::backdrop{{background:rgba(0,0,0,.6)}}
.dh{{display:flex;gap:12px;align-items:center}} .dh>div{{flex:1;min-width:0}} .dh .logo{{flex:none}}
.x{{background:none;border:0;color:var(--muted);font-size:1.2rem;cursor:pointer}}
.big-px{{font-size:1.8rem;font-weight:700;margin:14px 0 6px}} .big-px .px{{font-size:1.1rem;margin-left:10px}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px}}
.stats div{{background:var(--bg);border-radius:10px;padding:10px}} .stats span{{display:block;color:var(--muted);font-size:.75rem}}
footer{{margin-top:24px;color:var(--muted);font-size:.8rem}}
@media (max-width:1000px){{.grid{{grid-template-columns:1fr}} .kpis{{grid-template-columns:repeat(2,1fr)}} .panel+.panel{{margin-top:16px}}}}
@media (max-width:560px){{.wrap{{padding:16px}} .kpi strong{{font-size:1.4rem}} .stats{{grid-template-columns:repeat(2,1fr)}}}}
</style></head>
<body><div class="wrap">
<header class="top"><div><h1>Bot de trading</h1><p class="sub">Paper trading · informe del {ctx["today"]}</p></div>
<div>{pill}<span class="pill">Precios <b id="pxts">cargando…</b></span></div></header>

<nav class="tabs">{nav}</nav>

<section class="tab" id="resumen">
  <div class="kpis">
    {kpi("Simulación desde " + ctx["start"], pct(ctx["sim_ret"]), cls(ctx["sim_ret"]), ctx["sim_ret"] * 100, "%")}
    {kpi("Benchmark VWCE", pct(ctx["bench_ret"]), cls(ctx["bench_ret"]), ctx["bench_ret"] * 100, "%")}
    {kpi("Posiciones abiertas", len(ctx["positions"]), "", len(ctx["positions"]))}
    {kpi("Pronósticos hoy", len(ctx["picks"]), "", len(ctx["picks"]))}
  </div>
  <div class="grid">
    <div class="panel"><h2>Evolución de la simulación</h2>{spark(eq_vals)}{axis}</div>
    <div class="panel"><h2>Pronósticos de hoy</h2>{minis}</div>
  </div>
</section>

<section class="tab" id="pronosticos"><div class="panel"><h2>Pronósticos de hoy</h2>{picks}</div></section>
<section class="tab" id="cartera"><div class="panel"><h2>Cartera</h2>{positions}</div></section>
<section class="tab" id="senales"><div class="panel"><h2>Señales por activo</h2><div class="heat">{heat}</div>
  <p class="legend muted">Número de señales a favor (de 3). Con 2 o más, el bot compra. Pulsa una acción para ver su ficha.</p></div></section>
<section class="tab" id="actividad"><div class="panel"><h2>Actividad reciente</h2>{trades}</div></section>
<section class="tab" id="evaluacion"><div class="panel"><h2>Evaluación de pronósticos</h2>
  <p>{escape(ctx["eval_txt"])}</p>
  <p class="muted legend">Exceso = rentabilidad de cada acción menos la del VWCE desde su fecha, descontando un 0,2 % de costes. Un valor positivo significa que el criterio aporta algo frente al mercado.</p></div>
  <div class="panel" style="margin-top:16px"><h2>Backtest: tendencia frente a comprar y mantener</h2>
  <div class="row bt head"><span>Escenario</span><span>Anual</span><span>Caída máx.</span><span>Total</span></div>{bt}
  <p class="muted legend">Desde marzo de 2019, mismo cesto de 42 acciones frente a VWCE. Solo cubre la señal de tendencia, no la infravaloración. El cesto son las acciones de hoy, así que los escenarios que las mantienen salen favorecidos.</p></div></section>

{dialogs}
<footer>Simulación, no asesoramiento financiero. Datos de Yahoo Finance y Alpaca. Precios con retraso de hasta 15 minutos.</footer>
</div>
<script>
const tabs=[...document.querySelectorAll('.tabs button')], secs=[...document.querySelectorAll('.tab')];
function show(id){{
  if(!document.getElementById(id)) id='resumen';
  secs.forEach(s=>s.classList.toggle('on', s.id===id));
  tabs.forEach(b=>b.classList.toggle('on', b.dataset.t===id));
  document.querySelectorAll('.tab.on .pick,.tab.on .cell,.tab.on .row,.tab.on .mini').forEach((el,i)=>el.style.setProperty('--i',i%16));
  history.replaceState(null,'','#'+id);
}}
function countUp(){{
  if(matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('[data-n]').forEach(el=>{{
    const to=+el.dataset.n, suf=el.dataset.s||'', dec=suf==='%'?1:0, sg=suf==='%'&&to>0?'+':'';
    const t0=performance.now();
    const step=t=>{{ const k=Math.min(1,(t-t0)/900), e=1-Math.pow(1-k,3);
      el.textContent=sg+(to*e).toFixed(dec)+suf; if(k<1) requestAnimationFrame(step); }};
    requestAnimationFrame(step);
  }});
}}
countUp();
tabs.forEach(b=>b.onclick=()=>show(b.dataset.t));
show(location.hash.slice(1)||'resumen');

function ago(){{
  document.querySelectorAll('.ago,#pxts').forEach(el=>{{
    if(!el.dataset.ts) return;
    const m=Math.round((Date.now()-Date.parse(el.dataset.ts))/60000);
    el.textContent=m<60?'hace '+m+' min':'hace '+Math.round(m/60)+' h';
  }});
}}
async function precios(){{
  try{{
    const j=await (await fetch('prices.json?'+Date.now())).json();
    document.querySelectorAll('[data-p]').forEach(e=>{{
      const d=j.p[e.dataset.p]; if(!d) return;
      e.textContent=d.p.toFixed(2)+' '+(d.v>=0?'▲ +':'▼ ')+d.v.toFixed(2)+'%';
      e.className='px '+(d.v>=0?'pos':'neg');
      if(e.dataset.last&&e.dataset.last!==String(d.p)){{ e.classList.remove('tick'); void e.offsetWidth; e.classList.add('tick'); }}
      e.dataset.last=d.p;
    }});
    document.getElementById('pxts').dataset.ts=j.ts;
    ago();
  }}catch(e){{ /* sin precios: la página sigue mostrando el informe */ }}
}}
ago(); precios();
setInterval(precios, 60000); setInterval(ago, 60000);
</script>
</body></html>
"""
