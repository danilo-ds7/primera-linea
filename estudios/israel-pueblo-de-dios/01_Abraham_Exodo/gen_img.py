import numpy as np, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W = sys.argv[1]  # work dir
rng = np.random.default_rng(7)
light = np.array([236,214,165.]); dark = np.array([176,122,64.]); burn = np.array([105,48,20.])

def lowfreq(h, w, scale, seed):
    r = np.random.default_rng(seed)
    small = r.random((max(2,h//scale), max(2,w//scale)))
    return np.array(Image.fromarray((small*255).astype(np.uint8)).resize((w,h), Image.BICUBIC))/255.

def papiro(w, h, seed=1, vig=1.0):
    r = np.random.default_rng(seed)
    t = np.zeros((h,w))
    y = 0
    while y < h:
        s = r.integers(38,73); t[y:y+s,:] += r.uniform(-0.08,0.08); y += s
    x = 0
    while x < w:
        s = r.integers(30,80); t[:,x:x+s] += r.uniform(-0.03,0.03); x += s
    fib = r.random((h, w//12+1)); fib = np.array(Image.fromarray((fib*255).astype(np.uint8)).resize((w,h), Image.BILINEAR))/255.
    t += (fib-0.5)*0.10
    t += (lowfreq(h,w,160,seed+1)-0.5)*0.22
    t += (lowfreq(h,w,40,seed+2)-0.5)*0.08
    base = 0.25 + t
    img = light[None,None,:]*(1-base[...,None]) + dark[None,None,:]*base[...,None]
    yy, xx = np.mgrid[0:h,0:w]
    d = np.sqrt(((xx-w/2)/(w/2))**2 + ((yy-h/2)/(h/2))**2)
    v = vig*np.clip((d-0.72)/0.5,0,1)**1.6 * (0.75+0.25*lowfreq(h,w,60,seed+3))
    img = img*(1-v[...,None]) + burn[None,None,:]*v[...,None]
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8))

def piedra(w, h, seed=21):
    r = np.random.default_rng(seed)
    lt = np.array([241,231,206.]); dk = np.array([212,192,152.]); jn = np.array([170,146,108.])
    t = (lowfreq(h,w,180,seed)-0.5)*0.35 + (lowfreq(h,w,25,seed+1)-0.5)*0.25 + (r.random((h,w))-0.5)*0.18
    bh, bw = 216, 384
    J = np.zeros((h,w))
    for row in range(h//bh+1):
        y0 = row*bh; off = (row%2)*bw//2
        for col in range(-1, w//bw+2):
            x0 = col*bw - off
            ys, ye, xs, xe = max(0,y0), min(h,y0+bh), max(0,x0), min(w,x0+bw)
            if ys>=ye or xs>=xe: continue
            t[ys:ye, xs:xe] += r.uniform(-0.12,0.12)
            # drafted margin (Herodian style): slightly lighter band inside edges
            m = 14
            t[ys:ye, xs:xe][m:-m or None, m:-m or None] += 0.06
            J[ys:min(h,ys+4), xs:xe] = 1; J[ys:ye, xs:min(w,xs+4)] = 1
    t = 0.35 + t
    img = lt[None,None,:]*(1-t[...,None]) + dk[None,None,:]*t[...,None]
    Jb = np.array(Image.fromarray((J*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)))/255.*0.55
    img = img*(1-Jb[...,None]) + jn[None,None,:]*Jb[...,None]
    pits = r.random((h,w)) < 0.004
    img[pits] = img[pits]*0.85
    yy, xx = np.mgrid[0:h,0:w]
    d = np.sqrt(((xx-w/2)/(w/2))**2 + ((yy-h/2)/(h/2))**2)
    v = np.clip((d-0.85)/0.6,0,1)**1.8*0.6
    img = img*(1-v[...,None]) + np.array([120,92,60.])[None,None,:]*v[...,None]
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8))
bg = piedra(1920,1080); bg.save(f'{W}/piedra.jpg', quality=88)

HEBB = f'{W}/fonts/NotoHebrewSerif-700.ttf'
GRK = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
INK = (52,28,14)

def erode(im):
    a = np.array(im).astype(float)
    n = lowfreq(a.shape[0], a.shape[1], 6, 11)
    mask = (n < 0.07)
    a[mask] = a[mask]*0.5 + np.array([200,170,120])*0.5
    return Image.fromarray(a.astype(np.uint8))

def panel_heb(lines, name, size=60, seed=5):
    im = papiro(840,1200,seed,vig=0.3); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(HEBB, size)
    y = 120
    for ln in lines:
        d.text((800,y), ln, font=f, fill=INK, direction='rtl', language='he', anchor='ra'); y += int(size*1.55)
    return erode(im.filter(ImageFilter.GaussianBlur(0.6)))

def panel_grc(lines, name, size=46, seed=6, ov=()):
    im = papiro(840,1200,seed,vig=0.3); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(GRK, size)
    y = 110
    for ln in lines:
        d.text((380,y), ln, font=f, fill=INK)
        # nomina sacra overline
        for ns in ('ΘϹ',):
            i = ln.find(ns)
            if i >= 0:
                x0 = 380 + d.textlength(ln[:i], font=f); x1 = x0 + d.textlength(ns, font=f)
                d.line((x0, y-6, x1, y-6), fill=INK, width=3)
        y += int(size*1.7)
    return erode(im.filter(ImageFilter.GaussianBlur(0.6)))

def fade(panel, name):
    # composite onto the piece of papiro.jpg behind it (right side), smoothstep alpha
    x0 = int((396-178.6)/453.54*1920); x1 = int(396/453.54*1920)
    behind = bg.crop((x0,0,x1,1080)).resize(panel.size)
    w = panel.size[0]
    a = np.clip(np.arange(w)/(0.45*w),0,1); a = a*a*(3-2*a)
    A = np.tile(a,(panel.size[1],1))[...,None]
    out = np.array(behind)*(1-A) + np.array(panel)*A
    Image.fromarray(out.astype(np.uint8)).save(f'{W}/crops/{name}', quality=86)

# Gn 12:2-3 consonantal (BHS)
gn12 = ['ואעשך לגוי גדול','ואברכך ואגדלה','שמך והיה ברכה','ואברכה מברכיך','ומקללך אאר','ונברכו בך כל','משפחת האדמה']
fade(panel_heb(gn12,'gn12'), 'panel_gn12.jpg')
# Is 51:2
is51 = ['הביטו אל אברהם','אביכם ואל שרה','תחוללכם כי אחד','קראתיו','ואברכהו וארבהו']
fade(panel_heb(is51,'is51',seed=8), 'panel_is51.jpg')
# Ex 4:22 + 19:6
ex = ['כה אמר יהוה','בני בכרי ישראל','ואתם תהיו לי','ממלכת כהנים','וגוי קדוש']
fade(panel_heb(ex,'ex',seed=9), 'panel_ex.jpg')
# Gal 3:8 uncial, scriptio continua, 11 chars/line
txt = 'ΠΡΟΙΔΟΥϹΑΔΕΗΓΡΑΦΗΟΤΙΕΚΠΙϹΤΕΩϹΔΙΚΑΙΟΙΤΑΕΘΝΗΟΘϹΠΡΟΕΥΗΓΓΕΛΙϹΑΤΟΤΩΑΒΡΑΑΜΟΤΙΕΝΕΥΛΟΓΗΘΗϹΟΝΤΑΙΕΝϹΟΙΠΑΝΤΑΤΑΕΘΝΗ'
txt = txt.replace('ΟΘΣ','ΟΘΣ')
lines=[]; i=0
while i < len(txt):
    n = 11
    if txt[i:i+n].endswith('Θ'): n = 10
    lines.append(txt[i:i+n]); i += n
fade(panel_grc(lines,'gal38'), 'panel_gal38.jpg')

# Portada: Gn 15:5 consonantal + starfield
im = papiro(1600,600,12,vig=0.45); d = ImageDraw.Draw(im)
r = np.random.default_rng(3)
for _ in range(140):
    x, y = r.integers(30,1570), r.integers(20,250); s = r.choice([1,1,2,2,3])
    d.ellipse((x-s,y-s,x+s,y+s), fill=(120,70,30))
f = ImageFont.truetype(HEBB, 74)
d.text((800,300), 'הבט נא השמימה וספר הכוכבים', font=f, fill=INK, direction='rtl', language='he', anchor='ma')
d.text((800,420), 'אם תוכל לספר אתם', font=f, fill=INK, direction='rtl', language='he', anchor='ma')
erode(im.filter(ImageFilter.GaussianBlur(0.6))).save(f'{W}/crops/portada.jpg', quality=86)
print('ok')
