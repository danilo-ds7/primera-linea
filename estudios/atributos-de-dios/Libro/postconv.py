"""Pos-proceso tras convertir.py: comillas tipográficas en títulos, etiquetas con sufijo
del atributo (tomadas del capítulo del libro ya existente) y "Pink, 1930/2020" -> "Pink, 2020".
Uso: python3 postconv.py <convertido.tex> <capitulo_libro_existente.tex> <salida.tex>"""
import re, sys
src, ref, dst = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
r = open(ref, encoding='utf-8').read()

def quotes(m):
    t = m.group(2).replace('``', '“').replace("''", '”')
    return m.group(1) + t + '}'
s = re.sub(r'(\\(?:sub)*section\*?(?:\[[^\]]*\])?\{)((?:[^{}]|\{[^{}]*\})*)\}', quotes, s)
s = s.replace('Pink, 1930/2020', 'Pink, 2020')

labs_new = re.findall(r'\\label\{([^}]*)\}', s)
labs_ref = re.findall(r'\\label\{([^}]*)\}', r)
mp = {}
if len(labs_new) == len(labs_ref):
    mp = {a: b for a, b in zip(labs_new, labs_ref) if a != b}
else:
    # emparejar por orden solo los que coinciden en nombre base
    print('aviso: distinto número de etiquetas', len(labs_new), len(labs_ref), file=sys.stderr)
if mp:
    def relab(m):
        return m.group(1) + '{' + mp.get(m.group(2), m.group(2)) + '}'
    s = re.sub(r'(\\(?:label|ref|pageref|autoref))\{([^}]*)\}', relab, s)
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(mp), 'etiquetas renombradas')
