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
# Jn 4:24 en uncial (NA28), nomina sacra ΠΝΑ, ΘϹ, ΠΝΙ
jn = ['ΠΝΑΟΘϹΚΑΙ', 'ΤΟΥϹΠΡΟϹΚΥ', 'ΝΟΥΝΤΑϹΑΥ', 'ΤΟΝΕΝΠΝΙ', 'ΚΑΙΑΛΗΘΕΙΑ', 'ΔΕΙΠΡΟϹΚΥ', 'ΝΕΙΝ']
fundir(manuscrito(840, 1200, jn, 56, 220, 170, 128, GR, rtl=False, anc='ls', tinta=(52, 28, 14),
                  barras=[(0, 0, 3), (0, 4, 6), (3, 5, 8)]), 'panel_juan4.jpg')
# Nm 16:22 (BHS, consonantico)
nm = ['ויפלו', 'על פניהם', 'ויאמרו', 'אל אלהי', 'הרוחת', 'לכל בשר']
fundir(manuscrito(840, 1200, nm, 84, 790, 170, 150, HEB), 'panel_numeros16.jpg')
# Dt 4:12 (BHS, consonantico)
dt = ['קול דברים', 'אתם', 'שמעים', 'ותמונה', 'אינכם', 'ראים', 'זולתי קול']
fundir(manuscrito(840, 1200, dt, 80, 790, 150, 140, HEB), 'panel_deuteronomio4.jpg')
# 2 Co 3:17 en uncial (NA28), nomina sacra ΚϹ, ΠΝΑ, ΚΥ
co = ['ΟΔΕΚϹΤΟΠΝΑ', 'ΕϹΤΙΝΟΥΔΕ', 'ΤΟΠΝΑΚΥ', 'ΕΛΕΥΘΕΡΙΑ']
fundir(manuscrito(840, 1200, co, 58, 220, 260, 150, GR, rtl=False, anc='ls', tinta=(52, 28, 14),
                  barras=[(0, 3, 5), (0, 7, 10), (2, 2, 5), (2, 5, 7)]), 'panel_2corintios3.jpg')
# Portada: Jn 4:24a en uncial
port = manuscrito(1600, 600, ['ΠΝΑΟΘϹ', 'ΚΑΙΤΟΥϹΠΡΟϹΚΥΝΟΥΝΤΑϹ', 'ΑΥΤΟΝΕΝΠΝΙΚΑΙΑΛΗΘΕΙΑ'], 64, 330, 170, 150, GR,
                  rtl=False, anc='ls', tinta=(52, 28, 14), barras=[(0, 0, 3), (0, 4, 6), (2, 7, 10)])
port.save('crops/portada.jpg', quality=88)
print('ok')
