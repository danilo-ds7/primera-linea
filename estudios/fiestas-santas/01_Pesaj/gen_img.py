"""Genera los paneles de manuscrito y la portada de Pésaj en crops/ (usa gen_lib.py y papiro.jpg)."""
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Éx 12:13 (BHS, texto consonántico)
panel_hebreo(['והיה הדם לכם', 'לאת על הבתים', 'אשר אתם שם', 'וראיתי את', 'הדם ופסחתי', 'עלכם ולא', 'יהיה בכם נגף', 'למשחית'],
             'panel_exodo12_13.jpg', tam=76, paso=126)

# Lv 23:5 (BHS)
panel_hebreo(['בחדש הראשון', 'בארבעה עשר', 'לחדש', 'בין הערבים', 'פסח ליהוה'],
             'panel_levitico23_5.jpg', tam=80, paso=150)

# Éx 12:26-27 (BHS)
panel_hebreo(['מה העבדה', 'הזאת לכם', 'ואמרתם', 'זבח פסח', 'הוא ליהוה', 'אשר פסח', 'על בתי', 'בני ישראל'],
             'panel_exodo12_26.jpg', tam=76, paso=126)

# 1 Co 5:7 (NA28) en uncial: EKKAQARATE THN PALAIAN ZUMHN INA HTE NEON FURAMA KAQWS ESTE AZUMOI KAI GAR TO PASXA HMWN ETUQH XS
panel_griego(['ΕΚΚΑΘΑΡΑΤΕ', 'ΤΗΝΠΑΛΑΙΑΝ', 'ΖΥΜΗΝΙΝΑΗ', 'ΤΕΝΕΟΝΦΥΡΑ', 'ΜΑΚΑΘΩϹΕϹ', 'ΤΕΑΖΥΜΟΙ', 'ΚΑΙΓΑΡΤΟ', 'ΠΑϹΧΑΗΜΩΝ', 'ΕΤΥΘΗΧϹ'],
             'panel_1corintios5.jpg', tam=54, paso=108, barras=((8, 5, 7),))

# Portada: Éx 12:13b
portada_hebreo(['וראיתי את הדם', 'ופסחתי עלכם'])
print('ok')
