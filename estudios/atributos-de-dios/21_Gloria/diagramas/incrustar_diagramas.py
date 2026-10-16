"""Incrusta las figuras TikZ de la Conclusión (gloria_esquema_fig.tex, sincronia_fig.tex)
en la presentación, el capítulo suelto, el capítulo del libro y el artículo de la Introducción.
Uso (desde estudios/atributos-de-dios):  python3 21_Gloria/diagramas/incrustar_diagramas.py
Las figuras van entre los marcadores %<fig:NOMBRE> ... %</fig:NOMBRE> para poder volver a incrustarlas."""
import re, pathlib
B = pathlib.Path(__file__).resolve().parents[2]
D = B / "21_Gloria" / "diagramas"
def cuerpo(n):
    t = (D / f"{n}_fig.tex").read_text()
    return t[t.index("\\begin{tikzpicture}"):].strip()
def bloque(n, envoltura):
    fig = cuerpo(n)
    if envoltura and n == "gloria_esquema":
        envoltura = "\\resizebox{\\linewidth}{!}{FIG}"
    if envoltura:
        fig = envoltura.replace("FIG", fig)
    return f"%<fig:{n}>\n{fig}\n%</fig:{n}>"
OBJ = {
  "21_Gloria/body.tex": "\\resizebox{!}{0.88\\textheight}{FIG}",
  "21_Gloria/21_Gloria_capitulo.tex": None,
  "Libro/capitulos/21_gloria.tex": None,
  "00_Introduccion/articulo/body_art.tex": None,
  "00_Introduccion/articulo/Introduccion_Libro.tex": None,
}
PAT = {
  "gloria_esquema": [r"%<fig:gloria_esquema>.*?%</fig:gloria_esquema>",
                     r"\\begin\{tikzpicture\}\\node\[inner sep=0pt\]\{\\includegraphics\[[^\]]*\]\{(img/)?gloria_esquema\.pdf\}\};\\end\{tikzpicture\}",
                     r"\\includegraphics\[[^\]]*\]\{(img/)?gloria_esquema\.pdf\}"],
  "sincronia": [r"%<fig:sincronia>.*?%</fig:sincronia>",
                r"\\begin\{tikzpicture\}\\node\[inner sep=0pt\]\{\\includegraphics\[[^\]]*\]\{(img/)?sincronia\.pdf\}\};\\end\{tikzpicture\}",
                r"\\includegraphics\[[^\]]*\]\{(img/)?sincronia\.pdf\}"],
}
for rel, env in OBJ.items():
    p = B / rel; s = p.read_text(); n0 = s
    for n, pats in PAT.items():
        for pat in pats:
            if re.search(pat, s, flags=re.S):
                s = re.sub(pat, lambda m: bloque(n, env), s, count=1, flags=re.S)
                break
    if s != n0:
        p.write_text(s); print("actualizado", rel)
