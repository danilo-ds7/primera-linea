#!/usr/bin/env python3
"""Genera los léxicos de dominio público por número Strong para el Lector y el sitio, SOLO con las definiciones:
  app/lexicos/bdb/NNN.json     Brown, Driver y Briggs (1906), hebreo y arameo (números H): elementos <def>, por tronco y acepción
  app/lexicos/abbott/NNN.json  Abbott-Smith (1922), griego del NT (números G): elementos <gloss>, por acepción
Bloques de 250 números. Cada valor es una lista de artículos [lema, texto]; el texto va una acepción por línea.

Las traducciones al español (traducción propia de Primera Línea) están en app/lexicos/bdb-es/ y app/lexicos/abbott-es/,
con las mismas claves. Si se regenera el inglés, revisar que las claves coincidan (este script avisa las que falten).

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

def L(t): return t.split("}", 1)[-1]

def limpio(s): return re.sub(r'\s+',' ',s or '').strip(' ,;:.—-')
def defs_de(el, tag, saltar_sub=True):
    out=[]
    for c in el:
        n=L(c.tag)
        if n==tag:
            t=limpio(''.join(c.itertext()))
            if t and t not in out: out.append(t)
        elif n in ('sense','stem','status','page','pb','re','etym','note','form'): continue
        elif not saltar_sub:
            out+=defs_de(c,tag,False)
        else:
            out+=defs_de(c,tag,True)
    return out
def senses(el, tag, pref, pend=None):
    lines=[]
    for c in el:
        if L(c.tag)!='sense': continue
        st=next((s for s in c if L(s.tag)=='stem'),None)
        lab=pend
        if st is not None: lab=limpio(st.text)+'.'
        n=(c.get('n') or '').strip('.() ')
        num=((pref+'.' if pref and re.match(r'^[IVX]+$',pref) else pref)+n) if n else pref
        ds=defs_de(c,tag)
        if ds:
            head=' '.join(x for x in [lab, (num+'.') if num else None] if x)
            lines.append(((head+' ') if head else '')+', '.join(ds)); lab=None
        sub=senses(c,tag,num,lab)
        lines+=sub
        if lab and sub: lab=None
        pend=None
    return lines
def bdb(ruta):
    r=ruta+'/'
    idx=ET.parse(r+'LexicalIndex.xml').getroot(); por=collections.defaultdict(list)
    for x in idx.iter():
        if L(x.tag)=='xref' and x.get('bdb') and (x.get('strong') or '').isdigit():
            s='H'+str(int(x.get('strong')))
            if x.get('bdb') not in por[s]: por[s].append(x.get('bdb'))
    ent={}
    for e in ET.parse(r+'BrownDriverBriggs.xml').getroot().iter():
        if L(e.tag)=='entry' and e.get('id'):
            w=next((c for c in e if L(c.tag)=='w'),None)
            lines=[]; top=defs_de(e,'def')
            if top: lines.append(', '.join(top))
            lines+=senses(e,'def','')
            if lines: ent[e.get('id')]=[(w.text or '').strip() if w is not None else '', '\n'.join(lines)]
    d={}
    for s,ids in por.items():
        a=[ent[i] for i in ids if i in ent]
        if a: d[s]=a
    return d
def abbott(ruta):
    raiz=ET.parse(ruta+'/abbott-smith.tei.xml').getroot(); d=collections.defaultdict(list)
    for e in raiz.iter():
        if L(e.tag)!='entry': continue
        n=e.get('n') or ''
        if '|' not in n: continue
        lema,nums=n.split('|',1)
        lines=[]; top=defs_de(e,'gloss')
        if top: lines.append(', '.join(top))
        lines+=senses(e,'gloss','')
        if not lines: continue
        for g in re.findall(r'G(\d+)',nums): d['G'+str(int(g))].append([lema.strip(),'\n'.join(lines)])
    return dict(d)

def bloques(datos, carpeta):
    cub = collections.defaultdict(dict)
    for s, v in datos.items(): cub[int(s[1:]) // BLOQUE][s] = v
    d = os.path.join(SAL, carpeta); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.endswith(".json"): os.remove(os.path.join(d, f))
    for b, v in sorted(cub.items()):
        with open(os.path.join(d, "%03d.json" % b), "w", encoding="utf-8") as f:
            json.dump(v, f, ensure_ascii=False, separators=(",", ":"))

def faltan(datos, carpeta):
    d = os.path.join(SAL, carpeta + "-es"); es = {}
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith(".json"): es.update(json.load(open(os.path.join(d, f), encoding="utf-8")))
    sin = [k for k in datos if k not in es or len(es[k]) != len(datos[k])]
    if sin: print("  AVISO: %d números sin traducción al español en %s-es (p. ej. %s)" % (len(sin), carpeta, ", ".join(sin[:5])))

if __name__ == "__main__":
    B = bdb(sys.argv[1]); bloques(B, "bdb"); print("BDB:", len(B), "números H"); faltan(B, "bdb")
    A = abbott(sys.argv[2]); bloques(A, "abbott"); print("Abbott-Smith:", len(A), "números G"); faltan(A, "abbott")
