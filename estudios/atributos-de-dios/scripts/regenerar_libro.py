"""Regenera los capítulos del libro a partir de los capítulos sueltos (convertir.py + postconv.py).

Uso (desde estudios/atributos-de-dios):  python3 scripts/regenerar_libro.py [NN_Atributo ...]
Sin argumentos regenera todos los atributos. El título y la nota de cada capítulo se toman de las
dos primeras líneas del capítulo del libro ya existente. La Introducción (00) no se regenera: se
mantiene a mano en Libro/capitulos/00_introduccion.tex.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
todos = sorted(d for d in os.listdir('.') if re.match(r'\d\d_', d) and d != '00_Introduccion')
sel = sys.argv[1:] or todos
tmp = tempfile.mkdtemp()
for d in sel:
    n = d.lower()
    libro = f'Libro/capitulos/{n}.tex'
    src = f'{d}/{d}_capitulo.tex'
    l1, l2 = open(libro, encoding='utf-8').read().split('\n')[:2]
    titulo = re.sub(r'^% Capítulo: (.*) \(generado.*', r'\1', l1)
    nota = l2[2:]
    conv = os.path.join(tmp, n + '.conv.tex')
    subprocess.run(['python3', 'Libro/convertir.py', src, conv, titulo, nota], check=True, capture_output=True)
    r = subprocess.run(['python3', 'Libro/postconv.py', conv, libro, libro], capture_output=True, text=True)
    print(d, '->', libro, r.stdout.strip(), r.stderr.strip())
