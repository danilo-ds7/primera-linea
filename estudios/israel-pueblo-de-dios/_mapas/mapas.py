#!/usr/bin/env python3
"""
Mapas de la serie «Israel, el pueblo de Dios» (Yada) — estilo moderno.

Datos reales:
  · Costas, lagos y ríos GSHHS/WDB en resolución completa (basemap-data-hires).
  · Elevación y batimetría ETOPO1 (malla global de 10′, fatiando-data/earth-topography-10arcmin).
  · Sombreado fino de relieve (shadedrelief de Basemap).
Estilo: mar en azules por profundidad; tierra en verdes (Media Luna Fértil: costa del Levante, Nilo,
Éufrates-Tigris, montes del norte), arena en los desiertos y ocres en las alturas; trayectorias con
degradado, flechas y paradas numeradas.

Uso:  python3 mapas.py <id> [<id> ...] --out <carpeta_estudio>
      → <carpeta>/crops/mapa_<id>.pdf + crops/mapa_<id>_leyenda.tex (presentación)
      → <carpeta>/mapa_<id>.png (capítulo y web)
Requiere: pip install basemap basemap-data-hires netCDF4 scipy pillow numpy matplotlib
"""
import argparse, math, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects as pe, font_manager as fm, colors as mcolors
from matplotlib.collections import LineCollection
from matplotlib.path import Path
from matplotlib.patches import PathPatch, FancyArrowPatch, Rectangle, FancyBboxPatch, Circle, Polygon
from mpl_toolkits.basemap import Basemap
from PIL import Image, ImageDraw
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
DEM = os.environ.get("ISRAEL_DEM", os.path.join(HERE, "earth-topography-10arcmin.nc"))

def hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

# ------------------------------------------------------------------ paleta moderna
C = dict(
    # rutas (vivas, legibles sobre verde, arena y azul)
    carmesi=hx("#D62839"), naranja=hx("#F28C28"), violeta=hx("#7B2CBF"), turquesa=hx("#0F8B8D"),
    azul=hx("#1D4E89"), ocre=hx("#B5651D"),
    # cartografía
    texto=hx("#1F2933"), gris=hx("#52606D"), region=hx("#6B5B4B"), agua_txt=hx("#2F6690"),
    costa=hx("#3E6E8E"), rio=hx("#3D85C6"), lago=hx("#A9D3EA"), blanco=(1, 1, 1),
    capital=hx("#D62839"),
    # compatibilidad con nombres antiguos de mapas_datos.py
    ladrillo=hx("#D62839"), oro=hx("#F28C28"), cafe=hx("#7B2CBF"), cafeosc=hx("#1F2933"),
    piedra=hx("#FFFFFF"), sepia=hx("#6B5B4B"), tinta=hx("#1F2933"),
)
RUTA_TEX = {"carmesi": "D62839", "naranja": "F28C28", "violeta": "7B2CBF", "turquesa": "0F8B8D",
            "azul": "1D4E89", "ocre": "B5651D"}

MAR = [(0, "#D6ECF5"), (-150, "#B9DCEC"), (-600, "#93C3E0"), (-1500, "#74AED6"), (-3000, "#5B98C8"), (-5000, "#4A86BA")]
VERDE = [(-450, "#8DBB7A"), (0, "#A6CC8E"), (250, "#BFD79E"), (600, "#D3D7A3"), (1000, "#D6C394"),
         (1800, "#C2A27E"), (2800, "#AE9C8E"), (4200, "#ECE8E3")]
SECO = [(-450, "#DCCB9E"), (0, "#EFE0B9"), (250, "#EBD7AA"), (600, "#E2C89A"), (1000, "#D4B48A"),
        (1800, "#C19E7E"), (2800, "#AE9C8E"), (4200, "#ECE8E3")]

def rampa(z, stops):
    zs = np.array([s[0] for s in stops], float)
    cs = np.array([hx(s[1]) for s in stops])
    if zs[0] > zs[-1]:
        zs, cs = zs[::-1], cs[::-1]
    out = np.empty(z.shape + (3,))
    for k in range(3):
        out[..., k] = np.interp(z, zs, cs[:, k])
    return out

# ------------------------------------------------------------------ tipografía
def _fuente():
    nombres = {f.name for f in fm.fontManager.ttflist}
    return "Inter" if "Inter" in nombres else "DejaVu Sans"
FUENTE = _fuente()
plt.rcParams.update({"font.family": FUENTE, "pdf.fonttype": 42})
def halo(w=2.6, a=0.95):
    return [pe.withStroke(linewidth=w, foreground=(1, 1, 1, a))]

# ------------------------------------------------------------------ datos ráster
_SR = None
def sombreado_global():
    global _SR
    if _SR is None:
        import mpl_toolkits.basemap_data as bd
        p = os.path.join(bd.__path__[0], "shadedrelief.jpg")
        _SR = np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0
    return _SR

_Z = None
def elevacion_global():
    global _Z
    if _Z is None:
        import netCDF4
        d = netCDF4.Dataset(DEM)
        lon = d.variables["longitude"][:].astype(float); lat = d.variables["latitude"][:].astype(float)
        z = d.variables["topography"][:].astype(np.float32)
        _Z = (lon, lat, np.asarray(z))
    return _Z

def muestrear(LON, LAT):
    lon, lat, z = elevacion_global()
    fi = (LAT - lat[0]) / (lat[1] - lat[0])
    fj = (LON - lon[0]) / (lon[1] - lon[0])
    return ndimage.map_coordinates(z, [fi, fj], order=3, mode="nearest")

def muestrear_sombra(LON, LAT):
    g = sombreado_global(); H, W = g.shape
    fi = (90 - LAT) / 180 * H - 0.5; fj = (LON + 180) / 360 * W - 0.5
    return ndimage.map_coordinates(g, [fi, fj], order=1, mode="nearest")

# ------------------------------------------------------------------ geometría
def suavizar(pts, n=24):
    pts = np.asarray(pts, float)
    if len(pts) < 3:
        return np.vstack([np.linspace(pts[0], pts[-1], n)]) if len(pts) == 2 else pts
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

def compuesto(polys):
    codes, verts = [], []
    for v in polys:
        if len(v) < 3:
            continue
        verts.extend(v.tolist() + [v[0].tolist()])
        codes.extend([Path.MOVETO] + [Path.LINETO] * (len(v) - 1) + [Path.CLOSEPOLY])
    return Path(verts, codes)

# ------------------------------------------------------------------ fondo ráster
def fondo(m, ext, W, H, tierra, lagos, rios_segs, km_px, spec):
    x0, x1, y0, y1 = ext
    xs = np.linspace(x0, x1, W); ys = np.linspace(y1, y0, H)
    XX, YY = np.meshgrid(xs, ys)
    LON, LAT = m(XX, YY, inverse=True)
    Z = muestrear(LON, LAT)
    S = muestrear_sombra(LON, LAT)

    def a_px(v):
        return [((x - x0) / (x1 - x0) * (W - 1), (y1 - y) / (y1 - y0) * (H - 1)) for x, y in v]
    mimg = Image.new("L", (W, H), 0); d = ImageDraw.Draw(mimg)
    for v in tierra:
        d.polygon(a_px(v), fill=255)
    for v in lagos:
        d.polygon(a_px(v), fill=0)
    tierra_m = np.asarray(mimg) > 127

    # verdor: ríos, costa mediterránea del norte y montes del norte (Media Luna Fértil)
    rimg = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(rimg)
    for seg in rios_segs:
        if len(seg) > 1:
            dr.line(a_px(seg), fill=255, width=2)
    d_rio = ndimage.distance_transform_edt(np.asarray(rimg) < 128) * km_px
    d_mar = ndimage.distance_transform_edt(tierra_m) * km_px
    lluvia_norte = np.clip((LAT - 30.9) / 1.6, 0, 1)
    w = np.maximum.reduce([
        np.clip(1 - d_rio / spec.get("verde_rio_km", 22), 0, 1) * 0.95,
        np.clip(1 - d_mar / 70, 0, 1) * lluvia_norte * (LON < 37.2) * 0.9,
        np.clip((LAT - 35.6) / 1.8, 0, 1) * 0.75,
        np.clip((LON - 45.5) / 2.0, 0, 1) * np.clip((LAT - 33.5) / 1.5, 0, 1) * 0.6,
    ])
    w = ndimage.gaussian_filter(w, sigma=max(1.5, 6 / km_px))
    zt = np.where(tierra_m, Z, 0)
    col_t = rampa(zt, SECO) * (1 - w[..., None]) + rampa(zt, VERDE) * w[..., None]

    # sombreado: claro/oscuro relativo
    s = S - ndimage.gaussian_filter(S, sigma=max(8, 40 / km_px))
    s = s / (np.percentile(np.abs(s), 98) + 1e-6)
    sombra = 1 + 0.32 * np.clip(s, -1.3, 1.3)
    # sombreado adicional desde la elevación (ilumina NO)
    gy, gx = np.gradient(ndimage.gaussian_filter(zt, 1.0))
    hs = (-gx + gy) / (km_px * 1000)
    sombra *= 1 + 0.9 * np.clip(hs * 6, -0.25, 0.25)
    col_t = np.clip(col_t * sombra[..., None], 0, 1)

    # mar: batimetría + aclarado costero
    zm = np.minimum(Z, -5)
    col_m = rampa(zm, MAR)
    d_tierra = ndimage.distance_transform_edt(~tierra_m) * km_px
    brillo = np.clip(1 - d_tierra / 18, 0, 1)[..., None] * 0.35
    col_m = col_m * (1 - brillo) + np.array(hx("#E8F5FA")) * brillo

    img = np.where(tierra_m[..., None], col_t, col_m)
    # textura sutil
    rng = np.random.default_rng(7)
    img = np.clip(img + rng.normal(0, 0.006, img.shape[:2])[..., None], 0, 1)
    return img

# ------------------------------------------------------------------ leyenda LaTeX (presentación)
def nombre_color(col):
    for k, v in C.items():
        if k in RUTA_TEX and all(abs(a - b) < 1e-6 for a, b in zip(v, col)):
            return k
    return "carmesi"

def escribir_leyenda_tex(rutas, paradas, extra, ruta):
    filas = [r"\definecolor{mapa%s}{HTML}{%s}" % (k, v) for k, v in RUTA_TEX.items()]
    for txt, col, ls in rutas:
        patron = "" if ls == "-" else (",dash pattern=on 1.4pt off 1.6pt" if ls[1][0] <= 2 else ",dash pattern=on 3.6pt off 2pt")
        filas.append(r"\tikz[baseline=-0.6ex]{\draw[white,line width=3.2pt,line cap=round](0,0)--(0.62,0);"
                     r"\draw[mapa%s,line width=1.8pt,line cap=round%s,-{Latex[length=1.6mm]}](0,0)--(0.62,0);}~%s\par" %
                     (nombre_color(col), patron, txt.replace("→", r"$\to$")))
    if paradas:
        filas.append(r"\smallskip{\color{black!70}\textbf{Itinerario}}\par")
        items = []
        for n, (nombre, col) in enumerate(paradas, 1):
            items.append(r"\tikz[baseline=-0.7ex]\node[circle,fill=mapa%s,draw=white,line width=0.5pt,text=white,"
                         r"font=\fontsize{5}{5}\selectfont\bfseries,inner sep=0.6pt,minimum size=2.6mm]{%d};\,%s" %
                         (nombre_color(col), n, nombre))
        filas.append(r"\quad ".join(items) + r"\par")
    for txt, simb in extra:
        s = {"capital": r"\tikz[baseline=-0.6ex]\node[circle,fill=white,draw=mapacarmesi,line width=1.2pt,inner sep=1.4pt]{};",
             "ciudad": r"\tikz[baseline=-0.6ex]\node[circle,fill=white,draw=black!80,line width=0.8pt,inner sep=1.2pt]{};",
             "monte": r"$\blacktriangle$"}[simb]
        filas.append(r"\makebox[0.62cm][c]{%s}~%s\par" % (s, txt))
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
    n_ley = len([r for r in spec.get("rutas", []) if r.get("leyenda")]) + len(spec.get("leyenda_extra", []))
    hay_par = any(r.get("paradas") for r in spec.get("rutas", []))
    cols_ley = 1 if ancho_in < 5.5 else 2
    pie_in = 0.0 if modo == "pres" else (math.ceil(n_ley / cols_ley) + (1.6 if hay_par else 0)) * 0.19 + 0.16
    fig = plt.figure(figsize=(ancho_in, alto_in + pie_in))
    fr = alto_in / (alto_in + pie_in)
    ax = fig.add_axes([0, 1 - fr, 1, fr]); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_axis_off()
    pt_por_m = ancho_in * 72 / (x1 - x0)

    tierra, lagos = [], []
    for xy, tipo in zip(m.coastpolygons, m.coastpolygontypes):
        (tierra if tipo in (1, 3) else lagos).append(np.column_stack(xy))

    # ríos (resolución propia, opcional)
    mr = m if spec.get("rios_res") in (None, spec.get("resolucion", "f")) else Basemap(
        projection="merc", llcrnrlon=lon0, urcrnrlon=lon1, llcrnrlat=lat0, urcrnrlat=lat1,
        resolution=spec["rios_res"], area_thresh=1e9)
    lc = mr.drawrivers(color=C["rio"], linewidth=spec.get("rio_lw", 0.6) * max(factor, 0.7) ** 0.2, zorder=3.2, ax=ax)
    lc.set_alpha(spec.get("rio_alpha", 0.9))
    rios_segs = [np.asarray(s) for s in lc.get_segments()]

    W = spec.get("pix", 1900)
    H = int(W * alto_in / ancho_in)
    km_px = (lon1 - lon0) * 111.32 * math.cos(math.radians((lat0 + lat1) / 2)) / W
    img = fondo(m, (x0, x1, y0, y1), W, H, tierra, lagos, rios_segs, km_px, spec)
    ax.imshow(img, extent=(x0, x1, y0, y1), origin="upper", zorder=1, interpolation="bilinear")

    # retícula sutil
    paso = spec.get("reticula", 5 if (lon1 - lon0) > 8 else 1)
    for lo in np.arange(math.ceil(lon0 / paso) * paso, lon1, paso):
        xs, ys = zip(*[m(lo, la) for la in np.linspace(lat0, lat1, 40)])
        ax.plot(xs, ys, color="white", lw=0.4, alpha=0.45, zorder=2)
    for la in np.arange(math.ceil(lat0 / paso) * paso, lat1, paso):
        xs, ys = zip(*[m(lo, la) for lo in np.linspace(lon0, lon1, 40)])
        ax.plot(xs, ys, color="white", lw=0.4, alpha=0.45, zorder=2)

    # lagos y costa
    if lagos:
        ax.add_patch(PathPatch(compuesto(lagos), facecolor=C["lago"], edgecolor=C["costa"], lw=0.5, zorder=3))
    ax.add_patch(PathPatch(compuesto(tierra), facecolor="none", edgecolor=C["costa"], lw=0.6, alpha=0.9,
                           zorder=3.4, joinstyle="round"))

    # regiones
    for r in spec.get("regiones", []):
        lon, lat, txt = r[:3]; o = r[3] if len(r) > 3 else {}
        x, y = m(lon, lat)
        col = o.get("color", C["region"])
        if col in (C["ladrillo"],):
            col = C["carmesi"]
        t = " ".join(txt.upper()) if o.get("espaciado", True) else txt
        ax.text(x, y, t, fontsize=o.get("tam", 8.5) * 0.92, color=col, alpha=min(1, o.get("alpha", 0.8) + 0.1),
                ha="center", va="center", rotation=o.get("rot", 0), style=o.get("estilo", "normal"),
                fontweight="semibold" if o.get("peso") == "bold" else "light", zorder=4, path_effects=halo(2.2, 0.7))
    for lon, lat, txt, *o in spec.get("aguas", []):
        o = o[0] if o else {}
        x, y = m(lon, lat)
        ax.text(x, y, txt, fontsize=o.get("tam", 7.5) * 0.95, color=C["agua_txt"], style="italic", ha="center",
                va="center", rotation=o.get("rot", 0), zorder=4, alpha=0.95, fontweight="light")
    for ln in spec.get("lineas", []):
        xy = np.array([m(lo, la) for lo, la in ln["pts"]])
        xy = suavizar(xy) if ln.get("suave", True) else xy
        ax.plot(xy[:, 0], xy[:, 1], color="white", lw=3.2, alpha=0.8, zorder=5)
        ax.plot(xy[:, 0], xy[:, 1], color=C["texto"], lw=1.3, ls=(0, (4, 2.5)), zorder=5.1)
        if ln.get("rotulo"):
            lo, la, txt = ln["rotulo"]; x, y = m(lo, la)
            ax.text(x, y, txt, fontsize=6.3, style="italic", color=C["texto"], ha="center", zorder=5, path_effects=halo())

    # trayectorias: casing blanco + degradado + flechas + paradas numeradas
    ley_rutas, paradas = [], []
    for rt in spec.get("rutas", []):
        xy = np.array([m(lo, la) for lo, la in rt["pts"]])
        xs = suavizar(xy, 36) if rt.get("suave", True) else xy
        col = rt.get("color", C["carmesi"])
        lw = rt.get("lw", 2.0) * 1.15
        ls = rt.get("ls", "-")
        ax.plot(xs[:, 0], xs[:, 1], color="white", lw=lw + 2.6, alpha=0.95, zorder=6, solid_capstyle="round")
        segs = np.stack([xs[:-1], xs[1:]], axis=1)
        t = np.linspace(0, 1, len(segs))
        base = np.array(col); claro = base + (1 - base) * 0.55
        cols = claro[None, :] * (1 - t[:, None]) + base[None, :] * t[:, None]
        if ls == "-":
            ax.add_collection(LineCollection(segs, colors=cols, linewidths=lw, zorder=6.1, capstyle="round"))
        else:
            ax.plot(xs[:, 0], xs[:, 1], color=base, lw=lw, ls=ls, zorder=6.1, dash_capstyle="round")
        # flechas a lo largo
        largo = np.r_[0, np.cumsum(np.hypot(*np.diff(xs, axis=0).T))]
        fracs = rt.get("flechas", [0.33, 0.66])
        for f in list(fracs) + [1.0]:
            k = int(np.searchsorted(largo, largo[-1] * f))
            k = max(1, min(len(xs) - 1, k))
            a, b = xs[max(0, k - 3)], xs[k]
            col_k = cols[min(len(cols) - 1, k - 1)]
            ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=lw * (7.5 if f == 1.0 else 5.5),
                                         color=col_k, lw=0, zorder=6.3, shrinkA=0, shrinkB=0,
                                         path_effects=[pe.withStroke(linewidth=1.2, foreground="white")]))
        if rt.get("leyenda"):
            ley_rutas.append((rt["leyenda"], col, ls))
        for idx, nombre in rt.get("paradas", []):
            lo, la = rt["pts"][idx]
            paradas.append((lo, la, nombre, col))

    # ciudades
    nombres_paradas = {(round(p[0], 3), round(p[1], 3)) for p in paradas}
    for c in spec.get("ciudades", []):
        lon, lat, nombre = c[:3]; o = c[3] if len(c) > 3 else {}
        x, y = m(lon, lat)
        tipo = o.get("tipo", "ciudad")
        if tipo == "capital":
            ax.plot(x, y, marker="o", ms=6.2, mfc="white", mec=C["capital"], mew=1.8, zorder=7)
            ax.plot(x, y, marker="o", ms=2.2, mfc=C["capital"], mec="none", zorder=7.1)
        elif tipo == "monte":
            ax.plot(x, y, marker="^", ms=5.6, mfc=hx("#7A5C3E"), mec="white", mew=0.7, zorder=7)
        elif tipo == "region":
            pass
        else:
            ax.plot(x, y, marker="o", ms=4.2, mfc="white", mec=C["texto"], mew=1.0, zorder=7)
        dx, dy = o.get("d", (4, 3))
        if any(abs(lon - p[0]) < 0.06 and abs(lat - p[1]) < 0.06 for p in paradas):
            dx, dy = dx + (6 if dx > 0 else -6 if dx < 0 else 0), dy + (3 if dy > 0 else -3 if dy < 0 else 0)
        ha = "left" if dx > 0 else ("right" if dx < 0 else "center")
        va = "bottom" if dy > 0 else ("top" if dy < 0 else "center")
        ax.annotate(nombre, (x, y), xytext=(dx * 1.1, dy * 1.1), textcoords="offset points", ha=ha, va=va,
                    fontsize=o.get("tam", 7.2) * 0.95, fontweight="semibold" if tipo == "capital" else "medium",
                    color=C["texto"], zorder=8, path_effects=halo(2.8), style=o.get("estilo", "normal"))
    # paradas numeradas (encima de todo)
    for n, (lo, la, nombre, col) in enumerate(paradas, 1):
        x, y = m(lo, la)
        ax.plot(x, y, marker="o", ms=9.5, mfc=col, mec="white", mew=1.3, zorder=9)
        ax.text(x, y, str(n), fontsize=5.6, color="white", ha="center", va="center", fontweight="bold", zorder=9.1)

    # leyenda (capítulo/web)
    extra = spec.get("leyenda_extra", [])
    if modo == "pres":
        escribir_leyenda_tex(ley_rutas, [(p[2], p[3]) for p in paradas], extra, salida.replace(".pdf", "_leyenda.tex"))
    elif pie_in > 0:
        axl = fig.add_axes([0, 0, 1, 1 - fr]); axl.set_xlim(0, ancho_in); axl.set_ylim(0, pie_in); axl.set_axis_off()
        axl.add_patch(Rectangle((0, 0), ancho_in, pie_in, facecolor=hx("#F7F7F4"), edgecolor="none"))
        fs = 6.8; fila = 0.19; colw = ancho_in / cols_ley
        items = [("ruta", t, c, l) for t, c, l in ley_rutas] + [("sim", t, sm, None) for t, sm in extra]
        for k, (tipo, txt, col, ls) in enumerate(items):
            cx = 0.12 + (k % cols_ley) * colw; cy = pie_in - 0.14 - (k // cols_ley) * fila
            if tipo == "ruta":
                axl.plot([cx, cx + 0.32], [cy, cy], color="white", lw=4.6, solid_capstyle="round")
                axl.plot([cx, cx + 0.32], [cy, cy], color=col, lw=2.4, ls=ls, solid_capstyle="round")
            else:
                mk = {"capital": ("o", "white", C["capital"]), "ciudad": ("o", "white", C["texto"]),
                      "monte": ("^", hx("#7A5C3E"), "white")}[col]
                axl.plot([cx + 0.16], [cy], marker=mk[0], ms=5, mfc=mk[1], mec=mk[2], mew=1.2)
            axl.text(cx + 0.42, cy, txt, fontsize=fs, va="center", color=C["texto"])
        if paradas:
            cy = pie_in - 0.14 - math.ceil(len(items) / cols_ley) * fila - 0.03
            axl.text(0.12, cy, "Itinerario", fontsize=fs, va="center", color=C["gris"], fontweight="semibold")
            x = 0.12 + 0.62
            for n, (lo, la, nombre, col) in enumerate(paradas, 1):
                if x > ancho_in - 0.9:
                    x = 0.12 + 0.62; cy -= fila
                axl.plot([x], [cy], marker="o", ms=8.5, mfc=col, mec="white", mew=1.0)
                axl.text(x, cy, str(n), fontsize=5.2, color="white", ha="center", va="center", fontweight="bold")
                t = axl.text(x + 0.09, cy, nombre, fontsize=fs, va="center", color=C["texto"])
                x += 0.09 + len(nombre) * fs * 0.0078 + 0.2
        axl.plot([0, ancho_in], [pie_in, pie_in], color=C["texto"], lw=0.6)

    # escala
    km = spec.get("escala_km", 100)
    ex, ey = spec.get("escala_pos", (0.70, 0.06))
    lonm, latm = lon0 + (lon1 - lon0) * ex, lat0 + (lat1 - lat0) * ey
    xa, ya = m(lonm, latm)
    xb, _ = m(lonm + km / (111.32 * math.cos(math.radians(latm))), latm)
    hbar = (y1 - y0) * 0.007
    for i in range(2):
        ax.add_patch(Rectangle((xa + (xb - xa) * i / 2, ya), (xb - xa) / 2, hbar,
                               facecolor=C["texto"] if i == 0 else "white", edgecolor=C["texto"], lw=0.6, zorder=9))
    for xv, tv in [(xa, "0"), (xb, f"{km} km")]:
        ax.text(xv, ya + hbar * 2.4, tv, fontsize=6, ha="center", color=C["texto"], zorder=9, path_effects=halo())
    # norte
    nx, ny = spec.get("norte", (0.95, 0.88))
    ax.add_patch(Polygon([(nx, ny + 0.06), (nx - 0.012, ny), (nx, ny + 0.015), (nx + 0.012, ny)], closed=True,
                         transform=ax.transAxes, facecolor=C["texto"], edgecolor="white", lw=0.8, zorder=9))
    ax.text(nx, ny + 0.072, "N", transform=ax.transAxes, ha="center", fontsize=7.5, fontweight="bold",
            color=C["texto"], zorder=9, path_effects=halo())
    # título (solo capítulo/web)
    if spec.get("titulo") and modo != "pres":
        tx, ty = spec.get("titulo_pos", (0.5, 0.965))
        ax.text(tx, ty, spec["titulo"], transform=ax.transAxes, ha="center", va="top", fontsize=10.5,
                fontweight="semibold", color=C["texto"], zorder=10, path_effects=halo(3.5))
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, edgecolor=C["texto"], lw=0.8, zorder=12))
    if pie_in > 0:
        fig.add_artist(Rectangle((0, 0), 1, 1, transform=fig.transFigure, fill=False, edgecolor=C["texto"], lw=1.0))
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
        dibujar(sp, os.path.join(a.out, "crops", f"mapa_{i}.pdf"), factor=sp.get("factor_pres", 0.58), dpi=400, modo="pres")
        dibujar(sp, os.path.join(a.out, f"mapa_{i}.png"), factor=sp.get("factor_art", 0.86), dpi=260)
        print("ok", i)
