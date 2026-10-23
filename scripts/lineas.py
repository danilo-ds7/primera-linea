#!/usr/bin/env python3
"""Publica las líneas de tiempo (HTML independientes generados por la skill linea-de-tiempo).

Se ejecuta antes de cada render (pre-render en _quarto.yml). Por cada estudios/lineas/<slug>.html:

- lineas/<slug>-linea.html : la línea completa como página propia (se abre en una pestaña nueva),
  siempre en el tema de día y con el botón «Cerrar», que cierra la pestaña y vuelve a la presentación.
- lineas/_<slug>.html      : la línea pequeña (una sola línea con nodos) que lineas/<slug>.qmd incluye
  con {{< include _<slug>.html >}}; al tocarla abre lineas/<slug>-linea.html.
- lineas/<slug>/...        : las carpetas de recursos de la línea (fuentes, figuras, atlas, relieve...).

Los nodos de la línea pequeña salen de estudios/lineas/<slug>-mini.json; si no existe, de las eras.
"""
import json, re, shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RECURSOS = ("img", "fonts", "mapa", "relieve", "vendor")


def anio(y: float) -> str:
    y = round(y)
    return f"c. {abs(y)} a. e. c." if y < 0 else f"c. {y} e. c."


def datos(html: str) -> dict:
    return json.loads(re.search(r"^const DATA = (\{.*?\});\s*$", html, re.M | re.S).group(1))


def opciones(origen: Path, slug: str) -> dict:
    """Ajustes propios de cada línea, en estudios/lineas/<slug>-mini.json (nodos, emociones…)."""
    f = origen / f"{slug}-mini.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def colores(html: str) -> tuple:
    """Acento y oro del tema claro de la línea: la línea pequeña lleva los colores de cada línea."""
    m = re.search(r"\n:root\{([^}]*)\}", html)
    v = dict(re.findall(r"--([\w-]+):\s*([^;]+);", m.group(1))) if m else {}
    return v.get("accent", "#2350b8").strip(), v.get("gold", "#b8862b").strip()


def mini(html: str, slug: str, nodos_json: Path) -> str:
    """Línea pequeña: una sola línea con pocos nodos (lugares clave); toda ella abre la línea completa."""
    data = datos(html)
    n = len(data["events"])
    if nodos_json.exists():
        nodos = json.loads(nodos_json.read_text(encoding="utf-8"))["nodos"]
    else:
        bands = data["bands"][0]
        paso = max(1, len(bands) // 6)
        nodos = [{"es": b[2], "he": "", "y": b[0]} for b in bands[::paso]][:7]
    k = len(nodos)
    pts = []
    for i, nd in enumerate(nodos):
        x = 5 + i * (90 / (k - 1)) if k > 1 else 50
        he = f'<span class="lm-he" lang="he" dir="rtl">{nd["he"]}</span>' if nd.get("he") else ""
        y = anio(nd["y"]) if i == k - 1 else "c. " + str(abs(round(nd["y"])))
        pts.append(f'<span class="lm-nodo" style="left:{x:.2f}%;--d:{i * 0.12:.2f}s">{he}'
                   f'<span class="lm-pt"></span><span class="lm-es">{nd["es"]}</span>'
                   f'<span class="lm-y">{y}</span></span>')
    return f"""```{{=html}}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+Hebrew:wght@400;600&display=swap">
<a class="linea-mini" style="--lm-a:{colores(html)[0]};--lm-b:{colores(html)[1]}" href="{slug}-linea.html" target="_blank" rel="noopener" aria-label="Abrir la línea de tiempo interactiva en una pestaña nueva">
<span class="lm-head"><span class="lm-eyebrow">Línea de tiempo · {n} hitos</span><span class="lm-cta">Abrir <span aria-hidden="true">↗</span></span></span>
<span class="lm-track"><span class="lm-linea"></span>{"".join(pts)}</span>
</a>
```
"""


# Línea de emociones (para las líneas que la activan con "emociones": true): curva de 40 px cuya altura es
# la intensidad del hito (2–5) y cuyos tramos toman el color del tono (asombro, esperanza, tensión, crisis,
# renovación, reflexión), con un relleno suave debajo para ver cómo sube y baja la historia.
ARCO_EMOCIONES = r"""if(true){ // línea de emociones
    const H=40, yv=e=>H-4-(Math.max(1,Math.min(5,e.int))-1)*8.5;
    const a=sv('svg',{class:'arc emo',width:W,height:H}), pts=events.map(e=>[X(e.y),yv(e)]);
    const curva=(k)=>{ const [x0,y0]=pts[k-1],[x1,y1]=pts[k], mx=(x0+x1)/2; return ` C${mx},${y0} ${mx},${y1} ${x1},${y1}`; };
    let d=`M${pts[0][0]},${pts[0][1]}`; for(let k=1;k<pts.length;k++) d+=curva(k);
    a.append(sv('path',{class:'emo-area',d:d+` L${pts[pts.length-1][0]},${H} L${pts[0][0]},${H} Z`}));
    for(let k=1;k<pts.length;k++){ const t=sv('path',{class:'emo-tramo',d:`M${pts[k-1][0]},${pts[k-1][1]}`+curva(k)}); t.style.stroke=tones[events[k].tono].color; a.append(t); }
    events.forEach((e,k)=>{ const c=sv('circle',{cx:pts[k][0],cy:pts[k][1],r:3.8}); c.style.fill=tones[e.tono].color;
      c.append(sv('title',{},`${k+1}. ${e.title} · ${tones[e.tono].name} · intensidad ${e.int}`)); a.append(c); });
    canvas.append(a); }"""


def pagina(html: str, slug: str, op: dict = None) -> str:
    """La línea completa como página propia: tema de día, botón «Cerrar» y menú que cabe en el celular."""
    def cambiar(viejo, nuevo, regex=False):
        nonlocal html
        antes = html
        html = re.sub(viejo, nuevo, html, count=1, flags=re.S) if regex else html.replace(viejo, nuevo, 1)
        assert html != antes, f"lineas.py ({slug}): no se encontró «{viejo[:60]}»"

    # sitio en preparación: igual que el resto de las páginas, oculto a los buscadores
    cambiar('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">')

    # siempre se abre en el tema de día (Papiro): no sigue el modo oscuro del dispositivo ni recuerda el tema
    cambiar(r"\(function\(\)\{ let t=null; try\{t=localStorage\.getItem\('[^']+-theme'\);\}catch\(_\)\{\} "
            r"if\(t\) document\.documentElement\.dataset\.theme=t; \}\)\(\);",
            "document.documentElement.dataset.theme='light';", regex=True)
    html = html.replace("return r.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');",
                        "return r.dataset.theme||'light';")
    html = re.sub(r"try\{localStorage\.setItem\('[^']+-theme',r\.dataset\.theme\);\}catch\(_\)\{\}", "", html)

    # «← Primera Línea» pasa a «✕ Cerrar»: cierra la pestaña y deja a la vista la presentación
    cambiar(r'<a class="volver"[^>]*>.*?</a>',
            f'<a class="volver" id="tlCerrar" href="{slug}.html" title="Cerrar la línea de tiempo" '
            'aria-label="Cerrar la línea de tiempo"><span class="ico" aria-hidden="true"><svg viewBox="0 0 24 24">'
            '<path d="M6 6l12 12M18 6L6 18"/></svg></span><span> Cerrar</span></a>', regex=True)
    cierre = f"""<script>
document.getElementById('tlCerrar').addEventListener('click', function(e){{
  // abierta desde la presentación (pestaña nueva): se cierra y vuelve a ella; si no, va a la presentación
  if (history.length <= 1) {{ e.preventDefault(); window.close(); setTimeout(function(){{ location.href = '{slug}.html'; }}, 250); }}
}});
</script>
</html>"""
    cambiar(r"</script>\s*</html>\s*$", "</script>\n" + cierre, regex=True)

    # --- celular y tablet: menos memoria para el mapa ---------------------------------------------
    # Safari en iPhone cerraba la pestaña («Ocurrió un problema varias veces») al girar: el relieve son
    # imágenes de ~2000 px (~17 MB de memoria gráfica cada una) y el mapa se dibujaba a 3×. En celulares
    # (lado corto ≤ 600 px; el iPad queda con el relieve completo) se usa el relieve a la mitad (relieve/movil/, lo genera este script) y el mapa a 2× como máximo.
    cambiar(r"url:ATL_BASE\+r\.src\.replace\(/\^([\w-]+)\\//,''\)",
            r"url:ATL_BASE+(window.PL_MOVIL?r.src.replace(/^\1\/relieve\//,'relieve/movil/'):r.src.replace(/^\1\//,''))", regex=True)
    cambiar("const map=new maplibregl.Map({container:cont,",
            "const map=new maplibregl.Map({container:cont,pixelRatio:window.PL_MOVIL?Math.min(devicePixelRatio,2):devicePixelRatio,")
    cambiar("<script>\nconst DATA", "<script>\nwindow.PL_MOVIL=matchMedia('(pointer:coarse)').matches&&Math.min(screen.width,screen.height)<=600;\nconst DATA")

    # --- optimización del espacio: cada hito cabe entero entre el menú y la banda ------------------
    # En pantallas anchas (> 760 px), cada vez que se muestra un hito se prueban varias distribuciones
    # y se elige la que cabe con la letra más grande:
    #   · dos columnas (imagen/mapa/pasaje + texto): 5 repartos del ancho; en cada uno se busca (búsqueda
    #     binaria) el mayor tamaño que cabe en cada columna; gana el reparto con el mayor mínimo.
    #     Mapa: baja su alto. Pasaje (griego/hebreo): el recuadro ocupa todo el ancho y baja solo la letra.
    #   · portada: imagen al lado del texto o apilada; en pantallas horizontales se prefiere al lado.
    #   · hitos de una columna: se reduce el tamaño hasta que cabe.
    # Si ni al mínimo cabe, la columna se desplaza por dentro (nunca bajo la banda). En el celular, el hito
    # se desplaza entero.
    ajuste = """<script>
(function(){
  const ANCHO = () => innerWidth > 760;
  const sobra = c => c ? c.scrollHeight - c.clientHeight - 2 : 0;
  const cabe = (...els) => els.every(e => sobra(e) <= 1);
  // mayor k en [min, 1] con el que cabe (búsqueda binaria); devuelve k, o min - 0.1 si ni así cabe
  function kMax(poner, cabeYa, min){
    poner(1); if (cabeYa()) return 1;
    poner(min); if (!cabeYa()) return min - 0.1;
    let lo = min, hi = 1; for (let n = 0; n < 7; n++){ const k = (lo + hi) / 2; poner(k); if (cabeYa()) lo = k; else hi = k; }
    poner(lo); return lo;
  }
  function limpiar(s){
    s.style.gridTemplateColumns = ''; s.classList.remove('pl-lado');
    [...s.children].forEach(c => c.style.zoom = '');
    s.querySelectorAll('.vivo').forEach(v => { v.style.height = ''; v.style.minHeight = ''; });
    s.querySelectorAll('.escr').forEach(e => e.style.removeProperty('--pl-f'));
  }
  // columna de imagen, mapa o pasaje: devuelve qué tan grande queda (1 = tamaño normal)
  function medirMedia(c){
    const slot = c.querySelector(':scope>.mslot') || c, v = c.querySelector('.vivo'), e = c.querySelector('.escr');
    if (v){ v.style.height = ''; v.style.minHeight = ''; if (!cabe(slot, c)){ v.style.minHeight = '0'; v.style.height = Math.max(innerHeight <= 500 ? 140 : 240, v.getBoundingClientRect().height - Math.max(sobra(slot), sobra(c))) + 'px'; }
            return cabe(slot, c) ? 1 : 0.6; }
    if (e){ const k = kMax(k => e.style.setProperty('--pl-f', k), () => cabe(slot, c), 0.55);
            return 0.78 + (k - 0.55) * 0.22 / 0.45; }   // la letra del pasaje puede bajar más que el resto
    return kMax(k => c.style.zoom = k, () => cabe(slot, c), 0.7);
  }
  const medirTexto = t => kMax(k => t.style.zoom = k, () => cabe(t), 0.7);
  const REPARTOS = ['1.05fr 1fr', '1.35fr 1fr', '1fr 1.35fr', '1.7fr 1fr', '1fr 1.7fr'];
  function dosColumnas(s){
    const m = s.querySelector(':scope>.media'), t = s.querySelector(':scope>.text');
    const probar = r => { limpiar(s); const [a, b] = r.split(' ');
      s.style.gridTemplateColumns = `minmax(0,${a}) minmax(0,${b})`; return Math.min(medirMedia(m), medirTexto(t)); };
    let mejor = REPARTOS[0], pm = probar(mejor);
    if (pm < 1) for (const r of REPARTOS.slice(1)){ const p = probar(r); if (p > pm + 0.02){ pm = p; mejor = r; } if (pm >= 1) break; }
    probar(mejor);
  }
  function portada(s){
    const hijos = [...s.children].filter(c => !c.matches('.hero'));
    const probar = lado => { limpiar(s); s.classList.toggle('pl-lado', lado);
      return kMax(k => (lado ? hijos : [...s.children]).forEach(c => c.style.zoom = k), () => cabe(s), 0.62); };
    const horizontal = s.clientWidth / s.clientHeight > 1.25;
    const pl = probar(true), pa = probar(false);
    probar(horizontal ? pl >= pa - 0.08 : pl > pa + 0.02);
  }
  function unaColumna(s){ limpiar(s); kMax(k => [...s.children].forEach(c => c.style.zoom = k), () => cabe(s), 0.72); }
  function ajustar(s){
    if (!s) return;
    s.classList.add('pl-midiendo');   // sin la animación de entrada, que desplaza el texto unos píxeles
    try {
      limpiar(s);
      if (!ANCHO() || s.classList.contains('viaje')) return;
      if (s.classList.contains('title')) portada(s);
      else if (s.querySelector(':scope>.media') && s.querySelector(':scope>.text') && s.children.length === 2) dosColumnas(s);
      else if (!s.querySelector('.vivo')) unaColumna(s);
    } finally { s.classList.remove('pl-midiendo'); }
  }
  const actual = () => document.querySelector('.slide.on');
  let t = null; const pronto = () => { clearTimeout(t); t = setTimeout(() => ajustar(actual()), 60); };
  const track = document.getElementById('track');
  // solo cuando un hito pasa a ser el activo (no al medir, que también cambia sus clases)
  new MutationObserver(m => { if (m.some(x => x.target.classList && x.target.classList.contains('on') &&
      !(' ' + (x.oldValue || '') + ' ').includes(' on '))) pronto(); })
    .observe(track, { subtree: true, attributes: true, attributeFilter: ['class'], attributeOldValue: true });
  addEventListener('resize', pronto);
  track.addEventListener('load', pronto, true);   // imágenes que llegan después
  if (document.fonts) document.fonts.ready.then(pronto);
  pronto();
  window.plAjustar = ajustar;
})();
</script>
</html>"""
    cambiar(r"</html>\s*$", ajuste, regex=True)

    # --- todo en una pantalla: un botón por tarea y una banda de tiempo más baja ----------------
    # Fuera (repetían otra tarea o eran secundarios): «Arqueología» y «Hoy» del menú (el Atlas tiene sus
    # propias capas), las flechas grandes sobre el texto (repetían ← → de la banda y lo tapaban), los
    # filtros de la banda, el minimapa y «ver toda la línea» (se confundía con pantalla completa).
    # Se ocultan con CSS para no romper el código que los actualiza.
    # En la banda, ← antes que →
    cambiar(r'(<button id="tnext"[^>]*>.*?</button>)\s*(<button id="tprev"[^>]*>.*?</button>)', r"\2\n      \1", regex=True)
    # banda angosta: 2 filas de hitos más compactas, arriba del todo (sin la barra de filtros)
    cambiar(r"const (MINY=[^;\n]*?), ROWS=3,", r"let ROWS=2;\nconst \1,", regex=True)
    # La banda es una sola tira que crece ×1,6 con cada lupa «+»: en el iPhone llegaba a ~126.000 px de
    # ancho (~650 MB de memoria gráfica) y Safari cerraba la pestaña. El zoom máximo se calcula según la
    # pantalla para que la tira no pase de ~20.000 px en el celular ni de ~60.000 px en el computador.
    cambiar(r"(MKW=\d+), MAXZ=\d+;", r"\1;\nlet MAXZ=15;", regex=True)
    cambiar("function layout(){", "function layout(){ ROWS=innerHeight<=500?1:2;"   # celular en horizontal: 1 fila
            " { const lim=matchMedia('(pointer:coarse)').matches?20000:60000;"
            " MAXZ=Math.max(5,Math.floor(Math.log(lim/Math.max(200,view.clientWidth-80))/Math.log(1.6)));"
            " if(zoom>MAXZ) zoom=MAXZ; }")
    cambiar("ROWH=44", "ROWH=38")
    emociones = bool((op or {}).get("emociones"))
    if emociones:   # línea de emociones: la curva del tono y la intensidad de cada hito, sobre la banda
        cambiar(r"if\(false\)\{ // arco emocional.*?canvas\.append\(a\); \}", ARCO_EMOCIONES, regex=True)
        cambiar("ARC=22", "ARC=40")
    else:
        cambiar("ARC=22", "ARC=-2")
    cambiar("const axisY=h-50,", "const axisY=h-30,")
    html = html.replace("(top+38)", "(top+34)").replace("bandTop-top-38", "bandTop-top-34")
    cambiar("axisY+17", "axisY+13")
    cambiar("</style>", """/* Primera Línea: un botón por tarea, menú en su propia franja y banda de tiempo angosta */
#arqBtn,#hoyBtn,.stage>.arrow,#zfit,.tn-filtros,.mini{display:none!important}
/* menú arriba: franja propia (no flota sobre el mapa ni el texto); Cerrar a la izquierda */
.stage{padding-top:54px}
.topbar{top:0;left:0;right:0;height:54px;padding:0 16px;justify-content:flex-end;gap:8px;
  background:var(--bg);border-bottom:1px solid var(--rule)}
.topbar .volver{margin-right:auto}
.tb-grupo{box-shadow:none}
/* banda de tiempo angosta */
.tn{height:158px}
.mk{height:30px} .mk .mn{min-width:24px;height:24px}
.slide{padding-block:22px 22px;padding-inline:clamp(16px,6vw,96px)}
.pl-midiendo,.pl-midiendo *{animation:none!important;transition:none!important}
.tn-canvas{will-change:auto}
.slide{content-visibility:auto;contain-intrinsic-size:auto 100vw auto 100%}
@media (pointer:coarse) and (max-width:1100px){.slide.on .media img{animation:none}}
/* pantallas anchas: cada columna del hito se limita al alto disponible (el ajuste la encoge si hace falta) */
@media (min-width:761px){
  .slide:has(>.media):not(.viaje){grid-template-rows:minmax(0,1fr)}
  .slide:has(>.media):not(.viaje)>.media,.slide:has(>.media):not(.viaje)>.text{max-height:100%;overflow:auto;scrollbar-width:thin}
  /* imagen, mapa o pasaje: su recuadro se achica y se desplaza por dentro; la leyenda queda a la vista */
  .slide:has(>.media):not(.viaje)>.media{display:flex;flex-direction:column;overflow:hidden}
  .slide:has(>.media):not(.viaje)>.media>.mslot{flex:0 1 auto;min-height:0;overflow:auto;scrollbar-width:thin}
  .slide:has(>.media):not(.viaje)>.media>figcaption{flex:none}
  /* pasaje en griego o hebreo: el recuadro ocupa todo el ancho de su columna; el ajuste baja solo la letra */
  .slide:has(>.media):not(.viaje) .escr{width:100%;max-width:none;box-sizing:border-box}
  .escr .gr{font-size:calc(clamp(22px,2.3vw,30px) * var(--pl-f,1))}
  .escr .he{font-size:calc(clamp(23px,2.5vw,33px) * var(--pl-f,1))}
  .escr .tr{font-size:calc(clamp(17px,1.5vw,20px) * var(--pl-f,1))}
  /* portada lado a lado: la imagen a la izquierda, el texto a la derecha */
  .slide.title.pl-lado{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);grid-auto-rows:min-content;justify-items:start;
    text-align:left;align-content:center;column-gap:clamp(24px,4vw,64px);row-gap:10px}
  .slide.title.pl-lado>.hero{grid-column:1;grid-row:1 / span 8;align-self:center;justify-self:stretch;width:100%!important;height:auto!important;max-height:none}
  .slide.title.pl-lado>:not(.hero){grid-column:2}
  .slide.title.pl-lado .how{max-width:none}
  .slide.title.pl-lado>*{text-align:left}
}
@media (max-width:760px){
  .slide{padding-block:16px 16px}
  .vivo{height:34vh;min-height:220px} .vivo.viaje{height:38vh}
}
/* pantallas bajas (celular en horizontal): menú solo con iconos y banda de una fila */
@media (max-height:500px){
  .stage{padding-top:42px}
  .topbar{height:42px;padding:0 10px;gap:4px}
  .topbar span{display:none} .topbar span.ico{display:inline-grid}
  .topbar button,.topbar .volver{min-width:0;min-height:28px;padding:4px 9px;display:inline-grid;place-items:center}
  .tn{height:118px}
  .tn-tools{gap:0;padding-top:2px} .tn-tools button{height:27px} .tn-tools hr{margin:1px 0}
  .slide{padding-block:10px 10px}
  .atl-ley{display:none} .atl-capas button{font-size:11px;padding:3px 7px}
}
/* celular: iconos visibles (antes se ocultaban con el texto) y menú compacto */
@media (max-width:600px){
  .stage{padding-top:48px}
  .topbar{height:48px;padding:0 8px;gap:4px}
  .topbar span.ico{display:inline-grid}
  .topbar button,.topbar .volver{min-width:0;min-height:30px;padding:6px 8px;display:inline-grid;place-items:center}
}
</style>""")
    if emociones:
        cambiar("</style>", """/* línea de emociones (solo en las líneas que la activan) */
.tn{height:200px}
.arc.emo{top:2px}
.arc.emo .emo-area{fill:color-mix(in srgb,var(--accent) 9%,transparent);stroke:none}
.arc.emo .emo-tramo{fill:none;stroke-width:2.4;stroke-linecap:round;opacity:.9}
.arc.emo circle{stroke:var(--nav);stroke-width:1.5;pointer-events:auto}
.tn::after{content:"emociones";position:absolute;left:52px;top:3px;z-index:3;pointer-events:none;
  font:700 9.5px var(--f-ui);letter-spacing:.14em;text-transform:uppercase;color:var(--muted);opacity:.85;
  background:color-mix(in srgb,var(--nav) 85%,transparent);padding:0 4px;border-radius:3px}
@media (max-height:500px){.tn{height:160px}}
</style>""")
    return html


def relieve_movil(carpeta: Path):
    """Relieve a la mitad de resolución para celular y tablet (relieve/movil/): ~4 veces menos memoria."""
    if not carpeta.is_dir():
        return
    try:
        from PIL import Image
    except ImportError:   # sin Pillow, el celular usa el relieve completo (como copia)
        Image = None
    movil = carpeta / "movil"
    movil.mkdir(exist_ok=True)
    for f in carpeta.glob("*.webp"):
        if Image is None:
            shutil.copy2(f, movil / f.name); continue
        with Image.open(f) as im:
            im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS).save(movil / f.name, "WEBP", quality=82, method=6)
    print(f"{movil}: {len(list(movil.glob('*.webp')))} imágenes")


if __name__ == "__main__":
    origen = RAIZ / "estudios" / "lineas"
    destino = RAIZ / "lineas"
    destino.mkdir(exist_ok=True)
    for src in sorted(origen.glob("*.html")):
        slug = src.stem
        html = src.read_text(encoding="utf-8")
        (destino / f"_{slug}.html").write_text(mini(html, slug, origen / f"{slug}-mini.json"), encoding="utf-8")
        (destino / f"{slug}-linea.html").write_text(pagina(html, slug, opciones(origen, slug)), encoding="utf-8")
        print(f"lineas/{slug}-linea.html · lineas/_{slug}.html")
        for sub in RECURSOS:   # figuras TikZ, fuentes, atlas (MapLibre, relieve, capas)
            d = origen / slug / sub
            if d.is_dir():
                dst = destino / slug / sub
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(d, dst)
        for f in (origen / slug).glob("*.css"):   # hojas de estilo propias de la línea (p. ej. tema.css)
            shutil.copy2(f, destino / slug / f.name)
        relieve_movil(destino / slug / "relieve")

