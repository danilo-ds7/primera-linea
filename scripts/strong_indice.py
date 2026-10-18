#!/usr/bin/env python3
"""Genera datos/strong-h.json y datos/strong-g.json: índice forma/raíz -> número Strong
y una ficha breve por número (lema, transliteración, glosas RV 1909, definición de Strong).
Fuente: los archivos de morfología y léxicos de la app (app/morfo). Se corre a mano cuando cambien."""
import json, glob, re, unicodedata, collections, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(BASE, "app", "morfo")
OUT = os.path.join(BASE, "datos"); os.makedirs(OUT, exist_ok=True)

CANT = re.compile("[֑-ֽ֯׀׃-׆]")
MARKS = re.compile("[֑-ׇ]")
def he_pointed(w): return CANT.sub("", unicodedata.normalize("NFC", w)).replace("־", "").strip("׃׀ ,.;:")
def he_skel(w): return MARKS.sub("", unicodedata.normalize("NFC", w)).replace("־", "").strip("׃׀ ,.;:")
def gr_norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return w.replace("ς", "σ").strip(".,;:·’'")

VACIAS = {"no","mas","más","porque","así","pero","que","y","de","el","la","los","las","en","a","con","por","para","se","su","sus","lo","le","les","han","ha","es","del","al","un","una","mi","tu","mío","nuestro","conforme","como","cuando","pues","ni","o","este","esta","ese","esa"}
def ficha(e):
    pares = [(g, n) for g, n in zip(e.get("es", []), e.get("n", [])) if g.lower() not in VACIAS]
    tope = pares[0][1] if pares else 0
    es = ", ".join([g for g, n in pares if n >= max(2, tope * 0.08)][:6] or [g for g, n in pares[:1]])
    df = (e.get("df") or "").strip()
    if len(df) > 260: df = df[:257].rsplit(" ", 1)[0] + "…"
    return [e.get("l", ""), e.get("x", ""), es, df]

def construir(lex_file, form_files, norm, skel, prefijo, salida):
    lex = json.load(open(os.path.join(M, lex_file)))
    formas = collections.defaultdict(collections.Counter)
    esq = collections.defaultdict(collections.Counter)
    for f in form_files:
        d = json.load(open(f))
        for libro in d.values():
            for cap in libro.values():
                for vs in cap.values():
                    for t in vs:
                        w, s = t[0], t[1]
                        if not s or not s.startswith(prefijo): continue
                        s = s.split("/")[0]
                        if s not in lex: continue
                        formas[norm(w)][s] += 1
                        esq[skel(w)][s] += 1
    total = collections.Counter()
    for c in formas.values(): total.update(c)
    lemas = collections.defaultdict(list)
    for s, e in lex.items():
        if e.get("l"): lemas[skel(e["l"])].append(s); lemas[norm(e["l"])].append(s)
    def mejor(c): return c.most_common(1)[0][0]
    out = {"f": {k: mejor(v) for k, v in formas.items() if k},
           "l": {k: sorted(set(v), key=lambda s: -total[s]) [:3] for k, v in lemas.items() if k},
           "s": {k: mejor(v) for k, v in esq.items() if k},
           "x": {s: ficha(e) for s, e in lex.items()}}
    fichas = out.pop("x")
    idx = salida.replace(".json", "-indice.json"); fic = salida.replace(".json", "-fichas.json")
    json.dump(out, open(os.path.join(OUT, idx), "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(fichas, open(os.path.join(OUT, fic), "w"), ensure_ascii=False, separators=(",", ":"))
    for n in (idx, fic): print(n, os.path.getsize(os.path.join(OUT, n)) // 1024, "KB")

construir("lex-h.json", sorted(glob.glob(os.path.join(M, "he", "*.json"))), he_pointed, he_skel, "H", "strong-h.json")
construir("lex-g.json", sorted(glob.glob(os.path.join(M, "byz", "*.json"))), gr_norm, gr_norm, "G", "strong-g.json")
