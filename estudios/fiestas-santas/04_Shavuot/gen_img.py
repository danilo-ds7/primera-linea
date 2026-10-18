"""Imágenes del estudio 04_Shavuot: paneles de manuscrito (texto real BHS / NA28) y portada.
Uso: python3 gen_img.py   (desde esta carpeta; usa gen_lib.py y papiro.jpg)"""
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 23:16 (BHS, consonántico): "hasta el día siguiente del séptimo sábado contaréis cincuenta días..."
panel_hebreo(['עד ממחרת', 'השבת', 'השביעת', 'תספרו חמשים', 'יום והקרבתם', 'מנחה חדשה', 'ליהוה'],
             'panel_levitico23.jpg', tam=74)

# Éx 20:18 (BHS 20:18, consonántico): "y todo el pueblo veía las voces y las antorchas..."
panel_hebreo(['וכל העם', 'ראים את', 'הקולת ואת', 'הלפידם ואת', 'קול השפר', 'ואת ההר', 'עשן'],
             'panel_exodo20.jpg', tam=76)

# Jl 2:23b (BHS, consonántico): "porque os dio el moré para justicia, e hizo descender lluvia, moré y malqosh, en el primero"
panel_hebreo(['כי נתן לכם', 'את המורה', 'לצדקה ויורד', 'לכם גשם', 'מורה ומלקוש', 'בראשון'],
             'panel_joel2.jpg', tam=74, paso=150)

# Hch 2:1 en uncial (NA28): KAI EN TW SUMPLHROUSQAI THN HMERAN THS PENTHKOSTHS HSAN PANTES OMOU EPI TO AUTO
panel_griego(['ΚΑΙΕΝΤΩϹΥΜ', 'ΠΛΗΡΟΥϹΘΑΙ', 'ΤΗΝΗΜΕΡΑΝ', 'ΤΗϹΠΕΝΤΗ', 'ΚΟϹΤΗϹΗϹΑΝ', 'ΠΑΝΤΕϹΟΜΟΥ', 'ΕΠΙΤΟΑΥΤΟ'],
             'panel_hechos2.jpg')

# Portada: Lv 23:16a
portada_hebreo(['עד ממחרת השבת השביעת', 'תספרו חמשים יום'])
print('imágenes ok')
