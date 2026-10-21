#!/usr/bin/env python3
"""Genera los léxicos de dominio público por número Strong para el Lector y el sitio:
  app/lexicos/bdb/NNN.json     Brown, Driver y Briggs (1906), hebreo y arameo (números H)
  app/lexicos/abbott/NNN.json  Abbott-Smith (1922), griego del NT (números G)
Bloques de 250 números. Cada valor es una lista de artículos [título, texto].

Fuentes (se clonan aparte y se pasan como argumentos):
  https://github.com/openscriptures/HebrewLexicon            (BDB: texto de dominio público; marcado CC BY 4.0, Open Scriptures Hebrew Bible Project)
  https://github.com/translatable-exegetical-tools/Abbott-Smith  (dominio público)

Uso: python3 scripts/lexicos_publicos.py RUTA/HebrewLexicon RUTA/Abbott-Smith
Se corre a mano; los JSON quedan en el repositorio."""
import os, re, sys, json, collections
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAL = os.path.join(BASE, "app", "lexicos")
BLOQUE = 250

def local(tag): return tag.split("}", 1)[-1]

def texto(el, saltar=(), parrafo=(), numerar=()):
    """Texto plano del elemento: los nodos de «parrafo» empiezan línea nueva; «numerar» antepone su atributo n."""
    out = []
    def rec(e, top=False):
        t = local(e.tag)
        if t in saltar:
            if e.tail: out.append(e.tail)
            return
        if t in parrafo and not top: out.append("\n")
        if t in numerar and e.get("n"):
            n = e.get("n").strip(); out.append(n + ("" if n.endswith((".", ")")) else ".") + " ")
        if e.text: out.append(e.text)
        for c in e: rec(c)
        if e.tail: out.append(e.tail)
    rec(el, True)
    s = "".join(out)
    s = re.sub(r"[ \t\r]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()

def bloques(datos, carpeta):
    cub = collections.defaultdict(dict)
    for s, v in datos.items(): cub[int(s[1:]) // BLOQUE][s] = v
    d = os.path.join(SAL, carpeta); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.endswith(".json"): os.remove(os.path.join(d, f))
    for b, v in sorted(cub.items()):
        with open(os.path.join(d, "%03d.json" % b), "w", encoding="utf-8") as f:
            json.dump(v, f, ensure_ascii=False, separators=(",", ":"))

def bdb(ruta):
    idx = ET.parse(os.path.join(ruta, "LexicalIndex.xml")).getroot()
    por_id = collections.defaultdict(list)
    for x in idx.iter():
        if local(x.tag) == "xref" and x.get("bdb") and (x.get("strong") or "").isdigit():
            s = "H" + str(int(x.get("strong")))
            if x.get("bdb") not in por_id[s]: por_id[s].append(x.get("bdb"))
    lex = ET.parse(os.path.join(ruta, "BrownDriverBriggs.xml")).getroot()
    ent = {}
    for e in lex.iter():
        if local(e.tag) == "entry" and e.get("id"):
            w = next((c for c in e if local(c.tag) == "w"), None)
            ent[e.get("id")] = ((w.text or "").strip() if w is not None else "",
                                texto(e, saltar=("status", "page"), parrafo=("sense", "stem"), numerar=("sense",)))
    datos = {}
    for s, ids in por_id.items():
        arts = [[ent[i][0], ent[i][1]] for i in ids if i in ent and ent[i][1]]
        if arts: datos[s] = arts
    bloques(datos, "bdb"); return len(datos)

def abbott(ruta):
    raiz = ET.parse(os.path.join(ruta, "abbott-smith.tei.xml")).getroot()
    datos = collections.defaultdict(list)
    for e in raiz.iter():
        if local(e.tag) != "entry": continue
        n = e.get("n") or ""
        if "|" not in n: continue
        lema, nums = n.split("|", 1)
        t = texto(e, saltar=("pb", "note"), parrafo=("sense", "re"), numerar=("sense",))
        if not t: continue
        for g in re.findall(r"G(\d+)", nums):
            datos["G" + str(int(g))].append([lema.strip(), t])
    bloques(dict(datos), "abbott"); return len(datos)

if __name__ == "__main__":
    print("BDB:", bdb(sys.argv[1]), "números H")
    print("Abbott-Smith:", abbott(sys.argv[2]), "números G")
