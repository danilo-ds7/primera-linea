"""Herramientas para la revisión de redacción (regla 10, 19-10-2026).

  split  <capitulo.tex> <dir>      divide el .tex en trozos por \\section (00_cabeza, 01_, 02_, ..., 99_cola)
  join   <dir> <salida.tex>        vuelve a unir los trozos
  check  <original.tex> <nuevo.tex>  compara los invariantes (citas, versos, hebreo, griego, tablas,
                                   figuras, etiquetas, referencias bíblicas, cifras, citas APA)
"""
import re, sys, os, collections

BOOKS = r'(?:Gn|Éx|Ex|Lv|Nm|Dt|Jos|Jue|Rt|1~?S|2~?S|1~?R|2~?R|1~?Cr|2~?Cr|Esd|Neh|Est|Job|Sal|Pr|Ec|Cnt|Is|Jer|Lm|Lam|Ez|Dn|Os|Jl|Am|Abd|Jon|Mi|Nah|Hab|Sof|Hag|Zac|Mal|Mt|Mr|Lc|Jn|Hch|Ro|1~?Co|2~?Co|Gá|Ef|Flp|Col|1~?Ts|2~?Ts|1~?Ti|2~?Ti|Tit|Flm|He|Stg|1~?P|2~?P|1~?Jn|2~?Jn|3~?Jn|Jud|Ap)'

def split(src, d):
    s = open(src, encoding='utf-8').read()
    os.makedirs(d, exist_ok=True)
    i = s.index('\\begin{document}')
    try:
        j = s.index('\\section*{Referencias}')
    except ValueError:
        j = s.index('\\end{document}')
    head, body, tail = s[:i], s[i:j], s[j:]
    parts = re.split(r'(?m)^(?=\\section)', body)
    open(os.path.join(d, '00_cabeza.tex'), 'w', encoding='utf-8').write(head)
    for k, p in enumerate(parts, 1):
        m = re.search(r'\\section\*?\{((?:[^{}]|\{[^{}]*\})*)\}', p)
        name = re.sub(r'[^a-z0-9]+', '_', (m.group(1) if m else 'inicio').lower().encode('ascii', 'ignore').decode())[:40].strip('_')
        open(os.path.join(d, '%02d_%s.tex' % (k, name or 'sec')), 'w', encoding='utf-8').write(p)
    open(os.path.join(d, '99_cola.tex'), 'w', encoding='utf-8').write(tail)
    print('trozos:', len(parts))

def join(d, dst):
    fs = sorted(f for f in os.listdir(d) if f.endswith('.tex'))
    s = ''.join(open(os.path.join(d, f), encoding='utf-8').read() for f in fs)
    open(dst, 'w', encoding='utf-8').write(s)
    print('unido', len(fs), 'trozos ->', dst)

def inv(s):
    """Invariantes: multiconjuntos de elementos que no deben cambiar."""
    out = {}
    def env(name):
        return re.findall(r'\\begin\{%s\}.*?\\end\{%s\}' % (name, name), s, flags=re.S)
    out['cita'] = [re.sub(r'\s+', ' ', c) for c in env('cita')]
    out['verso'] = [re.sub(r'\s+', ' ', c) for c in env('verso')]
    out['tabular'] = [re.sub(r'\s+', ' ', c) for c in env('tabular')]
    out['tikz'] = [re.sub(r'\s+', ' ', c) for c in env('tikzpicture')]
    out['hebverso'] = re.findall(r'\\hebverso\{', s)
    out['heb'] = re.findall(r'\\heb[l]?\{((?:[^{}]|\{[^{}]*\})*)\}', s)
    out['grc'] = re.findall(r'\\grc\{((?:[^{}]|\{[^{}]*\})*)\}', s)
    out['label'] = re.findall(r'\\label\{([^}]*)\}', s)
    out['ref'] = re.findall(r'\\(?:ref|pageref|autoref)\{([^}]*)\}', s)
    out['section'] = re.findall(r'\\(?:sub)*section\*?(?:\[[^\]]*\])?\{((?:[^{}]|\{[^{}]*\})*)\}', s)
    out['bibl'] = re.findall(BOOKS + r'\.?~?\s?\d+[:\.]\d+(?:[-–]{1,2}\d+)?', s)
    out['cifra'] = re.findall(r'(?<![\w:\-–\.])\d{2,}(?![\w:\-–])', re.sub(r'\\(?:label|ref|pageref|fuente)\{[^}]*\}', '', s))
    out['apa'] = re.findall(r'\(([A-ZÁÉÍÓÚÑ][^()]{1,60}?,\s*(?:s\.?f\.?|\d{4}[a-z]?(?:/\d{4})?)[^()]*)\)', s)
    out['begin'] = re.findall(r'\\begin\{([a-zA-Z*]+)\}', s)
    out['includegraphics'] = re.findall(r'\\includegraphics', s)
    out['nota'] = re.findall(r'\\begin\{nota\}\[([^\]]*)\]', s)
    out['precision'] = re.findall(r'\\precision\{', s)
    out['emphterm'] = re.findall(r'\\emph\{([A-Za-zÀ-ÿ\'’\-]+)\}', s)
    return out

def check(a, b, quiet=False):
    A, B = inv(open(a, encoding='utf-8').read()), inv(open(b, encoding='utf-8').read())
    ok = True
    for k in A:
        ca, cb = collections.Counter(A[k]), collections.Counter(B[k])
        if ca != cb:
            if k in ('emphterm',):
                # los términos en cursiva pueden reordenarse; solo avisamos si desaparecen
                lost = ca - cb
                if not lost:
                    continue
                print(f'AVISO {k}: desaparecen {sum(lost.values())}: ' + ', '.join(f'{x}×{n}' for x, n in list(lost.items())[:12]))
                continue
            ok = False
            lost, new = ca - cb, cb - ca
            print(f'DIFERENCIA en {k}: faltan {sum(lost.values())}, nuevos {sum(new.values())}')
            for x, n in list(lost.items())[:8]:
                print('   - faltan:', (x[:160] + '…') if len(x) > 160 else x, f'×{n}')
            for x, n in list(new.items())[:8]:
                print('   + nuevos:', (x[:160] + '…') if len(x) > 160 else x, f'×{n}')
    wa = len(re.sub(r'\\[a-zA-Z]+', '', open(a, encoding='utf-8').read()).split())
    wb = len(re.sub(r'\\[a-zA-Z]+', '', open(b, encoding='utf-8').read()).split())
    print(f'palabras: {wa} -> {wb} ({(wb-wa)*100//max(wa,1):+d}%)')
    print('OK: invariantes conservados' if ok else 'HAY DIFERENCIAS: revisar')
    return ok

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'split': split(sys.argv[2], sys.argv[3])
    elif cmd == 'join': join(sys.argv[2], sys.argv[3])
    elif cmd == 'check': sys.exit(0 if check(sys.argv[2], sys.argv[3]) else 1)
