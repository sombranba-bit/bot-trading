"""Páginas del bot para GitHub Pages: portada (index.html) y panel (panel.html).

Sistema visual: menú lateral fijo (como la app de inglés y TachoTruck), paleta violeta de TachoTruck,
tacómetro del CV para la rentabilidad, cinta de precios de la mesa de pronósticos y colores de estado.
Sin dependencias: HTML, CSS y JS escritos a mano.
"""
import math
from html import escape
from urllib.parse import urlparse

NAMES = ["Tendencia", "Momentum", "Valor"]
SECTIONS = [("resumen", "Resumen", "grid"), ("pronosticos", "Pronósticos", "target"), ("cartera", "Cartera", "wallet"),
            ("senales", "Señales", "signal"), ("actividad", "Actividad", "activity"), ("evaluacion", "Evaluación", "flask")]
SECTOR_ES = {"Technology": "Tecnología", "Financial Services": "Financiero", "Healthcare": "Salud",
             "Consumer Defensive": "Consumo básico", "Consumer Cyclical": "Consumo discrecional",
             "Energy": "Energía", "Communication Services": "Comunicación", "Industrials": "Industria",
             "Utilities": "Suministros", "Real Estate": "Inmobiliario", "Basic Materials": "Materiales"}
SECTOR_ICON = {"Technology": "cpu", "Financial Services": "landmark", "Healthcare": "heart",
               "Consumer Defensive": "bag", "Consumer Cyclical": "bag", "Energy": "zap",
               "Communication Services": "radio", "Industrials": "factory", "Utilities": "bulb",
               "Real Estate": "building", "Basic Materials": "box"}

ICONS = {
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "wallet": '<path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H18v3"/><path d="M3 7.5v10A2.5 2.5 0 0 0 5.5 20H20V8H5.5A2.5 2.5 0 0 1 3 7.5z"/><circle cx="16.5" cy="14" r="1"/>',
    "signal": '<path d="M4 20v-5M9.5 20V11M15 20V7M20.5 20V3"/>',
    "activity": '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
    "flask": '<path d="M9 3h6M10 3v6L4.8 18.2A1.8 1.8 0 0 0 6.3 21h11.4a1.8 1.8 0 0 0 1.5-2.8L14 9V3"/><path d="M7.5 15h9"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    "cpu": '<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M4 10h3M4 14h3M17 10h3M17 14h3M10 4v3M14 4v3M10 17v3M14 17v3"/>',
    "landmark": '<path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "bag": '<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "zap": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "radio": '<circle cx="12" cy="12" r="2"/><path d="M8.5 8.5a5 5 0 0 0 0 7M15.5 8.5a5 5 0 0 1 0 7M5.6 5.6a9 9 0 0 0 0 12.8M18.4 5.6a9 9 0 0 1 0 12.8"/>',
    "factory": '<path d="M3 21V9l5 3V9l5 3V5h8v16z"/><path d="M7 21v-3M11 21v-3M15 21v-3M19 21v-3"/>',
    "bulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "building": '<rect x="5" y="3" width="14" height="18" rx="1.5"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>',
    "box": '<path d="M12 2.5l8.5 4.7v9.6L12 21.5l-8.5-4.7V7.2z"/><path d="M3.5 7.2L12 12l8.5-4.8M12 12v9.5"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>',
    "dot": '<circle cx="12" cy="12" r="3"/>',
}

CSS = """
:root{--paper:#0b0b0b;--paper2:#1a1a1a;--card:#121212;--ink:#f4f4f2;--mut:#8d8d8b;--rule:#ffffff17;--acc:#e8b23a;--acc2:#f6dc8e;
--glow:#c9962a;--drv:#c9962a;--work:#e8b23a;--av:#d9a441;--rest:#4ade80;--bad:#f87171;--ok:#4ade80;--warn:#fbbf24;
--accsoft:#2a2110;--oksoft:#12261b;--badsoft:#2a1515;--shadow:0 1px 2px rgba(0,0,0,.5),0 10px 30px rgba(0,0,0,.5);
--pos:var(--ok);--neg:var(--bad);--line:var(--rule);--txt:var(--ink);--muted:var(--mut);--a1:var(--acc);--a2:var(--acc2)}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--paper:#f6f1e4;--paper2:#ece5d2;--card:#fffdf7;--ink:#111111;--mut:#6b6558;
--rule:#e2d8bf;--acc:#9a6d0c;--acc2:#c99a2e;--glow:#b07a14;--drv:#b07a14;--work:#c99a2e;--av:#a9781a;--rest:#15803d;--bad:#b91c1c;--ok:#15803d;
--warn:#92580a;--accsoft:#f4e7c3;--oksoft:#dcefdc;--badsoft:#fbe2e2;--shadow:0 1px 2px rgba(17,17,17,.06),0 8px 24px rgba(17,17,17,.07)}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;color:var(--ink);background:var(--paper);font:15px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;
-webkit-font-smoothing:antialiased;overflow-x:hidden;transition:background-color .5s ease}
a{color:inherit;text-decoration:none}
button{font:inherit}
.num{font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.px,.tk,.gv,.when,.tape{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace}
.label{font:600 11px/1.2 Inter,system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--mut)}
.grad{background:linear-gradient(90deg,var(--acc),var(--acc2),var(--glow));background-size:200% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:sweep 6s linear infinite}
.pos{color:var(--pos)} .neg{color:var(--neg)} .muted{color:var(--mut)}
@keyframes sweep{to{background-position:200% center}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes growY{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}
@keyframes pulse{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--rest) 60%,transparent)}70%{box-shadow:0 0 0 8px transparent}100%{box-shadow:0 0 0 0 transparent}}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(24px,-16px)}}
@keyframes tape{to{transform:translateX(-50%)}}
@keyframes needle{from{transform:rotate(-135deg)}}
@keyframes fxUp{0%{opacity:0;transform:translate(-50%,8px) scale(.85)}15%{opacity:1;transform:translate(-50%,0) scale(1.05)}100%{opacity:0;transform:translate(-50%,-38px)}}
@keyframes shine{to{transform:translateX(100%)}}

/* ---- Estructura: menú lateral fijo + contenido ---- */
.shell{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}
.side{position:sticky;top:0;height:100vh;display:flex;flex-direction:column;gap:22px;padding:24px 16px;border-right:1px solid var(--rule);
background:linear-gradient(180deg,color-mix(in srgb,var(--acc) 12%,var(--paper)),var(--paper) 60%);overflow-y:auto}
.brand{display:flex;align-items:center;gap:12px;padding:0 8px}
.brand b{display:block;font-size:16px;font-weight:700;letter-spacing:-.01em}
.brand small{color:var(--mut);font-size:12px}
.mark{width:38px;height:38px;flex:none}
.nav{display:flex;flex-direction:column;gap:4px}
.nav .label{padding:0 10px;margin-bottom:6px}
.nav button,.nav a{display:flex;align-items:center;gap:12px;width:100%;padding:10px 12px;border:1px solid transparent;border-radius:12px;background:none;
color:var(--mut);font-size:15px;font-weight:600;text-align:left;cursor:pointer;transition:color .2s,background .2s,border-color .2s,transform .2s}
.nav button:hover,.nav a:hover{color:var(--ink);background:var(--paper2);transform:translateX(3px)}
.nav button.on{color:var(--ink);background:var(--card);border-color:color-mix(in srgb,var(--acc) 55%,transparent);box-shadow:inset 3px 0 0 var(--acc)}
.nav .ic{width:18px;height:18px;flex:none;color:var(--acc)}
.nav em{font-style:normal;margin-left:auto;font-size:11px;color:var(--mut);font-variant-numeric:tabular-nums;opacity:.7}
.side-foot{margin-top:auto;display:flex;flex-direction:column;gap:8px}
.side-foot>a{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:12px;color:var(--mut);font-size:15px;font-weight:600}
.side-foot>a:hover{color:var(--ink);background:var(--paper2)}.side-foot .ic{width:18px;height:18px;flex:none;color:var(--acc)}
.legend-c{display:grid;gap:6px;font-size:12px;color:var(--mut)}
.legend-c i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:8px;vertical-align:1px}
.main{min-width:0;padding:26px 34px 60px}
.top{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px 18px;margin-bottom:18px;animation:rise .5s ease both}
.top h1{margin:0;font-size:24px;font-weight:700;letter-spacing:-.02em}
.top p{margin:2px 0 0;color:var(--mut);font-size:14px}
.pills{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.pill{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;border:1px solid var(--rule);background:var(--card);font-size:13px}
.pill.ok{border-color:color-mix(in srgb,var(--ok) 50%,transparent);color:var(--ok)}
.pill.off{border-color:color-mix(in srgb,var(--warn) 50%,transparent);color:var(--warn)}
.pill i{width:8px;height:8px;border-radius:50%;background:var(--ok);animation:pulse 1.8s infinite}
.pill.off i{background:var(--warn);animation:none}
.tapewrap{margin:0 0 20px;overflow:hidden;border:1px solid var(--rule);border-radius:12px;background:var(--card);
mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
.tape{display:flex;width:max-content;animation:tape 46s linear infinite;padding:10px 0}
.tape .it{display:inline-flex;gap:8px;align-items:center;padding:0 20px;font-size:13px;border-right:1px solid var(--rule);font-variant-numeric:tabular-nums}
.tape b{color:var(--acc)} .tape em{font-style:normal;font-size:12px}
.view{display:none} .view.on{display:block;animation:rise .45s cubic-bezier(.2,.7,.2,1) both}
.stg{animation:rise .5s cubic-bezier(.2,.7,.2,1) backwards;animation-delay:calc(var(--i,0)*50ms)}

/* ---- Tarjetas y componentes ---- */
.feat{display:flex;gap:18px;align-items:center;cursor:pointer;background:linear-gradient(135deg,color-mix(in srgb,var(--acc) 16%,var(--card)),var(--card));border-color:color-mix(in srgb,var(--acc) 45%,transparent)}
.feat .pb{min-width:0;flex:1}.feat p{-webkit-line-clamp:2;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden;margin:8px 0 0;color:var(--mut);font-size:13.5px}
.feat .go{color:var(--mut);transition:transform .3s,color .3s}.feat:hover .go{transform:translateX(4px);color:var(--acc)}
.card{background:var(--card);border:1px solid var(--rule);border-radius:16px;box-shadow:var(--shadow);padding:20px;position:relative;overflow:hidden;
transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s ease,border-color .25s}
.card:hover{transform:translateY(-2px);border-color:color-mix(in srgb,var(--acc) 50%,transparent)}
.glow::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .35s;
background:radial-gradient(300px circle at var(--mx,50%) var(--my,50%),color-mix(in srgb,var(--acc) 16%,transparent),transparent 60%)}
.glow:hover::before{opacity:1}
.card h2{margin:0 0 14px;font-size:15px;font-weight:700;display:flex;align-items:center;gap:8px}
.card h2 .ic{width:18px;height:18px;color:var(--acc)}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:16px}
.kpi{border-top:3px solid var(--acc)}
.kpi .kh{display:flex;align-items:center;gap:8px;color:var(--mut);font-size:13px}
.kpi .kh .ic{width:16px;height:16px}
.kpi strong{display:block;font:700 28px/1.15 Inter,system-ui,sans-serif;margin:8px 0 0;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.grid2{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:16px}
.gauge{display:flex;flex-direction:column;align-items:center;gap:4px;width:230px}
.gauge svg{width:100%;overflow:visible;animation:fade .8s ease both}
.gauge .arc{fill:none;stroke:var(--rule);stroke-width:5;stroke-linecap:round}
.gauge .ticks line{stroke:var(--mut);stroke-width:1.2;opacity:.6}
.gauge .needle{transform-origin:50px 50px;transform:rotate(var(--a));animation:needle 1.8s cubic-bezier(.22,1,.36,1) .25s both}
.gauge .needle line{stroke:var(--acc);stroke-width:2.4;stroke-linecap:round}
.gauge .hub{fill:var(--acc)}
.gauge .gv{font:700 26px/1 Inter,system-ui,sans-serif;font-variant-numeric:tabular-nums}
.gauge .label{font-size:10.5px;white-space:nowrap}
.hero-card{display:grid;grid-template-columns:auto minmax(0,1fr);gap:24px;align-items:center;margin-bottom:16px}
.hero-card .txt p{margin:6px 0 0;color:var(--mut);font-size:14px}
.chart{width:100%;display:block;overflow:visible}
.chart .draw{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.4s ease-out forwards}
.chart .fill{opacity:0;animation:fade 1s .4s forwards}
.axis{display:flex;justify-content:space-between;color:var(--mut);font-size:12px;margin-top:8px;font-variant-numeric:tabular-nums}
.empty{padding:40px 0;text-align:center;color:var(--mut)}
.px{font-weight:600;font-size:13px;margin-left:6px;padding:1px 6px;border-radius:6px;color:var(--mut);font-variant-numeric:tabular-nums}
.px.pos{color:var(--ok);background:var(--oksoft)} .px.neg{color:var(--bad);background:var(--badsoft)}
.tick{animation:fade .6s}
.fx{position:fixed;z-index:120;pointer-events:none;font-weight:700;font-size:14px;font-variant-numeric:tabular-nums;animation:fxUp 1.1s ease-out forwards;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.mini{display:flex;gap:12px;align-items:center;padding:10px;border-radius:12px;transition:background .2s,transform .2s}
.mini:hover{background:var(--paper2);transform:translateX(3px)}
.mini b{font-weight:600}
.row{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr) minmax(0,.8fr);gap:10px;padding:11px 8px;border-bottom:1px solid var(--rule);align-items:center;font-size:14px;border-radius:10px;transition:background .2s}
.row:hover{background:var(--paper2)}
.row:last-child{border:0}
.row>span:last-child{text-align:right}
.bar{position:relative;height:8px;border-radius:6px;background:var(--paper2);overflow:hidden;margin-top:6px}
.bar>i{position:absolute;inset:0;border-radius:6px;background:linear-gradient(90deg,var(--acc),var(--acc2));transform-origin:left;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}

/* Señales de un vistazo */
.sig{display:inline-flex;gap:4px;align-items:center}
.sig i{width:9px;height:9px;border-radius:3px;background:var(--rule)}
.sig i.on{background:var(--acc)}
.sig.warn i.on{background:var(--glow)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font-size:11.5px;font-weight:600;padding:3px 9px;border-radius:999px;border:1px solid var(--rule);color:var(--mut)}
.chip.on{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 50%,transparent);background:var(--oksoft)}
.tk{font:600 11.5px Inter,system-ui,sans-serif;color:var(--acc);background:var(--accsoft);padding:1px 7px;border-radius:6px;font-variant-numeric:tabular-nums}
.sec{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:var(--mut);margin-top:2px}
.sec-ic{display:grid;place-items:center;width:22px;height:22px;border-radius:7px;background:var(--accsoft);color:var(--acc)}
.sec-ic .ic{width:14px;height:14px}
.sec-ic.glyph{font-weight:700;font-size:13px;color:var(--glow);background:color-mix(in srgb,var(--glow) 15%,transparent)}
.picks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.pick{display:flex;gap:14px;align-items:flex-start;cursor:pointer}
.pick .pb{min-width:0;flex:1}
.pick p{margin:6px 0 8px;font-size:13.5px;color:var(--mut);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.ttl{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.ttl strong{font-size:15px}
.meta{color:var(--mut);font-size:13px}
.go{color:var(--mut);transition:transform .3s,color .3s;margin-top:4px}
.pick:hover .go{transform:translateX(4px);color:var(--acc)}
/* Logos: monograma de color propio por ticker */
.logo{position:relative;width:52px;height:52px;flex:none;border-radius:14px;display:grid;place-items:center;overflow:hidden;color:var(--acc);
background:#0b0b0b;border:1px solid color-mix(in srgb,var(--acc) 60%,transparent);box-shadow:inset 0 -2px 0 var(--acc),0 6px 16px rgba(0,0,0,.35)}
.logo span{font:700 .8rem Inter,system-ui,sans-serif;letter-spacing:.01em;text-shadow:0 1px 2px rgba(0,0,0,.3)}
.logo img{position:absolute;inset:0;width:100%;height:100%;background:#fff;object-fit:contain;padding:9px;opacity:0;transition:opacity .5s}
.logo img.ok{opacity:1}
.logo.sm{width:36px;height:36px;border-radius:11px}.logo.sm span{font-size:.62rem}
.logo.lg{width:64px;height:64px;border-radius:18px}.logo.lg span{font-size:1rem}
.mini-list .mini{margin:0}

/* Tabla tipo tablero (evaluación) */
.board{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}
.board th{text-align:right;font-weight:600;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);padding:8px 10px;border-bottom:1px solid var(--rule)}
.board th:first-child,.board td:first-child{text-align:left}
.board td{padding:12px 10px;text-align:right;border-bottom:1px solid var(--rule)}
.board tr{transition:background .2s}
.board tbody tr:hover{background:var(--paper2)}
.board tr.best td:first-child{color:var(--ok)}
.board .tag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;margin-left:8px;background:var(--oksoft);color:var(--ok)}

/* Línea de tiempo de actividad */
.tl{position:relative;padding-left:22px;display:grid;gap:14px}
.tl::before{content:"";position:absolute;left:6px;top:6px;bottom:6px;width:2px;background:var(--rule);border-radius:2px}
.tl-item{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:baseline}
.tl-item::before{content:"";position:absolute;left:-22px;top:5px;width:12px;height:12px;border-radius:50%;background:var(--c,var(--acc));box-shadow:0 0 0 4px var(--paper)}
.tl-item .when{font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums}
.tl-item b{font-weight:600}

/* Señales: mapa de calor con colores de estado */
.heat{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:10px}
.cell{border-radius:14px;padding:12px;font-size:12.5px;display:flex;flex-direction:column;gap:4px;cursor:pointer;border:1px solid var(--rule);
background:var(--card);transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s,border-color .25s}
.cell:hover{transform:translateY(-3px);box-shadow:var(--shadow);border-color:var(--acc)}
.cell b{font-size:14px}
.cell span{color:var(--mut)}
.cell.v3{background:linear-gradient(135deg,var(--acc),var(--acc2));border-color:transparent;color:#0b0b0b}
.cell.v3 span,.cell.v3 .px{color:#0b0b0b;opacity:.85}
.cell.v2{background:color-mix(in srgb,var(--acc2) 18%,var(--card));border-color:color-mix(in srgb,var(--acc2) 40%,transparent)}
.cell.v1{background:color-mix(in srgb,var(--acc) 10%,var(--card))}
.cell.v0{opacity:.7}

/* Fichas */
.dlg{width:min(580px,92vw);color:var(--ink);background:var(--card);border:1px solid var(--rule);border-radius:18px;padding:22px;box-shadow:var(--shadow);margin:auto}
.dlg[open]{animation:pop .3s cubic-bezier(.2,.8,.2,1) both}
.dlg::backdrop{background:rgba(5,7,12,.6);backdrop-filter:blur(4px);animation:fade .3s ease both}
.dh{display:flex;gap:14px;align-items:center}.dh>div{flex:1;min-width:0}
.x{background:none;border:0;color:var(--mut);font-size:18px;cursor:pointer;padding:6px;border-radius:10px}
.x:hover{background:var(--paper2);color:var(--ink)}
.big-px{font-size:30px;font-weight:700;margin:16px 0 4px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.big-px .px{font-size:14px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}
.stats div{background:var(--paper2);border:1px solid var(--rule);border-radius:12px;padding:12px}
.stats span{display:block;color:var(--mut);font-size:11.5px}
.stats b{font-size:15px;font-variant-numeric:tabular-nums}

/* Portada */
.hero{position:relative;overflow:hidden;border-radius:22px;padding:44px 40px;border:1px solid var(--rule);background:var(--card);box-shadow:var(--shadow);
display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:36px;align-items:center;animation:rise .7s ease both}
.blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.25;pointer-events:none;animation:float 14s ease-in-out infinite}
.blob.b1{width:340px;height:340px;background:var(--acc);top:-150px;left:-100px}
.blob.b2{width:280px;height:280px;background:var(--acc2);bottom:-140px;right:-60px;animation-duration:17s}
.hero h1{position:relative;margin:0;font-size:clamp(2.2rem,5vw,3.4rem);line-height:1.05;letter-spacing:-.03em;font-weight:800}
.hero p{position:relative;color:var(--mut);font-size:1.05rem;margin:16px 0 24px;max-width:600px}
.hero-gauge{position:relative;display:flex;justify-content:center}
.cta{position:relative;display:flex;flex-wrap:wrap;gap:12px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:12px;font-weight:700;font-size:15px;border:1px solid var(--rule);background:var(--card);color:var(--ink);transition:transform .2s,box-shadow .25s,border-color .2s}
.btn.main{background:linear-gradient(135deg,var(--acc),var(--acc2));border-color:transparent;color:#0b0b0b}
.btn.main:hover{box-shadow:0 12px 30px color-mix(in srgb,var(--acc) 45%,transparent)}
.btn:hover{transform:translateY(-2px);border-color:var(--acc)}
.btn .ic{width:18px;height:18px;transition:transform .25s}.btn:hover .ic{transform:translateX(3px)}
.nav-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:20px}
button.nc{width:100%;text-align:left;font:inherit;color:inherit;cursor:pointer}
.nc{display:block;position:relative;overflow:hidden;padding:22px;border-radius:18px;border:1px solid var(--rule);background:var(--card);box-shadow:var(--shadow);
transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .3s,box-shadow .35s;border-top:3px solid var(--acc)}
.nc:hover{transform:translateY(-5px);box-shadow:0 18px 40px color-mix(in srgb,var(--acc) 22%,transparent)}
.nc .ico{display:grid;place-items:center;width:44px;height:44px;border-radius:13px;background:var(--accsoft);color:var(--acc);margin-bottom:14px;transition:transform .35s}
.nc:hover .ico{transform:rotate(-6deg) scale(1.06)}
.nc .ico .ic{width:22px;height:22px}
.nc h3{margin:0 0 6px;font-size:17px}
.nc p{margin:0 0 12px;color:var(--mut);font-size:14px}
.nc .tag{font-size:13px;font-weight:600;color:var(--acc)}
.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:16px}
.step{padding:20px;border-radius:16px;border:1px solid var(--rule);background:var(--card)}
.step .n{font:700 12px Inter,system-ui,sans-serif;color:var(--acc);letter-spacing:.1em}
.step h3{margin:8px 0 6px;font-size:16px}
.step p{margin:0;color:var(--mut);font-size:14px}
.sec-title{margin:32px 0 12px}
[data-reveal]{opacity:0;transform:translateY(20px);transition:opacity .7s ease,transform .7s cubic-bezier(.2,.8,.2,1)}
[data-reveal].in{opacity:1;transform:none}
footer{margin-top:28px;color:var(--mut);font-size:12.5px;text-align:center}

/* Móvil: el menú se convierte en una franja horizontal */
@media (max-width:980px){
  .shell{grid-template-columns:minmax(0,1fr)}
  .side{position:sticky;top:0;z-index:20;height:auto;flex-direction:row;align-items:center;gap:12px;padding:12px 14px;border-right:0;border-bottom:1px solid var(--rule);
  background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(10px);overflow-x:auto}
  .brand small,.side-foot,.nav .label,.nav em{display:none}
  .nav{flex-direction:row;gap:6px}
  .nav button,.nav a{width:auto;white-space:nowrap;padding:8px 12px;transform:none!important}
  .main{padding:18px 16px 50px}
  .kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
  .grid2,.picks,.steps,.nav-cards{grid-template-columns:minmax(0,1fr)}
  .hero{grid-template-columns:minmax(0,1fr);padding:28px 22px}
  .hero-card{grid-template-columns:minmax(0,1fr);justify-items:center;text-align:center}
}
@media (max-width:560px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.kpi strong{font-size:22px}.row{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr) minmax(0,.8fr);font-size:13px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}[data-reveal]{opacity:1;transform:none}}
"""

JS = """
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
function show(id){
  if(!$('#'+id)||!$('#'+id).classList.contains('view')) id='resumen';
  $$('.view').forEach(s=>s.classList.toggle('on',s.id===id));
  $$('.nav button').forEach(b=>b.classList.toggle('on',b.dataset.t===id));
  const on=$('.nav button.on'), tt=$('#titulo'); if(tt&&on) tt.textContent=on.querySelector('span').textContent;
  $$('.view.on .stg').forEach((el,i)=>el.style.setProperty('--i',i%16));
  history.replaceState(null,'','#'+id);
}
function countUp(){
  if(reduce) return;
  $$('[data-n]').forEach(el=>{
    const to=+el.dataset.n, suf=el.dataset.s||'', dec=suf==='%'?1:0, sg=suf==='%'&&to>0?'+':'';
    const t0=performance.now();
    const step=t=>{const k=Math.min(1,(t-t0)/1000),e=1-Math.pow(1-k,3);el.textContent=sg+(to*e).toFixed(dec)+suf;if(k<1)requestAnimationFrame(step);};
    requestAnimationFrame(step);
  });
}
function ago(){
  $$('.ago,#pxts').forEach(el=>{
    if(!el.dataset.ts) return;
    const m=Math.round((Date.now()-Date.parse(el.dataset.ts))/60000);
    el.textContent=m<60?'hace '+m+' min':'hace '+Math.round(m/60)+' h';
  });
}
function fx(el,txt,up){
  if(reduce) return;
  const r=el.getBoundingClientRect(), s=document.createElement('span');
  s.className='fx '+(up?'pos':'neg'); s.textContent=txt;
  s.style.left=(r.left+r.width/2)+'px'; s.style.top=(r.top-6)+'px';
  document.body.appendChild(s); setTimeout(()=>s.remove(),1150);
}
async function precios(){
  try{
    const j=await (await fetch('prices.json?'+Date.now())).json();
    $$('[data-p]').forEach(e=>{
      const d=j.p[e.dataset.p]; if(!d) return;
      const txt=d.p.toFixed(2)+' '+(d.v>=0?'▲ +':'▼ ')+d.v.toFixed(2)+'%';
      const prev=e.dataset.last?+e.dataset.last:null;
      if(prev!==null&&prev!==d.p){ fx(e,(d.p>prev?'▲ ':'▼ ')+Math.abs((d.p/prev-1)*100).toFixed(2)+'%',d.p>prev); e.classList.remove('tick');void e.offsetWidth;e.classList.add('tick'); }
      e.dataset.last=d.p;
      e.textContent=txt; e.className='px '+(d.v>=0?'pos':'neg');
    });
    const tp=$('#tape');
    if(tp){const items=Object.entries(j.p).map(([t,d])=>'<span class="it"><b>'+t+'</b>'+d.p.toFixed(2)+'<em class="'+(d.v>=0?'pos':'neg')+'">'+(d.v>=0?'▲ +':'▼ ')+d.v.toFixed(2)+'%</em></span>').join('');tp.innerHTML=items+items;}
    if($('#pxts')){$('#pxts').dataset.ts=j.ts;ago();}
  }catch(e){ /* sin precios: la página sigue mostrando el informe */ }
}
document.addEventListener('pointermove',e=>{
  const g=e.target.closest&&e.target.closest('.glow'); if(!g) return;
  const r=g.getBoundingClientRect();
  g.style.setProperty('--mx',(e.clientX-r.left)+'px'); g.style.setProperty('--my',(e.clientY-r.top)+'px');
});
$$('.logo img').forEach(img=>{if(img.complete&&img.naturalWidth>0)img.classList.add('ok');else img.addEventListener('load',()=>img.classList.add('ok'));});
if($('.nav button')){
  $$('.nav button').forEach(b=>b.onclick=()=>show(b.dataset.t));
  show(location.hash.slice(1)||'inicio');
  addEventListener('hashchange',()=>show(location.hash.slice(1)));
  $$('[data-go]').forEach(b=>b.onclick=()=>show(b.dataset.go));
}
if('IntersectionObserver' in window&&!reduce){
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{threshold:.12});
  $$('[data-reveal]').forEach(el=>io.observe(el));
} else $$('[data-reveal]').forEach(el=>el.classList.add('in'));
countUp(); ago(); precios();
setInterval(precios,60000); setInterval(ago,60000);
"""

BRAND_MARK = ('<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="gm" x1="0" y1="0" x2="1" y2="1">'
              '<stop offset="0" stop-color="#f6dc8e"/><stop offset="1" stop-color="#e8b23a"/></linearGradient></defs>'
              '<rect x="2" y="2" width="36" height="36" rx="11" fill="url(#gm)" opacity=".2"/>'
              '<path d="M9 27V19M16 27V13M23 27V17M30 27V9" stroke="url(#gm)" stroke-width="3" stroke-linecap="round"/></svg>')


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(name, ICONS["dot"])}</svg>')


def pct(x):
    return f"{x:+.1%}"


def cls(x):
    return "pos" if x >= 0 else "neg"


def gauge(v, label):
    """Tacómetro: la aguja va de -20 % (izquierda) a +20 % (derecha) y se mueve al cargar."""
    a = max(-1, min(1, v / 0.2)) * 135
    ticks = "".join(
        f'<line x1="{50 + 40 * math.sin(math.radians(k)):.1f}" y1="{50 - 40 * math.cos(math.radians(k)):.1f}" '
        f'x2="{50 + 46 * math.sin(math.radians(k)):.1f}" y2="{50 - 46 * math.cos(math.radians(k)):.1f}"/>'
        for k in range(-135, 136, 27))
    return (f'<div class="gauge"><svg viewBox="0 0 100 100" aria-hidden="true">'
            f'<path class="arc" d="M18.9 81.1 A44 44 0 1 1 81.1 81.1"/><g class="ticks">{ticks}</g>'
            f'<g class="needle" style="--a:{a:.1f}deg"><line x1="50" y1="56" x2="50" y2="14"/></g>'
            f'<circle class="hub" cx="50" cy="50" r="3.5"/></svg>'
            f'<span class="gv {cls(v)}">{pct(v)}</span><span class="label">{label}</span></div>')


def logo(t, info, size=""):
    # Monograma con color propio por ticker; el favicon de la empresa aparece encima si carga
    dom = urlparse(info.get("web") or "").netloc.replace("www.", "")
    img = (f'<img src="https://www.google.com/s2/favicons?domain={escape(dom)}&amp;sz=128" alt="" '
           f'loading="lazy" onerror="this.remove()">') if dom else ""
    return f'<div class="logo {size}"><span>{escape(t.split("-")[0][:5])}</span>{img}</div>'


def sector_mark(t, info):
    if t.endswith("-USD"):
        return '<span class="sec-ic glyph">₿</span>'
    return f'<span class="sec-ic">{icon(SECTOR_ICON.get(info.get("sector"), "dot"))}</span>'


def meta(c):
    s = SECTOR_ES.get(c.get("sector"), c.get("sector")) or "Sin sector"
    return escape(s) + (f" · {escape(c['industry'])}" if c.get("industry") else "")


def desc(info):
    return escape(info.get("summary") or f"Sin descripción disponible en Yahoo Finance. Sector: {info.get('sector') or 'n/d'}.")


def sig(flags):
    """Tres cuadraditos: uno por señal (tendencia, momentum, valor), encendido si se cumple."""
    cells = "".join(f'<i class="{"on" if on else ""}" title="{nm}"></i>' for nm, on in zip(NAMES, flags))
    return f'<span class="sig" aria-label="{sum(flags)} de 3 señales">{cells}</span>'


def spark(vals, h=240, extra=""):
    if len(vals) < 2:
        return '<div class="empty">Sin datos suficientes todavía.</div>'
    w = 800
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pts = [(i * w / (len(vals) - 1), h - (v - lo) / span * (h - 30) - 15) for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"0,{h} {line} {w},{h}"
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" class="chart {extra}" style="height:{h}px">'
            f'<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e8b23a" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="#e8b23a" stop-opacity="0"/></linearGradient></defs>'
            f'<polygon points="{area}" fill="url(#sg)" class="fill"/>'
            f'<polyline points="{line}" pathLength="1" class="draw" fill="none" stroke="var(--acc)" stroke-width="3" '
            f'stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')


def open_js(t):
    return f"document.getElementById('d-{t}').showModal()"


def pick_card(p):
    c, t = p["info"], p["ticker"]
    chips = "".join(f'<span class="chip{" on" if on else ""}">{nm}</span>' for nm, on in zip(NAMES, p["flags"]))
    return (f'<article class="card glow pick stg" role="button" tabindex="0" onclick="{open_js(t)}" '
            f'onkeydown="if(event.key===\'Enter\')this.click()">{logo(t, c)}<div class="pb">'
            f'<div class="ttl"><strong>{escape(c["name"])}</strong><span class="tk">{escape(t)}</span>{sig(p["flags"])}</div>'
            f'<div class="sec">{sector_mark(t, c)}{meta(c)}</div>'
            f'<div class="meta">{p["precio"]} USD <span class="px" data-p="{escape(t)}"></span></div>'
            f'<p>{desc(c)}</p><div class="chips">{chips}</div></div><span class="go">{icon("arrow")}</span></article>')


def mini_pick(p):
    return (f'<div class="mini stg">{logo(p["ticker"], p["info"], "sm")}<div><b>{escape(p["info"]["name"])}</b>'
            f'<div class="meta">{escape(p["ticker"])} · {p["votos"]}/3 · <span class="px" data-p="{escape(p["ticker"])}"></span></div></div></div>')


def heat_cell(t, f):
    return (f'<div class="cell v{f["n"]} stg" role="button" tabindex="0" onclick="{open_js(t)}"><b>{escape(t)}</b>'
            f'{sig(f["v"])}<span>{f["n"]}/3 señales</span><em class="px" data-p="{escape(t)}" style="font-style:normal"></em></div>')


def dialog(t, f):
    c = f["info"]
    chips = "".join(f'<span class="chip{" on" if on else ""}">{nm}</span>' for nm, on in zip(NAMES, f["v"]))
    pe = f"{c['pe']:.1f}" if c.get("pe") else "n/d"
    target = f"{c['target']:.2f} USD" if c.get("target") else "n/d"
    upside = pct(c["upside"]) if c.get("upside") is not None else "n/d"
    return (f'<dialog id="d-{escape(t)}" class="dlg">'
            f'<div class="dh">{logo(t, c, "lg")}<div><strong>{escape(c["name"])}</strong>'
            f'<div class="meta">{escape(t)} · {meta(c)}</div></div>'
            f'<button class="x" onclick="this.closest(\'dialog\').close()" aria-label="Cerrar">✕</button></div>'
            f'<div class="big-px"><span class="px" data-p="{escape(t)}"></span></div>'
            f'{spark(f["hist"], 140)}<p class="meta">Último año · cierre diario</p>'
            f'<p>{desc(c)}</p><div class="chips">{chips}</div>'
            f'<div class="stats"><div><span>P/E</span><b>{pe}</b></div>'
            f'<div><span>Precio objetivo</span><b>{target}</b></div>'
            f'<div><span>Potencial</span><b>{upside}</b></div>'
            f'<div><span>Señales</span><b>{f["n"]}/3</b></div></div></dialog>')


def kpi(label, value, c="", num=None, suf="", ic="grid"):
    data = f' data-n="{num}" data-s="{suf}"' if num is not None else ""  # num: cifra que la página anima al cargar
    return (f'<div class="card kpi glow stg"><div class="kh">{icon(ic)}<span>{label}</span></div>'
            f'<strong class="{c}"{data}>{value}</strong></div>')


def status_pill(st):
    if st is None:
        return '<span class="pill off"><i></i>Sin datos del bot todavía</span>'
    if st.get("parado"):
        return '<span class="pill off"><i></i>Bot parado (KILL_SWITCH)</span>'
    mercado = "Bolsa EE. UU. abierta" if st["mercado_abierto"] else "Bolsa EE. UU. cerrada (solo cripto)"
    return (f'<span class="pill ok"><i></i>Bot activo · <b class="ago" data-ts="{st["ts"]}">{st["ts"]}</b></span>'
            f'<span class="pill">{mercado}</span>')


def activity(r):
    compra = r["accion"] == "COMPRA"
    color = "var(--ok)" if compra else "var(--glow)"
    texto = "Entra en el cesto" if compra else "Sale: caída de más de un 20 % desde su máximo"
    return (f'<div class="tl-item stg" style="--c:{color}"><div><b>{"Compra" if compra else "Venta"} {escape(r["simbolo"])}</b>'
            f'<div class="meta">{texto}</div></div>'
            f'<span class="when">{escape(r["fecha"][:16].replace("T", " "))}</span></div>')


def page(title, body, today, sidebar=""):
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<meta name="description" content="Aldana Trading, bot de paper trading: cesto de acciones con filtro de caída, pronósticos y backtest frente a VWCE. Actualizado {today}.">
<style>{CSS}</style></head>
<body>
<div class="shell">
{sidebar}
<div class="main">
{body}
<footer>Simulación con dinero ficticio, no asesoramiento financiero. Datos de Yahoo Finance y Alpaca, con retraso de hasta 15 minutos. Actualizado el {today}.</footer>
</div>
</div>
<script>{JS}</script>
</body></html>
"""


def side_nav():
    """Menú lateral: Inicio y las secciones, todo en una página."""
    home = f'<button data-t="inicio">{icon("home")}<span>Inicio</span></button>'
    links = home + "".join(
        f'<button data-t="{k}">{icon(ic)}<span>{v}</span><em>{i:02d}</em></button>'
        for i, (k, v, ic) in enumerate(SECTIONS, 1))
    return f"""<aside class="side">
  <a class="brand" href="#inicio">{BRAND_MARK}<div><b>Aldana Trading</b><small>Paper trading</small></div></a>
  <nav class="nav"><span class="label">Secciones</span>{links}</nav>
  <div class="side-foot">
    <div class="legend-c"><span><i style="background:var(--acc)"></i>Señal cumplida</span>
    <span><i style="background:var(--ok)"></i>Compra</span><span><i style="background:var(--glow)"></i>Venta o caída</span></div>
  </div>
</aside>"""


def featured(p):
    """Tarjeta destacada: la acción con más señales (y más potencial) de hoy."""
    if not p:
        return ""
    c, t = p["info"], p["ticker"]
    return (f'<article class="card glow feat stg" role="button" tabindex="0" onclick="{open_js(t)}" '
            f'onkeydown="if(event.key===\'Enter\')this.click()">{logo(t, c, "lg")}<div class="pb">'
            f'<span class="label">Destacado de hoy · {p["votos"]}/3 señales</span>'
            f'<h2 style="font-size:20px;margin:6px 0 2px">{escape(c["name"])} <span class="tk">{escape(t)}</span></h2>'
            f'<div class="sec">{sector_mark(t, c)}{meta(c)}</div><p>{desc(c)}</p></div>'
            f'<span class="go">{icon("arrow")}</span></article>')


def render(ctx) -> str:
    """Panel: menú lateral con secciones, cada una con su propia vista."""
    eq = ctx["equity"]
    eq_vals = [v for _, v in eq]
    axis = (f'<div class="axis"><span>{eq[0][0]} · {eq[0][1]:,.0f} USD</span>'
            f'<span>{eq[-1][0]} · {eq[-1][1]:,.0f} USD</span></div>') if eq else ""
    total = sum(p["value"] for p in ctx["positions"]) or 1
    positions = "".join(
        f'<div class="row stg"><div><b>{escape(p["symbol"])}</b> <span class="px" data-p="{escape(p["ticker"])}"></span>'
        f'<div class="bar"><i style="animation-delay:{0.1 * i:.1f}s;transform:scaleX({p["value"] / total:.3f})"></i></div></div>'
        f'<span>{p["value"]:,.0f} USD</span><span class="{cls(p["pl"])}">{pct(p["pl"])}</span></div>'
        for i, p in enumerate(ctx["positions"])) or '<p class="muted">Sin posiciones abiertas.</p>'
    trades = "".join(activity(r) for r in ctx["trades"]) or '<p class="muted">Todavía no ha habido operaciones.</p>'
    best = max((float(r["total"]) for r in ctx["backtest"]), default=None)
    bt_rows = "".join(
        f'<tr class="{"best" if best is not None and float(r["total"]) == best else ""}"><td>{escape(r["escenario"])}'
        f'{"<span class=tag>mejor total</span>" if best is not None and float(r["total"]) == best else ""}</td>'
        f'<td>{pct(float(r["anual"]))}</td><td class="neg">{pct(float(r["max_caida"]))}</td>'
        f'<td class="{cls(float(r["total"]))}">{pct(float(r["total"]))}</td></tr>'
        for r in ctx["backtest"]) or '<tr><td colspan="4" class="muted">Sin resultados del backtest todavía.</td></tr>'
    no_picks = '<p class="muted">Ninguna acción cumple el criterio hoy.</p>'
    picks = "".join(pick_card(p) for p in ctx["picks"]) or no_picks
    minis = "".join(mini_pick(p) for p in ctx["picks"][:6]) or no_picks
    heat = "".join(heat_cell(t, f) for t, f in ctx["grid"])
    dialogs = "".join(dialog(t, f) for t, f in ctx["grid"])
    titulos = {k: v for k, v, _ in SECTIONS}
    tape = ""  # la cinta se rellena con precios.json al cargar
    body = f"""
<header class="top">
  <div><h1 id="titulo">Inicio</h1><p>Paper trading · informe del {ctx["today"]}</p></div>
  <div class="pills">{status_pill(ctx["status"])}<span class="pill">Precios <b id="pxts">cargando…</b></span></div>
</header>
<div class="tapewrap"><div class="tape" id="tape">{tape}<span class="it">Cargando precios…</span></div></div>

{inicio(ctx)}

<section class="view" id="resumen">
  {featured(ctx["picks"][0] if ctx["picks"] else None)}
  <div class="card glow hero-card" data-reveal>
    {gauge(ctx["sim_ret"], "Simulación desde " + ctx["start"])}
    <div class="txt"><span class="label">Rentabilidad de la simulación</span>
      <h2 style="font-size:22px;margin:6px 0 0">{pct(ctx["sim_ret"])} frente a {pct(ctx["bench_ret"])} de VWCE</h2>
      <p>Cesto de 42 acciones y bitcoin con filtro de caída. Comparado con el ETF global VWCE desde el mismo día.</p></div>
  </div>
  <div class="kpis">
    {kpi("Simulación", pct(ctx["sim_ret"]), cls(ctx["sim_ret"]), ctx["sim_ret"] * 100, "%", "chart")}
    {kpi("Benchmark VWCE", pct(ctx["bench_ret"]), cls(ctx["bench_ret"]), ctx["bench_ret"] * 100, "%", "target")}
    {kpi("Posiciones abiertas", len(ctx["positions"]), "", len(ctx["positions"]), "", "wallet")}
    {kpi("Pronósticos hoy", len(ctx["picks"]), "", len(ctx["picks"]), "", "signal")}
  </div>
  <div class="grid2">
    <div class="card glow" data-reveal><h2>{icon("chart")}Evolución de la simulación</h2>{spark(eq_vals, 240, "big")}{axis}</div>
    <div class="card glow" data-reveal><h2>{icon("target")}Pronósticos de hoy</h2><div class="mini-list">{minis}</div></div>
  </div>
</section>

<section class="view" id="pronosticos">
  <div class="card" data-reveal style="margin-bottom:14px"><h2>{icon("target")}Pronósticos de hoy</h2>
  <p class="muted" style="margin:0;font-size:13.5px">Acciones con al menos 2 de 3 señales: tendencia, momentum y valor. Informativo: el bot no compra por esta lista.</p></div>
  <div class="picks">{picks}</div>
</section>

<section class="view" id="cartera">
  <div class="card glow" data-reveal><h2>{icon("wallet")}Cartera</h2>{positions}</div>
</section>

<section class="view" id="senales">
  <div class="card" data-reveal><h2>{icon("signal")}Señales por activo</h2><div class="heat">{heat}</div>
  <p class="muted" style="font-size:13px;margin:14px 0 0">Las tres señales de cada acción, solo informativas. El bot opera con el cesto y sale de una acción si cae más de un 20 % desde su máximo anual. Pulsa una acción para ver su ficha.</p></div>
</section>

<section class="view" id="actividad">
  <div class="card glow" data-reveal><h2>{icon("activity")}Actividad reciente</h2><div class="tl">{trades}</div></div>
</section>

<section class="view" id="evaluacion">
  <div class="card glow" data-reveal style="margin-bottom:16px"><h2>{icon("flask")}Evaluación de pronósticos</h2>
  <p style="margin:0">{escape(ctx["eval_txt"])}</p>
  <p class="muted" style="font-size:13px;margin:10px 0 0">Exceso = rentabilidad de cada acción menos la del VWCE desde su fecha, descontando un 0,2 % de costes.</p></div>
  <div class="card" data-reveal><h2>{icon("chart")}Backtest: estrategias frente a comprar y mantener</h2>
  <table class="board"><thead><tr><th>Escenario</th><th>Anual</th><th>Caída máx.</th><th>Total</th></tr></thead>
  <tbody>{bt_rows}</tbody></table>
  <p class="muted" style="font-size:13px;margin:14px 0 0">Desde marzo de 2019, mismo cesto de 42 acciones frente a VWCE. El bot actual vende cada acción tras caer más de un 20 % desde su máximo anual. No incluye la infravaloración, que no se puede backtestear con datos gratuitos. El cesto son las acciones de hoy, así que los escenarios que las mantienen salen favorecidos.</p></div>
</section>

{dialogs}"""
    return page("Aldana Trading", body, ctx["today"], side_nav())


def inicio(ctx) -> str:
    """Vista de inicio: presentación y acceso a cada sección."""
    cards = [
        ("resumen", "Resumen", "grid", "Rentabilidad, cartera y comparativa frente a VWCE.", f"{pct(ctx['sim_ret'])} desde {ctx['start']}"),
        ("pronosticos", "Pronósticos", "target", "Acciones con al menos 2 de 3 señales. Informativo.", f"{len(ctx['picks'])} hoy"),
        ("cartera", "Cartera", "wallet", "Posiciones abiertas y su rentabilidad.", "Ver posiciones"),
        ("senales", "Señales", "signal", "Mapa de las 42 acciones y bitcoin.", "Mapa completo"),
        ("actividad", "Actividad", "activity", "Últimas compras y ventas del bot.", "Línea de tiempo"),
        ("evaluacion", "Evaluación", "flask", "Resultados de los pronósticos y backtest.", "Frente a VWCE"),
    ]
    nav = "".join(f"""<button class="nc" data-go="{k}" data-reveal>
  <span class="ico">{icon(ic)}</span><h3>{title}</h3><p>{desc_}</p><span class="tag">{tag}</span>
  <span style="position:absolute;right:20px;bottom:20px;color:var(--mut)">{icon("arrow")}</span></button>""" for k, title, ic, desc_, tag in cards)
    steps = [("01", "Cesto", "Mantiene las 42 acciones y bitcoin, con el mismo importe cada una."),
             ("02", "Filtro de caída", "Si una acción cae más de un 20 % desde su máximo anual, se vende y vuelve a entrar al recuperarse."),
             ("03", "Informe", "Cada día, la simulación frente a VWCE, y un aviso en Telegram por cada movimiento.")]
    step_html = "".join(f'<div class="step" data-reveal><span class="n">{n}</span><h3>{t}</h3><p>{d}</p></div>' for n, t, d in steps)
    return f"""<section class="view" id="inicio">
<section class="hero">
  <span class="blob b1"></span><span class="blob b2"></span>
  <div>
    <span class="label">Cesto con filtro de caídas</span>
    <h1 style="margin-top:12px"><span class="grad">Aldana Trading</span><br>con filtro de caídas</h1>
    <p>Simulación sobre 42 acciones y bitcoin. Un filtro vende lo que cae más de un 20 % desde su máximo anual, y todo se compara con el ETF global VWCE.</p>
    <div class="cta">
      <a class="btn main" href="#resumen">Abrir el panel {icon("arrow")}</a>
      <a class="btn" href="#evaluacion">Ver el backtest {icon("arrow")}</a>
    </div>
  </div>
  <div class="hero-gauge">{gauge(ctx["sim_ret"], "Desde " + ctx["start"])}</div>
</section>
<div class="label sec-title">Acceso</div>
<div class="nav-cards">{nav}</div>
<div class="label sec-title">Cómo funciona</div>
<div class="steps">{step_html}</div>
</section>
"""
