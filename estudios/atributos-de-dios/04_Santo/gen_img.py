import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
rng = np.random.default_rng(7)

def ruido(h, w, escala):
    s = rng.random((max(2, h // escala), max(2, w // escala)))
    return np.array(Image.fromarray((s * 255).astype('uint8')).resize((w, h), Image.BICUBIC)) / 255.0

def papiro(w, h, claro=(244, 236, 214), oscuro=(205, 186, 146), quemado=(150, 118, 70)):
    base = np.zeros((h, w))
    y = 0
    while y < h:
        alto = rng.integers(38, 72)
        base[y:y + alto, :] += rng.normal(0, 0.10)
        y += alto
    x = 0
    while x < w:
        ancho = rng.integers(60, 140)
        base[:, x:x + ancho] += rng.normal(0, 0.04)
        x += ancho
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

fondo = papiro(1920, 1080)
fondo.save('papiro.jpg', quality=88)

def manuscrito(w, h, lineas, tam, x_anchor, y0, paso, tinta=(30, 30, 52), anc='ra'):
    pap = papiro(w, h, claro=(234, 220, 186), oscuro=(196, 168, 120), quemado=(120, 84, 44))
    capa = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(capa)
    f = ImageFont.truetype('fonts/NotoHebrewSerif-700.ttf', tam)
    for i, l in enumerate(lineas):
        dr.text((x_anchor, y0 + i * paso), l, font=f, fill=255, direction='rtl', language='he', anchor=anc)
    er = (ruido(h, w, 3) > 0.18).astype('uint8') * 255
    capa = Image.fromarray((np.array(capa) * (er / 255)).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))
    tin = Image.new('RGB', (w, h), tinta)
    pap.paste(tin, (0, 0), capa)
    return pap

# Panel lateral: Is 6:3 en texto consonantico (BHS), ~12 caracteres por linea
panel_txt = ['קדוש קדוש', 'קדוש יהוה', 'צבאות מלא', 'כל הארץ', 'כבודו',
             '', 'אין קדוש', 'כיהוה כי', 'אין בלתך']
panel = manuscrito(840, 1200, panel_txt, 74, 790, 90, 112)
# fundido con el papiro de la lamina
x0 = int((396 - 178.6) / 453.54 * 1920); x1 = int(396 / 453.54 * 1920)
detras = fondo.crop((x0, 0, x1, 1080)).resize((840, 1200))
alfa = np.zeros((1200, 840))
t = np.clip(np.arange(840) / (0.45 * 840), 0, 1)
alfa[:] = t * t * (3 - 2 * t)
mezcla = (np.array(panel, float) * alfa[..., None] + np.array(detras, float) * (1 - alfa[..., None]))
Image.fromarray(mezcla.astype('uint8')).save('crops/panel_isaias6.jpg', quality=88)

# Panel Exodo 3:5
ex_txt = ['של נעליך', 'מעל רגליך', 'כי המקום', 'אשר אתה', 'עומד עליו', 'אדמת קדש', 'הוא']
panel2 = manuscrito(840, 1200, ex_txt, 74, 790, 120, 120)
mezcla2 = (np.array(panel2, float) * alfa[..., None] + np.array(detras, float) * (1 - alfa[..., None]))
Image.fromarray(mezcla2.astype('uint8')).save('crops/panel_exodo3.jpg', quality=88)

# Portada: el trisagio
port = manuscrito(1600, 600, ['קדוש קדוש קדוש יהוה צבאות', 'מלא כל הארץ כבודו'], 92, 800, 150, 170, anc='ma')
Image.fromarray(np.array(port)).save('crops/portada.jpg', quality=88)
print('ok')
