#!/usr/bin/env python3
"""Relieve sombreado para los mapas interactivos de las líneas de tiempo.

Entrada: los mosaicos Copernicus DEM GLO-90 de la rama `datos-relieve`
(datos-relieve/amplio.tif a 15" y datos-relieve/levante.tif a 3") y la costa de Natural Earth 1:10M.
Salida: imágenes WebP en Web Mercator (EPSG:3857) listas para MapLibre, en
estudios/lineas/<slug>/relieve/, y un indice.json con las esquinas de cada imagen.

Sombreado: iluminación multidireccional (cuatro azimuts, como en la cartografía suiza),
sombreado por pendiente y tintas hipsométricas de tono pergamino. El mar lleva un degradado
desde la costa («water lining» atenuado).

Uso: python3 scripts/lineas_relieve.py RUTA_DATOS_RELIEVE RUTA_NATURAL_EARTH [slug]
"""
import json, math, sys
from pathlib import Path
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy import ndimage
from PIL import Image

DEM, NE = Path(sys.argv[1]), Path(sys.argv[2])
SLUG = sys.argv[3] if len(sys.argv) > 3 else "abraham"
OUT = Path(__file__).resolve().parent.parent / "estudios" / "lineas" / SLUG / "relieve"
OUT.mkdir(parents=True, exist_ok=True)

# pergamino: (altura en m, color)
RAMPA = [(-450, (150, 160, 128)), (-200, (184, 186, 146)), (0, (226, 214, 170)), (150, (236, 223, 182)),
         (400, (232, 212, 164)), (800, (218, 190, 140)), (1300, (198, 166, 120)), (2000, (176, 148, 112)),
         (3000, (190, 176, 156)), (4200, (232, 228, 220))]
MAR = np.array((118, 164, 200), float)        # azul de atlas: mar abierto
MAR_COSTA = np.array((176, 208, 228), float)  # aguas someras junto a la costa

def merc(lon, lat):
    x = math.radians(lon) * 6378137
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * 6378137
    return x, y

def tierra(bounds_merc, shape, transform):
    land = json.load(open(NE / "ne_10m_land.geojson"))
    from shapely.geometry import shape as shp, box, mapping
    from shapely.ops import transform as stf
    import pyproj
    T = pyproj.Transformer.from_crs(4326, 3857, always_xy=True).transform
    w, s, e, n = bounds_merc
    caja = box(w, s, e, n)
    geoms = []
    for f in land["features"]:
        g = stf(T, shp(f["geometry"]).buffer(0))
        if g.intersects(caja):
            geoms.append(g.intersection(caja))
    return rasterize([(mapping(g), 1) for g in geoms], out_shape=shape, transform=transform, fill=0, dtype="uint8")

def sombreado(z, px, exag):
    """Hillshade multidireccional + pendiente. z en metros, px = tamaño de píxel en metros."""
    z = z * exag
    gy, gx = np.gradient(z, px)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    alt = math.radians(42)
    hs = np.zeros_like(z)
    for az, w in ((315, .45), (270, .2), (360, .2), (225, .15)):
        a = math.radians(360 - az + 90)
        hs += w * (math.sin(alt) * np.cos(slope) + math.cos(alt) * np.sin(slope) * np.cos(a - aspect))
    hs = np.clip(hs, 0, 1)
    hs = ndimage.gaussian_filter(hs, .6)
    return hs, slope

def tinta(z):
    zs = np.array([r[0] for r in RAMPA], float)
    cs = np.array([r[1] for r in RAMPA], float)
    out = np.empty(z.shape + (3,), float)
    for k in range(3):
        out[..., k] = np.interp(z, zs, cs[:, k])
    return out

def render(nombre, tif, latlon, ancho_px, exag, trozos=(1, 1)):
    s_, n_, w_, e_ = latlon
    xw, ys = merc(w_, s_); xe, yn = merc(e_, n_)
    W = ancho_px; H = int(round(W * (yn - ys) / (xe - xw)))
    tr = from_bounds(xw, ys, xe, yn, W, H)
    z = np.full((H, W), np.nan, np.float32)
    with rasterio.open(tif) as src:
        reproject(rasterio.band(src, 1), z, src_nodata=-32768, dst_nodata=np.nan, dst_transform=tr, dst_crs="EPSG:3857",
                  resampling=Resampling.cubic)
    land = tierra((xw, ys, xe, yn), (H, W), tr).astype(bool)
    z = np.where(np.isnan(z), 0, z)
    z = np.where(land, z, 0)
    px = (xe - xw) / W * math.cos(math.radians((s_ + n_) / 2))   # metros reales por píxel
    hs, slope = sombreado(z, px, exag)
    col = tinta(z)
    # mezcla: luz suave sobre tintas + oscurecimiento por pendiente
    luz = .55 + .62 * hs
    col = col * luz[..., None]
    col *= (1 - .18 * np.clip(np.degrees(slope) / 35, 0, 1))[..., None]
    # papel: grano muy fino
    rng = np.random.default_rng(7)
    col += rng.normal(0, 2.2, col.shape[:2])[..., None]
    # mar con degradado desde la costa
    d = ndimage.distance_transform_edt(~land) * (px / 1000)          # km al mar abierto
    t = np.clip(d / (14 if W / (e_ - w_) > 800 else 45), 0, 1)[..., None] ** .7
    mar = MAR_COSTA * (1 - t) + MAR * t
    col = np.where(land[..., None], col, mar)
    img = np.clip(col, 0, 255).astype(np.uint8)
    indice = []
    nx, ny = trozos
    for j in range(ny):
        for i in range(nx):
            x0, x1 = W * i // nx, W * (i + 1) // nx
            y0, y1 = H * j // ny, H * (j + 1) // ny
            f = f"{nombre}-{j}{i}.webp" if (nx, ny) != (1, 1) else f"{nombre}.webp"
            Image.fromarray(img[y0:y1, x0:x1]).save(OUT / f, "WEBP", quality=86, method=6)
            # esquinas en lon/lat: [NO, NE, SE, SO]
            def ll(px_, py_):
                X = xw + (xe - xw) * px_ / W; Y = yn - (yn - ys) * py_ / H
                lon = math.degrees(X / 6378137); lat = math.degrees(2 * math.atan(math.exp(Y / 6378137)) - math.pi / 2)
                return [round(lon, 6), round(lat, 6)]
            indice.append({"src": f"{SLUG}/relieve/{f}", "coords": [ll(x0, y0), ll(x1, y0), ll(x1, y1), ll(x0, y1)], "nivel": nombre})
            print(f, (x1 - x0, y1 - y0), (OUT / f).stat().st_size // 1024, "KB")
    return indice

idx = []
idx += render("amplio", DEM / "amplio.tif", (27.0, 40.0, 28.0, 51.0), 3600, 2.4, (2, 1))
idx += render("levante", DEM / "levante.tif", (29.5, 34.4, 33.3, 37.2), 4200, 1.5, (2, 3))
if SLUG == "moises":   # delta oriental, Sinaí, golfo de Aqaba y Madián, a 3" (rama datos-relieve: sur.tif)
    idx += render("sur", DEM / "sur.tif", (27.2, 31.6, 31.0, 36.6), 4800, 1.5, (2, 2))
(OUT / "indice.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1))
print("indice.json:", len(idx), "imágenes")
