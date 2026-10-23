"""Texto original para las fichas de la línea de Moisés, leído de los textos de dominio público
y abiertos que ya trae la app del sitio (no se transcribe a mano: así no se inventan vocales).

- Hebreo: Códice de Leningrado (WLC, app/biblias/codex), sin acentos de cantilación ni meteg.
- Griego: SBL Greek New Testament (app/morfo/sbl), palabra por palabra.
"""
import json, re
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
APP = RAIZ / "app"
LIBROS = {"Gn": 1, "Ex": 2, "Lv": 3, "Nm": 4, "Dt": 5, "Jos": 6, "Jue": 7, "1 S": 9, "1 R": 11, "2 R": 12, "Sal": 19, "Is": 23, "Jer": 24, "Os": 28, "Mi": 33,
          "Mt": 40, "Mc": 41, "Lc": 42, "Jn": 43, "Hch": 44, "Ro": 45, "1 Co": 46, "2 Co": 47, "Heb": 58, "Jud": 65, "Ap": 66}
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

@lru_cache(None)
def _grupo(carpeta, libro):
    for f in sorted((APP / carpeta).glob("g*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if str(libro) in d: return d[str(libro)]
    raise KeyError(libro)

def _limpia_he(t):
    t = re.sub("[\u0591-\u05AF\u05BD\u034F\u200C\u200D]", "", t)   # cantilación, meteg, CGJ
    t = t.replace("\u05C3", "").replace("\u05C0", "")              # sof pasuq, paseq
    t = re.sub(r"ך(?![\u05B0-\u05C7])", "ךְ", t)                         # kaf final sin sheva (convención del WLC digital)
    t = re.sub(r"\s*[פס]\s*$", "", t.strip())                           # marcas de párrafo (petuja/setuma) al final
    return re.sub(r"\s+", " ", t).strip()

def _versos(ref):
    """'Ex 3:13–15' → (libro, cap, [versos]); admite '3:13–15', '3:13.15', '3:13'."""
    if re.match(r"^(Jud|Abd|Flm|2 Jn|3 Jn) \d", ref) and ":" not in ref: ref = ref.replace(" ", " 1:", 1) if ref.count(" ") == 1 else ref   # libros de un capítulo
    m = re.match(r"^(\d? ?[A-Za-zé]+) (\d+):([\d–\-.,]+)$", ref)
    lib, cap, vs = m.group(1), int(m.group(2)), m.group(3)
    out = []
    for p in re.split(r"[.,]", vs):
        if re.search(r"[–-]", p):
            a, b = map(int, re.split(r"[–-]", p)); out += list(range(a, b + 1))
        else: out.append(int(p))
    return LIBROS[lib], cap, out

def he(ref, marcar=None):
    """Texto hebreo del WLC. Con varios versos, cada uno lleva su número (‸n‸ → <sup>)."""
    lib, cap, vs = _versos(ref)
    d = _grupo("biblias/codex", lib)[str(cap)]
    marcar = len(vs) > 1 if marcar is None else marcar
    return " ".join((f"‸{v}‸" if marcar else "") + _limpia_he(d[str(v)]) for v in vs)

def gr(ref):
    """Texto griego del SBLGNT; con varios versos, uno por línea con su número volado."""
    lib, cap, vs = _versos(ref)
    d = _grupo("morfo/sbl", lib)[str(cap)]
    lin = [" ".join(w[0] for w in d[str(v)]) for v in vs]
    if len(vs) == 1: return lin[0]
    return "\n".join(f"{str(v).translate(SUP)} {t}" for v, t in zip(vs, lin))

if __name__ == "__main__":
    print(he("Ex 3:14")); print(he("Ex 3:13–15")); print(gr("Heb 11:24–26")); print(he("Dt 6:4–5"))
