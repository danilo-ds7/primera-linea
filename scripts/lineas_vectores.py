#!/usr/bin/env python3
"""Capas vectoriales para los mapas interactivos (MapLibre): costa, ríos, lagos, fronteras y
ciudades actuales, a partir de Natural Earth 1:10M (dominio público), recortadas a la región y
simplificadas. Agrega ríos antiguos o menores que Natural Earth no trae (Balij, Jabur, Orontes,
brazo pelusíaco del Nilo y los afluentes del Jordán), trazados de forma esquemática.

Uso: python3 scripts/lineas_vectores.py RUTA_NATURAL_EARTH [slug]
Salida: estudios/lineas/<slug>/mapa/base.json
"""
import json, sys
from pathlib import Path
from shapely.geometry import shape, box, mapping, LineString

NE = Path(sys.argv[1]); SLUG = sys.argv[2] if len(sys.argv) > 2 else "abraham"
OUT = Path(__file__).resolve().parent.parent / "estudios" / "lineas" / SLUG / "mapa"
OUT.mkdir(parents=True, exist_ok=True)
CAJA = box(26, 25.5, 52.5, 41.5)

def rnd(o, nd=4):
    if isinstance(o, float): return round(o, nd)
    if isinstance(o, (list, tuple)): return [rnd(x, nd) for x in o]
    if isinstance(o, dict): return {k: rnd(v, nd) for k, v in o.items()}
    return o

def capa(nombre, filtro=lambda p: True, tol=.0015, props=lambda p: {}):
    feats = []
    for f in json.load(open(NE / f"{nombre}.geojson"))["features"]:
        p = f["properties"]
        if not filtro(p): continue
        g = shape(f["geometry"])
        if not g.is_valid: g = g.buffer(0)
        if not g.intersects(CAJA): continue
        g = g.intersection(CAJA).simplify(tol, preserve_topology=True)
        if g.is_empty: continue
        feats.append({"type": "Feature", "properties": props(p), "geometry": rnd(mapping(g))})
    return {"type": "FeatureCollection", "features": feats}

MODERNOS = {"Suez Canal", "Ismailiya Canal", "Gharraf Canal", "Hindiyah Channel"}
NOMBRES = {"Euphrates": "Éufrates", "Al Furat": "Éufrates", "Firat": "Éufrates", "Tigris": "Tigris", "Dicle": "Tigris",
           "Nile": "Nilo", "Jordan": "Jordán", "Shatt al Arab": "Shatt al-Arab", "Karkheh": "Karjé",
           "Rosetta Branch": "Brazo de Rosetta", "Damietta Branch": "Brazo de Damieta", "Shatt al Hillah": "Shatt al-Hilla"}
rios = capa("ne_10m_rivers_lake_centerlines", tol=.002,
            props=lambda p: {"n": NOMBRES.get(p.get("name"), p.get("name") or ""), "hoy": int(p.get("name") in MODERNOS),
                             "r": int(p.get("scalerank") or 9)})
EXTRA = [  # nombre, puntos (lat, lon), rango
    ("Balij", [(36.95, 39.08), (36.70, 39.10), (36.40, 39.05), (36.10, 39.05), (35.95, 39.02)], 5),
    ("Jabur", [(36.85, 40.07), (36.55, 40.40), (36.20, 40.60), (35.80, 40.55), (35.45, 40.50), (35.15, 40.43)], 5),
    ("Orontes", [(34.35, 36.40), (34.73, 36.70), (35.13, 36.75), (35.55, 36.40), (35.95, 36.35), (36.20, 36.15), (36.04, 35.96)], 6),
    ("Brazo pelusíaco (antiguo)", [(30.12, 31.25), (30.57, 31.51), (30.79, 31.82), (30.95, 32.20), (31.04, 32.55)], 4),
    ("Yarmuk", [(32.75, 36.02), (32.72, 35.87), (32.70, 35.75), (32.69, 35.63), (32.68, 35.57)], 7),
    ("Yaboc", [(32.14, 36.06), (32.17, 35.95), (32.20, 35.80), (32.18, 35.68), (32.17, 35.56)], 7),
    ("Arnón", [(31.50, 36.02), (31.47, 35.90), (31.47, 35.80), (31.48, 35.66), (31.46, 35.57)], 7),
    ("Quisón", [(32.58, 35.22), (32.65, 35.14), (32.71, 35.07), (32.79, 35.01), (32.82, 34.99)], 8),
    ("Besor", [(31.27, 34.82), (31.34, 34.68), (31.43, 34.56), (31.46, 34.50)], 8),
    ("Zered", [(30.95, 36.02), (31.03, 35.78), (31.12, 35.62), (31.17, 35.53)], 8),
]
for n, pts, r in EXTRA:
    rios["features"].append({"type": "Feature", "properties": {"n": n, "hoy": 0, "r": r, "esq": 1},
                             "geometry": {"type": "LineString", "coordinates": [[lo, la] for la, lo in pts]}})

NATURALES = {"Dead Sea": "Mar Salado", "Sea of Galilee": "Kinéret", "Lake Van": "Lago Van"}
lagos = capa("ne_10m_lakes", tol=.001, props=lambda p: {"n": NATURALES.get(p.get("name"), p.get("name") or ""),
                                                        "hoy": int(p.get("name") not in NATURALES)})
costa = capa("ne_10m_coastline", tol=.0012, props=lambda p: {})
fronteras = capa("ne_10m_admin_0_boundary_lines_land", tol=.002, props=lambda p: {})
PAISES = {"Iraq": "IRAK", "Syria": "SIRIA", "Turkey": "TURQUÍA", "Jordan": "JORDANIA", "Israel": "ISRAEL", "Lebanon": "LÍBANO",
          "Egypt": "EGIPTO", "Saudi Arabia": "ARABIA SAUDITA", "Iran": "IRÁN", "Kuwait": "KUWAIT", "Palestine": "PALESTINA", "Cyprus": "CHIPRE"}
paises = []
for f in json.load(open(NE / "ne_10m_admin_0_countries.geojson"))["features"]:
    p = f["properties"]; n = PAISES.get(p.get("NAME_EN") or p.get("NAME"))
    if n and p.get("LABEL_X"):
        paises.append({"n": n, "c": rnd([p["LABEL_X"], p["LABEL_Y"]], 3)})
CIUDADES = {"Baghdad": "Bagdad", "Damascus": "Damasco", "Amman": "Ammán", "Jerusalem": "Jerusalén", "Cairo": "El Cairo",
            "Beirut": "Beirut", "Aleppo": "Alepo", "Mosul": "Mosul", "Basra": "Basora", "Tel Aviv-Yafo": "Tel Aviv",
            "Gaza": "Gaza", "Nablus": "Nablus", "Hebron": "Hebrón", "Beersheba": "Beerseba", "Sanliurfa": "Şanlıurfa",
            "Gaziantep": "Gaziantep", "Raqqa": "Raqqa", "Dayr az Zawr": "Deir ez-Zor", "Nasiriyah": "Nasiriya",
            "Haifa": "Haifa", "Alexandria": "Alejandría", "Port Said": "Port Said", "Suez": "Suez", "Ismailia": "Ismailía",
            "Kuwait": "Kuwait", "Homs": "Homs", "Tripoli": "Trípoli", "Kirkuk": "Kirkuk", "Najaf": "Nayaf", "Karbala": "Kerbala",
            "Aqaba": "Áqaba", "Eilat": "Eilat", "Antakya": "Antioquía (Antakya)", "Hama": "Hama", "Irbid": "Irbid",
            "Ramallah": "Ramala", "Al Hillah": "Hilla", "Tikrit": "Tikrit", "Diyarbakir": "Diyarbakır", "Adana": "Adana"}
ciudades = []
for f in json.load(open(NE / "ne_10m_populated_places_simple.geojson"))["features"]:
    p = f["properties"]; n = CIUDADES.get(p.get("name"))
    if n and CAJA.contains(shape(f["geometry"])):
        lo, la = f["geometry"]["coordinates"]
        ciudades.append({"n": n, "c": [round(lo, 4), round(la, 4)], "cap": int(p.get("adm0cap") or 0)})
vistos = set(); ciudades = [c for c in ciudades if not (c["n"] in vistos or vistos.add(c["n"]))]
base = {"rios": rios, "lagos": lagos, "costa": costa, "fronteras": fronteras, "paises": paises, "ciudades": ciudades,
        "fuente": "Natural Earth 1:10M (dominio público); ríos menores y brazo pelusíaco trazados de forma esquemática."}
(OUT / "base.json").write_text(json.dumps(base, ensure_ascii=False, separators=(",", ":")))
print({k: (len(v["features"]) if isinstance(v, dict) else len(v)) for k, v in base.items() if k != "fuente"},
      (OUT / "base.json").stat().st_size // 1024, "KB")
