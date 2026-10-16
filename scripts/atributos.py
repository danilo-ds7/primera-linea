#!/usr/bin/env python3
"""
Series de estudios en LaTeX («Atributos de Dios», «Festividades santas»): convierte los
estudios en páginas del sitio.

Se ejecuta solo antes de cada `quarto render` / `quarto preview` (ver _quarto.yml).
No hay que tocarlo para agregar un estudio: basta con subir la carpeta.

Por cada serie de SERIES (más abajo):
Fuente:  estudios/<carpeta>/NN_Nombre/           (los .tex tal como salen del proyecto de estudio)
Salida:  <salida>/<slug>.qmd                     (página web, generada; no editar a mano)
         <salida>/pdf/<slug>-*.pdf               (descargas)
         <salida>/img/<slug>/...                 (figuras TikZ en SVG e imágenes)

Reglas de detección (por carpeta NN_Nombre):
  - Un .tex con \\documentclass{beamer}  -> presentación (solo PDF).
  - Un .tex con otra clase (article...)  -> capítulo: PDF + página web.
  - La carpeta «Libro» se compila aparte como libro completo.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Cada serie: carpeta de fuentes LaTeX -> carpeta de páginas generadas.
#   requerida: si no genera ninguna página, la publicación falla (para no publicar la serie vacía por error).
SERIES = [
    {"nombre": "Atributos de Dios", "fuente": "atributos-de-dios", "salida": "atributos",
     "etiqueta": "Atributo", "libro_pdf": "la-gloria-de-dios-libro.pdf", "requerida": True},
    {"nombre": "Festividades santas", "fuente": "fiestas-santas", "salida": "festividades",
     "etiqueta": "Fiesta", "libro_pdf": "fiestas-santas-libro.pdf", "requerida": False},
]

# Serie en proceso (las fija usar_serie)
SERIE = SERIES[0]
FUENTE = RAIZ / "estudios" / SERIE["fuente"]
SALIDA = RAIZ / SERIE["salida"]
FILTRO = RAIZ / "scripts" / "atributos.lua"
CACHE = RAIZ / ".atributos-cache"

TIENE_TEX = shutil.which("xelatex") is not None
# pandoc propio o el que trae Quarto
PANDOC = [shutil.which("pandoc")] if shutil.which("pandoc") else [shutil.which("quarto") or "quarto", "pandoc"]
TIENE_CAIRO = shutil.which("pdftocairo") is not None


def usar_serie(serie):
    global SERIE, FUENTE, SALIDA
    SERIE = serie
    FUENTE = RAIZ / "estudios" / serie["fuente"]
    SALIDA = RAIZ / serie["salida"]


def log(msg):
    print(f"[{SERIE['salida']}] {msg}", flush=True)
    if os.environ.get("GITHUB_ACTIONS") and msg.startswith(("ERROR", "AVISO")):
        print(f"::warning title={SERIE['nombre']}::{msg}", flush=True)


# --------------------------------------------------------------------------- utilidades LaTeX

def leer_llave(s, i, abre="{", cierra="}"):
    """s[i] == abre. Devuelve (contenido, índice después del cierre)."""
    assert s[i] == abre
    nivel, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == abre:
            nivel += 1
        elif c == cierra:
            nivel -= 1
            if nivel == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("llave sin cerrar")


def saltar_espacios(s, i):
    while i < len(s) and s[i] in " \t":
        i += 1
    return i


def reemplazar_comando(s, nombre, fn, nargs=1):
    r"""Reemplaza \nombre{a}{b}... por fn(a, b, ...)."""
    patron = re.compile(r"\\" + re.escape(nombre) + r"(?![A-Za-z@])")
    salida, pos = [], 0
    while True:
        m = patron.search(s, pos)
        if not m:
            break
        j = saltar_espacios(s, m.end())
        args = []
        try:
            for _ in range(nargs):
                j = saltar_espacios(s, j)
                if j >= len(s) or s[j] != "{":
                    raise ValueError
                a, j = leer_llave(s, j)
                args.append(a)
        except ValueError:
            salida.append(s[pos:m.end()])
            pos = m.end()
            continue
        salida.append(s[pos:m.start()])
        salida.append(fn(*args))
        pos = j
    salida.append(s[pos:])
    return "".join(salida)


def quitar_comentarios(s):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", l) for l in s.splitlines())


def texto_plano(s):
    """Versión en texto de un fragmento LaTeX corto (para títulos y descripciones)."""
    r = subprocess.run(PANDOC + ["-f", "latex", "-t", "plain", "--wrap=none"],
                       input=s, capture_output=True, text=True)
    return re.sub(r"\s+", " ", r.stdout).strip()


def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def es_principal(p):
    t = quitar_comentarios(p.read_text(errors="ignore"))
    return bool(re.search(r"^\s*\\documentclass", t, flags=re.M)) and "\\begin{document}" in t


def clase_documento(tex):
    m = re.search(r"\\documentclass(\[[^\]]*\])?\{([^}]*)\}", tex)
    return m.group(2) if m else None


# --------------------------------------------------------------------------- compilación PDF

def huella(carpeta):
    h = hashlib.sha1()
    for p in sorted(carpeta.rglob("*")):
        if p.is_file() and p.suffix in {".tex", ".jpg", ".png", ".pdf", ".ttf", ".otf", ".sty", ".cls"} \
                and not (p.suffix == ".pdf"):
            h.update(str(p.relative_to(carpeta)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def compilar(tex_path):
    """Compila con XeLaTeX si el PDF falta o la carpeta cambió. Devuelve la ruta del PDF o None."""
    pdf = tex_path.with_suffix(".pdf")
    sello = CACHE / (slugify(str(tex_path.relative_to(RAIZ / "estudios"))) + ".sha1")
    actual = huella(tex_path.parent)
    if pdf.exists() and sello.exists() and sello.read_text() == actual:
        return pdf
    if not TIENE_TEX:
        if pdf.exists():
            log(f"sin XeLaTeX: uso el PDF existente de {tex_path.name}")
            return pdf
        log(f"AVISO: falta XeLaTeX, no se pudo compilar {tex_path.name}")
        return None
    log(f"compilando {tex_path.relative_to(FUENTE)}")
    for pasada in range(3):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                           cwd=tex_path.parent, capture_output=True, text=True)
        if r.returncode != 0:
            lineas = [l for l in r.stdout.splitlines() if l.startswith("!")][:3]
            log(f"ERROR compilando {tex_path.name}: {' | '.join(lineas)}")
            return pdf if pdf.exists() else None
    CACHE.mkdir(exist_ok=True)
    sello.write_text(actual)
    return pdf


# --------------------------------------------------------------------------- TikZ -> SVG

def figuras_tikz(tex, preambulo, carpeta_tex, destino, slug):
    """Extrae cada tikzpicture, la compila aparte y la reemplaza por \\includegraphics{svg}."""
    figuras = re.findall(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", tex, flags=re.S)
    if not figuras:
        return tex
    destino.mkdir(parents=True, exist_ok=True)
    clave = hashlib.sha1((preambulo + "".join(figuras)).encode()).hexdigest()[:12]
    listas = [destino / f"fig-{i + 1}.svg" for i in range(len(figuras))]
    sello = destino / f".tikz-{clave}"
    if not sello.exists() or not all(p.exists() for p in listas):
        if not (TIENE_TEX and TIENE_CAIRO):
            log("AVISO: sin XeLaTeX/pdftocairo, las figuras TikZ no se generan")
        else:
            trabajo = CACHE / f"tikz-{SERIE['salida']}-{slug}"
            if trabajo.exists():
                shutil.rmtree(trabajo)
            shutil.copytree(carpeta_tex, trabajo, ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log"))
            pre = re.sub(r"\\usepackage(\[[^\]]*\])?\{geometry\}", "", preambulo)
            doc = (pre + "\n\\usepackage[active,tightpage]{preview}\\PreviewEnvironment{tikzpicture}"
                   "\\setlength\\PreviewBorder{6pt}\\pagestyle{empty}\n\\begin{document}\n"
                   + "\n\n".join(figuras) + "\n\\end{document}\n")
            (trabajo / "figuras.tex").write_text(doc)
            ok = True
            for _ in range(2):
                r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "figuras.tex"],
                                   cwd=trabajo, capture_output=True, text=True)
                if r.returncode != 0:
                    ok = False
                    log(f"ERROR en figuras TikZ de {slug}")
                    break
            if ok:
                for i, p in enumerate(listas):
                    subprocess.run(["pdftocairo", "-svg", "-f", str(i + 1), "-l", str(i + 1),
                                    str(trabajo / "figuras.pdf"), str(p)], check=False)
                for viejo in destino.glob(".tikz-*"):
                    viejo.unlink()
                sello.write_text("ok")
    contador = iter(range(1, len(figuras) + 1))
    return re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
                  lambda m: f"\\includegraphics{{img/{slug}/fig-{next(contador)}.svg}}", tex, flags=re.S)


# --------------------------------------------------------------------------- LaTeX -> Markdown

def entornos_definidos(preambulo):
    """Entornos propios (tcolorbox / newenvironment): nombre -> info."""
    info = {}
    for m in re.finditer(r"\\(newtcolorbox|newenvironment)\{(\w+)\}(\[(\d)\])?(\[[^\]]*\])?", preambulo):
        tipo, nombre, nargs, opcional = m.group(1), m.group(2), m.group(4), m.group(5)
        # cuerpo de la definición (hasta la siguiente definición)
        resto = preambulo[m.end():]
        fin = re.search(r"\\(newtcolorbox|newenvironment|newcommand|title)\b", resto)
        cuerpo = resto[:fin.start()] if fin else resto
        d = {"nargs": int(nargs or 0), "opcional": opcional is not None, "cuerpo": cuerpo}
        mt = re.search(r"\\begin\{tabular\}\{((?:[^{}]|\{[^{}]*\})*)\}(.*?)\\midrule", cuerpo, flags=re.S)
        if mt:
            d["tabla"] = mt.group(1)
            d["encabezado"] = mt.group(2).replace("\\toprule", "").strip()
        if "after upper" in cuerpo:
            d["fuente_abajo"] = ", RVR1960" if "RVR1960" in cuerpo else ""
        mtit = re.search(r"\\bfseries\\color\{\w+\}([^}]+)\}", cuerpo)
        if mtit and nombre == "filologia":
            d["rotulo"] = mtit.group(1).strip()
        mt2 = re.search(r"title=\{([^{}]*)#1([^{}]*)\}", cuerpo)
        if mt2:
            d["titulo_patron"] = (mt2.group(1), mt2.group(2))
        info[nombre] = d
    return info


def columnas(spec):
    spec = re.sub(r"[@<>!]\{(?:[^{}]|\{[^{}]*\})*\}", "", spec)
    spec = re.sub(r"\*\{(\d+)\}\{([^}]*)\}", lambda m: m.group(2) * int(m.group(1)), spec)
    return len(re.findall(r"[lcrXpmbLPCR](?:\{[^}]*\})?", spec)) or 1


def preparar(tex, slug, carpeta_tex, destino_img):
    """Deja el cuerpo del .tex en una forma que pandoc entiende bien."""
    tex = quitar_comentarios(tex)
    preambulo, _, cuerpo = tex.partition("\\begin{document}")
    cuerpo = cuerpo.split("\\end{document}")[0]

    # Título, subtítulo y resumen
    titulo, subtitulo = "", ""
    mt = re.search(r"\\title\{", preambulo)
    if mt:
        crudo, _ = leer_llave(preambulo, mt.end() - 1)
        partes = re.split(r"\\\\(?:\[[^\]]*\])?", crudo)
        limpio = lambda t: texto_plano(re.sub(r"\\(color\{\w+\}|bfseries|mdseries|large|Large|normalsize|small)", "", t))
        titulo = limpio(partes[0])
        subtitulo = " · ".join(filter(None, (limpio(p) for p in partes[1:])))
    resumen = ""
    ma = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", cuerpo, flags=re.S)
    if ma:
        resumen = ma.group(1)
        cuerpo = cuerpo.replace(ma.group(0), "\\begin{resumen}" + ma.group(1) + "\\end{resumen}")

    cuerpo = figuras_tikz(cuerpo, preambulo, carpeta_tex, destino_img, slug)

    entornos = entornos_definidos(preambulo)

    # Comandos con significado propio -> entornos (pandoc los convierte en bloques con clase)
    cuerpo = reemplazar_comando(cuerpo, "fuente", lambda a: f"\n\\begin{{fuente}}{a}\\end{{fuente}}\n")
    cuerpo = reemplazar_comando(cuerpo, "hebverso",
                                lambda a: f"\n\\begin{{hebverso}}\\foreignlanguage{{hebrew}}{{{a}}}\\end{{hebverso}}\n")
    cuerpo = reemplazar_comando(cuerpo, "refapa", lambda a: f"\n\\begin{{refapa}}{a}\\end{{refapa}}\n")
    cuerpo = reemplazar_comando(cuerpo, "precision",
                                lambda a: f"\n\\begin{{nota}}\\begin{{rotulo}}Precisión\\end{{rotulo}}{a}\\end{{nota}}\n")
    for quitar in ["maketitle", "tableofcontents", "newpage", "clearpage", "noindent", "centering",
                   "smallskip", "medskip", "bigskip", "par"]:
        cuerpo = re.sub(r"\\" + quitar + r"(?![A-Za-z@])", "\n\n" if quitar == "par" else "", cuerpo)
    cuerpo = re.sub(r"\\thispagestyle\{[^}]*\}", "", cuerpo)
    cuerpo = re.sub(r"\\renewcommand\{\\arraystretch\}\{[^}]*\}", "", cuerpo)
    cuerpo = re.sub(r"\\(vspace|hspace)\*?\{[^}]*\}", "", cuerpo)

    # Entornos propios: título opcional/obligatorio -> rótulo dentro del bloque; tablas integradas
    for nombre, d in entornos.items():
        patron = re.compile(r"\\begin\{" + nombre + r"\}")
        partes, pos = [], 0
        for m in patron.finditer(cuerpo):
            if m.start() < pos:
                continue
            j = m.end()
            arg = None
            if d["nargs"]:
                j2 = saltar_espacios(cuerpo, j)
                if d["opcional"] and j2 < len(cuerpo) and cuerpo[j2] == "[":
                    arg, j = leer_llave(cuerpo, j2, "[", "]")
                elif not d["opcional"] and j2 < len(cuerpo) and cuerpo[j2] == "{":
                    arg, j = leer_llave(cuerpo, j2)
            fin = cuerpo.find("\\end{" + nombre + "}", j)
            contenido = cuerpo[j:fin]
            if "tabla" in d:
                n = columnas(d["tabla"])
                contenido = (f"\\begin{{tabular}}{{{'l' * n}}}\n{d['encabezado']}\n" + contenido.strip()
                             + "\n\\end{tabular}")
            rot = ""
            if arg and "titulo_patron" in d:
                rot = f"\\begin{{rotulo}}{d['titulo_patron'][0]}{arg}{d['titulo_patron'][1]}\\end{{rotulo}}"
            elif arg and "fuente_abajo" not in d:
                rot = f"\\begin{{rotulo}}{d.get('rotulo', '') + ': ' if d.get('rotulo') else ''}{arg}\\end{{rotulo}}"
            elif d.get("rotulo") and not arg:
                rot = f"\\begin{{rotulo}}{d['rotulo']}\\end{{rotulo}}"
            pie = ""
            if arg and "fuente_abajo" in d:
                pie = f"\n\\begin{{fuente}}({arg}{d['fuente_abajo']})\\end{{fuente}}\n"
            partes.append(cuerpo[pos:m.start()])
            partes.append(f"\\begin{{{nombre}}}{rot}\n{contenido}{pie}\\end{{{nombre}}}")
            pos = fin + len("\\end{" + nombre + "}")
        partes.append(cuerpo[pos:])
        cuerpo = "".join(partes)

    # Tablas: columnas a l/c/r simples
    cuerpo = re.sub(r"\\begin\{tabular\}(\{(?:[^{}]|\{[^{}]*\})*\})",
                    lambda m: "\\begin{tabular}{" + "l" * columnas(m.group(1)[1:-1]) + "}", cuerpo)
    cuerpo = re.sub(r"\\begin\{tabularx\}\{[^}]*\}(\{(?:[^{}]|\{[^{}]*\})*\})",
                    lambda m: "\\begin{tabular}{" + "l" * columnas(m.group(1)[1:-1]) + "}", cuerpo)
    cuerpo = cuerpo.replace("\\end{tabularx}", "\\end{tabular}")

    # Macros sencillas que pandoc sabe expandir
    macros = r"""
\newcommand{\heb}[1]{\foreignlanguage{hebrew}{#1}}
\newcommand{\hebl}[1]{\foreignlanguage{hebrew}{#1}}
\newcommand{\grc}[1]{\foreignlanguage{greek}{#1}}
\newcommand{\SENOR}{\textsc{Señor}}
\newcommand{\destacar}[1]{\textbf{#1}}
"""
    propias = {"heb", "hebl", "grc", "SENOR", "destacar", "fuente", "hebverso", "refapa", "precision"}
    for m in re.finditer(r"\\newcommand\{\\(\w+)\}(\[\d\])?(\[[^\]]*\])?\{", preambulo):
        if m.group(1) in propias:
            continue
        try:
            cuerpo_def, _ = leer_llave(preambulo, m.end() - 1)
        except ValueError:
            continue
        if any(x in cuerpo_def for x in ["\\hangindent", "\\hfill", "\\par", "tcolorbox"]):
            continue
        macros += preambulo[m.start():m.end() - 1] + "{" + cuerpo_def + "}\n"

    return titulo, subtitulo, resumen, macros + cuerpo


def a_markdown(latex):
    r = subprocess.run(PANDOC + ["-f", "latex", "-t", "markdown-raw_html-native_spans-simple_tables-multiline_tables-grid_tables+pipe_tables",
                        "--wrap=none", "--shift-heading-level-by=1", "--lua-filter", str(FILTRO)],
                       input=latex, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    for aviso in r.stderr.splitlines():
        if "Skipped" in aviso or "unknown" in aviso.lower():
            pass
    return r.stdout


# --------------------------------------------------------------------------- páginas

def fecha(carpeta):
    """Fecha del último cambio de la carpeta según git (o del archivo, si no hay git)."""
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(carpeta)],
                       cwd=RAIZ, capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    import datetime
    t = max(p.stat().st_mtime for p in carpeta.rglob("*.tex"))
    return datetime.date.fromtimestamp(t).isoformat()


def yaml_str(t):
    return json.dumps(t, ensure_ascii=False)


def escribir_pagina(estudio, md):
    e = estudio
    descargas = []
    for d in e["pdfs"]:
        descargas.append(f'<a class="btn {"primary" if not descargas else "ghost"}" href="pdf/{d["archivo"]}" download>'
                         f'{d["etiqueta"]}</a>')
    cabecera = f"""---
title: {yaml_str(e["titulo"])}
subtitle: {yaml_str(e["subtitulo"])}
description: {yaml_str(e["descripcion"])}
date: {e["fecha"]}
categories: [{yaml_str(SERIE["nombre"])}]
order: {e["orden"]}
numero: {yaml_str(e["etiqueta_num"])}
body-classes: estudio-tex
toc: true
toc-title: "En este estudio"
toc-depth: 2
---

<!-- Página generada por scripts/atributos.py a partir de {e["fuente"]}. No editar: se reemplaza en cada publicación. -->

```{{=html}}
<div class="descargas">{"".join(descargas)}</div>
```

"""
    (SALIDA / f"{e['slug']}.qmd").write_text(cabecera + md)


def procesar_estudio(carpeta, orden):
    texs = sorted(p for p in carpeta.rglob("*.tex") if es_principal(p))
    capitulo = next((p for p in texs if clase_documento(p.read_text()) != "beamer"), None)
    presentaciones = [p for p in texs if clase_documento(p.read_text()) == "beamer"]
    if not capitulo:
        log(f"AVISO: {carpeta.name} no tiene capítulo (solo presentación); se omite la página web")
        return None

    m = re.match(r"(\d+)_(.+)", carpeta.name)
    numero = int(m.group(1)) if m else orden
    tex = capitulo.read_text()
    slug_base = slugify(m.group(2) if m else carpeta.name)

    titulo, subtitulo, resumen, latex = preparar(tex, slug_base, capitulo.parent, SALIDA / "img" / slug_base)
    for img in capitulo.parent.glob("*"):
        if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".svg"} and img.stem not in {"papiro", "papiro_crema"}:
            (SALIDA / "img" / slug_base).mkdir(parents=True, exist_ok=True)
            shutil.copy2(img, SALIDA / "img" / slug_base / img.name)
            latex = latex.replace("{" + img.name + "}", "{img/" + slug_base + "/" + img.name + "}")
    md = a_markdown(latex)

    pdfs = []
    pdf = compilar(capitulo)
    if pdf:
        nombre = f"{slug_base}-estudio.pdf"
        shutil.copy2(pdf, SALIDA / "pdf" / nombre)
        pdfs.append({"archivo": nombre, "etiqueta": "Descargar el estudio (PDF)"})
    for p in presentaciones:
        pdf = compilar(p)
        if pdf:
            nombre = f"{slug_base}-presentacion.pdf"
            shutil.copy2(pdf, SALIDA / "pdf" / nombre)
            pdfs.append({"archivo": nombre, "etiqueta": "Descargar la presentación (PDF)"})

    descripcion = texto_plano(resumen).split(". ")[0].rstrip(".") + "." if resumen else ""
    estudio = {
        "slug": slug_base, "titulo": titulo or carpeta.name, "subtitulo": subtitulo,
        "descripcion": descripcion, "orden": numero,
        "etiqueta_num": "Introducción" if numero == 0 else f"{SERIE['etiqueta']} {numero}",
        "fuente": str(capitulo.relative_to(RAIZ)), "pdfs": pdfs, "fecha": fecha(carpeta),
    }
    escribir_pagina(estudio, md)
    log(f"página lista: {SERIE['salida']}/{slug_base}.qmd ({len(pdfs)} PDF)")
    return estudio


def procesar_serie(serie):
    """Genera las páginas de una serie. Devuelve False si una serie requerida quedó vacía."""
    usar_serie(serie)
    (SALIDA / "pdf").mkdir(parents=True, exist_ok=True)
    if not FUENTE.exists():
        log("sin carpeta de estudios todavía")
        (SALIDA / "serie.json").write_text(json.dumps({"estudios": [], "libro": {}}, indent=2))
        return not serie["requerida"]
    for viejo in SALIDA.glob("*.qmd"):
        viejo.unlink()

    estudios = []
    for i, carpeta in enumerate(sorted(p for p in FUENTE.iterdir() if p.is_dir())):
        if carpeta.name.lower() == "libro" or carpeta.name.startswith((".", "_")):
            continue
        try:
            e = procesar_estudio(carpeta, i)
            if e:
                estudios.append(e)
        except Exception as ex:  # un estudio con problemas no debe botar el sitio
            log(f"ERROR en {carpeta.name}: {ex}")

    libro = {}
    maestro = next((p for p in (FUENTE / "Libro").glob("*.tex")
                    if "\\begin{document}" in quitar_comentarios(p.read_text(errors="ignore"))), None) \
        if (FUENTE / "Libro").exists() else None
    if maestro:
        pdf = compilar(maestro)
        if pdf:
            shutil.copy2(pdf, SALIDA / "pdf" / serie["libro_pdf"])
            libro = {"archivo": "pdf/" + serie["libro_pdf"]}

    (SALIDA / "serie.json").write_text(json.dumps({"estudios": estudios, "libro": libro},
                                                  ensure_ascii=False, indent=2))
    if not estudios:
        if serie["requerida"]:
            log("ERROR: no se generó ninguna página de la serie")
            return False
        log("todavía no hay estudios publicados")
    return True


def main():
    ok = [procesar_serie(s) for s in SERIES]
    if not all(ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
