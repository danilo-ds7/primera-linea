# Paneles de manuscrito y portada del estudio 03_Primicias (texto consonántico BHS y uncial NA28)
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 23:10b (BHS): וּקְצַרְתֶּם אֶת־קְצִירָהּ וַהֲבֵאתֶם אֶת־עֹמֶר רֵאשִׁית קְצִירְכֶם אֶל־הַכֹּהֵן
panel_hebreo(['וקצרתם את', 'קצירה', 'והבאתם את', 'עמר ראשית', 'קצירכם', 'אל הכהן'], 'panel_levitico23_10.jpg')

# Lv 23:11 (BHS): וְהֵנִיף אֶת־הָעֹמֶר לִפְנֵי יְהוָה לִרְצֹנְכֶם מִמָּחֳרַת הַשַּׁבָּת יְנִיפֶנּוּ הַכֹּהֵן
panel_hebreo(['והניף את', 'העמר לפני', 'יהוה', 'לרצנכם', 'ממחרת', 'השבת', 'יניפנו', 'הכהן'],
             'panel_levitico23_11.jpg', tam=74, paso=128)

# Jer 2:3a (BHS, ketiv): קֹדֶשׁ יִשְׂרָאֵל לַיהוָה רֵאשִׁית תְּבוּאָתֹה
panel_hebreo(['קדש ישראל', 'ליהוה', 'ראשית', 'תבואתה', 'כל אכליו', 'יאשמו'], 'panel_jeremias2_3.jpg')

# 1 Co 15:20 (NA28): Νυνὶ δὲ Χριστὸς ἐγήγερται ἐκ νεκρῶν ἀπαρχὴ τῶν κεκοιμημένων
# uncial, scriptio continua, nomen sacrum ΧϹ con línea superior
panel_griego(['ΝΥΝΙΔΕΧϹΕΓΗ', 'ΓΕΡΤΑΙΕΚΝΕ', 'ΚΡΩΝΑΠΑΡΧΗ', 'ΤΩΝΚΕΚΟΙ', 'ΜΗΜΕΝΩΝ'],
             'panel_1corintios15.jpg', barras=((0, 6, 8),))

# Portada: Lv 23:10 (BHS) עֹמֶר רֵאשִׁית קְצִירְכֶם / אֶל־הַכֹּהֵן
portada_hebreo(['והבאתם את עמר ראשית קצירכם', 'אל הכהן'])
print('ok')
