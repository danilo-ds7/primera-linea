"""Paneles de manuscrito y portada del estudio 00 (Introducción: Las solemnidades del SEÑOR).
Texto hebreo consonántico según el Códice de Leningrado (BHS/WLC); griego en uncial según NA28."""
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 23:2  דבר אל בני ישראל ואמרת אלהם מועדי יהוה אשר תקראו אתם מקראי קדש אלה הם מועדי
panel_hebreo(['דבר אל בני', 'ישראל ואמרת', 'אלהם מועדי', 'יהוה אשר', 'תקראו אתם',
              'מקראי קדש', 'אלה הם מועדי'], 'panel_levitico23_2.jpg', tam=78, paso=140)

# Lv 23:3  ששת ימים תעשה מלאכה וביום השביעי שבת שבתון מקרא קדש כל מלאכה לא תעשו
panel_hebreo(['ששת ימים', 'תעשה מלאכה', 'וביום השביעי', 'שבת שבתון', 'מקרא קדש',
              'כל מלאכה', 'לא תעשו'], 'panel_levitico23_3.jpg', tam=76, paso=140)

# Gn 2:3  ויברך אלהים את יום השביעי ויקדש אתו כי בו שבת מכל מלאכתו אשר ברא אלהים לעשות
panel_hebreo(['ויברך אלהים', 'את יום', 'השביעי', 'ויקדש אתו', 'כי בו שבת',
              'מכל מלאכתו', 'אשר ברא', 'אלהים לעשות'], 'panel_genesis2_3.jpg', tam=74, paso=128)

# He 4:9  ἄρα ἀπολείπεται σαββατισμὸς τῷ λαῷ τοῦ θεοῦ  (nomen sacrum ΘΥ)
panel_griego(['ΑΡΑΑΠΟΛΕΙ', 'ΠΕΤΑΙϹΑΒ', 'ΒΑΤΙϹΜΟϹ', 'ΤΩΛΑΩΤΟΥ', 'ΘΥ'],
             'panel_hebreos4_9.jpg', tam=60, paso=150, barras=((4, 0, 2),))

# Portada: Lv 23:2  מועדי יהוה אשר תקראו אתם מקראי קדש
portada_hebreo(['מועדי יהוה אשר תקראו אתם', 'מקראי קדש'])
print('ok')
