"""Paneles de manuscrito y portada del estudio 07 (Sukkot). Ejecutar desde esta carpeta: python3 gen_img.py"""
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 23:42-43a (BHS, texto consonántico; nótese la grafía defectiva בסכת en el v. 42)
panel_hebreo(['בסכת תשבו', 'שבעת ימים', 'כל האזרח', 'בישראל ישבו', 'בסכת למען', 'ידעו דרתיכם', 'כי בסכות', 'הושבתי'],
             'panel_levitico23.jpg', tam=72, paso=116)

# Dt 16:15b (BHS)
panel_hebreo(['כי יברכך', 'יהוה אלהיך', 'בכל תבואתך', 'ובכל מעשה', 'ידיך', 'והיית', 'אך שמח'],
             'panel_deuteronomio16.jpg', tam=78, paso=140)

# Zac 14:16b (BHS)
panel_hebreo(['ועלו מדי', 'שנה בשנה', 'להשתחות', 'למלך יהוה', 'צבאות', 'ולחג את', 'חג הסכות'],
             'panel_zacarias14.jpg', tam=80, paso=140)

# Jn 7:38 en uncial (NA28), scriptio continua y sin puntuación, como en los papiros
panel_griego(['ΟΠΙϹΤΕΥΩΝ', 'ΕΙϹΕΜΕΚΑΘΩϹ', 'ΕΙΠΕΝΗΓΡΑ', 'ΦΗΠΟΤΑΜΟΙ', 'ΕΚΤΗϹΚΟΙΛΙ', 'ΑϹΑΥΤΟΥΡΕΥ', 'ϹΟΥϹΙΝΥΔΑ', 'ΤΟϹΖΩΝΤΟϹ'],
             'panel_juan7.jpg', tam=54, paso=122)

# Portada: Lv 23:42 (BHS)
portada_hebreo(['בסכת תשבו שבעת ימים', 'כל האזרח בישראל ישבו בסכת'], tam=88, paso=170)
print('ok')
