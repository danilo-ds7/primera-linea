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


# ---------- líneas de la era común, en griego, con cartas en vez de altares y pictogramas de transporte ----------
# (META: era_comun, altar_nombre/altar_lang, labw_solo, medios). Pablo es la primera que los usa.
if META.get("era_comun"):
    rep("l.textContent=isMaj?`${-y} a. e. c.`:String(-y);", "l.textContent=isMaj?(y<0?`${-y} a. e. c.`:`${y} e. c.`):String(Math.abs(y));")
    rep("const yr = y => `${Math.round(-y)}`;", "const yr = y => `${Math.abs(Math.round(y))}`;")
    rep("s.append(sv('text',{x:X(v),y:278,class:'axl'},String(-v)));", "s.append(sv('text',{x:X(v),y:278,class:'axl'},String(Math.abs(v))));")
    rep("s.append(sv('text',{x:X1,y:294,class:'axl','text-anchor':'end'},'a. e. c.'));", "s.append(sv('text',{x:X1,y:294,class:'axl','text-anchor':'end'},m.lo>=0?'e. c.':'a. e. c.'));")
if META.get("altar_nombre"):   # «Carta escrita aquí»: la ficha del lugar y el pictograma del marcador
    nom = META["altar_nombre"]; gr = META.get("altar_lang") == "el"
    cita = '<div class="gr" lang="grc">' if gr else '<div class="he" lang="he" dir="rtl">'
    rep('const alt=A?`<div class="lab">Altar ${A.n} · ${esc(A.ref)}</div><div class="alt"><div class="he" lang="he" dir="rtl">${esc(A.he)}</div>',
        'const alt=A?`<div class="lab">' + nom + 's · ${esc(A.ref)}</div><div class="alt">' + cita + '${esc(A.he)}</div>')
    rep('<div class="lab">Atributo de Dios que se revela</div><p>${esc(A.attr)}</p><div class="lab">Significado</div><p>${esc(A.theo)}</p><div class="lab">Aplicación</div>',
        f'<div class="lab">{META.get("altar_lab1", "Tema central")}</div><p>${{esc(A.attr)}}</p><div class="lab">{META.get("altar_lab2", "Lo que enseña")}</div><p>${{esc(A.theo)}}</p><div class="lab">{META.get("altar_lab3", "Para hoy")}</div>')
    rep("${KIND[L.k]||'Lugar'}${A?` · altar ${A.n}`:''}", "${KIND[L.k]||'Lugar'}${A?` · " + nom.lower() + "s`:''}")
    # pictograma del marcador: un rollo (carta) en vez del altar con llama
    rep_re(r'<span class="atl-alt"><svg viewBox="-14 -26 28 30" aria-hidden="true">.*?</svg>',
           '<span class="atl-alt"><svg viewBox="-14 -26 28 30" aria-hidden="true"><path d="M-9,-22 H7 a4,4 0 0 1 4,4 V-6 a3,3 0 0 1 -3,3 H-6 a3,3 0 0 1 -3,-3 Z" fill="#f1e6cf" stroke="#3a2f14" stroke-width="1.2"/><path d="M-9,-22 a3,3 0 0 0 -3,3 v13 a3,3 0 0 0 3,3 h3" fill="#d8c7a3" stroke="#3a2f14" stroke-width="1.2"/><path d="M-5,-16 H6 M-5,-12 H6 M-5,-8 H2" stroke="#8c2634" stroke-width="1.4" stroke-linecap="round"/></svg>')
    rep("rotate(45deg)} .atl-ley .lg-h", "rotate(45deg)} .atl-ley .lg-c{background:#f1e6cf;border-color:#8c2634;border-radius:2px} .atl-ley .lg-h")
    rep('<span><i class="lg-b"></i>Lugar bíblico</span>', f'<span><i class="lg-b"></i>Lugar bíblico</span><span><i class="lg-c"></i>{nom}</span>')
if META.get("portada_lang") == "el":   # nombre de la portada en griego, de izquierda a derecha
    rep('<div class="pm-he" lang="he" dir="rtl" aria-hidden="true">', '<div class="pm-he" lang="grc" aria-hidden="true">')
    rep(".pm-he{font-family:var(--f-he);", ".pm-he{font-family:var(--f-gr);font-style:italic;")
    rep("if(e.cine) t.append(el('div',{class:'stat',lang:'he'},", "if(e.cine) t.append(el('div',{class:'stat'+(e.cine.he===false?' gr':''),lang:e.cine.he===false?'grc':'he'},")
    rep(".stat{font-family:var(--f-he);direction:rtl;", ".stat.gr{font-family:var(--f-gr);direction:ltr;font-style:italic}\n.stat{font-family:var(--f-he);direction:rtl;")
if META.get("labw_solo"):   # rótulos de mar y región solo los de la línea; sin el relieve esquemático del Levante
    rep("const LAB_W=[...(DATA.labw||[]),", "const LAB_W=[...(DATA.labw||[])]; const LAB_W_LEVANTE=[")
    rep("const RIDGES=[", "const RIDGES=[]; const RIDGES_LEVANTE=[")
    rep("const RIDGES_W=[", "const RIDGES_W=[]; const RIDGES_W_LEVANTE=[")
if META.get("medios"):   # pictogramas de transporte: tramos por mar (nave) y a pie (caminante) en mapas, atlas y fichas
    medio_js = """const MEDIO_INNER={
  mar:'<circle r="11" fill="var(--surface)" opacity=".85"/><path d="M-8.5,2 Q0,6 8.5,2 L6.5,7 Q0,9 -6.5,7 Z" fill="COL"/><path d="M0,2 V-8.5" stroke="COL" stroke-width="1.5"/><path d="M1.2,-8 L7.5,-1 L1.2,-1 Z" fill="COL"/><path d="M-1.2,-6.5 L-6.5,-.5 L-1.2,-.5 Z" fill="COL" opacity=".75"/>',
  pie:'<circle r="11" fill="var(--surface)" opacity=".85"/><circle cx="1" cy="-7.5" r="2.1" fill="COL"/><path d="M.6,-4.5 L-1,1 L-3.5,7 M-1,1 L3,4.5 L3.5,7.5 M-3,-2 L1,-1.5 L4.5,1.5" stroke="COL" stroke-width="1.7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
  carro:'<circle r="11" fill="var(--surface)" opacity=".85"/><path d="M-8,0 H5 L7,-5 H-3 Z" fill="COL"/><circle cx="-4" cy="3.5" r="2.6" fill="none" stroke="COL" stroke-width="1.6"/><circle cx="3.5" cy="3.5" r="2.6" fill="none" stroke="COL" stroke-width="1.6"/>',
  asno:'<circle r="11" fill="var(--surface)" opacity=".85"/><path d="M-7,1 H4 L6,-4 L8,-2 L7,2 L5,2 L5,6 M-5,1 V6 M2,1 V6 M-7,1 L-8,-3" stroke="COL" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
  caballo:'<circle r="11" fill="var(--surface)" opacity=".85"/><path d="M-7,2 H3 L5,-5 L8,-3 L8,0 L6,0 L6,7 M-5,2 V7 M1,2 V7 M-7,2 L-9,-2 M3,-5 L0,-8" stroke="COL" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'};
const MEDIO_NOM={mar:'Por mar, en nave',pie:'A pie, por calzada',carro:'En carro',asno:'En asno o mula',caballo:'A caballo'};
const medioSVG=(k,col)=>`<svg viewBox="-12 -12 24 24" aria-hidden="true">${(MEDIO_INNER[k]||'').replace(/COL/g,col||'currentColor')}</svg>`;
"""
    rep("const LAB_W=[", medio_js + "const LAB_W=[")
    # mapas SVG de cada hito: glifo a mitad del trayecto
    rep("for(let k=1;k<10;k++){ const [qx,qy]=at(P,k/10); boxes.push([qx-4,qy-4,8,8]); } });",
        "for(let k=1;k<10;k++){ const [qx,qy]=at(P,k/10); boxes.push([qx-4,qy-4,8,8]); }\n"
        "    if(p.medio&&MEDIO_INNER[p.medio]){ const [gx,gy]=at(P,p.gf||.5); const g=sv('g',{class:'medio onmap',transform:`translate(${gx},${gy}) scale(${(p.gs||1)*F*.95})`}); g.innerHTML=MEDIO_INNER[p.medio].replace(/COL/g,col); g.style.animationDelay=(.6+i*.35)+'s'; A(g); boxes.push([gx-11*F,gy-11*F,22*F,22*F]); } });")
    # atlas: trazo discontinuo para el mar y marcadores con el pictograma a mitad de cada tramo
    rep("properties:{n:t.n,v:t.vuelta?1:0},geometry:{type:'LineString',coordinates:curva(t.pts)}", "properties:{n:t.n,v:t.vuelta?1:0,m:t.medio||''},geometry:{type:'LineString',coordinates:curva(t.pts)}")
    rep_re(r"(\{id:'ruta',type:'line',source:'ruta',layout:\{'line-cap':'round','line-join':'round'\},\s*paint:\{.*?\},)filter:\['==',\['get','v'\],0\]\},",
           lambda q: q.group(1) + "filter:['all',['==',['get','v'],0],['!=',['get','m'],'mar']]},\n    " + q.group(1).replace("id:'ruta',", "id:'ruta-mar',").replace("'line-cap':'round',", "") + "filter:['all',['==',['get','v'],0],['==',['get','m'],'mar']]},")
    rep_re(r"(\{id:'ruta-mar',type:'line',source:'ruta',layout:\{'line-join':'round'\},\s*paint:\{)", r"\1'line-dasharray':[1.8,1.4],")
    rep("['ruta-casco','ruta','ruta-v','ruta-toque'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.relato&&verRuta)));",
        "['ruta-casco','ruta','ruta-mar','ruta-v','ruta-toque'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.relato&&verRuta)));")
    rep("const verTodo=ev.viaje||ATL.full, hl=new Set(ev.hl||[]), alt=new Set(ev.altars||[]), foco=new Set(ev.focus||[]);\n  if(C.relato){",
        "const verTodo=ev.viaje||ATL.full, hl=new Set(ev.hl||[]), alt=new Set(ev.altars||[]), foco=new Set(ev.focus||[]);\n"
        "  if(C.relato&&verTodo) ATL.data.tramos.forEach(t=>{ if(!t.medio||!MEDIO_INNER[t.medio]) return; const mid=t.pts[Math.floor(t.pts.length/2)];\n"
        "    const n=el('button',{type:'button',class:'atl-medio m-'+t.medio,'aria-label':`Tramo ${t.n}: ${MEDIO_NOM[t.medio]}`}); n.innerHTML=medioSVG(t.medio,'currentColor'); n.onclick=e=>{ e.stopPropagation(); atlasTramo(t.n); };\n"
        "    n.dataset.minz=4.2; const k=new maplibregl.Marker({element:n,anchor:'center'}).setLngLat(lonlat(mid)).addTo(m); ATL.mk.push(k); });\n  if(C.relato){")
    rep('<span class="pp-k">Tramo ${t.n} de ${T.length} · ≈ ${fmtKm(d)} km</span><b>${esc(t.de)} → ${esc(t.a)}</b></div>',
        '<span class="pp-k">Tramo ${t.n} de ${T.length} · ≈ ${fmtKm(d)} km</span><b>${esc(t.de)} → ${esc(t.a)}</b>${t.medio&&MEDIO_INNER[t.medio]?`<span class="pp-medio m-${t.medio}">${medioSVG(t.medio)} ${MEDIO_NOM[t.medio]}</span>`:``}</div>')
    rep("en ${T.length} tramos, a pie, ", "en ${T.length} tramos: ≈ ${fmtKm(T.filter(t=>t.medio!=='mar').reduce((a,t)=>a+kmTramo(t),0))} km a pie y ≈ ${fmtKm(T.filter(t=>t.medio==='mar').reduce((a,t)=>a+kmTramo(t),0))} km por mar, ")
    rep("'Recorrer hoy en Google Maps (a pie)'", "t.medio==='mar'?'Ver el trayecto hoy en Google Maps':'Recorrer hoy en Google Maps (a pie)'")
    rep('<span><i class="lg-r"></i>Camino</span>', '<span class="lg-ico m-pie">${medioSVG("pie")}A pie</span><span class="lg-ico m-mar">${medioSVG("mar")}Por mar</span>')
    rep_re(r"leyenda\.innerHTML='(.*?)';", lambda q: "leyenda.innerHTML=`" + q.group(1) + "`;")
    css_medios = """
/* pictogramas de transporte (tramos por mar y a pie) */
.atl-medio{width:26px;height:26px;padding:0;border:0;border-radius:50%;background:transparent;color:#1a4f7a;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,.35);transition:transform .15s}
.atl-medio.m-pie{color:#9a4a2a} .atl-medio:hover{transform:scale(1.15)} .atl-medio svg{width:100%;height:100%;display:block}
.pp-medio{display:inline-flex;align-items:center;gap:4px;margin-top:4px;font:600 11px var(--f-ui);color:#1a4f7a;text-transform:uppercase;letter-spacing:.04em}
.pp-medio.m-pie{color:#9a4a2a} .pp-medio svg{width:18px;height:18px}
.atl-ley .lg-ico{display:inline-flex;align-items:center;gap:3px;color:#1a4f7a} .atl-ley .lg-ico.m-pie{color:#9a4a2a} .atl-ley .lg-ico svg{width:16px;height:16px}
g.medio.onmap{animation:pop .5s both}
"""
    rep_re(r"\n</style>\n", "\n" + css_medios.replace("\\", "\\\\") + "</style>\n")

# textos originales: edición indicada en cada pasaje (por defecto BHS / SBLGNT)
assert "/*DATA*/" in motor
motor = motor.replace("/*DATA*/", json.dumps(DATA, ensure_ascii=False, separators=(", ", ": ")))

out = LINEAS / f"{SLUG}.html"
out.write_text(motor, encoding="utf-8")
print(out, f"{len(motor)//1024} KB · {N} hitos · {len(DATA['refs'])} referencias")
