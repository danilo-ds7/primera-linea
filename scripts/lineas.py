#!/usr/bin/env python3
"""Integra una línea de tiempo (HTML independiente generado por la skill linea-de-tiempo)
dentro de una página Quarto, con su CSS acotado al contenedor y la pantalla completa sobre
ese mismo contenedor.

Se ejecuta antes de cada render (pre-render en _quarto.yml): toma cada estudios/lineas/<slug>.html
y escribe lineas/_<slug>.html, que lineas/<slug>.qmd incluye con {{< include _<slug>.html >}}.
"""
import re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

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
    #{ID}{{position:relative;height:min(82vh,860px);min-height:560px;border:1px solid var(--rule);border-radius:12px;overflow:hidden;container-type:size;box-shadow:0 30px 50px -30px rgba(19,26,44,.35);font-size:16px;line-height:1.4}}
    #{ID} *{{box-sizing:border-box}}
    #{ID} p,#{ID} h1,#{ID} h2,#{ID} h3{{text-align:left;letter-spacing:0;font-family:var(--f-display)}}
    #{ID} .slide.tl-portada p{{text-align:center}}
    #{ID} .tl-app{{height:100%}}
    #{ID}.tl-full{{position:fixed;inset:0;z-index:3000;height:100vh;height:100dvh;border-radius:0;border:0}}
    #{ID}:fullscreen{{height:100vh;border-radius:0;border:0}}
    #{ID} .scrim{{z-index:2000}} #{ID} .drawer{{z-index:2001}} #{ID} #pop{{z-index:2002}}
    #{ID} .tl-topbar{{z-index:6}}
    @media (max-width:600px){{#{ID}{{height:78vh;height:78dvh;min-height:520px}}}}
    """

    # --- JS: tema, pantalla completa y teclado sobre el contenedor -------------
    js = js.replace("document.documentElement.dataset.theme=t", f"TL.dataset.theme=t")
    js = js.replace("const r=document.documentElement; const dark", "const r=TL; const dark")
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
    js = js.replace("document.addEventListener('keydown',e=>{\n  if(e.key==='Escape'){ hidePop(); return closeDrawer(); }",
                    "document.addEventListener('keydown',e=>{\n  if(e.key==='Escape'){ hidePop(); if($('#drawer').classList.contains('on')) return closeDrawer(); if(TL.classList.contains('tl-full')){ TL.classList.remove('tl-full'); fsLabel(); } return; }\n  if(!(fsOn()||TL.matches(':hover')||TL.contains(document.activeElement))) return;")
    js = js.replace("const $ = s => document.querySelector(s);", f"const TL=document.getElementById('{ID}');\nconst $ = s => TL.querySelector(s);")
    js = js.replace("$('#drawer').classList", "$('#drawer').classList")
    # enlace «← Primera Línea» del topbar: aquí no hace falta
    body = re.sub(r'<a class="volver"[^>]*>.*?</a>', "", body)
    body = body.replace('<main class="stage"', '<div class="stage"').replace("</main>", "</div>")   # <main> confunde a Quarto
    body = body.replace('<aside class="drawer"', '<div class="drawer"').replace("</aside>", "</div>")  # <aside> = margen para Quarto

    out = f"""```{{=html}}
<link rel="stylesheet" href="{fonts}">
<style>
{css}
</style>
<div id="{ID}" class="linea-tiempo-marco" tabindex="-1" aria-label="Línea de tiempo interactiva">
{body}
</div>
<script>
(function(){{
{js}
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
