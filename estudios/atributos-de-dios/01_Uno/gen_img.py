"""Imágenes de 01_Uno: paneles de manuscrito y portada.
Ejecutar desde la carpeta 01_Uno:  python3 gen_img.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

rng = np.random.default_rng(1)

def ruido(h, w, escala):
    s = rng.random((max(2, h // escala), max(2, w // escala)))
    return np.array(Image.fromarray((s * 255).astype('uint8')).resize((w, h), Image.BICUBIC)) / 255.0

def papiro(w, h, claro=(244, 236, 214), oscuro=(205, 186, 146), quemado=(150, 118, 70)):
    base = np.zeros((h, w)); y = 0
    while y < h:
        alto = rng.integers(38, 72); base[y:y + alto, :] += rng.normal(0, 0.10); y += alto
    x = 0
    while x < w:
        ancho = rng.integers(60, 140); base[:, x:x + ancho] += rng.normal(0, 0.04); x += ancho
    fibras = np.array(Image.fromarray((rng.random((h // 2, w // 40)) * 255).astype('uint8')).resize((w, h), Image.BILINEAR)) / 255.0
    base += (fibras - 0.5) * 0.25 + (ruido(h, w, 180) - 0.5) * 0.45
    base = (base - base.min()) / (base.max() - base.min())
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vin = np.clip((d - 0.75) / 0.6, 0, 1) ** 1.6
    c1, c2, c3 = (np.array(c, float) for c in (claro, oscuro, quemado))
    img = c1 * (1 - base[..., None] * 0.45) + c2 * (base[..., None] * 0.45)
    img = img * (1 - vin[..., None] * 0.65) + c3 * (vin[..., None] * 0.65)
    return Image.fromarray(np.clip(img, 0, 255).astype('uint8'))

def entintar(pap, capa, tinta=(30, 30, 52)):
    w, h = pap.size
    er = (ruido(h, w, 3) > 0.18).astype('uint8') * 255
    capa = Image.fromarray((np.array(capa) * (er / 255)).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))
    pap.paste(Image.new('RGB', (w, h), tinta), (0, 0), capa)
    return pap

def linea_heb(dr, x_der, y, segmentos, fuente, tam):
    """Escribe de derecha a izquierda; cada segmento es (texto, factor de tamaño).
    Las letras grandes (factor > 1) comparten la línea base con las demás."""
    x = x_der
    for texto, f in segmentos:
        fnt = ImageFont.truetype(fuente, int(tam * f))
        ancho = dr.textlength(texto, font=fnt, direction='rtl', language='he')
        dr.text((x, y), texto, font=fnt, fill=255, direction='rtl', language='he', anchor='rs')
        x -= ancho

def manuscrito(w, h, lineas, tam, x_anchor, y0, paso, fuente, rtl=True, anc='ra', tinta=(30, 30, 52), barras=()):
    pap = papiro(w, h, claro=(234, 220, 186), oscuro=(196, 168, 120), quemado=(120, 84, 44))
    capa = Image.new('L', (w, h), 0); dr = ImageDraw.Draw(capa)
    f = ImageFont.truetype(fuente, tam)
    for i, l in enumerate(lineas):
        if isinstance(l, list):           # línea con letras de distinto tamaño
            linea_heb(dr, x_anchor, y0 + i * paso + int(tam * 1.02), l, fuente, tam)
        elif rtl:
            dr.text((x_anchor, y0 + i * paso), l, font=f, fill=255, direction='rtl', language='he', anchor=anc)
        else:
            dr.text((x_anchor, y0 + i * paso), l, font=f, fill=255, anchor=anc)
    for (i, a, b) in barras:  # línea superior de nomen sacrum: línea i, caracteres a..b
        l = lineas[i]
        x1 = x_anchor + dr.textlength(l[:a], font=f); x2 = x_anchor + dr.textlength(l[:b], font=f)
        yb = y0 + i * paso - int(tam * 0.92)
        dr.line((x1, yb, x2, yb), fill=255, width=5)
    return entintar(pap, capa, tinta)

fondo = Image.open('papiro.jpg')
x0 = int((396 - 178.6) / 453.54 * 1920); x1 = int(396 / 453.54 * 1920)
detras = fondo.crop((x0, 0, x1, 1080)).resize((840, 1200))
t = np.clip(np.arange(840) / (0.45 * 840), 0, 1)
alfa = np.zeros((1200, 840)); alfa[:] = t * t * (3 - 2 * t)
def fundir(p, nombre):
    m = np.array(p, float) * alfa[..., None] + np.array(detras, float) * (1 - alfa[..., None])
    Image.fromarray(m.astype('uint8')).save('crops/' + nombre, quality=88)

HEB = 'fonts/NotoHebrewSerif-700.ttf'
GR = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
G = 1.55  # tamaño de las letras grandes del texto masorético (ayin de shema y dalet de ejad)

# Dt 6:4 (BHS, consonántico), con la ayin y la dalet grandes: שמע ישראל יהוה אלהינו יהוה אחד
dt = [[('שמ', 1), ('ע', G)], 'ישראל', 'יהוה', 'אלהינו', 'יהוה', [('אח', 1), ('ד', G)]]
fundir(manuscrito(840, 1200, dt, 92, 790, 150, 165, HEB), 'panel_deuteronomio6.jpg')
# Zac 14:9 (BHS): ביום ההוא יהיה יהוה אחד ושמו אחד
za = ['ביום ההוא', 'יהיה', 'יהוה', 'אחד', 'ושמו', 'אחד']
fundir(manuscrito(840, 1200, za, 92, 790, 170, 165, HEB), 'panel_zacarias14.jpg')
# 1 R 18:39 (BHS): יהוה הוא האלהים יהוה הוא האלהים
re_ = ['ויפלו', 'על פניהם', 'ויאמרו', 'יהוה הוא', 'האלהים', 'יהוה הוא', 'האלהים']
fundir(manuscrito(840, 1200, re_, 82, 790, 150, 150, HEB), 'panel_1reyes18.jpg')
# 1 Co 8:6 en uncial (NA28), con nomina sacra: ΑΛΛ ΗΜΙΝ ΕΙϹ ΘϹ Ο ΠΑΤΗΡ ... ΚΑΙ ΕΙϹ ΚϹ ΙϹ ΧϹ
co = ['ΑΛΛΗΜΙΝΕΙϹ', 'ΘϹΟΠΑΤΗΡ', 'ΕΞΟΥΤΑΠΑΝ', 'ΤΑΚΑΙΗΜΕΙϹ', 'ΕΙϹΑΥΤΟΝ', 'ΚΑΙΕΙϹΚϹ', 'ΙϹΧϹΔΙΟΥ', 'ΤΑΠΑΝΤΑ']
fundir(manuscrito(840, 1200, co, 56, 200, 150, 124, GR, rtl=False, anc='ls', tinta=(40, 30, 50),
                  barras=[(1, 0, 2), (5, 6, 8), (6, 0, 4)]), 'panel_1corintios8.jpg')
# Portada: Dt 6:4 en una línea, con las letras grandes
port = papiro(1600, 600, claro=(234, 220, 186), oscuro=(196, 168, 120), quemado=(120, 84, 44))
capa = Image.new('L', (1600, 600), 0); dr = ImageDraw.Draw(capa)
seg = [('שמ', 1), ('ע', G), (' ישראל יהוה אלהינו יהוה ', 1), ('אח', 1), ('ד', G)]
ancho = sum(dr.textlength(s, font=ImageFont.truetype(HEB, int(96 * f)), direction='rtl', language='he') for s, f in seg)
linea_heb(dr, 800 + ancho / 2, 360, seg, HEB, 96)
entintar(port, capa).save('crops/portada.jpg', quality=88)
print('ok')
