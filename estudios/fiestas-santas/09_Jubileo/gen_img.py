# Paneles de manuscrito y portada del estudio «El Jubileo» (serie Festividades santas).
# Usa gen_lib.py (papiro.jpg ya generado). Ejecutar desde esta carpeta: python3 gen_img.py
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 25:10 (BHS, texto consonántico)
panel_hebreo(['וקדשתם את', 'שנת החמשים', 'שנה וקראתם', 'דרור בארץ', 'לכל ישביה',
              'יובל הוא', 'תהיה לכם'], 'panel_levitico25.jpg', tam=78)

# Is 61:1 (BHS, texto consonántico)
panel_hebreo(['רוח אדני', 'יהוה עלי', 'יען משח יהוה', 'אתי לבשר', 'ענוים שלחני',
              'לחבש לנשברי', 'לב לקרא', 'לשבוים דרור'], 'panel_isaias61.jpg', tam=70, paso=124)

# Job 19:25 (BHS, texto consonántico)
panel_hebreo(['ואני ידעתי', 'גאלי חי', 'ואחרון', 'על עפר', 'יקום'], 'panel_job19.jpg', tam=84, paso=170)

# Lc 4:18b (NA28) en uncial: APESTALKEN ME KHRYXAI AIXMALWTOIS AFESIN KAI TYFLOIS ANABLEYIN,
# APOSTEILAI TEQRAYSMENOUS EN AFESEI
panel_griego(['ΑΠΕϹΤΑΛΚΕΝ', 'ΜΕΚΗΡΥΞΑΙ', 'ΑΙΧΜΑΛΩΤΟΙ', 'ϹΑΦΕϹΙΝΚΑΙ', 'ΤΥΦΛΟΙϹΑΝΑ',
              'ΒΛΕΨΙΝΑΠΟ', 'ϹΤΕΙΛΑΙΤΕ', 'ΘΡΑΥϹΜΕΝΟΥ', 'ϹΕΝΑΦΕϹΕΙ'], 'panel_lucas4.jpg', tam=54, paso=112)

# Portada: Lv 25:10b
portada_hebreo(['וקראתם דרור בארץ', 'לכל ישביה'])
print('ok')
