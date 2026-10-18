#!/usr/bin/env python3
"""
Predicaciones: convierte las carpetas de estudios/predicaciones/ en la sección «Predicaciones» del sitio.

Se ejecuta solo antes de cada `quarto render` / `quarto preview` (ver _quarto.yml) y en GitHub Actions.
No hay que tocarlo para agregar una predicación: basta con subir la carpeta.

Fuente (lo que se sube):
  estudios/predicaciones/<tipo>/NN_Nombre/          una carpeta por predicación
      *.pdf                                          la predicación para descargar (o un .tex, que se compila)
      *.mp3 | *.m4a | *.ogg | *.wav                  el audio (opcional)
      ficha.txt                                      datos de la predicación (opcional, ver README)
  estudios/predicaciones/series/NN_Serie/            una carpeta por serie
      serie.txt                                      título y descripción de la serie (opcional)
      NN_Nombre/                                     cada predicación de la serie, igual que arriba

  Tipos: biograficas, tematicas, autoayuda, otras (y series).

Salida (generada; no editar a mano, está en .gitignore):
  predicaciones/<slug>.qmd                           página de cada predicación
  predicaciones/pdf/<slug>.pdf                       descarga
  predicaciones/audio/<slug>.<ext>                   audio
  predicaciones/_indice.md                           tarjetas de la página Predicaciones (la incluye predicaciones.qmd)
"""
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "estudios" / "predicaciones"
SALIDA = RAIZ / "predicaciones"

TIPOS = [
    # carpeta, nombre en plural (sección), nombre en singular (etiqueta), descripción de la sección
    ("biograficas", "Biográficas", "Predicación biográfica",
     "La vida de un personaje de la Escritura leída a la luz del Dios que lo llamó."),
    ("tematicas", "Temáticas", "Predicación temática",
     "Un tema recorrido por toda la Biblia, dejando que la Escritura se explique con la Escritura."),
    ("autoayuda", "Autoayuda", "Autoayuda",
     "La Palabra aplicada a la vida diaria: luchas, decisiones y esperanza."),
    ("otras", "Otras predicaciones", "Predicación",
     "Exposiciones de un pasaje y predicaciones de ocasión."),
]
AUDIO = {".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".aac": "audio/aac", ".ogg": "audio/ogg",
         ".oga": "audio/ogg", ".opus": "audio/ogg", ".wav": "audio/wav"}
LIMITE_GITHUB = 95 * 1024 * 1024   # GitHub rechaza archivos de más de 100 MB

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def log(msg):
    print(f"[predicaciones] {msg}", flush=True)
    if os.environ.get("GITHUB_ACTIONS") and msg.startswith(("ERROR", "AVISO")):
        print(f"::warning title=Predicaciones::{msg}", flush=True)


# --------------------------------------------------------------------------- utilidades

def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def nombre_legible(carpeta):
    """«03_Abraham_el_peregrino» -> (3, «Abraham el peregrino»)."""
    m = re.match(r"(\d+)[_\-\s]+(.+)", carpeta)
    numero, resto = (int(m.group(1)), m.group(2)) if m else (None, carpeta)
    texto = resto.replace("_", " ").strip()
    return numero, texto[:1].upper() + texto[1:]


def leer_ficha(ruta):
    """Lee un archivo de líneas «clave: valor». Las claves no distinguen mayúsculas ni tildes."""
    datos = {}
    if not ruta or not ruta.exists():
        return datos
    clave = None
    for linea in ruta.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-zÁÉÍÓÚáéíóúñÑ ]+):\s*(.*)$", linea)
        if m and not linea.startswith((" ", "\t")):
            clave = slugify(m.group(1)).replace("-", "_")
            datos[clave] = m.group(2).strip().strip('"')
        elif clave:   # continuación de un valor largo (por ejemplo, la descripción)
            datos[clave] = (datos[clave] + " " + linea.strip()).strip()
    return datos


def buscar_ficha(carpeta, *nombres):
    for n in nombres:
        for p in carpeta.iterdir():
            if p.is_file() and p.name.lower() == n:
                return p
    return None


def fecha_iso(texto):
    """Acepta 2026-10-18, 18-10-2026 o 18/10/2026. Devuelve AAAA-MM-DD o None."""
    if not texto:
        return None
    texto = texto.strip()
    for formato in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(texto, formato).date().isoformat()
        except ValueError:
            pass
    log(f"AVISO: no entendí la fecha «{texto}» (usa AAAA-MM-DD)")
    return None


def fecha_larga(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def fecha_git(carpeta):
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(carpeta)],
                       cwd=RAIZ, capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    t = max((p.stat().st_mtime for p in carpeta.rglob("*") if p.is_file()), default=0)
    return datetime.date.fromtimestamp(t).isoformat() if t else datetime.date.today().isoformat()


def duracion(audio):
    """Duración «42 min» con ffprobe, si está instalado."""
    if not shutil.which("ffprobe"):
        return ""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(audio)], capture_output=True, text=True)
    try:
        s = float(r.stdout.strip())
    except ValueError:
        return ""
    minutos = round(s / 60)
    if minutos >= 60:
        return f"{minutos // 60} h {minutos % 60:02d} min"
    return f"{max(minutos, 1)} min"


def compilar_tex(carpeta):
    """Si la predicación viene en LaTeX y sin PDF, la compila con XeLaTeX."""
    texs = [p for p in carpeta.glob("*.tex") if "\\begin{document}" in p.read_text(errors="ignore")]
    if not texs:
        return None
    tex = texs[0]
    pdf = tex.with_suffix(".pdf")
    if pdf.exists() and pdf.stat().st_mtime >= tex.stat().st_mtime:
        return pdf
    if not shutil.which("xelatex"):
        log(f"AVISO: falta XeLaTeX, no se pudo compilar {tex.name}")
        return pdf if pdf.exists() else None
    log(f"compilando {tex.relative_to(FUENTE)}")
    for _ in range(3):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                           cwd=carpeta, capture_output=True, text=True)
        if r.returncode != 0:
            lineas = [l for l in r.stdout.splitlines() if l.startswith("!")][:3]
            log(f"ERROR compilando {tex.name}: {' | '.join(lineas)}")
            break
    return pdf if pdf.exists() else None


def esc(t):
    return html.escape(t or "", quote=True)


def yaml_str(t):
    return json.dumps(t or "", ensure_ascii=False)


# --------------------------------------------------------------------------- lectura

def leer_predicacion(carpeta, orden, tipo, serie=None):
    numero, nombre = nombre_legible(carpeta.name)
    ficha = leer_ficha(buscar_ficha(carpeta, "ficha.txt", "ficha.yml", "ficha.yaml", "ficha.md"))

    pdfs = sorted(p for p in carpeta.glob("*.pdf"))
    pdf = pdfs[0] if pdfs else compilar_tex(carpeta)
    audios = sorted(p for p in carpeta.iterdir() if p.is_file() and p.suffix.lower() in AUDIO)
    audio_url = ficha.get("audio", "")
    if audio_url and not re.match(r"https?://", audio_url):
        audio_url = ""

    if not pdf and not audios and not audio_url:
        log(f"AVISO: {carpeta.relative_to(FUENTE)} no tiene PDF ni audio; se omite")
        return None
    for p in [pdf, *audios]:
        if p and p.stat().st_size > LIMITE_GITHUB:
            log(f"AVISO: {p.name} pesa {p.stat().st_size // (1024 * 1024)} MB; "
                "GitHub no acepta archivos de más de 100 MB (comprímelo o usa «audio:» con un enlace)")

    return {
        "carpeta": carpeta, "numero": numero if numero is not None else orden,
        "titulo": ficha.get("titulo") or nombre,
        "pasaje": ficha.get("pasaje") or ficha.get("texto") or ficha.get("cita") or "",
        "descripcion": ficha.get("descripcion") or ficha.get("resumen") or "",
        "lugar": ficha.get("lugar") or ficha.get("iglesia") or "",
        "fecha_predicada": fecha_iso(ficha.get("fecha")),
        "tipo": tipo, "serie": serie, "pdf": pdf, "audio": audios[0] if audios else None,
        "audio_url": audio_url,
    }


def leer_todo():
    tipos = {clave: [] for clave, *_ in TIPOS}
    series = []
    if not FUENTE.exists():
        return tipos, series
    conocidas = {c for c, *_ in TIPOS} | {"series"}
    for p in sorted(FUENTE.iterdir()):
        if p.is_dir() and p.name not in conocidas and not p.name.startswith((".", "_")):
            log(f"AVISO: carpeta «{p.name}» no es un tipo conocido "
                f"({', '.join(sorted(conocidas))}); se omite")

    for clave, *_ in TIPOS:
        base = FUENTE / clave
        if not base.exists():
            continue
        for i, c in enumerate(sorted(x for x in base.iterdir() if x.is_dir() and not x.name.startswith((".", "_")))):
            p = leer_predicacion(c, i + 1, clave)
            if p:
                tipos[clave].append(p)

    base = FUENTE / "series"
    if base.exists():
        for i, s in enumerate(sorted(x for x in base.iterdir() if x.is_dir() and not x.name.startswith((".", "_")))):
            numero, nombre = nombre_legible(s.name)
            ficha = leer_ficha(buscar_ficha(s, "serie.txt", "serie.yml", "serie.yaml", "serie.md"))
            serie = {"titulo": ficha.get("titulo") or nombre,
                     "descripcion": ficha.get("descripcion") or "",
                     "slug": "serie-" + slugify(ficha.get("titulo") or nombre), "predicaciones": []}
            for j, c in enumerate(sorted(x for x in s.iterdir() if x.is_dir() and not x.name.startswith((".", "_")))):
                p = leer_predicacion(c, j + 1, "series", serie)
                if p:
                    serie["predicaciones"].append(p)
            if serie["predicaciones"]:
                series.append(serie)
            else:
                log(f"AVISO: la serie «{serie['titulo']}» todavía no tiene predicaciones")
    return tipos, series


# --------------------------------------------------------------------------- escritura

def etiqueta_tipo(p):
    if p["serie"]:
        return f"Serie · {p['serie']['titulo']}"
    return next(singular for c, _, singular, _ in TIPOS if c == p["tipo"])


def preparar_archivos(todas):
    usados = set()
    for p in todas:
        slug = slugify(p["titulo"]) or "predicacion"
        if slug in usados:
            slug = f"{slug}-{slugify(p['carpeta'].parent.name)}"
        n, base = 2, slug
        while slug in usados:
            slug, n = f"{base}-{n}", n + 1
        usados.add(slug)
        p["slug"] = slug
        if p["pdf"]:
            shutil.copy2(p["pdf"], SALIDA / "pdf" / f"{slug}.pdf")
            p["pdf_web"] = f"pdf/{slug}.pdf"
        if p["audio"]:
            ext = p["audio"].suffix.lower()
            shutil.copy2(p["audio"], SALIDA / "audio" / f"{slug}{ext}")
            p["audio_web"] = f"audio/{slug}{ext}"
            p["audio_tipo"] = AUDIO[ext]
            p["duracion"] = duracion(p["audio"])
        elif p["audio_url"]:
            p["audio_web"] = p["audio_url"]
            ext = Path(p["audio_url"].split("?")[0]).suffix.lower()
            p["audio_tipo"] = AUDIO.get(ext, "")
            p["duracion"] = ""
        p["fecha"] = p["fecha_predicada"] or fecha_git(p["carpeta"])


def reproductor(p, compacto=False):
    if not p.get("audio_web"):
        return ""
    tipo = f' type="{p["audio_tipo"]}"' if p.get("audio_tipo") else ""
    clase = "pred-audio compacto" if compacto else "pred-audio"
    return (f'<audio class="{clase}" controls preload="none">'
            f'<source src="{esc(p["audio_web"])}"{tipo}>'
            f'Tu navegador no reproduce audio: <a href="{esc(p["audio_web"])}">descarga el audio</a>.</audio>')


def escribir_pagina(p, anterior=None, siguiente=None):
    # Título, pasaje (subtítulo), tipo (categorías), descripción y fecha ya los muestra la cabecera de Quarto.
    meta = []
    if p["lugar"]:
        meta.append(f'<span>{esc(p["lugar"])}</span>')
    if p.get("duracion"):
        meta.append(f'<span>{p["duracion"]}</span>')

    botones = []
    if p.get("pdf_web"):
        botones.append(f'<a class="btn primary" href="{p["pdf_web"]}" download>Descargar la predicación (PDF)</a>')
    if p.get("audio_web"):
        extra = " download" if not p["audio_web"].startswith("http") else ' target="_blank" rel="noopener"'
        botones.append(f'<a class="btn ghost" href="{esc(p["audio_web"])}"{extra}>Descargar el audio</a>')

    lector = ""
    if p.get("pdf_web"):
        lector = (f'<div class="pred-pdf"><object data="{p["pdf_web"]}#view=FitH" type="application/pdf">'
                  f'<p>Este navegador no muestra el PDF aquí. <a href="{p["pdf_web"]}">Ábrelo o descárgalo</a>.</p>'
                  f'</object></div>')

    nav = ""
    if p["serie"]:
        s = p["serie"]
        partes = [f'<a class="pred-serie-volver" href="../predicaciones.html#{s["slug"]}">'
                  f'Serie: {esc(s["titulo"])} · {s["predicaciones"].index(p) + 1} de {len(s["predicaciones"])}</a>']
        if anterior:
            partes.append(f'<a class="btn ghost" href="{anterior["slug"]}.html">← {esc(anterior["titulo"])}</a>')
        if siguiente:
            partes.append(f'<a class="btn ghost" href="{siguiente["slug"]}.html">{esc(siguiente["titulo"])} →</a>')
        nav = f'<nav class="pred-serie-nav">{"".join(partes)}</nav>'

    categorias = ["Predicaciones", etiqueta_tipo(p) if not p["serie"] else p["serie"]["titulo"]]

    texto = f"""---
title: {yaml_str(p["titulo"])}
subtitle: {yaml_str(p["pasaje"])}
description: {yaml_str(p["descripcion"] or (p["pasaje"] and f"Predicación sobre {p['pasaje']}."))}
date: {p["fecha"]}
categories: [{", ".join(yaml_str(c) for c in categorias)}]
body-classes: predicacion-pag
toc: false
language:
  title-block-published: "{'Predicada el' if p['fecha_predicada'] else 'Fecha de publicación'}"
---

<!-- Página generada por scripts/predicaciones.py a partir de {p["carpeta"].relative_to(RAIZ)}. No editar: se reemplaza en cada publicación. -->

```{{=html}}
<div class="pred-cabecera">
<div class="pred-meta">{"".join(meta)}</div>
{reproductor(p)}
<div class="descargas">{"".join(botones)}</div>
{nav}
</div>
{lector}
<p class="pred-volver"><a href="../predicaciones.html">← Todas las predicaciones</a></p>
```
"""
    (SALIDA / f"{p['slug']}.qmd").write_text(texto, encoding="utf-8")


def tarjeta(p, num=None):
    meta = []
    if p["pasaje"]:
        meta.append(f'<span class="pred-pasaje">{esc(p["pasaje"])}</span>')
    if p.get("duracion"):
        meta.append(f'<span>{p["duracion"]}</span>')
    formatos = []
    if p.get("audio_web"):
        formatos.append("Audio")
    if p.get("pdf_web"):
        formatos.append("PDF")
    rotulo = f"Predicación {num}" if num else etiqueta_tipo(p)
    desc = f'<p>{esc(p["descripcion"])}</p>' if p["descripcion"] else ""
    return (f'<article class="pred-card">'
            f'<a class="pred-card-link" href="predicaciones/{p["slug"]}.html">'
            f'<span class="attr-num">{esc(rotulo)}</span><h3>{esc(p["titulo"])}</h3>'
            f'<span class="pred-meta">{"".join(meta)}</span>{desc}</a>'
            f'{reproductor(p, compacto=True)}'
            f'<a class="pred-card-pie" href="predicaciones/{p["slug"]}.html">'
            f'<span>{" · ".join(formatos)}</span><b>{"Escuchar y descargar" if p.get("audio_web") else "Leer y descargar"} →</b></a>'
            f'</article>')


def escribir_indice(tipos, series):
    secciones = []
    filtros = ['<button type="button" class="on" data-f="todas">Todas</button>']
    for clave, plural, _, descripcion in TIPOS:
        lista = tipos[clave]
        if not lista:
            continue
        filtros.append(f'<button type="button" data-f="{clave}">{plural}</button>')
        secciones.append(
            f'<section class="pred-seccion" id="{clave}" data-f="{clave}">'
            f'<div class="pred-seccion-head"><h2>{plural}</h2><p>{esc(descripcion)}</p></div>'
            f'<div class="pred-grid">{"".join(tarjeta(p) for p in lista)}</div></section>')
    if series:
        filtros.append('<button type="button" data-f="series">Series</button>')
        bloques = []
        for s in series:
            desc = f'<p>{esc(s["descripcion"])}</p>' if s["descripcion"] else ""
            n = len(s["predicaciones"])
            bloques.append(
                f'<div class="pred-serie" id="{s["slug"]}">'
                f'<div class="pred-serie-head"><span class="label">Serie · {n} predicaci{"ón" if n == 1 else "ones"}</span>'
                f'<h3>{esc(s["titulo"])}</h3>{desc}</div>'
                f'<div class="pred-grid">{"".join(tarjeta(p, i + 1) for i, p in enumerate(s["predicaciones"]))}</div></div>')
        secciones.append(
            f'<section class="pred-seccion" id="series" data-f="series">'
            f'<div class="pred-seccion-head"><h2>Series de predicaciones</h2>'
            f'<p>Predicaciones que recorren un libro o un tema en varias partes, para escucharlas en orden.</p></div>'
            f'{"".join(bloques)}</section>')

    if not secciones:
        cuerpo = ('<div class="callout callout-style-simple callout-note no-icon"><div class="callout-body d-flex">'
                  '<div class="callout-body-container">Las predicaciones están en preparación y se irán publicando aquí, '
                  'con su audio y su PDF.</div></div></div>')
    else:
        barra = f'<div class="pred-filtros" role="group" aria-label="Filtrar por tipo">{"".join(filtros)}</div>' \
            if len(filtros) > 2 else ""
        cuerpo = barra + "".join(secciones) + SCRIPT_FILTROS

    (SALIDA / "_indice.md").write_text(
        "<!-- Generado por scripts/predicaciones.py. No editar. -->\n\n```{=html}\n" + cuerpo + "\n```\n",
        encoding="utf-8")


SCRIPT_FILTROS = """
<script>
(function(){
  var bar=document.querySelector('.pred-filtros'); if(!bar) return;
  var secs=document.querySelectorAll('.pred-seccion');
  function usar(f){
    bar.querySelectorAll('button').forEach(function(b){ b.classList.toggle('on', b.dataset.f===f); b.setAttribute('aria-pressed', b.dataset.f===f); });
    secs.forEach(function(s){ s.hidden = f!=='todas' && s.dataset.f!==f; });
  }
  bar.addEventListener('click',function(e){ var b=e.target.closest('button'); if(b) usar(b.dataset.f); });
  var h=location.hash.replace('#','');
  if(h && bar.querySelector('[data-f="'+h+'"]')) usar(h);
  /* un solo audio sonando a la vez */
  document.addEventListener('play',function(e){
    document.querySelectorAll('audio').forEach(function(a){ if(a!==e.target) a.pause(); });
  },true);
})();
</script>
"""


def main():
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    (SALIDA / "pdf").mkdir(parents=True)
    (SALIDA / "audio").mkdir(parents=True)

    tipos, series = leer_todo()
    todas = [p for lista in tipos.values() for p in lista] + [p for s in series for p in s["predicaciones"]]
    preparar_archivos(todas)

    for lista in tipos.values():
        for p in lista:
            escribir_pagina(p)
    for s in series:
        ps = s["predicaciones"]
        for i, p in enumerate(ps):
            escribir_pagina(p, ps[i - 1] if i > 0 else None, ps[i + 1] if i + 1 < len(ps) else None)

    escribir_indice(tipos, series)
    if todas:
        log(f"{len(todas)} predicaciones publicadas ({len(series)} series)")
    else:
        log("todavía no hay predicaciones publicadas")


if __name__ == "__main__":
    main()
