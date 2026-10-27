"""Páginas del bot para GitHub Pages: portada (index.html) y panel (panel.html). Sin dependencias: HTML, CSS y JS a mano."""
from html import escape
from urllib.parse import urlparse

NAMES = ["Tendencia", "Momentum", "Valor"]
TABS = [("resumen", "Resumen", "grid"), ("pronosticos", "Pronósticos", "target"), ("cartera", "Cartera", "wallet"),
        ("senales", "Señales", "signal"), ("actividad", "Actividad", "activity"), ("evaluacion", "Evaluación", "flask")]
SECTOR_ES = {"Technology": "Tecnología", "Financial Services": "Financiero", "Healthcare": "Salud",
             "Consumer Defensive": "Consumo básico", "Consumer Cyclical": "Consumo discrecional",
             "Energy": "Energía", "Communication Services": "Comunicación", "Industrials": "Industria",
             "Utilities": "Suministros", "Real Estate": "Inmobiliario", "Basic Materials": "Materiales"}
SECTOR_ICON = {"Technology": "cpu", "Financial Services": "landmark", "Healthcare": "heart",
               "Consumer Defensive": "bag", "Consumer Cyclical": "bag", "Energy": "zap",
               "Communication Services": "radio", "Industrials": "factory", "Utilities": "bulb",
               "Real Estate": "building", "Basic Materials": "box"}

# Iconos vectoriales propios (trazo de 1,8 px, estilo lineal)
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
    "dot": '<circle cx="12" cy="12" r="3"/>',
}

CSS = """
:root{--bg:#05080f;--card:rgba(18,26,42,.62);--line:rgba(148,163,184,.14);--txt:#e8eef7;--muted:#8b98ab;
--pos:#34d399;--neg:#fb7185;--warn:#fbbf24;--a1:#7dd3fc;--a2:#a78bfa;--acc:#7dd3fc}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--bg:#f4f6fb;--card:rgba(255,255,255,.8);--line:rgba(15,23,42,.1);
--txt:#0f172a;--muted:#5b6778;--pos:#059669;--neg:#e11d48;--warn:#b45309;--acc:#2563eb;--a1:#2563eb;--a2:#7c3aed}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;color:var(--txt);background:var(--bg);font:15px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;overflow-x:hidden;
background-image:radial-gradient(1100px 620px at 8% -12%,rgba(125,211,252,.14),transparent 60%),radial-gradient(900px 520px at 100% 4%,rgba(167,139,250,.13),transparent 60%);background-attachment:fixed}
a{color:inherit;text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:22px 26px 40px}
.mono,.px,.kpi strong,.big-px,.tape{font-family:"JetBrains Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}
.grad{background:linear-gradient(90deg,var(--a1),var(--a2),var(--a1));background-size:200% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 7s linear infinite}
@keyframes shine{to{background-position:200% center}}
@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes flash{0%{background:rgba(125,211,252,.35)}100%{background:transparent}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(52,211,153,.6)}70%{box-shadow:0 0 0 8px rgba(52,211,153,0)}100%{box-shadow:0 0 0 0 rgba(52,211,153,0)}}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(30px,-20px)}}
@keyframes tape{to{transform:translateX(-50%)}}
/* cabecera */
.top{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px 16px;margin-bottom:20px;animation:in .5s ease both}
.brand{display:flex;align-items:center;gap:12px}
.brand b{display:block;font-size:1.15rem;letter-spacing:-.01em}
.brand small{color:var(--muted);font-size:.8rem}
.mark{width:38px;height:38px;flex:none;filter:drop-shadow(0 4px 14px rgba(125,211,252,.25))}
.pills{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.pill{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;border:1px solid var(--line);font-size:.82rem;background:var(--card);backdrop-filter:blur(8px)}
.pill.ok{border-color:rgba(52,211,153,.5);color:var(--pos)} .pill.off{border-color:rgba(251,191,36,.5);color:var(--warn)}
.pill i{width:8px;height:8px;border-radius:50%;background:var(--pos);animation:pulse 1.8s infinite}
.pill.off i{background:var(--warn);animation:none}
.back{font-size:.85rem;color:var(--muted);border:1px solid var(--line);padding:6px 12px;border-radius:999px;transition:color .2s,border-color .2s,transform .2s}
.back:hover{color:var(--txt);border-color:var(--a1);transform:translateX(-2px)}
/* pestañas deslizantes */
.tabs{position:relative;display:flex;gap:2px;overflow-x:auto;padding:4px;margin:0 0 22px;border-radius:999px;background:var(--card);border:1px solid var(--line);scrollbar-width:none;animation:in .5s .05s ease both}
.tabs::-webkit-scrollbar{display:none}
.tabs button{position:relative;z-index:1;display:flex;align-items:center;gap:8px;border:0;background:none;color:var(--muted);padding:9px 16px;border-radius:999px;font:600 .9rem Inter,system-ui,sans-serif;cursor:pointer;white-space:nowrap;transition:color .25s,transform .15s}
.tabs button:hover{color:var(--txt)} .tabs button:active{transform:scale(.96)} .tabs button.on{color:var(--txt)}
.ind{position:absolute;top:4px;bottom:4px;left:4px;width:0;border-radius:999px;background:linear-gradient(135deg,rgba(125,211,252,.22),rgba(167,139,250,.22));border:1px solid rgba(125,211,252,.35);transition:left .45s cubic-bezier(.2,.8,.2,1),width .45s cubic-bezier(.2,.8,.2,1)}
.tab{display:none} .tab.on{display:block;animation:in .45s cubic-bezier(.2,.8,.2,1) both}
.stg{animation:in .5s cubic-bezier(.2,.8,.2,1) backwards;animation-delay:calc(var(--i,0)*45ms)}
.ic{width:18px;height:18px;flex:none}
/* tarjetas */
.kpi,.panel,.dlg,.card{background:var(--card);border:1px solid var(--line);border-radius:18px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:transform .3s cubic-bezier(.2,.8,.2,1),box-shadow .3s ease,border-color .3s}
.glow{position:relative;overflow:hidden}
.glow::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .35s;background:radial-gradient(280px circle at var(--mx,50%) var(--my,50%),rgba(125,211,252,.16),transparent 60%)}
.glow:hover::before{opacity:1}
.kpi{padding:18px} .kpi:hover,.panel:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(0,0,0,.28);border-color:rgba(125,211,252,.3)}
.panel{padding:20px}
.kh{display:flex;align-items:center;gap:10px;color:var(--muted);font-size:.84rem}
.kico{display:grid;place-items:center;width:30px;height:30px;border-radius:10px;background:linear-gradient(135deg,rgba(125,211,252,.2),rgba(167,139,250,.2));color:var(--acc)}
.kpi strong{display:block;font-size:1.9rem;margin-top:8px;letter-spacing:-.02em}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px}
.grid{display:grid;grid-template-columns:2fr 1fr;gap:16px}
h2{margin:0 0 14px;font-size:1rem;font-weight:700;display:flex;align-items:center;gap:8px}
h2 .ic{color:var(--acc)}
.chart{width:100%;display:block;overflow:visible}
.chart .draw{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.4s ease-out forwards}
.chart .fill{opacity:0;animation:fade 1s .4s forwards}
.axis{display:flex;justify-content:space-between;color:var(--muted);font-size:.78rem;margin-top:8px}
.empty,.muted{color:var(--muted)} .empty{padding:40px 0;text-align:center}
.pos{color:var(--pos)} .neg{color:var(--neg)}
.px{font-weight:600;margin-left:6px;font-size:.85rem;color:var(--muted);border-radius:6px;padding:0 4px}
.px.pos{color:var(--pos)} .px.neg{color:var(--neg)}
.tick{animation:flash 1s ease-out}
.row{display:grid;grid-template-columns:1.4fr 1fr .8fr;gap:8px;padding:10px 0;border-bottom:1px solid var(--line);font-size:.92rem;align-items:center;transition:background .2s,padding .2s}
.row:hover{background:rgba(125,211,252,.05);padding-left:8px;padding-right:8px;border-radius:10px}
.row:last-child{border:0} .row span:last-child{text-align:right}
.bt{grid-template-columns:2fr 1.2fr 1fr 1fr} .bt span+span{text-align:right} .bt.head{color:var(--muted);font-size:.8rem;border-bottom:1px solid var(--line)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:8px;background:var(--muted)}
.dot.c{background:var(--pos)} .dot.v{background:var(--neg)}
/* logos y sectores */
.logo{position:relative;width:54px;height:54px;flex:none;border-radius:15px;display:grid;place-items:center;overflow:hidden;color:#fff;background:linear-gradient(135deg,hsl(var(--h) 85% 62%),hsl(calc(var(--h) + 48) 80% 42%));box-shadow:inset 0 1px 0 rgba(255,255,255,.3),0 6px 16px rgba(0,0,0,.25)}
.logo span{font:800 .8rem "JetBrains Mono",ui-monospace,monospace;letter-spacing:-.02em;text-shadow:0 1px 2px rgba(0,0,0,.3)}
.logo img{position:absolute;inset:0;width:100%;height:100%;background:#fff;object-fit:contain;padding:9px;opacity:0;transition:opacity .5s}
.logo img.ok{opacity:1}
.logo.sm{width:36px;height:36px;border-radius:11px} .logo.sm span{font-size:.62rem}
.logo.lg{width:68px;height:68px;border-radius:19px} .logo.lg span{font-size:1rem}
.sec{display:inline-flex;align-items:center;gap:6px;font-size:.78rem;color:var(--muted);margin-top:2px}
.sec-ic{display:grid;place-items:center;width:22px;height:22px;border-radius:7px;background:rgba(125,211,252,.12);color:var(--acc)}
.sec-ic .ic{width:14px;height:14px}
.glyph{font:700 .85rem "JetBrains Mono",monospace;color:#f7931a;background:rgba(247,147,26,.14)}
.pick{display:flex;gap:16px;align-items:center;padding:16px;border-radius:16px;border:1px solid transparent;cursor:pointer;margin-bottom:6px}
.pick:hover{border-color:var(--line);background:rgba(125,211,252,.05);transform:translateX(4px)}
.pick .go{margin-left:auto;color:var(--muted);transition:transform .3s,color .3s}
.pick:hover .go{transform:translateX(4px);color:var(--acc)}
.pb{min-width:0;flex:1}
.ttl{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline}
.tk{font:600 .78rem "JetBrains Mono",monospace;color:var(--acc);background:rgba(125,211,252,.1);padding:1px 7px;border-radius:6px}
.pick p{margin:6px 0;font-size:.9rem;color:var(--txt);opacity:.85;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.meta{color:var(--muted);font-size:.84rem}
.mini{display:flex;gap:12px;align-items:center;padding:10px;border-radius:14px;transition:background .2s,transform .2s}
.mini:hover{background:rgba(125,211,252,.06);transform:translateX(3px)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font-size:.72rem;padding:3px 9px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
.chip.on{border-color:rgba(52,211,153,.5);color:var(--pos);background:rgba(52,211,153,.08)}
/* señales */
.heat{display:grid;grid-template-columns:repeat(auto-fill,minmax(128px,1fr));gap:10px}
.cell{border-radius:14px;padding:12px;font-size:.8rem;display:flex;flex-direction:column;gap:3px;cursor:pointer;border:1px solid var(--line);transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s}
.cell:hover{transform:translateY(-3px) scale(1.02);box-shadow:0 10px 24px rgba(0,0,0,.3)}
.cell b{font:700 .92rem "JetBrains Mono",monospace} .cell span{opacity:.8} .cell em{font-style:normal}
.v0{background:rgba(148,163,184,.08);color:var(--muted)} .v1{background:rgba(52,211,153,.12);color:#86efac}
.v2{background:linear-gradient(135deg,rgba(52,211,153,.35),rgba(52,211,153,.18));color:#ecfdf5} .v3{background:linear-gradient(135deg,#34d399,#10b981);color:#022c22;box-shadow:0 0 22px rgba(52,211,153,.35)}
.legend{font-size:.82rem;margin-top:14px}
/* fichas */
.dlg{width:min(580px,92vw);color:var(--txt);padding:22px;margin:auto}
.dlg[open]{animation:pop .3s cubic-bezier(.2,.8,.2,1) both}
.dlg::backdrop{background:rgba(2,6,14,.7);backdrop-filter:blur(4px);animation:fade .3s ease both}
.dh{display:flex;gap:14px;align-items:center}.dh>div{flex:1;min-width:0}
.x{background:none;border:0;color:var(--muted);font-size:1.2rem;cursor:pointer;padding:6px;border-radius:10px;transition:background .2s,color .2s}
.x:hover{background:rgba(125,211,252,.1);color:var(--txt)}
.big-px{font-size:2rem;font-weight:700;margin:16px 0 4px;letter-spacing:-.02em}.big-px .px{font-size:1.05rem}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}
.stats div{background:rgba(125,211,252,.05);border:1px solid var(--line);border-radius:14px;padding:12px}
.stats span{display:block;color:var(--muted);font-size:.72rem} .stats b{font:600 1rem "JetBrains Mono",monospace}
footer{margin-top:28px;color:var(--muted);font-size:.8rem;text-align:center}
/* portada */
.hero{position:relative;overflow:hidden;border-radius:26px;padding:56px 40px;border:1px solid var(--line);background:var(--card);animation:in .7s ease both}
.blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.4;pointer-events:none;animation:float 14s ease-in-out infinite}
.blob.b1{width:340px;height:340px;background:#7dd3fc;top:-120px;left:-80px}
.blob.b2{width:300px;height:300px;background:#a78bfa;bottom:-130px;right:-60px;animation-duration:17s}
.hero h1{position:relative;margin:0;font-size:clamp(2.2rem,5.5vw,3.8rem);line-height:1.05;letter-spacing:-.03em}
.hero p{position:relative;max-width:620px;color:var(--muted);font-size:1.05rem;margin:16px 0 26px}
.cta{position:relative;display:flex;flex-wrap:wrap;gap:12px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:999px;font-weight:700;font-size:.95rem;transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s}
.btn.main{background:linear-gradient(135deg,var(--a1),var(--a2));color:#06101c;box-shadow:0 10px 30px rgba(125,211,252,.25)}
.btn.alt{border:1px solid var(--line);background:var(--card)}
.btn:hover{transform:translateY(-2px)} .btn.main:hover{box-shadow:0 16px 40px rgba(125,211,252,.35)}
.btn .ic{transition:transform .25s}.btn:hover .ic{transform:translateX(3px)}
.tapewrap{margin:18px 0 26px;overflow:hidden;border-radius:14px;border:1px solid var(--line);background:var(--card);mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
.tape{display:flex;width:max-content;animation:tape 40s linear infinite;padding:12px 0}
.tape .it{display:inline-flex;gap:8px;align-items:center;padding:0 22px;font-size:.85rem;border-right:1px solid var(--line)}
.tape b{color:var(--acc)} .tape em{font-style:normal;font-size:.78rem}
.nav-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px}
.nc{display:block;padding:22px;border-radius:20px;border:1px solid var(--line);background:var(--card);backdrop-filter:blur(10px);transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .3s,box-shadow .35s;position:relative;overflow:hidden}
.nc:hover{transform:translateY(-6px);border-color:rgba(125,211,252,.45);box-shadow:0 20px 44px rgba(0,0,0,.3)}
.nc .ico{display:grid;place-items:center;width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,rgba(125,211,252,.22),rgba(167,139,250,.22));color:var(--acc);margin-bottom:16px;transition:transform .35s}
.nc:hover .ico{transform:rotate(-6deg) scale(1.06)}
.nc .ico .ic{width:24px;height:24px}
.nc h3{margin:0 0 6px;font-size:1.1rem} .nc p{margin:0 0 14px;color:var(--muted);font-size:.9rem}
.nc .tag{font:600 .8rem "JetBrains Mono",monospace;color:var(--acc)}
.nc .arr{position:absolute;right:20px;bottom:20px;color:var(--muted);transition:transform .3s,color .3s}
.nc:hover .arr{transform:translateX(5px);color:var(--acc)}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:16px}
.step{padding:20px;border-radius:18px;border:1px solid var(--line);background:var(--card)}
.step .n{font:700 .8rem "JetBrains Mono",monospace;color:var(--acc)}
.step h3{margin:8px 0 6px;font-size:1rem} .step p{margin:0;color:var(--muted);font-size:.9rem}
.sec-title{font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:34px 0 14px;font-weight:700}
[data-reveal]{opacity:0;transform:translateY(22px);transition:opacity .7s ease,transform .7s cubic-bezier(.2,.8,.2,1)}
[data-reveal].in{opacity:1;transform:none}
:focus-visible{outline:2px solid var(--a1);outline-offset:3px;border-radius:12px}
@media (max-width:1000px){.grid{grid-template-columns:1fr}.kpis,.nav-cards{grid-template-columns:repeat(2,1fr)}.steps{grid-template-columns:1fr}}
@media (max-width:560px){.wrap{padding:16px}.kpis,.nav-cards{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.kpi strong{font-size:1.5rem}.hero{padding:36px 22px}.row{grid-template-columns:1.3fr 1fr .8fr;font-size:.85rem}}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation:none!important;transition:none!important}[data-reveal]{opacity:1;transform:none}}
"""

JS = """
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
function moveInd(){const b=$('.tabs button.on'),ind=$('.ind');if(!b||!ind)return;ind.style.left=b.offsetLeft+'px';ind.style.width=b.offsetWidth+'px';}
function show(id){
  if(!$('#'+id)||!$('#'+id).classList.contains('tab')) id='resumen';
  $$('.tab').forEach(s=>s.classList.toggle('on',s.id===id));
  $$('.tabs button').forEach(b=>b.classList.toggle('on',b.dataset.t===id));
  $$('.tab.on .stg').forEach((el,i)=>el.style.setProperty('--i',i%16));
  moveInd(); history.replaceState(null,'','#'+id);
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
async function precios(){
  try{
    const j=await (await fetch('prices.json?'+Date.now())).json();
    $$('[data-p]').forEach(e=>{
      const d=j.p[e.dataset.p]; if(!d) return;
      const txt=d.p.toFixed(2)+' '+(d.v>=0?'▲ +':'▼ ')+d.v.toFixed(2)+'%';
      if(e.textContent!==txt&&e.textContent){e.classList.remove('tick');void e.offsetWidth;e.classList.add('tick');}
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
document.querySelectorAll('.logo img').forEach(img=>{if(img.complete&&img.naturalWidth>0)img.classList.add('ok');else img.addEventListener('load',()=>img.classList.add('ok'));});
if($('.tabs')){
  $$('.tabs button').forEach(b=>b.onclick=()=>show(b.dataset.t));
  show(location.hash.slice(1)||'resumen');
  addEventListener('resize',moveInd);
}
if('IntersectionObserver' in window&&!reduce){
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{threshold:.12});
  $$('[data-reveal]').forEach(el=>io.observe(el));
} else $$('[data-reveal]').forEach(el=>el.classList.add('in'));
countUp(); ago(); precios();
setInterval(precios,60000); setInterval(ago,60000);
"""

BRAND_MARK = ('<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="gm" x1="0" y1="0" x2="1" y2="1">'
              '<stop offset="0" stop-color="#7dd3fc"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>'
              '<rect x="2" y="2" width="36" height="36" rx="11" fill="url(#gm)" opacity=".18"/>'
              '<path d="M9 27V19M16 27V13M23 27V17M30 27V9" stroke="url(#gm)" stroke-width="3" stroke-linecap="round"/></svg>')


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(name, ICONS["dot"])}</svg>')


def logo(t, info, size=""):
    # Monograma con color propio por ticker; el favicon de la empresa aparece encima si carga
    h = sum(map(ord, t)) * 37 % 360
    dom = urlparse(info.get("web") or "").netloc.replace("www.", "")
    img = (f'<img src="https://www.google.com/s2/favicons?domain={escape(dom)}&amp;sz=128" alt="" '
           f'loading="lazy" onerror="this.remove()">') if dom else ""
    return (f'<div class="logo {size}" style="--h:{h}"><span>{escape(t.split("-")[0][:5])}</span>{img}</div>')


def sector_mark(t, info):
    if t.endswith("-USD"):
        return '<span class="sec-ic glyph">₿</span>'
    return f'<span class="sec-ic">{icon(SECTOR_ICON.get(info.get("sector"), "dot"))}</span>'


def meta(c):
    s = SECTOR_ES.get(c.get("sector"), c.get("sector")) or "Sin sector"
    return escape(s) + (f" · {escape(c['industry'])}" if c.get("industry") else "")


def desc(info):
    return escape(info.get("summary") or f"Sin descripción disponible en Yahoo Finance. Sector: {info.get('sector') or 'n/d'}.")


def pct(x):
    return f"{x:+.1%}"


def cls(x):
    return "pos" if x >= 0 else "neg"


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
            f'<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7dd3fc" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="#7dd3fc" stop-opacity="0"/></linearGradient></defs>'
            f'<polygon points="{area}" fill="url(#sg)" class="fill"/>'
            f'<polyline points="{line}" pathLength="1" class="draw" fill="none" stroke="var(--acc)" stroke-width="3" '
            f'stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')


def open_js(t):
    return f"document.getElementById('d-{t}').showModal()"


def pick_card(p):
    c, t = p["info"], p["ticker"]
    chips = "".join(f'<span class="chip{" on" if on else ""}">{nm}</span>' for nm, on in zip(NAMES, p["flags"]))
    return (f'<article class="pick glow stg" role="button" tabindex="0" onclick="{open_js(t)}" '
            f'onkeydown="if(event.key===\'Enter\')this.click()">{logo(t, c)}<div class="pb">'
            f'<div class="ttl"><strong>{escape(c["name"])}</strong><span class="tk">{escape(t)}</span></div>'
            f'<div class="sec">{sector_mark(t, c)}{meta(c)}</div>'
            f'<div class="meta">{p["precio"]} USD <span class="px" data-p="{escape(t)}"></span></div>'
            f'<p>{desc(c)}</p><div class="chips">{chips}</div></div><span class="go">{icon("arrow")}</span></article>')


def mini_pick(p):
    return (f'<div class="mini stg">{logo(p["ticker"], p["info"], "sm")}<div><b>{escape(p["info"]["name"])}</b>'
            f'<div class="meta">{escape(p["ticker"])} · {p["votos"]}/3 señales '
            f'<span class="px" data-p="{escape(p["ticker"])}"></span></div></div></div>')


def heat_cell(t, f):
    return (f'<div class="cell v{f["n"]} stg" role="button" tabindex="0" onclick="{open_js(t)}"><b>{escape(t)}</b>'
            f'<span>{f["n"]}/3 señales</span><em class="px" data-p="{escape(t)}"></em></div>')


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
    return (f'<div class="kpi glow stg"><div class="kh"><span class="kico">{icon(ic)}</span><span>{label}</span></div>'
            f'<strong class="{c}"{data}>{value}</strong></div>')


def status_pill(st):
    if st is None:
        return '<span class="pill off"><i></i>Sin datos del bot todavía</span>'
    if st.get("parado"):
        return '<span class="pill off"><i></i>Bot parado (KILL_SWITCH)</span>'
    mercado = "Bolsa EE. UU. abierta" if st["mercado_abierto"] else "Bolsa EE. UU. cerrada (solo cripto)"
    return (f'<span class="pill ok"><i></i>Bot activo · último ciclo <b class="ago" data-ts="{st["ts"]}">{st["ts"]}</b></span>'
            f'<span class="pill">{mercado}</span>')


def page(title, body, today):
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<meta name="description" content="Bot de trading en paper trading: cesto de acciones con filtro de caída, pronósticos y backtest frente a VWCE. Actualizado {today}.">
<style>{CSS}</style></head>
<body><div class="wrap">
{body}
<footer>Simulación con dinero ficticio, no asesoramiento financiero. Datos de Yahoo Finance y Alpaca, con retraso de hasta 15 minutos. Actualizado el {today}.</footer>
</div>
<script>{JS}</script>
</body></html>
"""


def render(ctx) -> str:
    """Panel: pestañas con los datos del informe."""
    eq = ctx["equity"]
    eq_vals = [v for _, v in eq]
    axis = (f'<div class="axis"><span>{eq[0][0]} · {eq[0][1]:,.0f} USD</span>'
            f'<span>{eq[-1][0]} · {eq[-1][1]:,.0f} USD</span></div>') if eq else ""
    positions = "".join(
        f'<div class="row stg"><b>{escape(p["symbol"])} <span class="px" data-p="{escape(p["ticker"])}"></span></b>'
        f'<span>{p["value"]:,.0f} USD</span><span class="{cls(p["pl"])}">{pct(p["pl"])}</span></div>'
        for p in ctx["positions"]) or '<p class="muted">Sin posiciones abiertas.</p>'
    trades = "".join(
        f'<div class="row stg"><span class="muted">{escape(r["fecha"][:16].replace("T", " "))}</span>'
        f'<b><i class="dot {"c" if r["accion"] == "COMPRA" else "v"}"></i>{escape(r["simbolo"])}</b>'
        f'<span class="{"pos" if r["accion"] == "COMPRA" else "neg"}">{escape(r["accion"])}</span></div>'
        for r in ctx["trades"]) or '<p class="muted">Todavía no ha habido operaciones.</p>'
    bt = "".join(
        f'<div class="row bt stg"><b>{escape(r["escenario"])}</b><span>{pct(float(r["anual"]))} al año</span>'
        f'<span class="neg">{pct(float(r["max_caida"]))}</span><span class="{cls(float(r["total"]))}">{pct(float(r["total"]))}</span></div>'
        for r in ctx["backtest"]) or '<p class="muted">Sin resultados del backtest todavía.</p>'
    no_picks = '<p class="muted">Ninguna acción cumple el criterio hoy.</p>'
    picks = "".join(pick_card(p) for p in ctx["picks"]) or no_picks
    minis = "".join(mini_pick(p) for p in ctx["picks"][:6]) or no_picks
    heat = "".join(heat_cell(t, f) for t, f in ctx["grid"])
    dialogs = "".join(dialog(t, f) for t, f in ctx["grid"])
    nav = "".join(f'<button data-t="{k}">{icon(ic)}<span>{v}</span></button>' for k, v, ic in TABS)
    body = f"""
<header class="top">
  <a class="brand" href="index.html">{BRAND_MARK}<div><b>Bot de trading</b><small>Paper trading · informe del {ctx["today"]}</small></div></a>
  <div class="pills">{status_pill(ctx["status"])}<span class="pill">Precios <b id="pxts">cargando…</b></span>
  <a class="back" href="index.html">← Inicio</a></div>
</header>
<nav class="tabs"><span class="ind"></span>{nav}</nav>

<section class="tab" id="resumen">
  <div class="kpis">
    {kpi("Simulación desde " + ctx["start"], pct(ctx["sim_ret"]), cls(ctx["sim_ret"]), ctx["sim_ret"] * 100, "%", "chart")}
    {kpi("Benchmark VWCE", pct(ctx["bench_ret"]), cls(ctx["bench_ret"]), ctx["bench_ret"] * 100, "%", "target")}
    {kpi("Posiciones abiertas", len(ctx["positions"]), "", len(ctx["positions"]), "", "wallet")}
    {kpi("Pronósticos hoy", len(ctx["picks"]), "", len(ctx["picks"]), "", "signal")}
  </div>
  <div class="grid">
    <div class="panel glow"><h2>{icon("chart")}Evolución de la simulación</h2>{spark(eq_vals, 240, "big")}{axis}</div>
    <div class="panel glow"><h2>{icon("target")}Pronósticos de hoy</h2>{minis}</div>
  </div>
</section>

<section class="tab" id="pronosticos"><div class="panel"><h2>{icon("target")}Pronósticos de hoy</h2>
  <p class="muted legend">Acciones con al menos 2 de 3 señales. Informativo: el bot no compra por esta lista.</p>{picks}</div></section>
<section class="tab" id="cartera"><div class="panel"><h2>{icon("wallet")}Cartera</h2>{positions}</div></section>
<section class="tab" id="senales"><div class="panel"><h2>{icon("signal")}Señales por activo</h2><div class="heat">{heat}</div>
  <p class="legend muted">Número de señales a favor (de 3), solo informativo. El bot opera con el cesto y sale de una acción si cae más de un 20 % desde su máximo anual. Pulsa una acción para ver su ficha.</p></div></section>
<section class="tab" id="actividad"><div class="panel"><h2>{icon("activity")}Actividad reciente</h2>{trades}</div></section>
<section class="tab" id="evaluacion">
  <div class="panel"><h2>{icon("flask")}Evaluación de pronósticos</h2>
  <p>{escape(ctx["eval_txt"])}</p>
  <p class="muted legend">Exceso = rentabilidad de cada acción menos la del VWCE desde su fecha, descontando un 0,2 % de costes.</p></div>
  <div class="panel" style="margin-top:16px"><h2>{icon("chart")}Backtest: estrategias frente a comprar y mantener</h2>
  <div class="row bt head"><span>Escenario</span><span>Anual</span><span>Caída máx.</span><span>Total</span></div>{bt}
  <p class="muted legend">Desde marzo de 2019, mismo cesto de 42 acciones frente a VWCE. El bot actual vende cada acción tras caer más de un 20 % desde su máximo anual. No incluye la infravaloración, que no se puede backtestear con datos gratuitos. El cesto son las acciones de hoy, así que los escenarios que las mantienen salen favorecidos.</p></div>
</section>

{dialogs}"""
    return page("Panel · Bot de trading", body, ctx["today"])


def landing(ctx) -> str:
    """Portada: acceso a todas las secciones del panel."""
    cards = [
        ("resumen", "Resumen", "grid", "Rentabilidad, cartera y comparativa frente a VWCE.", f"{pct(ctx['sim_ret'])} desde {ctx['start']}"),
        ("pronosticos", "Pronósticos", "target", "Acciones con al menos 2 de 3 señales. Informativo.", f"{len(ctx['picks'])} hoy"),
        ("cartera", "Cartera", "wallet", "Posiciones abiertas y su rentabilidad.", "Ver posiciones"),
        ("senales", "Señales", "signal", "Mapa de las 42 acciones y bitcoin.", "Mapa completo"),
        ("actividad", "Actividad", "activity", "Últimas compras y ventas del bot.", "Últimas operaciones"),
        ("evaluacion", "Evaluación", "flask", "Resultados de los pronósticos y backtest.", "Frente a VWCE"),
    ]
    nav = "".join(f"""<a class="nc" href="panel.html#{k}" data-reveal>
  <span class="ico">{icon(ic)}</span><h3>{title}</h3><p>{desc_}</p><span class="tag">{tag}</span>
  <span class="arr">{icon("arrow")}</span></a>""" for k, title, ic, desc_, tag in cards)
    steps = [("01", "Cesto", "box", "El bot mantiene las 42 acciones y bitcoin, con el mismo importe cada una."),
             ("02", "Filtro de caída", "shield", "Si una acción cae más de un 20 % desde su máximo anual, se vende y vuelve a entrar al recuperarse."),
             ("03", "Informe", "clock", "Cada día, la simulación frente a VWCE, y un aviso en Telegram por cada movimiento.")]
    step_html = "".join(f'<div class="step" data-reveal><span class="n">{n}</span><h3>{t}</h3>'
                        f'<p>{d}</p></div>' for n, t, _, d in steps)
    body = f"""
<header class="top">
  <a class="brand" href="index.html">{BRAND_MARK}<div><b>Bot de trading</b><small>Paper trading · simulación</small></div></a>
  <div class="pills">{status_pill(ctx["status"])}</div>
</header>

<section class="hero">
  <span class="blob b1"></span><span class="blob b2"></span>
  <h1><span class="grad">Bot de trading</span><br>que aprende a no caer tanto</h1>
  <p>Simulación con dinero ficticio sobre 42 acciones y bitcoin. Un filtro vende lo que cae más de un 20 % desde su máximo, y todo se compara con el ETF global VWCE.</p>
  <div class="cta">
    <a class="btn main" href="panel.html">Abrir el panel {icon("arrow")}</a>
    <a class="btn alt" href="panel.html#evaluacion">Ver el backtest {icon("arrow")}</a>
  </div>
</section>

<div class="tapewrap" data-reveal><div class="tape" id="tape"><span class="it">Cargando precios…</span></div></div>

<div class="sec-title">Acceso</div>
<div class="nav-cards">{nav}</div>

<div class="sec-title">Cómo funciona</div>
<div class="steps">{step_html}</div>
"""
    return page("Bot de trading", body, ctx["today"])
