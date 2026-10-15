#!/usr/bin/env python3
"""
Raíces al estilo BDB a partir de los números Strong (app Lector).

Agrega a los léxicos de la app (app/morfo/lex-h.json y lex-g.json):
  rz  -> número Strong de la raíz a la que llega la palabra (si no es ella misma).
  fz  -> en la entrada de la raíz: todas las palabras que derivan de ella,
         directa o indirectamente (la "familia" completa, como en BDB).

Regla para llegar a la raíz (la misma que usa la app): se sigue la derivación
de Strong ("from H7999") mientras la palabra derive, sea de la misma raíz o sea
una forma reforzada de otra; se detiene en las compuestas ("from X and Y"),
en las raíces primitivas y a los 5 pasos.

Uso:  python3 scripts/raices.py      (se puede volver a correr: recalcula todo)
"""
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
MORFO = os.path.join(AQUI, "..", "app", "morfo")
SIGUE = {"de", "igual", "ref"}


def cadena(s, L):
    cad, vistos, x = [], set(), s
    for _ in range(5):
        e = L.get(x)
        if not e or x in vistos:
            break
        vistos.add(x)
        r = e.get("r") or []
        if not r or e.get("rel") not in SIGUE or re.search(r" and ", (e.get("dv") or "")[:80]):
            break
        x = r[0]
        if x not in L:
            break
        cad.append(x)
    return cad


def orden(s):
    return int(s[1:]) if s[1:].isdigit() else 0


def procesar(nombre):
    ruta = os.path.join(MORFO, nombre)
    with open(ruta, encoding="utf-8") as f:
        L = json.load(f)
    for e in L.values():
        e.pop("rz", None)
        e.pop("fz", None)
    familias = {}
    for s in L:
        cad = cadena(s, L)
        if cad:
            raiz = cad[-1]
            L[s]["rz"] = raiz
            familias.setdefault(raiz, set()).add(s)
    for raiz, fam in familias.items():
        L[raiz]["fz"] = sorted(fam, key=orden)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(L, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{nombre}: {sum(1 for e in L.values() if 'rz' in e)} palabras con raíz, {len(familias)} raíces con familia")


if __name__ == "__main__":
    procesar("lex-h.json")
    procesar("lex-g.json")
