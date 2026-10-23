"""Descarga teselas Copernicus GLO-90 (AWS Open Data) y genera dos mosaicos int16:
- amplio.tif : 27–40 N, 28–51 E a 15" (para los mapas de Mesopotamia, Siria y Egipto)
- levante.tif: 29.5–34.5 N, 33–37.5 E a 3" (resolución nativa, para Canaán)
- sur.tif    : 27–32 N, 31–37 E a 3" (delta oriental, Sinaí, golfo de Aqaba y Madián, para la línea de Moisés)
Solo se generan los mosaicos que aún no están en la rama."""
import concurrent.futures as cf, subprocess, numpy as np, rasterio
from rasterio.merge import merge
from rasterio.enums import Resampling
from pathlib import Path
D = Path("datos-relieve"); T = Path("/tmp/teselas"); T.mkdir(exist_ok=True)
URL = "https://copernicus-dem-90m.s3.amazonaws.com/{n}/{n}.tif"
def nombre(la, lo):
    return f"Copernicus_DSM_COG_30_{'N' if la>=0 else 'S'}{abs(la):02d}_00_{'E' if lo>=0 else 'W'}{abs(lo):03d}_00_DEM"
def bajar(t):
    la, lo = t; n = nombre(la, lo); f = T / f"{n}.tif"
    r = subprocess.run(["curl", "-sf", "-o", str(f), URL.format(n=n)])
    return f if r.returncode == 0 and f.exists() else None
def mosaico(lat0, lat1, lon0, lon1, res, salida):
    if (D / salida).exists(): print(salida, "ya existe"); return
    teselas = [(la, lo) for la in range(lat0, lat1) for lo in range(lon0, lon1)]
    with cf.ThreadPoolExecutor(16) as ex:
        fs = [f for f in ex.map(bajar, teselas) if f]
    print(salida, len(fs), "teselas de", len(teselas))
    srcs = [rasterio.open(f) for f in fs]
    arr, tr = merge(srcs, bounds=(lon0, lat0, lon1, lat1), res=res, nodata=-32768, resampling=Resampling.average)
    a = arr[0]; a[a < -1000] = -32768
    perfil = dict(driver="GTiff", height=a.shape[0], width=a.shape[1], count=1, dtype="int16", crs="EPSG:4326",
                  transform=tr, nodata=-32768, compress="deflate", predictor=2, zlevel=9, tiled=True)
    with rasterio.open(D / salida, "w", **perfil) as o:
        o.write(np.round(a).astype("int16"), 1)
    for s in srcs: s.close()
mosaico(27, 40, 28, 51, 15 / 3600, "amplio.tif")
mosaico(29, 35, 33, 38, 3 / 3600, "levante.tif")   # se recorta a 29.5–34.5 / 33–37.5 al dibujar
mosaico(27, 32, 31, 37, 3 / 3600, "sur.tif")       # Moisés: Gosén, Sinaí, Madián
(D / "FUENTE.txt").write_text("Copernicus DEM GLO-90 (ESA, 2021), © DLR e.V. 2010-2014 y © Airbus Defence and Space GmbH 2014-2018, "
                              "provisto bajo licencia COPERNICUS por la Unión Europea y la ESA. Descargado de AWS Open Data.\n")
