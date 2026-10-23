#!/usr/bin/env python3
"""Genera una línea de tiempo nueva con el mismo motor que la de Abraham.

El motor (HTML, CSS y JS de estudios/lineas/abraham.html) se toma tal cual, se ajustan los textos
y parámetros propios de cada línea (título, portada, años, atlas…) y se inyectan los datos de
estudios/lineas/<slug>/datos.py (objeto DATA y diccionario META). Así todas las líneas comparten la
misma interactividad y una mejora del motor se lleva a las demás volviendo a generar.

Uso: python3 scripts/lineas_generar.py moises
Después: python3 scripts/lineas_tikz.py moises   (mapas, portada y cronología en TikZ)
"""
import html, importlib.util, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LINEAS = RAIZ / "estudios" / "lineas"
SLUG = sys.argv[1]

spec = importlib.util.spec_from_file_location("datos", LINEAS / SLUG / "datos.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
DATA, META = mod.DATA, mod.META

src = (LINEAS / "abraham.html").read_text(encoding="utf-8")
m = re.search(r"const DATA = (\{.*?\});\nconst \{events", src, re.S)
DATA_ABR = json.loads(m.group(1))
motor = src[:m.start(1)] + "/*DATA*/" + src[m.end(1):]

def rep(viejo, nuevo, n=1):
    global motor
    k = motor.count(viejo)
    assert k == n, f"se esperaban {n} apariciones y hay {k}: {viejo[:90]!r}"
    motor = motor.replace(viejo, nuevo)

def rep_re(patron, nuevo, n=1, flags=re.S):
    global motor
    motor, k = re.subn(patron, nuevo, motor, flags=flags)
    assert k == n, f"se esperaban {n} reemplazos y hubo {k}: {patron[:90]!r}"

N = len(DATA["events"])
# DATA.geo: la geografía de los mapas SVG de respaldo es la misma (Natural Earth + geoBoundaries)
DATA.setdefault("geo", DATA_ABR["geo"])
DATA.setdefault("tones", DATA_ABR["tones"])

# ---------- cabecera ----------
rep_re(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(META["desc"])}">')
rep("<title>Abraham, el peregrino</title>", f"<title>{html.escape(META['titulo'])}</title>")
rep('url("abraham/fonts/', f'url("{SLUG}/fonts/', 10)

# ---------- tema visual propio (estudios/lineas/<slug>/tema.css) ----------
tema = LINEAS / SLUG / "tema.css"
if tema.exists():
    t = re.sub(r"/\*.*?\*/\s*", "", tema.read_text(encoding="utf-8").split("/*TEMA:ERAS*/")[0], flags=re.S).strip()
    eras = tema.read_text(encoding="utf-8").split("/*TEMA:ERAS*/")[1].strip()
    rep_re(r"\n:root\{.*?\n(?=html,body\{height:100%;margin:0\})", "\n" + t.replace("\\", "\\\\") + "\n")
    rep_re(r"\n\.c0\{[^\n]*\n(?:\.c[1-8][^\n]*\n)+", "\n" + eras + "\n")
    rep("const TEMAS=[['light','Papiro'],['dark','Noche'],['jerusalen','Piedra de Jerusalén']];",
        "const TEMAS=" + json.dumps(META["temas"], ensure_ascii=False) + ";")
    rep("letter-spacing:0;color:var(--olive)}", "letter-spacing:0;color:var(--accent)}")   # título de la portada
    rep(".hero .hw{font-family:var(--f-he);fill:var(--olive)}", ".hero .hw{font-family:var(--f-he);fill:var(--accent)}")
    rep("/* tres temas: Papiro (claro), Noche (oscuro) y Piedra de Jerusalén */", "/* tres temas: " + ", ".join(n for _, n in META["temas"]) + " */")

# ---------- versión sin JavaScript ----------
def plano(t):
    t = re.sub(r"\[\[[a-z]+:[^|\]]*\|([^\]]*)\]\]", r"\1", t or ""); return html.escape(t)
nojs = [f'<div class="nojs"><h1>{html.escape(META["titulo"])}</h1><p class="d">{html.escape(META["subtitulo"])}</p>',
        f'<p><i>{html.escape(META["epi_txt"])}</i> ({html.escape(META["epi_ref"])})</p>',
        '<p class="aviso"><b>Versión de lectura.</b> Este visor no ejecuta JavaScript, así que aquí se muestra el contenido en texto. '
        'Para la línea de tiempo interactiva (mapas, zoom y navegación), abre el archivo en Safari o Chrome, o usa el enlace publicado.</p>']
for i, e in enumerate(DATA["events"]):
    nojs.append(f'<p class="era">{html.escape(DATA["eranames"][str(e["era"])])}</p><h2>{i+1}. {html.escape(e["title"])}</h2><p class="d">{html.escape(e["date"])}</p><p>{plano(e["text"])}</p>')
    if e.get("det"): nojs.append(f'<div class="det">{plano(e["det"])}</div>')
    if e.get("com"): nojs.append("<ul>" + "".join(f"<li><b>{html.escape(w)}</b>: {plano(x)}</li>" for w, x in e["com"]) + "</ul>")
    md = e.get("media") or {}
    if md.get("tipo") == "escritura":
        r = DATA["refs"][md["ref"]]
        if r.get("he"):
            cls = "gr" if r.get("lang") == "el" else "he"
            nojs.append(f'<div class="{cls}">{html.escape(re.sub("‸[^‸]+‸", "", r["he"]))}</div>')
        nojs.append(f'<p><i>{html.escape(r["tr"])}</i></p>')
    if e.get("refs"): nojs.append('<p class="r">Referencias: ' + "; ".join(html.escape(DATA["refs"][k]["label"]) for k in e["refs"]) + "</p>")
fu = sorted((r["apa"] for r in DATA["refs"].values() if r.get("apa")), key=str.lower)
nojs.append("<h2>Fuentes</h2><ol>" + "".join(f"<li>{html.escape(a)}</li>" for a in fu) + "</ol></div></noscript>")
rep_re(r'<div class="nojs">.*?</noscript>', "".join(nojs).replace("\\", "\\\\"))

# ---------- cuerpo ----------
rep('aria-label="Línea de tiempo de la vida de Abraham"', f'aria-label="Línea de tiempo de {META["vida"]}"')
rep('aria-label="Atlas del camino de Abraham"', f'aria-label="{META["atlas_titulo"]}"')
rep('title="Atlas del camino de Abraham"', f'title="{META["atlas_titulo"]}"')
rep("<h2>De Ur a Macpela</h2>", f"<h2>{META['atlas_h2']}</h2>")
rep('aria-label="Minimapa: toda la vida de Abraham"', f'aria-label="Minimapa: toda {META["vida"]}"')
rep("> Altares</button>", f"> {META.get('filtro_altar', 'Altares')}</button>")

# ---------- JavaScript ----------
rep("'tl-abraham-hito'", f"'tl-{SLUG}-hito'", 2)
rep("'tl-abraham-theme'", f"'tl-{SLUG}-theme'", 2)
rep("const ATL_BASE='abraham/';", f"const ATL_BASE='{SLUG}/';")
rep(r"r.src.replace(/^abraham\//,'')", f"r.src.replace(/^{SLUG}\\//,'')")
# relieve: los niveles de detalle (todo lo que no sea «amplio») aparecen al acercar
rep("...(r.nivel==='levante'?{minzoom:5.6}:{})", "...(r.nivel!=='amplio'?{minzoom:5.6}:{})")
B = META["atlas_limites"]   # [[lon0,lat0],[lon1,lat1]]
rep("maxBounds:[[28.05,27.05],[50.95,39.95]]", f"maxBounds:{json.dumps(B)}")
rep("center:[38,33],zoom:5", f"center:{json.dumps(META['atlas_centro'])},zoom:5")
rep("ATL.ev={bbox:[29.4,37.6,30.8,47.2],viaje:1}", f"ATL.ev={{bbox:{json.dumps(META['atlas_bbox'])},viaje:1}}")
rep("en unos cien años de vida en camino.", META["tramos_total"])
rep("nota:'Ruta alternativa por el Éufrates, Carquemis, Alepo y el valle del Orontes.'", "nota:t.altnota||'Ruta alternativa.'")
rep("<p class=\"pp-cit\" style=\"padding:0 14px 12px\">— Curso «Explorando la Tierra Bíblica de Israel»</p>",
    "<p class=\"pp-cit\" style=\"padding:0 14px 12px\">— ${esc(r.fuente||'Curso «Explorando la Tierra Bíblica de Israel»')}</p>")
rep("${A?'Altar de Abraham':'Lugar'}", f"${{A?'{META['altar_rotulo']}':'Lugar'}}")
# rótulos de mapa propios de la línea (golfos, desiertos, pueblos) en los mapas SVG de respaldo
rep("const LAB_W=[", "const LAB_W=[...(DATA.labw||[]),")
# filtro «altares»: altares y santuario
rep("altar:e=>e.media&&(e.media.altars||[]).length&&(e.media.focus||[]).length||/altar/i.test(e.title)",
    "altar:e=>e.media&&(e.media.altars||[]).length&&(e.media.focus||[]).length||" + META["filtro_altar_re"] + ".test(e.title)")
# navegador temporal
rep("const MINY=-2186, MAXY=-1980,", f"const MINY={META['miny']}, MAXY={META['maxy']},")
# zoom automático (skill linea-de-tiempo): donde los hitos están apretados se acerca lo necesario para leerlos
rep("const z=userZ?zoom:5;",
    "let z=5; if(!userZ){ const y=events[cur-1].y; let g=Infinity; if(cur>1) g=Math.min(g,y-events[cur-2].y); if(cur<N) g=Math.min(g,events[cur].y-y); "
    f"z={META.get('zoom_base', 3)}; while(z<13&&g*fit*Math.pow(1.6,z)<74) z++; }} else z=zoom;")
# lugares que se reconocen en los pasajes para abrirlos en el atlas
rep_re(r"const LUGREF=\[.*?\];", "const LUGREF=" + json.dumps(META["lugref"], ensure_ascii=False) + ";")
# fondo de palabras de la diapositiva cinematográfica
rep("const W=['מִזְבֵּחַ','אַבְרָהָם','יִצְחָק','מוֹרִיָּה','הַר','עֹלָה','אַיִל','בְּרִית'];", "const W=" + json.dumps(META["cine_palabras"], ensure_ascii=False) + ";")
# portada
rep("alt:'Abraham y sus cuatro altares, en hebreo: Ur, Siquem, Betel, Hebrón y Moriah'", "alt:" + json.dumps(META["portada_alt"], ensure_ascii=False))
rep("'aria-label':'Abraham y sus cuatro altares, en hebreo'", "'aria-label':" + json.dumps(META["portada_alt"], ensure_ascii=False))
rep_re(r'<div class="eyebrow">Línea de tiempo interactiva · \$\{N\} hitos · [^<]*</div>',
       f'<div class="eyebrow">Línea de tiempo interactiva · ${{N}} hitos · {META["anios"]}</div>')
rep("<h1>Abraham<span>Peregrino y constructor de altares</span></h1>", f"<h1>{META['h1']}<span>{META['h1_sub']}</span></h1>")
rep_re(r'<p class="epi">.*?</p>', f'<p class="epi">{META["epi_html"]}</p>')
rep('<p class="sub">Texto bíblico, tradición judía y arqueología</p>', f'<p class="sub">{META["sub"]}</p>')
rep_re(r'<p class="how">.*?</p>`\);', f'<p class="how">{META["how"]}</p>`);')
# tema de día al abrir (el sitio ya lo fuerza; aquí también en la página suelta)
rep("\ntemaRotulo();\n", "\ntemaRaiz().dataset.theme='light'; temaRotulo();\n")

# ---------- portada propia: mapa del camino + nombre hebreo + «tres vidas» ----------
if DATA.get("portada_tres"):
    he = META["portada_he"]
    portada_js = """(function buildTitle(){
  const s=el('section',{class:'slide title c2','aria-label':'Portada'}); s.classList.add('pm');
  const fig=el('figure',{class:'pm-mapa'});
  if(DATA.portada){ const im=el('img',{src:DATA.portada.src,alt:%(alt)s,decoding:'async'}); im.style.aspectRatio=String(DATA.portada.ratio); fig.append(im); }
  fig.append(el('figcaption',{},esc(DATA.portada_cap||'')));
  const tx=el('div',{class:'pm-texto'});
  tx.innerHTML=`<div class="eyebrow">Línea de tiempo interactiva · ${N} hitos · %(anios)s</div>
    <div class="pm-cab"><h1>%(h1)s<span>%(h1_sub)s</span></h1><div class="pm-he" lang="he" dir="rtl" aria-hidden="true">%(he)s</div></div>
    <p class="epi">%(epi)s</p>
    <div class="pm-lab">%(tres_lab)s</div><div class="pm-tres"></div>`;
  const tres=tx.querySelector('.pm-tres');
  DATA.portada_tres.forEach(([c,a,l,t,n],k)=>{ const b=el('button',{type:'button',class:c+' pop','aria-label':`${l}, años ${a}: ir al hito ${n}`});
    b.style.animationDelay=(.15+k*.12)+'s'; b.innerHTML=`<span class="pm-a">${a}</span><b>${esc(l)}</b><small>${esc(t)}</small>`; b.onclick=()=>go(n); tres.append(b); });
  const bx=el('div',{class:'btns'}), b=el('button',{class:'start',type:'button'}); b.textContent='Comenzar →'; b.onclick=()=>go(1); bx.append(b);
  const last=store.get(); if(last>1&&last<=N){ const c=el('button',{class:'ghost',type:'button'}); c.textContent=`Continuar en el hito ${last}`; c.onclick=()=>go(last); bx.append(c); }
  tx.append(bx);
  const how=el('details',{class:'pm-how'}); how.innerHTML=`<summary>Cómo se usa</summary><p class="how">%(how)s</p>`; tx.append(how);
  s.append(fig,tx); track.append(s);
})();
""" % {"alt": json.dumps(META["portada_alt"], ensure_ascii=False), "anios": META["anios"], "he": he, "h1": META["h1"], "h1_sub": META["h1_sub"],
       "epi": META["epi_html"], "tres_lab": META["tres_lab"], "how": META["how"]}
    rep_re(r"\(function buildTitle\(\)\{.*?\n\}\)\(\);\n", portada_js.replace("\\", "\\\\"))
    css_pm = """
/* portada propia: mapa del camino a un lado, nombre y «tres vidas» al otro */
.slide.title.pm{grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);justify-items:stretch;text-align:left;align-items:center;align-content:safe center;gap:clamp(22px,4vw,60px);padding-top:62px;padding-bottom:18px}
.slide.title.pm p{text-align:left}
.pm .pm-mapa{margin:0;display:grid;gap:8px;justify-items:center;min-width:0}
.pm .pm-mapa img{display:block;width:min(100%,560px);max-height:min(64vh,620px);object-fit:contain;height:auto;border-radius:8px;box-shadow:var(--shadow);border:1px solid var(--rule)}
.pm .pm-mapa figcaption{font-family:var(--f-ui);font-size:12.5px;color:var(--muted);max-width:52ch;text-align:center;line-height:1.4}
.pm .pm-texto{display:grid;gap:10px;justify-items:start;min-width:0}
.pm .pm-cab{display:flex;align-items:flex-end;justify-content:space-between;gap:10px 22px;flex-wrap:wrap;width:100%;max-width:640px}
.pm .pm-he{font-family:var(--f-he);font-weight:600;font-size:clamp(54px,6.6vw,96px);line-height:.9;color:var(--accent);letter-spacing:0}
.pm h1{text-align:left;color:var(--ink);font-size:clamp(32px,4.2vw,54px)}
.pm h1 span{color:var(--gold-ink)}
.pm .epi{margin:0;font-style:italic;font-size:clamp(16px,1.6vw,20px);color:var(--ink)}
.pm .pm-lab{font-family:var(--f-mono);font-variant:small-caps;letter-spacing:.14em;font-size:13px;color:var(--muted);margin-top:6px}
.pm .pm-tres{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;width:100%;max-width:640px}
.pm .pm-tres button{all:unset;box-sizing:border-box;cursor:pointer;display:grid;align-content:start;gap:2px;padding:9px 12px 10px;border-radius:10px;background:var(--surface);
  border:1px solid var(--rule);border-top:4px solid var(--c);box-shadow:0 10px 22px -18px rgba(0,0,0,.6);transition:transform .2s,box-shadow .2s}
.pm .pm-tres button:hover,.pm .pm-tres button:focus-visible{transform:translateY(-3px);box-shadow:0 16px 26px -18px rgba(0,0,0,.7)}
.pm .pm-tres button:focus-visible{outline:2px solid var(--c);outline-offset:2px}
.pm .pm-tres .pm-a{font-family:var(--f-ui);font-weight:700;font-size:12px;letter-spacing:.06em;color:var(--c-ink)}
.pm .pm-tres b{font-family:var(--f-display);font-size:19px;color:var(--ink)}
.pm .pm-tres small{font-family:var(--f-ui);font-size:12.5px;line-height:1.35;color:var(--muted)}
.pm .btns{justify-content:flex-start;margin-top:4px}
.pm .pm-how{font-family:var(--f-ui);font-size:13.5px;color:var(--muted);max-width:66ch}
.pm .pm-how summary{cursor:pointer;font-weight:700;color:var(--accent-ink)}
.pm .pm-how .how{margin:.5em 0 0;text-align:left}
@media (max-height:860px) and (min-width:761px){
  .pm .pm-he{font-size:clamp(48px,5.4vw,72px)} .pm h1{font-size:clamp(30px,3.6vw,46px)} .pm .pm-texto{gap:7px}
  .pm .pm-tres small{font-size:11.5px} .pm .pm-mapa img{max-height:58vh} .pm .pm-mapa figcaption{display:none}
}
@media (max-width:760px){
  .slide.title.pm{grid-template-columns:minmax(0,1fr);gap:14px;align-content:start;padding-top:52px}
  .pm .pm-mapa img{max-height:30vh;width:auto}
  .pm .pm-he{font-size:56px}
  .pm .pm-tres{gap:6px} .pm .pm-tres button{padding:8px 8px 9px} .pm .pm-tres b{font-size:16px} .pm .pm-tres small{display:none}
}
"""
    rep_re(r"\n</style>\n", "\n" + css_pm.replace("\\", "\\\\") + "</style>\n")

# textos originales: edición indicada en cada pasaje (por defecto BHS / SBLGNT)
assert "/*DATA*/" in motor
motor = motor.replace("/*DATA*/", json.dumps(DATA, ensure_ascii=False, separators=(", ", ": ")))

out = LINEAS / f"{SLUG}.html"
out.write_text(motor, encoding="utf-8")
print(out, f"{len(motor)//1024} KB · {N} hitos · {len(DATA['refs'])} referencias")
