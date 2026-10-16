"""Imágenes de 12_Sabiduria: paneles de manuscrito, portada y simulación de bandada (murmuración).
Ejecutar desde la carpeta 12_Sabiduria:  python3 gen_img.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.spatial import cKDTree

rng = np.random.default_rng(12)

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
    for (i, a, b) in barras:  # línea superior de nomen sacrum: línea i, caracteres a..b
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

# Pr 8:30 (BHS, consonántico)
pr = ['ואהיה אצלו', 'אמון', 'ואהיה', 'שעשעים', 'יום יום', 'משחקת', 'לפניו', 'בכל עת']
fundir(manuscrito(840, 1200, pr, 78, 790, 120, 132, HEB), 'panel_proverbios8.jpg')
# Gn 50:20 (BHS)
gn = ['ואתם', 'חשבתם עלי', 'רעה', 'אלהים', 'חשבה לטבה', 'להחית', 'עם רב']
fundir(manuscrito(840, 1200, gn, 80, 790, 150, 150, HEB), 'panel_genesis50.jpg')
# Ro 11:33 en uncial (NA28), nomen sacrum ΘΥ
ro = ['ΩΒΑΘΟϹΠΛΟΥ', 'ΤΟΥΚΑΙϹΟΦΙ', 'ΑϹΚΑΙΓΝΩ', 'ϹΕΩϹΘΥΩϹ', 'ΑΝΕΞΕΡΑΥ', 'ΝΗΤΑΤΑΚΡΙ', 'ΜΑΤΑΑΥΤΟΥ']
fundir(manuscrito(840, 1200, ro, 56, 230, 170, 132, GR, rtl=False, anc='ls', tinta=(52, 28, 14), barras=[(3, 4, 6)]), 'panel_romanos11.jpg')
# Col 1:17 en uncial: ΚΑΙ ΑΥΤΟϹ ΕϹΤΙΝ ΠΡΟ ΠΑΝΤΩΝ ΚΑΙ ΤΑ ΠΑΝΤΑ ΕΝ ΑΥΤΩ ϹΥΝΕϹΤΗΚΕΝ
co = ['ΚΑΙΑΥΤΟϹΕϹ', 'ΤΙΝΠΡΟΠΑΝ', 'ΤΩΝΚΑΙΤΑ', 'ΠΑΝΤΑΕΝ', 'ΑΥΤΩϹΥΝΕ', 'ϹΤΗΚΕΝ']
fundir(manuscrito(840, 1200, co, 58, 230, 200, 140, GR, rtl=False, anc='ls', tinta=(52, 28, 14)), 'panel_colosenses1.jpg')
# Portada: Pr 3:19
port = manuscrito(1600, 600, ['יהוה בחכמה יסד ארץ', 'כונן שמים בתבונה'], 92, 800, 150, 170, HEB, anc='ma')
port.save('crops/portada.jpg', quality=88)

# ---------------- Bandada: modelo de Reynolds (1987) con 7 vecinos topológicos (Ballerini et al., 2008) -------
def bandada(n=5000, pasos=420, semilla=5):
    r = np.random.default_rng(semilla)
    u = r.random(n) * 2 * np.pi; v = r.normal(0, 1, n)
    pos = np.c_[14 * np.cos(u) * (1 + 0.3 * v), 5 * np.sin(2 * u) + v, 1.2 * r.normal(0, 1, n)]  # lámina curvada
    vel = np.c_[-np.sin(u), np.cos(2 * u), np.zeros(n)] * 0.8 + r.normal(0, 0.05, (n, 3))
    cuadros = []
    for k in range(pasos):
        arbol = cKDTree(pos)
        d, idx = arbol.query(pos, k=8)
        vec = idx[:, 1:]
        sep = ((pos[:, None, :] - pos[vec]) / (d[:, 1:, None] ** 2 + 0.02)).sum(1)
        ali = vel[vec].mean(1) - vel
        coh = pos[vec].mean(1) - pos
        g = pos - pos.mean(0)
        centro = -g * np.array([0.0006, 0.0014, 0.0030])   # el grupo permanece sobre el dormidero
        giro = np.cross(vel, [0.2, 0.3, 1]) * 0.022          # virajes del conjunto
        vel += 0.012 * sep + 0.16 * ali + 0.006 * coh + centro + giro + r.normal(0, 0.006, vel.shape)
        rap = np.linalg.norm(vel, axis=1, keepdims=True)
        vel = vel / rap * np.clip(rap, 0.7, 1.2)
        pos += vel * 0.1
        if k in (pasos - 200, pasos - 100, pasos - 1):
            cuadros.append(pos.copy())
    return cuadros

def cielo(w, h):
    yy = np.linspace(0, 1, h)[:, None]
    arriba = np.array([22, 52, 98], float); medio = np.array([96, 120, 160], float); abajo = np.array([236, 196, 120], float)
    c = np.where(yy < 0.55, arriba + (medio - arriba) * (yy / 0.55), medio + (abajo - medio) * ((yy - 0.55) / 0.45))
    img = np.repeat(c[:, None, :], w, axis=1)[:, :, :] if c.ndim == 2 else c
    img = np.broadcast_to(c[:, None, :] if c.ndim == 2 else c, (h, w, 3)).copy()
    return img

def pintar(p, w=1600, h=900, nombre='bandada.jpg', horizonte=True):
    img = cielo(w, h)
    q = p - p.mean(0)
    ang = 0.35
    x = q[:, 0] * np.cos(ang) - q[:, 1] * np.sin(ang); y = q[:, 2] + 0.35 * q[:, 1]; z = q[:, 0] * np.sin(ang) + q[:, 1] * np.cos(ang)
    esc = 0.62 * min(w / (x.max() - x.min() + 1e-6), h / (y.max() - y.min() + 1e-6))
    px = (w / 2 + x * esc).astype(int); py = (h * 0.42 - y * esc).astype(int)
    tam = np.clip(1.3 + 0.10 * (z - z.min()), 1.0, 2.8)
    capa = Image.new('L', (w, h), 0); dr = ImageDraw.Draw(capa)
    for a, b, s in zip(px, py, tam):
        dr.ellipse((a - s, b - s * 0.7, a + s, b + s * 0.7), fill=235)
    capa = capa.filter(ImageFilter.GaussianBlur(0.5))
    al = np.array(capa, float)[..., None] / 255
    img = img * (1 - al) + np.array([20, 20, 30]) * al
    if horizonte:  # siluetas de colinas
        xs = np.arange(w)
        hor = (h * 0.86 + 18 * np.sin(xs / 140) + 10 * np.sin(xs / 47 + 1)).astype(int)
        for i in range(w):
            img[hor[i]:, i] = [28, 30, 40]
    Image.fromarray(np.clip(img, 0, 255).astype('uint8')).save('crops/' + nombre, quality=90)

cuadros = bandada()
for i, c in enumerate(cuadros, 1):
    pintar(c, nombre=f'bandada_{i}.jpg')
print('ok')
