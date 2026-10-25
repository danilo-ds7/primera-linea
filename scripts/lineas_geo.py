#!/usr/bin/env python3
"""Geografía de respaldo (SVG y TikZ) para una línea de tiempo cuyo escenario no es el Levante:
polígonos de tierra, lagos y ríos de Natural Earth 1:10M, recortados y simplificados, con el formato
DATA.geo del motor ({wide:{lands,lakes,rivers}, lev:{land,lakes,rivers,land2}}, coordenadas [lat, lon]).

Uso: python3 scripts/lineas_geo.py RUTA_NATURAL_EARTH <slug>
Salida: estudios/lineas/<slug>/mapa/geo.json (datos.py lo incorpora a DATA.geo)
"""
import json, sys
from pathlib import Path
from shapely.geometry import shape, box, MultiPolygon, Polygon, MultiLineString, LineString
from shapely.ops import unary_union

NE = Path(sys.argv[1]); SLUG = sys.argv[2]
OUT = Path(__file__).resolve().parent.parent / "estudios" / "lineas" / SLUG / "mapa"
REGION = {"pablo": dict(wide=box(-10, 29.0, 42.0, 47.0), tol_w=.012,
                        lev=[box(22.3, 37.6, 23.3, 38.3), box(35.15, 31.68, 35.32, 31.87), box(34.3, 31.6, 35.9, 33.1), box(14.1, 35.7, 14.7, 36.15), box(12.35, 41.75, 12.62, 41.98)],
                        tol_l=.0015, rios=["Tiber", "Tevere", "Po", "Danube", "Vardar", "Axios", "Strymon", "Struma", "Maritsa", "Evros", "Büyük Menderes", "Buyuk Menderes", "Gediz", "Sakarya",
                                           "Kizil Irmak", "Kızılırmak", "Seyhan", "Ceyhan", "Asi", "Orontes", "Nile", "Jordan", "Rosetta Branch", "Damietta Branch", "Volturno", "Arno", "Euphrates"])}[SLUG]
NOMBRES = {"Tiber": "Tíber", "Tevere": "Tíber", "Danube": "Danubio", "Vardar": "Axios", "Strymon": "Estrimón", "Struma": "Estrimón", "Maritsa": "Hebro", "Evros": "Hebro", "Büyük Menderes": "Meandro",
           "Buyuk Menderes": "Meandro", "Gediz": "Hermo", "Sakarya": "Sangario", "Kizil Irmak": "Halis", "Kızılırmak": "Halis", "Seyhan": "Saro", "Ceyhan": "Píramo", "Asi": "Orontes", "Nile": "Nilo",
           "Jordan": "Jordán", "Rosetta Branch": "Nilo", "Damietta Branch": "Nilo", "Euphrates": "Éufrates"}

def rings(g):
    polys = list(g.geoms) if isinstance(g, MultiPolygon) else [g] if isinstance(g, Polygon) else []
    out = []
    for p in polys:
        if p.area < 1e-4: continue
        out.append([[round(y, 4), round(x, 4)] for x, y in p.exterior.coords])
    return out

def lines(g):
    ls = list(g.geoms) if isinstance(g, MultiLineString) else [g] if isinstance(g, LineString) else []
    return [[[round(y, 4), round(x, 4)] for x, y in l.coords] for l in ls if l.length > .05]

land = unary_union([shape(f["geometry"]).buffer(0) for f in json.load(open(NE / "ne_10m_land.geojson"))["features"]])
lakes_raw = [shape(f["geometry"]).buffer(0) for f in json.load(open(NE / "ne_10m_lakes.geojson"))["features"] if (f["properties"].get("scalerank") or 9) <= 6]
rios_raw = [(f["properties"].get("name"), shape(f["geometry"])) for f in json.load(open(NE / "ne_10m_rivers_lake_centerlines.geojson"))["features"]
            if f["properties"].get("name") in REGION["rios"] and (f["properties"].get("scalerank") or 9) <= 7]

def nivel(caja, tol, nombrar):
    L = rings(land.intersection(caja).simplify(tol, preserve_topology=True))
    K = [r for g in lakes_raw if g.intersects(caja) for r in rings(g.intersection(caja).simplify(tol, preserve_topology=True))]
    R = []
    for n, g in rios_raw:
        if not g.intersects(caja): continue
        for l in lines(g.intersection(caja).simplify(tol * 1.5, preserve_topology=True)):
            R.append([NOMBRES.get(n, n), l] if nombrar else l)
    return L, K, R

Lw, Kw, Rw = nivel(REGION["wide"], REGION["tol_w"], True)
EXTRA = {"pablo": [("Meandro", [[38.05, 29.6], [37.95, 29.0], [37.85, 28.4], [37.75, 28.0], [37.62, 27.6], [37.53, 27.3]]), ("Orontes", [[34.35, 36.40], [34.73, 36.70], [35.13, 36.75], [35.55, 36.40], [35.95, 36.35], [36.20, 36.15], [36.04, 35.96]]),
                   ("Axios", [[41.8, 21.5], [41.2, 21.9], [40.9, 22.4], [40.65, 22.7]]), ("Estrimón", [[41.9, 23.2], [41.4, 23.3], [41.1, 23.5], [40.83, 23.85], [40.78, 23.86]]), ("Cidno", [[37.10, 34.85], [36.95, 34.88], [36.80, 34.92], [36.70, 34.90]]),
                   ("Hermo", [[38.6, 28.5], [38.5, 27.9], [38.6, 27.3], [38.55, 26.9]])]}.get(SLUG, [])
Rw += [[n, pts] for n, pts in EXTRA if n not in {r[0] for r in Rw}]
lev_caja = unary_union(REGION["lev"])
Ll, Kl, Rl = nivel(lev_caja, REGION["tol_l"], False)
geo = {"wide": {"lands": Lw, "lakes": Kw, "rivers": Rw}, "lev": {"land": Ll, "lakes": Kl, "rivers": Rl, "land2": Ll}}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "geo.json").write_text(json.dumps(geo, ensure_ascii=False, separators=(",", ":")))
print("wide:", len(Lw), "tierras,", len(Kw), "lagos,", len(Rw), "ríos |", "lev:", len(Ll), "tierras |", (OUT / "geo.json").stat().st_size // 1024, "KB")
