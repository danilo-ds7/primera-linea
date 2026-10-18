from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 25:4 (BHS, consonántico)
panel_hebreo(['ובשנה', 'השביעת', 'שבת שבתון', 'יהיה לארץ', 'שבת ליהוה', 'שדך לא תזרע', 'וכרמך לא', 'תזמר'],
             'panel_levitico25.jpg', tam=72, paso=122)
# Dt 15:1-2a (BHS, consonántico)
panel_hebreo(['מקץ שבע', 'שנים תעשה', 'שמטה', 'וזה דבר', 'השמטה שמוט', 'כל בעל משה', 'ידו'],
             'panel_deuteronomio15.jpg', tam=76, paso=140)
# Jer 34:17b (BHS, consonántico)
panel_hebreo(['הנני קרא', 'לכם דרור', 'נאם יהוה', 'אל החרב', 'אל הדבר', 'ואל הרעב'],
             'panel_jeremias34.jpg', tam=80, paso=150)
# Mt 6:12 (NA28) en uncial, scriptio continua
panel_griego(['ΚΑΙΑΦΕϹΗΜΙ', 'ΝΤΑΟΦΕΙΛΗ', 'ΜΑΤΑΗΜΩΝ', 'ΩϹΚΑΙΗΜΕΙϹ', 'ΑΦΗΚΑΜΕΝ', 'ΤΟΙϹΟΦΕΙΛΕ', 'ΤΑΙϹΗΜΩΝ'],
             'panel_mateo6.jpg')
# Portada: Lv 25:4a
portada_hebreo(['ובשנה השביעת שבת שבתון', 'יהיה לארץ שבת ליהוה'], tam=88, paso=170)
print('ok')
