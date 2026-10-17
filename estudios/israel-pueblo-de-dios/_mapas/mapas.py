#!/usr/bin/env python3
"""
Mapas de la serie «Israel, el pueblo de Dios» (Primera Línea).

Cartografía real: costas, lagos y ríos GSHHS/WDB en resolución completa (basemap-data-hires)
y relieve sombreado global (shadedrelief de Basemap), teñido con la paleta café ladrillo.
Sin azul: el mar va en piedra fría con rayado de grabado.

Uso:  python3 mapas.py <id> [<id> ...] --out <carpeta_estudio>
      Genera <carpeta>/crops/mapa_<id>.pdf (Beamer) y <carpeta>/mapa_<id>.png (capítulo y web).
Requiere: pip install basemap basemap-data-hires pillow numpy matplotlib
"""
import argparse, math, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects as pe, font_manager as fm
from matplotlib.path import Path
from matplotlib.patches import PathPatch, FancyArrowPatch, Rectangle
from mpl_toolkits.basemap import Basemap
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ paleta (sin azul)
C = dict(
    ladrillo=(158/255, 70/255, 40/255), cafe=(96/255, 52/255, 30/255), cafeosc=(50/255, 25/255, 13/255),
    oro=(196/255, 148/255, 40/255), piedra=(240/255, 228/255, 203/255), sepia=(104/255, 86/255, 62/255),
    tinta=(44/255, 28/255, 18/255),
    mar=(226/255, 219/255, 201/255), rayado=(150/255, 132/255, 104/255), costa=(84/255, 58/255, 36/255),
    rio=(122/255, 98/255, 72/255), verde=(92/255, 98/255, 52/255),
)
TIERRA = [(0.0, (248, 240, 220)), (0.45, (234, 218, 184)), (0.75, (212, 186, 140)), (1.0, (168, 128, 86))]

# ------------------------------------------------------------------ tipografía
def _fuente():
    for c in ["/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-regular.otf",
              os.path.join(HERE, "texgyrepagella-regular.otf")]:
        if os.path.exists(c):
            fm.fontManager.addfont(c)
            for v in ["bold", "italic", "bolditalic"]:
                p = c.replace("regular", v)
                if os.path.exists(p):
                    fm.fontManager.addfont(p)
            return "TeX Gyre Pagella"
    return "DejaVu Serif"
FUENTE = _fuente()
plt.rcParams.update({"font.family": FUENTE, "pdf.fonttype": 42})
HALO = [pe.withStroke(linewidth=2.6, foreground=C["piedra"] + (0.92,))]
HALO_F = [pe.withStroke(linewidth=3.4, foreground=C["piedra"] + (0.95,))]

# ------------------------------------------------------------------ relieve
_RELIEVE = None
def relieve_global():
    global _RELIEVE
    if _RELIEVE is None:
        import mpl_toolkits.basemap_data as bd
        p = os.path.join(os.path.dirname(bd.__file__) if bd.__file__ else bd.__path__[0], "shadedrelief.jpg")
        im = np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0
        _RELIEVE = im
    return _RELIEVE

def relieve_teñido(m, lon0, lon1, lat0, lat1, ancho=1800):
    """Recorta el relieve, lo reproyecta a Mercator y lo tiñe con la rampa TIERRA."""
    g = relieve_global()
    H, W = g.shape
    x0, y0 = m(lon0, lat0); x1, y1 = m(lon1, lat1)
    alto = int(ancho * (y1 - y0) / (x1 - x0))
    xs = np.linspace(x0, x1, ancho); ys = np.linspace(y1, y0, alto)
    XX, YY = np.meshgrid(xs, ys)
    LON, LAT = m(XX, YY, inverse=True)
    col = ((LON + 180) / 360 * W).clip(0, W - 1.001)
    fil = ((90 - LAT) / 180 * H).clip(0, H - 1.001)
    c0 = np.floor(col).astype(int); r0 = np.floor(fil).astype(int)
    fc = col - c0; fr = fil - r0
    v = (g[r0, c0] * (1 - fc) * (1 - fr) + g[r0, c0 + 1] * fc * (1 - fr) +
         g[r0 + 1, c0] * (1 - fc) * fr + g[r0 + 1, c0 + 1] * fc * fr)
    # contraste: el relieve original es claro en llanos y oscuro en sombras
    v = 1 - v
    lo, hi = np.percentile(v, 2), np.percentile(v, 99.5)
    v = ((v - lo) / max(hi - lo, 1e-6)).clip(0, 1) ** 0.9
    rgb = np.zeros(v.shape + (3,))
    for i in range(len(TIERRA) - 1):
        a, ca = TIERRA[i]; b, cb = TIERRA[i + 1]
        mask = (v >= a) & (v <= b)
        t = ((v - a) / (b - a))[mask][:, None]
        rgb[mask] = np.array(ca) * (1 - t) + np.array(cb) * t
    ruido = np.random.default_rng(3).normal(0, 2.2, v.shape)[..., None]
    rgb = (rgb + ruido).clip(0, 255) / 255.0
    return rgb, (x0, x1, y0, y1)

# ------------------------------------------------------------------ geometría
def suavizar(pts, n=24):
    """Catmull-Rom por los puntos (en coordenadas proyectadas)."""
    pts = np.asarray(pts, float)
    if len(pts) < 3:
        return pts
    P = np.vstack([pts[0], pts, pts[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return np.array(out)

def poligonos_tierra(m):
    tierra, lagos = [], []
    for xy, tipo in zip(m.coastpolygons, m.coastpolygontypes):
        verts = np.column_stack(xy)
        (tierra if tipo in (1, 3) else lagos).append(verts)
    return tierra, lagos

def compuesto(polys):
    codes, verts = [], []
    for v in polys:
        if len(v) < 3:
            continue
        verts.extend(v.tolist() + [v[0].tolist()])
        codes.extend([Path.MOVETO] + [Path.LINETO] * (len(v) - 1) + [Path.CLOSEPOLY])
    return Path(verts, codes)

# ------------------------------------------------------------------ leyenda en LaTeX (presentación)
def _tex_color(col):
    for k, v in C.items():
        if all(abs(a - b) < 1e-6 for a, b in zip(v, col)):
            return k
    return "ladrillo"

def escribir_leyenda_tex(leyenda, extra, ruta):
    filas = []
    for txt, col, ls, lw in leyenda:
        if ls == "-":
            patron = ""
        elif ls[1][0] <= 2:
            patron = ",dash pattern=on 1.2pt off 1.4pt"
        else:
            patron = ",dash pattern=on 3.4pt off 1.8pt"
        filas.append(r"\tikz[baseline=-0.6ex]\draw[%s,line width=1.5pt,line cap=round%s](0,0)--(0.6,0);~%s\par" %
                     (_tex_color(col), patron, txt.replace("→", r"$\to$")))
    for txt, simb in extra:
        s = {"capital": r"\textcolor{ladrillo}{\rule{0.55ex}{0.55ex}}", "ciudad": r"\textcolor{cafeosc}{\textbullet}",
             "monte": r"\textcolor{cafe}{$\blacktriangle$}"}[simb]
        filas.append(r"\makebox[0.6cm][c]{%s}~%s\par" % (s, txt))
    with open(ruta, "w") as f:
        f.write("{\\scriptsize\\RaggedRight\n" + "\n".join(filas) + "}\n")

# ------------------------------------------------------------------ dibujo
def dibujar(spec, salida, factor=1.0, dpi=230, modo="art"):
    lon0, lon1, lat0, lat1 = spec["extension"]
    ancho_in = spec.get("ancho", 7.2) * factor
    m = Basemap(projection="merc", llcrnrlon=lon0, urcrnrlon=lon1, llcrnrlat=lat0, urcrnrlat=lat1,
                resolution=spec.get("resolucion", "f"), area_thresh=spec.get("area_min", 1.0))
    x0, y0 = m(lon0, lat0); x1, y1 = m(lon1, lat1)
    alto_in = ancho_in * (y1 - y0) / (x1 - x0)
    fig = plt.figure(figsize=(ancho_in, alto_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_axis_off()
    escala_pt = ancho_in * 72 / (x1 - x0)  # puntos por metro proyectado

    # mar + rayado de grabado
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=C["mar"], edgecolor="none", zorder=0))
    paso = (y1 - y0) / (alto_in * 72 / 3.2)
    for y in np.arange(y0, y1, paso):
        ax.plot([x0, x1], [y, y], color=C["rayado"], lw=0.25, alpha=0.35, zorder=0.5, solid_capstyle="butt")

    tierra, lagos = poligonos_tierra(m)
    pt = compuesto(tierra)
    # halo de costa (líneas de agua, estilo grabado)
    for k, (w, a) in enumerate([(5.5, 0.10), (3.2, 0.16)]):
        ax.add_patch(PathPatch(pt, facecolor="none", edgecolor=C["costa"], lw=w, alpha=a, zorder=1 + k * 0.01, joinstyle="round", capstyle="round"))
    # relieve recortado a tierra
    rgb, ext = relieve_teñido(m, lon0, lon1, lat0, lat1, ancho=spec.get("pix", 1800))
    img = ax.imshow(rgb, extent=ext, origin="upper", zorder=2, interpolation="bilinear")
    clip = PathPatch(pt, transform=ax.transData, facecolor="none", edgecolor="none")
    ax.add_patch(clip); img.set_clip_path(clip)
    # lagos
    if lagos:
        pl = compuesto(lagos)
        ax.add_patch(PathPatch(pl, facecolor=C["mar"], edgecolor=C["costa"], lw=0.5, zorder=3))
    # ríos
    try:
        mr = m if spec.get("rios_res") in (None, spec.get("resolucion", "f")) else Basemap(
            projection="merc", llcrnrlon=lon0, urcrnrlon=lon1, llcrnrlat=lat0, urcrnrlat=lat1,
            resolution=spec["rios_res"], area_thresh=1e9)
        lc = mr.drawrivers(color=C["rio"], linewidth=spec.get("rio_lw", 0.55), zorder=3.2, ax=ax)
        lc.set_alpha(spec.get("rio_alpha", 0.85))
    except Exception as e:
        print("ríos:", e)
    # costa
    ax.add_patch(PathPatch(pt, facecolor="none", edgecolor=C["costa"], lw=0.75, zorder=3.4, joinstyle="round"))

    # regiones (versalitas espaciadas)
    for r in spec.get("regiones", []):
        lon, lat, txt = r[:3]
        o = r[3] if len(r) > 3 else {}
        x, y = m(lon, lat)
        t = " ".join(txt.upper()) if o.get("espaciado", True) else txt
        ax.text(x, y, t, fontsize=o.get("tam", 9), color=o.get("color", C["sepia"]), alpha=o.get("alpha", 0.8),
                ha="center", va="center", rotation=o.get("rot", 0), style=o.get("estilo", "normal"),
                fontweight=o.get("peso", "normal"), zorder=4, path_effects=HALO)
    # aguas (rótulos en cursiva)
    for lon, lat, txt, *o in spec.get("aguas", []):
        o = o[0] if o else {}
        x, y = m(lon, lat)
        ax.text(x, y, txt, fontsize=o.get("tam", 7.5), color=C["costa"], style="italic", ha="center",
                va="center", rotation=o.get("rot", 0), zorder=4, alpha=0.9)
    # líneas (fronteras aproximadas)
    for ln in spec.get("lineas", []):
        xy = np.array([m(lo, la) for lo, la in ln["pts"]])
        if ln.get("suave", True):
            xy = suavizar(xy)
        ax.plot(xy[:, 0], xy[:, 1], color=ln.get("color", C["cafeosc"]), lw=ln.get("lw", 1.2),
                ls=ln.get("ls", (0, (4, 2.5))), zorder=5, alpha=ln.get("alpha", 0.9))
        if ln.get("rotulo"):
            lo, la, txt = ln["rotulo"]
            x, y = m(lo, la)
            ax.text(x, y, txt, fontsize=6.5, style="italic", color=C["cafeosc"], ha="center", zorder=5,
                    path_effects=HALO)
    # rutas
    leyenda = []
    for rt in spec.get("rutas", []):
        xy = np.array([m(lo, la) for lo, la in rt["pts"]])
        xy = suavizar(xy, 30) if rt.get("suave", True) else xy
        col = rt.get("color", C["ladrillo"]); lw = rt.get("lw", 2.0)
        ls = rt.get("ls", "-")
        ax.plot(xy[:, 0], xy[:, 1], color=C["piedra"], lw=lw + 2.2, alpha=0.75, zorder=6, solid_capstyle="round")
        ax.plot(xy[:, 0], xy[:, 1], color=col, lw=lw, ls=ls, zorder=6.1, solid_capstyle="round",
                dash_capstyle="round")
        # flecha final y flechas intermedias
        n = len(xy)
        marcas = [n - 1] + [int(n * f) for f in rt.get("flechas", [0.5])]
        for k in marcas:
            k = max(1, min(n - 1, k))
            a, b = xy[max(0, k - 2)], xy[k]
            ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=lw * 6.5, color=col,
                                         lw=0, zorder=6.2, shrinkA=0, shrinkB=0))
        if rt.get("leyenda"):
            leyenda.append((rt["leyenda"], col, ls, lw))
    # ciudades
    for c in spec.get("ciudades", []):
        lon, lat, nombre = c[:3]
        o = c[3] if len(c) > 3 else {}
        x, y = m(lon, lat)
        tipo = o.get("tipo", "ciudad")
        if tipo == "capital":
            ax.plot(x, y, marker="s", ms=5.2, mfc=C["ladrillo"], mec=C["cafeosc"], mew=0.8, zorder=7)
        elif tipo == "monte":
            ax.plot(x, y, marker="^", ms=5.5, mfc=C["cafe"], mec=C["cafeosc"], mew=0.6, zorder=7)
        elif tipo == "region":
            pass
        else:
            ax.plot(x, y, marker="o", ms=3.8, mfc=C["cafeosc"], mec=C["piedra"], mew=0.8, zorder=7)
        dx, dy = o.get("d", (4, 3))
        ha = "left" if dx > 0 else ("right" if dx < 0 else "center")
        va = "bottom" if dy > 0 else ("top" if dy < 0 else "center")
        ax.annotate(nombre, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                    fontsize=o.get("tam", 7.2), fontweight="bold" if tipo == "capital" else o.get("peso", "normal"),
                    color=C["tinta"], zorder=8, path_effects=HALO_F, style=o.get("estilo", "normal"))
    # leyenda
    extra = spec.get("leyenda_extra", [])
    if modo == "pres":
        escribir_leyenda_tex(leyenda, extra, salida.replace(".pdf", "_leyenda.tex"))
    if (leyenda or extra) and modo != "pres":
        lx, ly = spec.get("leyenda_pos", (0.025, 0.035))
        filas = leyenda + extra
        fila = 6.6 * 1.75 / (alto_in * 72)
        h = fila * len(filas) + fila * 0.9
        w = max(len(f[0]) for f in filas) * 6.6 * 0.47 / (ancho_in * 72) + 0.1
        ax.add_patch(Rectangle((lx, ly), w, h, transform=ax.transAxes, facecolor=C["piedra"], alpha=0.93,
                               edgecolor=C["cafe"], lw=0.7, zorder=9))
        for i, f in enumerate(filas):
            yy = ly + h - fila * 0.95 - i * fila
            if len(f) == 4:
                txt, col, ls, lw = f
                ax.plot([lx + 0.012, lx + 0.012 + 30 / (ancho_in * 72)], [yy, yy], transform=ax.transAxes, color=col, ls=ls,
                        lw=lw, zorder=10, solid_capstyle="round")
            else:
                txt, simb = f
                mk = {"capital": ("s", C["ladrillo"]), "ciudad": ("o", C["cafeosc"]), "monte": ("^", C["cafe"])}[simb]
                ax.plot([lx + 0.012 + 15 / (ancho_in * 72)], [yy], transform=ax.transAxes, marker=mk[0], ms=4.5, mfc=mk[1],
                        mec=C["cafeosc"], zorder=10)
            ax.text(lx + 0.012 + 36 / (ancho_in * 72), yy, txt, transform=ax.transAxes, fontsize=6.6, va="center", color=C["tinta"],
                    zorder=10)
    # escala
    km = spec.get("escala_km", 100)
    ex, ey = spec.get("escala_pos", (0.70, 0.06))
    lonm, latm = lon0 + (lon1 - lon0) * ex, lat0 + (lat1 - lat0) * ey
    xa, ya = m(lonm, latm)
    dlon = km / (111.32 * math.cos(math.radians(latm)))
    xb, _ = m(lonm + dlon, latm)
    for i in range(4):
        ax.add_patch(Rectangle((xa + (xb - xa) * i / 4, ya), (xb - xa) / 4, (y1 - y0) * 0.008,
                               facecolor=C["cafeosc"] if i % 2 == 0 else C["piedra"], edgecolor=C["cafeosc"],
                               lw=0.5, zorder=9))
    ax.text(xa, ya + (y1 - y0) * 0.016, "0", fontsize=6, ha="center", color=C["tinta"], zorder=9, path_effects=HALO)
    ax.text(xb, ya + (y1 - y0) * 0.016, f"{km} km", fontsize=6, ha="center", color=C["tinta"], zorder=9,
            path_effects=HALO)
    # norte
    nx, ny = spec.get("norte", (0.95, 0.88))
    ax.annotate("", xy=(nx, ny + 0.07), xytext=(nx, ny), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=C["cafeosc"], lw=1.1, mutation_scale=10), zorder=9)
    ax.text(nx, ny + 0.085, "N", transform=ax.transAxes, ha="center", fontsize=8, fontweight="bold",
            color=C["cafeosc"], zorder=9, path_effects=HALO)
    # título
    if spec.get("titulo") and modo != "pres":
        tx, ty = spec.get("titulo_pos", (0.5, 0.965))
        ax.text(tx, ty, spec["titulo"], transform=ax.transAxes, ha="center", va="top", fontsize=10.5,
                fontweight="bold", color=C["ladrillo"], zorder=9, path_effects=HALO_F)
    # marco doble
    for i, (w, col) in enumerate([(2.2, C["cafe"]), (0.6, C["oro"])]):
        ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, edgecolor=col, lw=w, zorder=11))
    fig.savefig(salida, dpi=dpi)
    plt.close(fig)

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    from mapas_datos import MAPAS
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "crops"), exist_ok=True)
    for i in a.ids:
        sp = MAPAS[i]
        # presentación: dibujado al tamaño real de la lámina (rótulos legibles al proyectar)
        f_pres = sp.get("factor_pres", 0.58)
        dibujar(sp, os.path.join(a.out, "crops", f"mapa_{i}.pdf"), factor=f_pres, dpi=400, modo="pres")
        # capítulo y web
        dibujar(sp, os.path.join(a.out, f"mapa_{i}.png"), factor=sp.get("factor_art", 0.86), dpi=260)
        print("ok", i)
