"""Convierte el capítulo de artículo (estudios-teo) al formato del libro maestro."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
titulo = sys.argv[3] if len(sys.argv) > 3 else 'La santidad de Dios'
nota = sys.argv[4] if len(sys.argv) > 4 else 'Texto ancla: Isaías 6:1–8. Clasificación: Identidad; incomunicable en su plenitud, comunicable como reflejo.'
s = open(src, encoding='utf-8').read()

# Cuerpo: desde la primera \section hasta antes de Referencias
ini = s.index('\\section{')
fin = s.index('\\section*{Referencias}')
body = s[ini:fin]

LIBROS = {'1~Co': '1 Corintios', '1~P': '1 Pedro', '1~S': '1 Samuel', '2~Co': '2 Corintios',
          '1~Ts': '1 Tesalonicenses', '1~Jn': '1 Juan', 'Ap': 'Apocalipsis', 'Col': 'Colosenses',
          'Is': 'Isaías', 'Jn': 'Juan', 'Lv': 'Levítico', 'Ro': 'Romanos', 'Sal': 'Salmos',
          'Éx': 'Éxodo', 'Nah': 'Nahúm', 'Nm': 'Números', 'Dt': 'Deuteronomio', 'Gn': 'Génesis',
          'Lam': 'Lamentaciones', 'Sof': 'Sofonías', 'Mt': 'Mateo', 'He': 'Hebreos', 'Ef': 'Efesios',
          'Stg': 'Santiago', 'Jer': 'Jeremías', 'Os': 'Oseas', 'Hab': 'Habacuc',
          'Mi': 'Miqueas', 'Jon': 'Jonás', 'Mal': 'Malaquías', 'Jue': 'Jueces', 'Lc': 'Lucas',
          'Tit': 'Tito', '1~Ti': '1 Timoteo', 'Jl': 'Joel', 'Mr': 'Marcos', 'Hch': 'Hechos',
          'Pr': 'Proverbios', 'Dn': 'Daniel', 'Ec': 'Eclesiastés', '1~R': '1 Reyes', '2~Ti': '2 Timoteo'}

def ref_larga(r):
    r = r.strip('()')
    m = re.match(r'(.+?)\s+([\d:\-, ]+?)(\s*\[[^\]]*\])?$', r)
    libro, cap = m.group(1), m.group(2)
    extra = (m.group(3) or '').replace('--', '–')
    if libro == 'Sal':
        libro = 'Salmo'
    return f"{(libro if libro == 'Salmo' else LIBROS.get(libro, libro))} {cap.replace('--', '–')}{extra}"

# Versos: cita -> verso
def verso(m):
    texto, ref = m.group(1).strip(), m.group(2)
    return '\\begin{verso}{%s}\n%s\n\\end{verso}' % (ref_larga(ref), texto)
body = re.sub(r'\\begin\{cita\}(.*?)\\fuente\{(\([^}]*\))\}\\end\{cita\}', verso, body, flags=re.S)

# Precisiones
def prec(m):
    t = m.group(1).strip()
    t = t[0].lower() + t[1:]
    return '\\precision{%s}' % t
body = re.sub(r'\\begin\{nota\}\[Precisión\](.*?)\\end\{nota\}', prec, body, flags=re.S)
def prectext(m):
    t = m.group(1).strip()
    return '\\precision{(textual) %s}' % (t[0].lower() + t[1:])
body = re.sub(r'\\begin\{nota\}\[Precisión textual\](.*?)\\end\{nota\}', prectext, body, flags=re.S)

# Apartados filológicos: tabla de 3 columnas -> entorno del libro; prosa -> filologiatexto
def filo(m):
    titulo, cont = m.group(1), m.group(2).strip()
    tab = re.search(r'\\begin\{tabular\}\{[^\n]*\}\n(.*?)\\end\{tabular\}', cont, flags=re.S)
    if tab:
        filas = re.sub(r'\\\\\[2pt\]', r'\\\\', tab.group(1)).strip()
        if not filas.endswith('\\\\'):
            filas += ' \\\\'
        return '\\begin{filologia}{%s}\n%s\n\\end{filologia}' % (titulo, filas)
    return '\\begin{filologiatexto}{%s}\n%s\n\\end{filologiatexto}' % (titulo, cont)
body = re.sub(r'\\begin\{filologia\}\[(.*?)\](.*?)\\end\{filologia\}', filo, body, flags=re.S)

# Glosario como sección final del capítulo
body = body.replace('\\section*{Glosario}', '\\section*{Glosario del capítulo}')

assert '\\begin{cita}' not in body and '\\begin{nota}' not in body, 'quedan entornos sin convertir'
cab = ('%% Capítulo: %s (generado desde %s)\n%% %s\n\n' % (titulo, src, nota))
open(dst, 'w', encoding='utf-8').write(cab + body)
print('ok', len(body))
