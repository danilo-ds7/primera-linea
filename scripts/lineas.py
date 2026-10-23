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
<a class="linea-mini" href="{slug}-linea.html" target="_blank" rel="noopener" aria-label="Abrir la línea de tiempo interactiva en una pestaña nueva">
<span class="lm-head"><span class="lm-eyebrow">Línea de tiempo · {n} hitos</span><span class="lm-cta">Abrir <span aria-hidden="true">↗</span></span></span>
<span class="lm-track"><span class="lm-linea"></span>{"".join(pts)}</span>
</a>
```
"""


def pagina(html: str, slug: str) -> str:
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

    # celular: el menú mostraba botones vacíos (ocultaba también los iconos) y no cabía entero
    cambiar("</style>", """@media (max-width:600px){
  .topbar span.ico{display:inline-grid}
  .topbar{left:10px;justify-content:flex-end;gap:4px}
  .topbar button,.topbar .volver{min-width:0;min-height:30px;padding:6px 8px;display:inline-grid;place-items:center}
}
</style>""")
    return html


if __name__ == "__main__":
    origen = RAIZ / "estudios" / "lineas"
    destino = RAIZ / "lineas"
    destino.mkdir(exist_ok=True)
    for src in sorted(origen.glob("*.html")):
        slug = src.stem
        html = src.read_text(encoding="utf-8")
        (destino / f"_{slug}.html").write_text(mini(html, slug, origen / f"{slug}-mini.json"), encoding="utf-8")
        (destino / f"{slug}-linea.html").write_text(pagina(html, slug), encoding="utf-8")
        print(f"lineas/{slug}-linea.html · lineas/_{slug}.html")
        for sub in RECURSOS:   # figuras TikZ, fuentes, atlas (MapLibre, relieve, capas)
            d = origen / slug / sub
            if d.is_dir():
                dst = destino / slug / sub
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(d, dst)
        for f in (origen / slug).glob("*.css"):   # hojas de estilo propias de la línea (p. ej. tema.css)
            shutil.copy2(f, destino / slug / f.name)
