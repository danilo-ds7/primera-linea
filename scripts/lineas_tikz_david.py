#!/usr/bin/env python3
"""Mapas de atlas en TikZ para las líneas de tiempo.

Lee el objeto DATA de estudios/lineas/<slug>.html, dibuja cada mapa (media.tipo == "mapa")
como un tikzpicture con geografía real (los mismos polígonos de Natural Earth y geoBoundaries
que usa la versión interactiva), lo compila con XeLaTeX y lo convierte a SVG con pdftocairo.
Escribe los SVG en estudios/lineas/<slug>/img/mapa-NN.svg y anota en el HTML, dentro de cada
media, un objeto `tikz` con la ruta del SVG y los puntos tocables (altares, lugares, estaciones)
en porcentaje, para que la página superponga los botones sobre la imagen.

Uso: python3 scripts/lineas_tikz.py [slug]      (por defecto: abraham)
"""
import json, math, re, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SLUG = sys.argv[1] if len(sys.argv) > 1 else "david"
HTML = RAIZ / "estudios" / "lineas" / f"{SLUG}.html"
IMG = RAIZ / "estudios" / "lineas" / SLUG / "img"
TRABAJO = RAIZ / ".cache" / f"tikz-lineas-{SLUG}"
FONTS = RAIZ / "estudios" / "atributos-de-dios" / "01_Preexistencia" / "fonts"

H_CM = 9.0            # alto de cada mapa en cm (el ancho sale del bbox)
ASPECT = 0.849        # cos(32°): un grado de longitud mide 0,849 grados de latitud

# --- datos ------------------------------------------------------------------
src = HTML.read_text(encoding="utf-8")
m = re.search(r"const DATA = (\{.*?\});\nconst \{events", src, re.S)
DATA = json.loads(m.group(1))
EV, SITES, ALT, GEO = DATA["events"], DATA["sites"], DATA.get("altars", {}), DATA["geo"]

# Ríos y relieve esquemáticos (copiados del motor interactivo)
RIOS = [["Yarmuk", [[32.75, 36.02], [32.72, 35.87], [32.70, 35.75], [32.69, 35.63], [32.68, 35.57]], 1],
        ["Yaboc", [[32.14, 36.06], [32.17, 35.95], [32.20, 35.80], [32.18, 35.68], [32.17, 35.56]], 1],
        ["Arnón", [[31.50, 36.02], [31.47, 35.90], [31.47, 35.80], [31.48, 35.66], [31.46, 35.57]], 1],
        ["Quisón", [[32.58, 35.22], [32.65, 35.14], [32.71, 35.07], [32.79, 35.01], [32.82, 34.99]], 0],
        ["Yarkón", [[32.12, 34.98], [32.11, 34.90], [32.10, 34.83], [32.09, 34.77]], 0],
        ["Sorec", [[31.80, 35.10], [31.80, 34.98], [31.86, 34.87], [31.93, 34.75], [31.94, 34.71]], 0],
        ["Besor", [[31.27, 34.82], [31.34, 34.68], [31.43, 34.56], [31.46, 34.50]], 1],
        ["Zered", [[30.95, 36.02], [31.03, 35.78], [31.12, 35.62], [31.17, 35.53]], 0]]
RIDGES = [[.12, .38, [[33.10, 35.50], [32.98, 35.42], [32.84, 35.32], [32.72, 35.28], [32.55, 35.30], [32.40, 35.25], [32.22, 35.25], [32.05, 35.22], [31.85, 35.17], [31.65, 35.10], [31.45, 35.02], [31.22, 34.95]]],
          [.07, .34, [[32.58, 35.12], [32.68, 35.03], [32.78, 34.98], [32.83, 34.95]]], [.05, .3, [[32.55, 35.37], [32.47, 35.42]]],
          [.12, .34, [[33.02, 36.00], [32.80, 35.88], [32.45, 35.87], [32.10, 35.86], [31.75, 35.82], [31.40, 35.80], [31.10, 35.74]]]]
RIDGES_W = [[.55, .30, [[38.0, 44.2], [37.1, 45.1], [36.0, 46.0], [35.0, 46.9], [34.0, 47.8], [33.0, 48.7]]],
            [.45, .30, [[37.15, 36.2], [37.55, 37.9], [38.10, 39.6], [38.45, 41.3], [38.7, 43.0]]],
            [.30, .30, [[36.4, 36.2], [35.4, 35.9], [34.6, 36.2], [33.9, 35.9], [33.4, 35.75]]],
            [.30, .28, [[33.4, 36.2], [33.0, 36.1]]], [.35, .30, [[28.95, 33.75], [28.55, 34.05], [28.2, 34.35]]],
            [.30, .22, [[29.9, 32.2], [29.3, 32.4], [28.7, 32.7]]]]
LAB_W = [["Mar Mediterráneo", 33.6, 31.8, "seal", 13, 0, 130], ["Golfo Pérsico", 28.5, 49.0, "seal", 12, 0, 130], ["Golfo Pérsico", 30.0, 48.9, "seal", 11, 130, 9999],
         ["Éufrates", 34.9, 41.55, "seal", 12, 0, 90], ["Tigris", 35.3, 43.3, "seal", 12, 0, 90], ["Nilo", 28.9, 31.55, "seal", 12, 0, 200], ["Jordán", 32.3, 35.95, "seal", 10, 0, 60],
         ["MESOPOTAMIA", 34.2, 43.6, "reg", 12, 0, 90], ["ARAM-NAHARAIM", 37.0, 40.2, "reg", 11.5, 0, 90], ["SINAR", 31.65, 46.9, "reg", 11.5, 0, 90], ["CANAÁN", 31.9, 35.35, "reg", 11.5, 0, 70],
         ["EGIPTO", 29.4, 30.7, "reg", 12, 0, 90], ["ELAM", 32.6, 48.3, "reg", 11.5, 0, 90], ["DESIERTO SIRIO", 32.5, 40.0, "reg", 12, 0, 90], ["ARABIA", 28.6, 40.5, "reg", 12, 0, 90],
         ["SINAÍ", 29.0, 33.9, "reg", 11, 0, 90], ["ANATOLIA", 38.4, 36.0, "reg", 11.5, 0, 90], ["Zagros", 35.2, 47.6, "rel", 11.5, 0, 90], ["Tauro", 38.0, 38.7, "rel", 11.5, 0, 90], ["Líbano", 34.0, 36.35, "rel", 10.5, 0, 90],
         ["CANAÁN", 31.75, 35.2, "reg", 12, 70, 200], ["EGIPTO", 30.0, 31.6, "reg", 12, 90, 9999], ["Mar Mediterráneo", 31.7, 33.3, "seal", 12, 90, 9999], ["Mar Salado", 31.35, 35.5, "seal", 11, 90, 9999],
         ["Jordán", 32.2, 35.55, "seal", 10, 90, 9999], ["Neguev", 30.9, 34.9, "rel", 11, 90, 9999], ["SINAÍ", 29.9, 33.7, "reg", 11, 90, 9999], ["Montes de Judea", 31.55, 35.1, "rel", 10, 120, 9999], ["ARABIA", 31.0, 36.9, "reg", 11, 90, 9999],
         ["SINAR", 31.1, 46.2, "reg", 12, 130, 9999], ["Éufrates", 31.0, 46.0, "seal", 11, 130, 9999], ["Tigris", 31.9, 46.7, "seal", 11, 130, 9999], ["ELAM", 31.2, 47.2, "reg", 11, 130, 9999], ["DESIERTO", 30.5, 44.9, "reg", 11, 130, 9999]]
LAB_LEV_REL = [["Sarón", 32.22, 34.97], ["Sefelá", 31.66, 34.93], ["Neguev", 31.12, 34.86], ["Galilea", 32.92, 35.33], ["Montes de Judea", 31.62, 35.22]]
LAB_LEV_REG = [["Galaad", 32.30, 35.80], ["Amón", 31.98, 35.82], ["Moab", 31.40, 35.78], ["Filistea", 31.55, 34.55]]

PREAMBULO = r"""\documentclass{article}
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\TeXXeTstate=1
\newfontfamily\hebfont[Path=FONTSDIR/,BoldFont=NotoHebrewSerif-700.ttf,Script=Hebrew]{NotoHebrewSerif-400.ttf}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,decorations.pathmorphing,backgrounds}
\usepackage[active,tightpage]{preview}\PreviewEnvironment{tikzpicture}\setlength\PreviewBorder{0pt}
\pagestyle{empty}
% paleta papiro (la misma de la línea)
\definecolor{land}{HTML}{EBE9D2}\definecolor{land2}{HTML}{E0DDC0}\definecolor{sea}{HTML}{C4D8E6}\definecolor{seadeep}{HTML}{A9C5D8}
\definecolor{ink}{HTML}{22301A}\definecolor{muted}{HTML}{5E6A4A}\definecolor{rule}{HTML}{BCC5A0}\definecolor{sepia}{HTML}{7B6540}
\definecolor{river}{HTML}{4F86A8}\definecolor{olive}{HTML}{5F7A2D}\definecolor{terra}{HTML}{A85A30}\definecolor{gold}{HTML}{C9A43C}
\definecolor{wine}{HTML}{8A3B45}\definecolor{blue}{HTML}{3F6F99}\definecolor{teal}{HTML}{2F6F74}\definecolor{earth}{HTML}{4A3B1F}\definecolor{grey}{HTML}{86876F}
\tikzset{
  sitio/.style={circle,fill=terra,draw=white,line width=.6pt,inner sep=0pt,minimum size=5.5pt},
  ctx/.style={circle,fill=grey,fill opacity=.6,inner sep=0pt,minimum size=2.4pt},
  etq/.style={font=\scshape\fontsize{8.5}{9}\selectfont,text=ink,inner sep=1.3pt,fill=land,fill opacity=.72,text opacity=1,rounded corners=1pt},
  etqtrayecto/.style={font=\sffamily\fontsize{6.8}{7}\selectfont,text=ink,inner sep=1.4pt,fill=land,fill opacity=.85,text opacity=1,rounded corners=1pt},
  mar/.style={font=\itshape\fontsize{8}{9}\selectfont,text=river!80!ink},
  region/.style={font=\scshape\fontsize{8}{9}\selectfont,text=muted},
  relieve/.style={font=\itshape\fontsize{7.5}{8}\selectfont,text=sepia},
  grat/.style={font=\sffamily\fontsize{5.5}{6}\selectfont,text=muted},
  trayecto/.style={terra,line width=1.4pt,line cap=round,line join=round,-{Stealth[length=6pt,width=5pt]}},
  insignia/.style={circle,fill=wine,draw=white,line width=.5pt,inner sep=0pt,minimum size=9pt,font=\sffamily\bfseries\fontsize{5.5}{6}\selectfont,text=white},
}
% cuerno de aceite (unción), con hilo de aceite y gota, y número de orden
\tikzset{altar/.pic={
  \fill[earth] (0,0) circle (1.3pt);
  \filldraw[fill=land2,draw=earth,line width=.45pt] (-9pt,22pt) .. controls (-7pt,34pt) and (6pt,40pt) .. (15pt,33pt) .. controls (22pt,27pt) and (21pt,17pt) .. (14pt,9pt) .. controls (16pt,16pt) and (16pt,24pt) .. (11pt,29pt) .. controls (5pt,35pt) and (-3pt,32pt) .. (-5pt,22pt) -- cycle;
  \filldraw[fill=rule,draw=earth,line width=.4pt] (-9pt,22pt) .. controls (-7pt,18pt) and (-4pt,18pt) .. (-5pt,22pt) .. controls (-5.5pt,24.5pt) and (-8.5pt,24.5pt) .. (-9pt,22pt) -- cycle;
  \fill[gold] (-8.4pt,19.5pt) .. controls (-7.6pt,15.5pt) and (-5.2pt,12pt) .. (-3.2pt,9.2pt) .. controls (-2.2pt,7.6pt) and (-1.3pt,5.6pt) .. (-.6pt,3.6pt) -- (-2pt,3pt) .. controls (-3pt,5pt) and (-4.6pt,7.2pt) .. (-6pt,9.8pt) .. controls (-7.8pt,13.2pt) and (-9.4pt,16.4pt) .. (-9.6pt,19.5pt) -- cycle;
  \fill[terra] (0,1pt) .. controls (1.8pt,3.5pt) and (2.6pt,5pt) .. (1.6pt,6.4pt) .. controls (1pt,7.2pt) and (-1pt,7.2pt) .. (-1.6pt,6.4pt) .. controls (-2.6pt,5pt) and (-1.8pt,3.5pt) .. (0,1pt) -- cycle;
}}
\begin{document}
"""

def proj(lat, lon):
    return lon * ASPECT, lat

def fmt(v):
    return f"{v:.3f}"

def thin(pts, d):
    out = [pts[0]]
    for q in pts[1:-1]:
        l = out[-1]
        if math.hypot(q[0] - l[0], q[1] - l[1]) >= d:
            out.append(q)
    out.append(pts[-1])
    return out

def path(pts, closed=False, smooth=True):
    """Lista lat/lon → coordenadas TikZ (lon·cos, lat)."""
    cs = " ".join(f"({fmt(lon * ASPECT)},{fmt(lat)})" for lat, lon in pts)
    if smooth and len(pts) > 2:
        return f"plot[smooth{', smooth cycle' if closed else ''},tension=.45] coordinates {{{cs}}}"
    return cs.replace(") (", ") -- (") + (" -- cycle" if closed else "")

def inb(B, lat, lon, pad_lat=.03, pad_lon=.08):
    return B[0] + pad_lat < lat < B[1] - pad_lat and B[2] + pad_lon < lon < B[3] - pad_lon

def mapa_tikz(n, m):
    """Devuelve (código tikz, puntos tocables en %)."""
    B = m["bbox"]; wide = bool(m.get("wide"))
    G = GEO["wide"] if wide else GEO["lev"]
    H = 412.0; SC = H / (B[1] - B[0])              # misma escala lógica que el motor interactivo
    F = m.get("fs") or (1.3 if SC < 60 else 1.15 if SC < 120 else 1.0)
    S = H_CM / (B[1] - B[0])                       # cm por grado de latitud
    W_cm = (B[3] - B[2]) * ASPECT * S
    thin_d = (2.4 if wide else 3.2) / SC           # umbral de simplificación en grados
    pct = lambda lat, lon: (100 * (lon - B[2]) / (B[3] - B[2]), 100 * (B[1] - lat) / (B[1] - B[0]))
    kmb = m.get("kmbar") or (20 if SC > 120 else 50 if SC > 60 else 200)
    km_cm = kmb / 111 * S
    GS = m.get("grid") or (.5 if SC > 120 else 1 if SC > 60 else 2)
    L = []
    A = L.append
    A(f"\\begin{{tikzpicture}}[x={{({S:.5f}cm,0)}},y={{(0,{S:.5f}cm)}}]")
    A(f"\\useasboundingbox ({fmt(B[2]*ASPECT)},{fmt(B[0])}) rectangle ({fmt(B[3]*ASPECT)},{fmt(B[1])});")
    A(f"\\clip ({fmt(B[2]*ASPECT)},{fmt(B[0])}) rectangle ({fmt(B[3]*ASPECT)},{fmt(B[1])});")
    # mar con degradado suave y orlas de costa
    A(f"\\shade[top color=sea,bottom color=seadeep] ({fmt(B[2]*ASPECT-1)},{fmt(B[0]-1)}) rectangle ({fmt(B[3]*ASPECT+1)},{fmt(B[1]+1)});")
    rings = G["lands"] if wide else [(G.get("land2") or G["land"])[0]]
    landP = []
    for r in rings:
        pts = thin(r[:-1], thin_d)
        landP.append(path(pts, closed=True, smooth=not wide))
    for w, op in ((7, .12), (3.6, .2), (1.4, .35)):
        for p in landP:
            A(f"\\draw[land,line width={w}pt,opacity={op},line join=round] {p};")
    for p in landP:
        A(f"\\fill[land] {p};")
    # retícula
    A("\\begin{scope}")
    for p in landP:
        A(f"\\clip {p};")
    la = math.ceil(B[0] / GS) * GS
    while la <= B[1]:
        A(f"\\draw[sepia,line width=.25pt,opacity=.28,dash pattern=on .6pt off 2pt] ({fmt(B[2]*ASPECT-1)},{fmt(la)}) -- ({fmt(B[3]*ASPECT+1)},{fmt(la)});"); la += GS
    lo = math.ceil(B[2] / GS) * GS
    while lo <= B[3]:
        A(f"\\draw[sepia,line width=.25pt,opacity=.28,dash pattern=on .6pt off 2pt] ({fmt(lo*ASPECT)},{fmt(B[0]-1)}) -- ({fmt(lo*ASPECT)},{fmt(B[1]+1)});"); lo += GS
    # relieve: cordilleras como trazos suaves superpuestos
    for w, op, pts in (RIDGES + RIDGES_W if wide else RIDGES):
        lw = min(w * SC, 30) * .55           # px → pt, algo más estrecho que en pantalla
        for f, o in ((1.0, .07), (.85, .07), (.7, .08), (.55, .09), (.4, .1), (.25, .11)):
            A(f"\\draw[sepia,opacity={o:.2f},line width={lw*f:.2f}pt,line cap=round,line join=round] {path(pts)};")
    if not wide:
        valle = max(G["rivers"], key=len)
        A(f"\\draw[olive,opacity=.16,line width={min(.07*SC,14)/1.33:.2f}pt,line cap=round] {path(thin(valle, thin_d))};")
    A("\\end{scope}")
    for z in m.get("zones", []):
        col = (z.get("col") or "gold").replace("var(--", "").replace(")", "")
        A(f"\\filldraw[fill={col},fill opacity=.16,draw={col},opacity=.8,line width=1pt,dash pattern=on 4pt off 2.5pt] {path(z['pts'], closed=True)};")
    # ríos y lagos
    rv = [r[1] for r in G["rivers"]] if wide else G["rivers"] + [r[1] for r in RIOS]
    for r in rv:
        A(f"\\draw[river,line width=.55pt,line cap=round,line join=round] {path(thin(r, thin_d*1.4))};")
    for lk in G["lakes"]:
        A(f"\\filldraw[fill=sea,draw=river,line width=.5pt] {path(thin(lk[:-1], thin_d*.8), closed=True)};")
    for p in landP:
        A(f"\\draw[sepia,line width=.55pt,opacity=.65,line join=round] {p};")
    # rótulos de mares y regiones (se omiten si pisan un lugar, un altar o una estación)
    hl = m.get("hl") or []; altars = m.get("altars") or []; focus = set(m.get("focus") or [])
    ocupado = []
    for key in hl + altars:
        la_, lo_ = SITES[key][0], SITES[key][1]
        ocupado.append((lo_ - .4 / S / ASPECT, lo_ + 1.2 / S / ASPECT, la_ - .3 / S, la_ + .75 / S))   # punto + rótulo a la derecha + altar encima
    for st in m.get("stations", []):
        key = st[1]; ov = st[3] if len(st) > 3 else None
        la_, lo_ = (ov[0], ov[1]) if ov else (SITES[key][0], SITES[key][1])
        ocupado.append((lo_ - 1.4 / S / ASPECT, lo_ + .6 / S / ASPECT, la_ - .5 / S, la_ + .5 / S))
    def lab(t, lat, lon, cls, fs, anchor="center", rot=0, extra=""):
        if not inb(B, lat, lon): return
        w = len(t) * .5 * fs * F * .78 / 28.45 / (S * ASPECT)  # ancho aprox en grados de lon
        x = lon
        x0 = x - w / 2 if anchor == "center" else x - w if anchor == "east" else x
        if x0 < B[2] + .04 or x0 + w > B[3] - .04: return
        h = fs * F * .78 / 28.45 / S
        if any(x0 < o[1] and x0 + w > o[0] and lat - h / 2 < o[3] and lat + h / 2 > o[2] for o in ocupado): return
        st = {"seal": "mar", "reg": "region", "rel": "relieve"}[cls]
        A(f"\\node[{st},font=\\fontsize{{{fs*F*.78:.1f}}}{{{fs*F*.9:.1f}}}\\selectfont,anchor={anchor},rotate={rot}{extra}] at ({fmt(lon*ASPECT)},{fmt(lat)}) {{{t}}};")
    if wide:
        for t, la_, lo_, c, fs, mn, mx in LAB_W:
            if mn <= SC < mx: lab(t, la_, lo_, c, fs)
    else:
        if B[2] < 34.6:
            la_ = min(max(32.45, B[0] + .3), B[1] - .3); lo_ = max(B[2] + .12, 34.2 + (la_ - 31.25) * .55 - .12)
            A(f"\\node[mar,font=\\fontsize{{8.5}}{{9}}\\selectfont,rotate=68] at ({fmt(lo_*ASPECT)},{fmt(la_)}) {{Mar Grande (Mediterráneo)}};")
        lab("Mar Salado", 31.36, 35.37, "seal", 12, anchor="east"); lab("Kinéret", 32.80, 35.70, "seal", 12, anchor="west"); lab("Jordán", 32.14, 35.60, "seal", 12, anchor="west")
        for nme, pts, k in RIOS:
            if k:
                q = pts[int(len(pts) * .55)]; lab(nme, q[0] + .03, q[1] + .02, "seal", 10, anchor="west")
        for nme, la_, lo_ in LAB_LEV_REL: lab(nme, la_, lo_, "rel", 10.5)
        for nme, la_, lo_ in LAB_LEV_REG: lab(nme, la_, lo_, "reg", 10.5)
    # trayectos
    spots = []
    for p in m.get("paths", []):
        col = (p.get("col") or "var(--c)").replace("var(--", "").replace(")", "")
        if col == "c": col = "terra"
        pts = p["pts"]
        arrow = "" if p.get("arrow") is False else "-{Stealth[length=6pt,width=5pt]}"
        lw = (p.get("w") or 3) / 1.33 * 1.1
        A(f"\\draw[white,opacity=.55,line width={lw+2.2:.2f}pt,line cap=round,line join=round] {path(pts)};")
        A(f"\\draw[{col},line width={lw:.2f}pt,line cap=round,line join=round,{arrow}] {path(pts)};")
        if p.get("lab"):
            # punto a la fracción lf del trayecto
            P = [(lon * ASPECT, lat) for lat, lon in pts]
            segs = [math.hypot(P[i][0]-P[i-1][0], P[i][1]-P[i-1][1]) for i in range(1, len(P))]
            d = sum(segs) * (p.get("lf") or .5); x, y, an = P[-1][0], P[-1][1], 0
            for i, l in enumerate(segs):
                if d <= l or i == len(segs) - 1:
                    t = d / l if l else 0
                    x = P[i][0] + (P[i+1][0]-P[i][0]) * t; y = P[i][1] + (P[i+1][1]-P[i][1]) * t
                    an = math.atan2(P[i+1][1]-P[i][1], P[i+1][0]-P[i][0]); break
                d -= l
            side = p.get("side") or 1
            nx, ny = -math.sin(an) * side, math.cos(an) * side
            off = 10 / 28.45 / S
            A(f"\\node[etqtrayecto] at ({fmt(x + nx*off*ASPECT)},{fmt(y + ny*off)}) {{{p['lab']}}};")
    for a, b in m.get("route", []):
        A(f"\\draw[trayecto] ({fmt(SITES[a][1]*ASPECT)},{fmt(SITES[a][0])}) to[bend left=12] ({fmt(SITES[b][1]*ASPECT)},{fmt(SITES[b][0])});")
    # lugares de contexto
    if m.get("ctx") is not False and not wide:
        for key, (la_, lo_, nme, _) in SITES.items():
            if key in hl or key in altars or not inb(B, la_, lo_): continue
            A(f"\\node[ctx] at ({fmt(lo_*ASPECT)},{fmt(la_)}) {{}};")
    # lugares destacados
    boxes = []
    for key in hl:
        if key in altars: continue
        la_, lo_, nme, _ = SITES[key]
        A(f"\\node[sitio] at ({fmt(lo_*ASPECT)},{fmt(la_)}) {{}};")
        spots.append([key, *pct(la_, lo_), "sitio", None])
    # altares numerados
    for i, key in enumerate(altars):
        la_, lo_, nme, _ = SITES[key]
        an = (ALT.get(key) or {}).get("n", i + 1); old = bool(focus) and key not in focus
        A(f"\\pic[scale={.6*F:.2f}{',opacity=.5' if old else ''}] at ({fmt(lo_*ASPECT)},{fmt(la_)}) {{altar}};")
        A(f"\\node[insignia{',opacity=.5' if old else ''}] at ($({fmt(lo_*ASPECT)},{fmt(la_)})+({11*F:.1f}pt,{22*F:.1f}pt)$) {{{an}}};")
        spots.append([key, *pct(la_, lo_), "altar", an])
    # estaciones numeradas (agrupadas si coinciden)
    grupos = {}
    for st in m.get("stations", []):
        nn, key = st[0], st[1]; ring = st[2] if len(st) > 2 else False; ov = st[3] if len(st) > 3 else None
        la_, lo_ = (ov[0], ov[1]) if ov else (SITES[key][0], SITES[key][1])
        g = grupos.setdefault((round(la_, 2), round(lo_, 2)), {"key": key, "la": la_, "lo": lo_, "list": []})
        g["list"].append((nn, ring))
    for g in grupos.values():
        for k, (nn, ring) in enumerate(g["list"]):
            dx = -(9 + k * 12) * F; dy = -7 * F
            A(f"\\node[insignia{',draw=gold,line width=1.1pt' if ring else ''}] at ($({fmt(g['lo']*ASPECT)},{fmt(g['la'])})+({dx:.1f}pt,{dy:.1f}pt)$) {{{nn}}};")
            spots.append([g["key"], pct(g["la"], g["lo"])[0] + dx / (W_cm * 28.45) * 100, pct(g["la"], g["lo"])[1] - dy / (H_CM * 28.45) * 100, "estacion", nn])
    for t, la_, lo_, c in m.get("notes", []):
        lab(t.replace("↙", "$\\swarrow$").replace("↗", "$\\nearrow$").replace("→", "$\\rightarrow$"), la_, lo_, c or "reg", 11)
    # etiquetas de lugares, con elección de lado para no taparse
    lbls = [(k, SITES[k][0], SITES[k][1], SITES[k][2], True) for k in altars] + [(k, SITES[k][0], SITES[k][1], SITES[k][2], False) for k in hl if k not in altars]
    deg_pt = 1 / 28.45 / S                 # grados de latitud por punto
    taken = [(*pct(SITES[k][0], SITES[k][1]), 2.2, 2.2) for k in hl + altars]
    for key, la_, lo_, nme, isA in lbls:
        w_pt = len(nme) * 5.1 * F; o = (13 if isA else 7) * F
        cand = [(o, 0, "west"), (-o, 0, "east"), (o, 9, "west"), (o, -9, "west"), (-o, 9, "east"), (-o, -9, "east"), (o, -20, "west"), (-o, 20, "east")]
        pick = cand[0]
        for dx, dy, anc in cand:
            x = lo_ + dx * deg_pt / ASPECT; y = la_ + dy * deg_pt
            x0 = x if anc == "west" else x - w_pt * deg_pt / ASPECT
            if x0 < B[2] + .02 or x0 + w_pt * deg_pt / ASPECT > B[3] - .02 or y - 5 * deg_pt < B[0] + .02 or y + 5 * deg_pt > B[1] - .02: continue
            bx = (pct(y, x0)[0], pct(y, x0)[1] - 1.2, w_pt / (W_cm * 28.45) * 100, 2.6)
            if not any(bx[0] < q[0] + q[2] and bx[0] + bx[2] > q[0] and bx[1] < q[1] + q[3] and bx[1] + bx[3] > q[1] for q in taken):
                pick = (dx, dy, anc); break
        dx, dy, anc = pick
        x0 = lo_ + dx * deg_pt / ASPECT; y0 = la_ + dy * deg_pt
        taken.append((pct(y0, x0 if anc == "west" else x0 - w_pt * deg_pt / ASPECT)[0], pct(y0, x0)[1] - 1.2, w_pt / (W_cm * 28.45) * 100, 2.6))
        A(f"\\node[etq,anchor={anc}{',font=\\scshape\\bfseries\\fontsize{8.5}{9}\\selectfont' if isA else ''}] at ({fmt(x0*ASPECT)},{fmt(y0)}) {{{nme}}};")
    # retícula: cifras en los bordes
    la = math.ceil((B[0] + .05) / GS) * GS
    while la < B[1] - .05:
        A(f"\\node[grat,anchor=south west] at ({fmt(B[2]*ASPECT)},{fmt(la)}) {{{la:g}° N}};"); la += GS
    lo = math.ceil((B[2] + .1) / GS) * GS
    while lo < B[3] - .1:
        A(f"\\node[grat,anchor=north west] at ({fmt(lo*ASPECT)},{fmt(B[1])}) {{{lo:g}° E}};"); lo += GS
    # escala y rosa de los vientos
    A(f"\\begin{{scope}}[shift={{({fmt(B[2]*ASPECT)},{fmt(B[0])})}},x=1cm,y=1cm]")
    A(f"\\fill[land,opacity=.85,rounded corners=1pt] (.25,.2) rectangle ({.45+km_cm:.3f},.72);")
    A(f"\\draw[ink,line width=1pt] (.35,.4) -- ({.35+km_cm:.3f},.4); \\draw[ink,line width=.6pt] (.35,.33) -- (.35,.47) ({.35+km_cm:.3f},.33) -- ({.35+km_cm:.3f},.47);")
    A(f"\\node[grat,font=\\sffamily\\fontsize{{6}}{{6}}\\selectfont,anchor=south west,text=ink] at (.33,.44) {{{kmb} km}};")
    A("\\end{scope}")
    A(f"\\begin{{scope}}[shift={{({fmt(B[3]*ASPECT)},{fmt(B[1])})}},x=1cm,y=1cm]")
    A("\\fill[land,opacity=.85] (-.55,-.55) circle (.36);")
    A("\\draw[sepia,line width=.3pt] (-.55,-.55) circle (.3); \\fill[ink] (-.55,-.33) -- (-.6,-.55) -- (-.5,-.55) -- cycle; \\fill[land2,draw=ink,line width=.3pt] (-.55,-.77) -- (-.6,-.55) -- (-.5,-.55) -- cycle;")
    A("\\draw[ink,line width=.3pt] (-.77,-.55) -- (-.33,-.55);")
    A("\\node[grat,text=ink,font=\\sffamily\\bfseries\\fontsize{6}{6}\\selectfont] at (-.55,-.2) {N};")
    A("\\end{scope}")
    # marco doble
    A(f"\\draw[rule,line width=.4pt] ({fmt(B[2]*ASPECT)},{fmt(B[0])}) rectangle ({fmt(B[3]*ASPECT)},{fmt(B[1])});")
    A(f"\\draw[sepia,line width=1pt] ([shift={{(1.5pt,1.5pt)}}]{fmt(B[2]*ASPECT)},{fmt(B[0])}) rectangle ([shift={{(-1.5pt,-1.5pt)}}]{fmt(B[3]*ASPECT)},{fmt(B[1])});")
    A("\\end{tikzpicture}")
    # coordenadas relativas a la esquina del mapa: evita «Dimension too large» en los mapas de gran escala
    OX, OY = B[2] * ASPECT, B[0]
    tikz = re.sub(r"(\(|\])(-?\d+\.\d{3}),(-?\d+\.\d{3})\)", lambda q: f"{q.group(1)}{float(q.group(2))-OX:.3f},{float(q.group(3))-OY:.3f})", "\n".join(L))
    return tikz, spots, round(W_cm / H_CM, 4)


def portada_tikz():
    W, H = 18.0, 6.3
    L = []; A = L.append
    A("\\begin{tikzpicture}[x=1cm,y=1cm]")
    A(f"\\useasboundingbox (0,0) rectangle ({W},{H});")
    A(f"\\shade[top color=land!60!white,bottom color=land] (0,0) rectangle ({W},{H});")
    A(f"\\draw[rule,line width=.4pt] (.12,.12) rectangle ({W-.12},{H-.12}); \\draw[sepia,line width=1pt] (.22,.22) rectangle ({W-.22},{H-.22});")
    A(f"\\node[text=olive,font=\\hebfont\\bfseries\\fontsize{{52}}{{56}}\\selectfont] at ({W/2},{H-1.75}) {{\\beginR דָּוִד\\endR}};")
    A(f"\\node[grat,font=\\sffamily\\fontsize{{6.5}}{{7}}\\selectfont,anchor=north east] at ({W-.5},{H-.45}) {{se lee de derecha a izquierda $\\leftarrow$}};")
    # el camino: Belén (unción 1), Ela (la honda), Adulam (la cueva), Hebrón (unción 2), Guihón/Jerusalén (unción 3)
    xs = [1.3, 4.95, 8.6, 12.25, 15.9]; ys = [1.9, 2.4, 2.6, 2.4, 1.9]
    A(f"\\draw[rule,line width=.9pt,dash pattern=on .5pt off 3pt,line cap=round] plot[smooth,tension=.7] coordinates {{{' '.join(f'({x},{y})' for x,y in zip(xs,ys))}}};")
    nombres = [("בֵּית לֶחֶם", "Belén", 1), ("עֵמֶק הָאֵלָה", "Valle de Ela", 0), ("עֲדֻלָּם", "Adulam", 0), ("חֶבְרוֹן", "Hebrón", 2), ("גִּיחוֹן", "Guihón · Jerusalén", 3)]
    for (he, es, k), x, y in zip(nombres, xs, ys):
        if k:
            A(f"\\pic[scale=1.1] at ({x},{y+.05}) {{altar}};")
            A(f"\\node[insignia,minimum size=11pt,font=\\sffamily\\bfseries\\fontsize{{6.5}}{{7}}\\selectfont] at ({x+.55},{y+1.05}) {{{k}}};")
        elif es == "Valle de Ela":
            # honda: dos cuerdas y la bolsa con la piedra
            A(f"\\draw[earth,line width=.6pt,line cap=round] ({x-.35},{y+.55}) .. controls ({x-.15},{y+.2}) .. ({x},{y+.05}) .. controls ({x+.15},{y+.2}) .. ({x+.35},{y+.55});")
            A(f"\\filldraw[fill=land2,draw=earth,line width=.5pt] ({x},{y+.05}) ellipse (.17 and .09); \\fill[grey] ({x},{y+.05}) circle (1.6pt);")
        else:
            # cueva: arco oscuro
            A(f"\\filldraw[fill=earth,draw=earth] ({x-.3},{y}) -- ({x-.3},{y+.25}) arc (180:0:.3) -- ({x+.3},{y}) -- cycle; \\fill[land] ({x-.18},{y}) -- ({x-.18},{y+.2}) arc (180:0:.18) -- ({x+.18},{y}) -- cycle;")
        A(f"\\node[text=ink,font=\\hebfont\\fontsize{{12}}{{13}}\\selectfont,anchor=north] at ({x},{y-.28}) {{\\beginR {he}\\endR}};")
        A(f"\\node[text=muted,font=\\scshape\\fontsize{{8}}{{9}}\\selectfont,anchor=north] at ({x},{y-.78}) {{{es}}};")
    A("\\end{tikzpicture}")
    return "\n".join(L), round(W / H, 4)

def cronos_tikz(m):
    W, H = 13.0, 9.0; lo, hi = m["lo"], m["hi"]; X = lambda v: .9 + (v - lo) / (hi - lo) * (W - 1.5)
    L = []; A = L.append
    A("\\begin{tikzpicture}[x=1cm,y=1cm]")
    A(f"\\useasboundingbox (0,0) rectangle ({W},{H});")
    A(f"\\node[text=ink,font=\\itshape\\fontsize{{9}}{{10}}\\selectfont,anchor=north] at ({W/2},{H-.15}) {{{m.get('foot','')}}};")
    v = lo
    while v <= hi:
        A(f"\\draw[rule,line width=.3pt,dash pattern=on 1pt off 1.5pt] ({X(v):.3f},.95) -- ({X(v):.3f},{H-.9});")
        A(f"\\node[grat,font=\\sffamily\\fontsize{{7}}{{8}}\\selectfont,anchor=north] at ({X(v):.3f},.9) {{{-v}}};"); v += m.get("step", 100)
    A(f"\\node[grat,font=\\sffamily\\fontsize{{7}}{{8}}\\selectfont,anchor=north east] at ({W-.3},.45) {{a.\\,e.\\,c.}};")
    A(f"\\draw[ink,line width=.5pt] (.9,.95) -- ({W-.6},.95);")
    for i, (t, a, b, col, ev) in enumerate(m["rows"]):
        col = col.replace("var(--", "").replace(")", "")
        y = H - 1.95 - i * 1.85
        A(f"\\node[text=ink,font=\\bfseries\\fontsize{{8.5}}{{9.5}}\\selectfont,anchor=south west] at (.9,{y+.62:.3f}) {{{t}}};")
        A(f"\\filldraw[fill={col},fill opacity={'.25' if ev else '.5'},draw={col},rounded corners=1.5pt,line width=.6pt] ({X(a):.3f},{y-.22:.3f}) rectangle ({X(b):.3f},{y+.22:.3f});")
        for k, (n, vv) in enumerate(ev or []):
            A(f"\\filldraw[fill={col},draw=land!50!white,line width=.6pt] ({X(vv):.3f},{y:.3f}) circle (2.8pt);")
            A(f"\\node[text=ink,font=\\sffamily\\fontsize{{7}}{{8}}\\selectfont,anchor={'north' if k%2 else 'south'}] at ({X(vv):.3f},{y - .32 if k%2 else y + .32:.3f}) {{{n}}};")
    A(f"\\draw[rule,line width=.4pt] (.15,.15) rectangle ({W-.15},{H-.15});")
    A("\\end{tikzpicture}")
    return "\n".join(L), round(W / H, 4)

# --- generar -----------------------------------------------------------------
IMG.mkdir(parents=True, exist_ok=True)
if TRABAJO.exists(): shutil.rmtree(TRABAJO)
TRABAJO.mkdir(parents=True)
figs, meta = [], []
for i, e in enumerate(EV):
    md = e.get("media")
    if not md or md.get("tipo") != "mapa": continue
    tikz, spots, ratio = mapa_tikz(i + 1, md)
    figs.append(tikz); meta.append((i, spots, ratio))
extras = []
tp, rp = portada_tikz(); figs.append(tp); extras.append(("portada", rp, None))
for i, e in enumerate(EV):
    md = e.get("media")
    if md and md.get("tipo") == "cronos":
        tc, rc = cronos_tikz(md); figs.append(tc); extras.append((f"cronos-{i+1:02d}", rc, i))
(TRABAJO / "mapas.tex").write_text(PREAMBULO.replace("FONTSDIR", str(FONTS)) + "\n\n".join(figs) + "\n\\end{document}\n", encoding="utf-8")
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "mapas.tex"], cwd=TRABAJO, capture_output=True, text=True)
    if r.returncode != 0:
        log = (TRABAJO / "mapas.log").read_text(errors="ignore")
        print(log[log.find("!"):][:3000]); sys.exit(1)
for k, (i, spots, ratio) in enumerate(meta):
    out = IMG / f"mapa-{i+1:02d}.svg"
    subprocess.run(["pdftocairo", "-svg", "-f", str(k + 1), "-l", str(k + 1), str(TRABAJO / "mapas.pdf"), str(out)], check=True)
    svg = out.read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*>\s*", "", svg)
    svg = re.sub(r"-?\d+\.\d+", lambda q: f"{float(q.group()):.2f}".rstrip("0").rstrip("."), svg)   # dos decimales bastan
    svg = re.sub(r"\s+", " ", svg).replace("> <", "><")
    out.write_text(svg, encoding="utf-8")
    EV[i]["media"]["tikz"] = {"src": f"{SLUG}/img/mapa-{i+1:02d}.svg", "ratio": ratio, "spots": [[s[0], round(s[1], 2), round(s[2], 2), s[3], s[4]] for s in spots]}
    print(f"mapa-{i+1:02d}.svg  {out.stat().st_size//1024} KB  ratio {ratio}")
for k, (nombre, ratio, i) in enumerate(extras):
    out = IMG / f"{nombre}.svg"
    subprocess.run(["pdftocairo", "-svg", "-f", str(len(meta) + k + 1), "-l", str(len(meta) + k + 1), str(TRABAJO / "mapas.pdf"), str(out)], check=True)
    svg = out.read_text(encoding="utf-8"); svg = re.sub(r"<\\?xml[^>]*>\\s*", "", svg)
    svg = re.sub(r"-?\\d+\\.\\d+", lambda q: f"{float(q.group()):.2f}".rstrip("0").rstrip("."), svg); svg = re.sub(r"\\s+", " ", svg).replace("> <", "><")
    out.write_text(svg, encoding="utf-8")
    if i is None: DATA["portada"] = {"src": f"{SLUG}/img/{nombre}.svg", "ratio": ratio}
    else: EV[i]["media"]["tikz"] = {"src": f"{SLUG}/img/{nombre}.svg", "ratio": ratio}
    print(f"{nombre}.svg  {out.stat().st_size//1024} KB")
# anotar el HTML (solo el objeto DATA)
nuevo = json.dumps(DATA, ensure_ascii=False, separators=(", ", ": "))
src2 = src[:m.start(1)] + nuevo + src[m.end(1):]
HTML.write_text(src2, encoding="utf-8")
print("DATA actualizado en", HTML.name)
