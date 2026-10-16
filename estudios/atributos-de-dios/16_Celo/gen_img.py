import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
rng = np.random.default_rng(17)

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

def manuscrito(w, h, lineas, tam, x_anchor, y0, paso, fuente, rtl=True, anc='ra', tinta=(30, 30, 52), barras=()):
    pap = papiro(w, h, claro=(234, 220, 186), oscuro=(196, 168, 120), quemado=(120, 84, 44))
    capa = Image.new('L', (w, h), 0); dr = ImageDraw.Draw(capa)
    f = ImageFont.truetype(fuente, tam)
    for i, l in enumerate(lineas):
        if rtl:
            dr.text((x_anchor, y0 + i * paso), l, font=f, fill=255, direction='rtl', language='he', anchor=anc)
        else:
            dr.text((x_anchor, y0 + i * paso), l, font=f, fill=255, anchor=anc)
    for (i, a, b) in barras:  # linea superior de nomina sacra: linea i, caracteres a..b
        l = lineas[i]
        x1 = x_anchor + dr.textlength(l[:a], font=f); x2 = x_anchor + dr.textlength(l[:b], font=f)
        yb = y0 + i * paso - int(tam * 0.92)
        dr.line((x1, yb, x2, yb), fill=255, width=5)
    er = (ruido(h, w, 3) > 0.18).astype('uint8') * 255
    capa = Image.fromarray((np.array(capa) * (er / 255)).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))
    pap.paste(Image.new('RGB', (w, h), tinta), (0, 0), capa)
    return pap

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
# Ex 34:14 (BHS, consonantico)
ex = ['כי לא', 'תשתחוה', 'לאל אחר', 'כי יהוה', 'קנא שמו', 'אל קנא', 'הוא']
fundir(manuscrito(840, 1200, ex, 84, 790, 150, 140, HEB), 'panel_exodo34.jpg')
# Is 9:6 [9:5 TM] final: la mem cerrada de lemarbeh (ketiv)
isa = ['לםרבה', 'המשרה', 'ולשלום', 'אין קץ', 'קנאת', 'יהוה צבאות', 'תעשה זאת']
fundir(manuscrito(840, 1200, isa, 80, 790, 150, 140, HEB), 'panel_isaias9.jpg')
# Nm 25:11
nm = ['פינחס', 'בן אלעזר', 'השיב', 'את חמתי', 'בקנאו', 'את קנאתי', 'בתוכם']
fundir(manuscrito(840, 1200, nm, 80, 790, 150, 140, HEB), 'panel_numeros25.jpg')
# 2 Co 11:2 en uncial (NA28), nomina sacra ΘΥ y ΧΩ
gr = ['ΖΗΛΩΓΑΡΥΜΑϹ', 'ΘΥΖΗΛΩΗΡΜΟ', 'ϹΑΜΗΝΓΑΡΥ', 'ΜΑϹΕΝΙΑΝΔΡΙ', 'ΠΑΡΘΕΝΟΝΑΓ', 'ΝΗΝΠΑΡΑϹΤΗ', 'ϹΑΙΤΩΧΩ']
fundir(manuscrito(840, 1200, gr, 54, 220, 170, 128, GR, rtl=False, anc='ls', tinta=(52, 28, 14),
                  barras=[(1, 0, 2), (6, 5, 7)]), 'panel_2corintios11.jpg')
# Portada: Ex 34:14b
port = manuscrito(1600, 600, ['כי יהוה קנא שמו', 'אל קנא הוא'], 96, 800, 160, 180, HEB, anc='ma')
port.save('crops/portada.jpg', quality=88)
print('ok')
