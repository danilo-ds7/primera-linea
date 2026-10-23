#!/usr/bin/env python3
"""Integra una línea de tiempo (HTML independiente generado por la skill linea-de-tiempo)
dentro de una página Quarto, con su CSS acotado al contenedor y la pantalla completa sobre
ese mismo contenedor.

Se ejecuta antes de cada render (pre-render en _quarto.yml): toma cada estudios/lineas/<slug>.html
y escribe lineas/_<slug>.html, que lineas/<slug>.qmd incluye con {{< include _<slug>.html >}}.
"""
import json, re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

def anio(y: float) -> str:
    y = round(y)
    return f"c. {abs(y)} a. e. c." if y < 0 else f"c. {y} e. c."

def mini(js: str, ID: str) -> str:
    """Línea pequeña: eras y hitos a escala, todo un botón que abre la línea completa."""
    data = json.loads(re.search(r"^const DATA = (\{.*?\});\s*$", js, re.M | re.S).group(1))
    bands = data["bands"][0]
    ys = [e["y"] for e in data["events"]]
    y0, y1 = min(bands[0][0], min(ys)), max(bands[-1][1], max(ys))
    esc = lambda y: (y - y0) / (y1 - y0) * 100
    eras = []
    for i, (a, b, nombre, _) in enumerate(bands):
        w = esc(b) - esc(a)
        eras.append(f'<span class="lm-era" data-w="{"s" if w < 9 else "l"}" style="left:{esc(a):.2f}%;width:{w:.2f}%;--i:{i % 4}" title="{nombre}"><i>{nombre}</i></span>')
    dots = "".join(f'<span class="lm-dot" style="left:{esc(y):.2f}%"></span>' for y in ys)
    n = len(ys)
    return f"""<button type="button" class="linea-mini" id="{ID}-mini" aria-controls="{ID}" aria-expanded="false" aria-label="Abrir la línea de tiempo interactiva">
<span class="lm-head"><span class="lm-eyebrow">Línea de tiempo interactiva · {n} hitos</span><span class="lm-cta">Abrir la línea de tiempo →</span></span>
<span class="lm-track">{"".join(eras)}{dots}</span>
<span class="lm-years"><span>{anio(y0)}</span><span>{anio(y1)}</span></span>
</button>"""

def embed(src: Path, dst: Path, ID: str):
    html = src.read_text(encoding="utf-8")

    # --- piezas ---------------------------------------------------------------
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    body = re.search(r'(<div class="app">.*?<div id="pop" role="tooltip"></div>)', html, re.S).group(1)
    js = re.search(r"<script>\n(const DATA = .*?)</script>\s*</html>", html, re.S).group(1)
    fonts = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com[^"]+)">', html).group(1)

    # --- clases que chocan con las del sitio -------------------------------------
    ren = {"app": "tl-app", "band": "tl-band", "hero": "tl-hero", "sub": "tl-sub",
           "chips": "tl-chips", "ghost": "tl-ghost", "topbar": "tl-topbar"}
    for a, b in ren.items():
        css = re.sub(rf"\.{a}\b", f".{b}", css)
        body = re.sub(rf'class="{a}\b', f'class="{b}', body)
        js = re.sub(rf"class:\s*'{a}\b", f"class:'{b}", js)
        js = re.sub(rf"class=\"{a}\b", f'class="{b}', js)
    # diapositiva de portada: .title choca con el título de Quarto
    css = re.sub(r"\.title\b", ".tl-portada", css)
    js = js.replace("'slide title c2'", "'slide tl-portada c2'")
    js = js.replace("$('#themeBtn')", "$('#themeBtn')")

    # --- CSS: el contenedor hace de :root y de body ----------------------------
    css = css.replace("html,body{height:100%;margin:0}\n", "")
    css = re.sub(r"\nbody\{[^}]*\}", "", css, count=1)
    css = css.replace(":root:not([data-theme=\"light\"])", f"#{ID}:not([data-theme=\"light\"])")
    css = css.replace(":root[data-theme=\"dark\"]", f"#{ID}[data-theme=\"dark\"]")
    css = css.replace(":root[data-theme=\"jerusalen\"]", f"#{ID}[data-theme=\"jerusalen\"]")
    css = css.replace(":root{", f"#{ID}{{")
    css = re.sub(r"(\d+)vh\b", r"\1cqh", css)          # alturas relativas al contenedor, no a la ventana
    css = re.sub(r"(\d+)vw\b", r"\1cqw", css)

    def scope(block: str) -> str:
        """Antepone #ID a cada selector (recursivo en @media)."""
        out, i = [], 0
        while i < len(block):
            m = re.compile(r"\s*([^{}]+)\{", re.S).match(block, i)
            if not m:
                out.append(block[i:]); break
            sel = m.group(1).strip()
            # buscar el cierre equilibrado
            depth, j = 1, m.end()
            while depth:
                if block[j] == "{": depth += 1
                elif block[j] == "}": depth -= 1
                j += 1
            inner = block[m.end():j-1]
            if sel.startswith("@media"):
                out.append(f"{sel}{{{scope(inner)}}}\n")
            elif sel.startswith("@keyframes") or sel.startswith("@font-face"):
                out.append(f"{sel}{{{inner}}}\n")
            else:
                parts = []
                for s in sel.split(","):
                    s = s.strip()
                    if not s: continue
                    if s.startswith(f"#{ID}"): parts.append(s)
                    elif s.startswith("*"): parts.append(f"#{ID} {s}")
                    else: parts.append(f"#{ID} {s}")
                out.append(",".join(parts) + "{" + inner + "}\n")
            i = j
        return "".join(out)

    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = scope(css)
    css += f"""
    #{ID}{{position:relative;width:min(100vw - 32px,1440px);margin-left:calc(50% - min(50vw - 16px,720px));height:clamp(720px,90vh,1040px);border:1px solid var(--rule);border-radius:12px;overflow:hidden;container-type:size;box-shadow:0 30px 50px -30px rgba(19,26,44,.35);font-size:16px;line-height:1.4}}
    #{ID} *{{box-sizing:border-box}}
#{ID}{{font-family:var(--f-display);color:var(--ink)}}
#{ID} .slide{{padding-block:44px 28px}}
    #{ID} p,#{ID} li,#{ID} h1,#{ID} h2,#{ID} h3{{text-align:left;letter-spacing:0;font-family:var(--f-display)}}
    #{ID} .slide.tl-portada p{{text-align:center}}
    #{ID} .tl-app{{height:100%}}
    #{ID}.tl-full{{position:fixed;inset:0;z-index:3000;height:100vh;height:100dvh;border-radius:0;border:0}}
    #{ID}:fullscreen{{height:100vh;border-radius:0;border:0}}
    #{ID} .scrim{{z-index:2000}} #{ID} .drawer{{z-index:2001}} #{ID} #pop{{z-index:2002}}
    #{ID} .tl-topbar{{z-index:6}}
#{ID} .tn{{height:254px}} #{ID}:fullscreen .tn,#{ID}.tl-full .tn{{height:258px}}
    @media (max-width:600px){{#{ID} .tn{{height:206px}} #{ID}{{height:88vh;height:88dvh;min-height:600px;width:100vw;margin-left:calc(50% - 50vw);border-radius:0;border-inline:0}}}}
    """

    # --- JS: tema, pantalla completa y teclado sobre el contenedor -------------
    js = js.replace("document.documentElement.dataset.theme=t", f"TL.dataset.theme=t")
    js = js.replace("function temaRaiz(){ return document.documentElement; }", "function temaRaiz(){ return TL; }")
    # Siempre se abre en el tema de día (Papiro): no sigue el modo oscuro del dispositivo ni recuerda el tema
    js = re.sub(r"\(function\(\)\{ let t=null; try\{t=localStorage\.getItem\('[^']+-theme'\);\}catch\(_\)\{\} if\(t\) TL\.dataset\.theme=t; \}\)\(\);",
                "TL.dataset.theme='light';", js, count=1)
    assert "TL.dataset.theme='light';" in js, "lineas.py: no se encontró la carga del tema guardado"
    js = js.replace("return r.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');", "return r.dataset.theme||'light';")
    js = re.sub(r"try\{localStorage\.setItem\('[^']+-theme',r\.dataset\.theme\);\}catch\(_\)\{\}", "", js)
    js = re.sub(r"function toggleFS\(\)\{.*?\n(?=function fsLabel)",
    f"""function fsOn(){{ return !!(document.fullscreenElement||document.webkitFullscreenElement)||TL.classList.contains('tl-full'); }}
    function toggleFS(){{ const d=document;
      try{{ if(d.fullscreenElement||d.webkitFullscreenElement){{ (d.exitFullscreen||d.webkitExitFullscreen).call(d); return; }}
           if(TL.classList.contains('tl-full')){{ TL.classList.remove('tl-full'); fsLabel(); return; }}
           const f=TL.requestFullscreen||TL.webkitRequestFullscreen;
           if(f){{ const p=f.call(TL); if(p&&p.catch) p.catch(()=>{{ TL.classList.add('tl-full'); fsLabel(); }}); }}
           else {{ TL.classList.add('tl-full'); fsLabel(); }} }}catch(_){{ TL.classList.add('tl-full'); fsLabel(); }} }}
    """, js, flags=re.S)
    js = js.replace("function fsLabel(){ const on=!!(document.fullscreenElement||document.webkitFullscreenElement);",
                    "function fsLabel(){ const on=fsOn(); setTimeout(()=>{ layout(); centerOn(cur,false); },60);")
    js = js.replace("if(!(document.documentElement.requestFullscreen||document.documentElement.webkitRequestFullscreen)) $('#fsBtn').hidden=true;", "")
    teclas = "  if(e.key==='Escape'){ hidePop(); return closeDrawer(); }"
    assert teclas in js, "lineas.py: no se encontró el manejador de Escape"
    js = js.replace(teclas, "  if(e.key==='Escape'){ hidePop(); if($('#drawer').classList.contains('on')) return closeDrawer(); if(TL.classList.contains('tl-full')){ TL.classList.remove('tl-full'); fsLabel(); return; } if(fsOn()) return; cerrarTL(); return; }\n  if(!(fsOn()||TL.matches(':hover')||TL.contains(document.activeElement))) return;")
    js = js.replace("const $ = s => document.querySelector(s);", f"const TL=document.getElementById('{ID}');\nconst $ = s => TL.querySelector(s);")
    js = js.replace("$('#drawer').classList", "$('#drawer').classList")
    # enlace «← Primera Línea» del topbar: aquí no hace falta
    body = re.sub(r'<a class="volver"[^>]*>.*?</a>',
                  '<button type="button" class="volver" id="tlCerrar" title="Cerrar la línea de tiempo (Esc)" aria-label="Cerrar la línea de tiempo"><span class="ico" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></span><span> Cerrar</span></button>', body)
    body = body.replace('<main class="stage"', '<div class="stage"').replace("</main>", "</div>")   # <main> confunde a Quarto
    body = body.replace('<aside class="drawer"', '<div class="drawer"').replace("</aside>", "</div>")  # <aside> = margen para Quarto

    out = f"""```{{=html}}
<link rel="stylesheet" href="{fonts}">
<style>
{css}
</style>
{mini(js, ID)}
<div id="{ID}" class="linea-tiempo-marco" tabindex="-1" aria-label="Línea de tiempo interactiva" hidden>
{body}
</div>
<script>
(function(){{
{js}
/* --- abrir / cerrar la línea desde la línea pequeña --- */
const MINI=document.getElementById('{ID}-mini');
function abrirTL(){{ TL.hidden=false; MINI.hidden=true; MINI.setAttribute('aria-expanded','true');
  setTimeout(()=>{{ try{{ layout(); centerOn(cur,false); }}catch(_){{}} TL.scrollIntoView({{behavior:'smooth',block:'start'}}); TL.focus({{preventScroll:true}}); }},40); }}
function cerrarTL(){{ const d=document;
  try{{ if(d.fullscreenElement||d.webkitFullscreenElement) (d.exitFullscreen||d.webkitExitFullscreen).call(d); }}catch(_){{}}
  TL.classList.remove('tl-full'); hidePop(); if($('#drawer').classList.contains('on')) closeDrawer();
  TL.hidden=true; MINI.hidden=false; MINI.setAttribute('aria-expanded','false');
  MINI.scrollIntoView({{behavior:'smooth',block:'center'}}); MINI.focus({{preventScroll:true}}); }}
MINI.addEventListener('click',abrirTL);
$('#tlCerrar').addEventListener('click',cerrarTL);
if(location.hash==='#linea') abrirTL();
}})();
</script>
```
"""
    dst.write_text(out, encoding="utf-8")
    print(f"{dst}: {len(out)//1024} KB")

if __name__ == "__main__":
    origen = RAIZ / "estudios" / "lineas"
    destino = RAIZ / "lineas"
    destino.mkdir(exist_ok=True)
    for src in sorted(origen.glob("*.html")):
        embed(src, destino / f"_{src.stem}.html", f"tl-{src.stem}")
        for sub in ("img", "fonts", "mapa", "relieve", "vendor"):   # figuras TikZ, fuentes, atlas (MapLibre, relieve, capas)
            d = origen / src.stem / sub
            if d.is_dir():
                dst = destino / src.stem / sub
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(d, dst)
