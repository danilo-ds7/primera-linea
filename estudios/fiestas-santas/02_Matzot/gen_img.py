from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 23:6 (BHS, consonántico)
panel_hebreo(['ובחמשה עשר', 'יום לחדש', 'הזה חג', 'המצות ליהוה', 'שבעת ימים', 'מצות', 'תאכלו'], 'panel_levitico23.jpg')
# Éx 12:39a (BHS, consonántico)
panel_hebreo(['ויאפו את', 'הבצק אשר', 'הוציאו', 'ממצרים עגת', 'מצות כי לא', 'חמץ כי גרשו', 'ממצרים'], 'panel_exodo12.jpg', tam=76)
# Dt 16:3 (BHS, consonántico)
panel_hebreo(['שבעת ימים', 'תאכל עליו', 'מצות לחם', 'עני כי', 'בחפזון', 'יצאת מארץ', 'מצרים'], 'panel_deuteronomio16.jpg')
# 1 Co 5:7b-8a en uncial (NA28): ΚΑΙ ΓΑΡ ΤΟ ΠΑΣΧΑ ΗΜΩΝ ΕΤΥΘΗ ΧΡΙΣΤΟΣ ΩΣΤΕ ΕΟΡΤΑΖΩΜΕΝ ΜΗ ΕΝ ΖΥΜΗ ΠΑΛΑΙΑ ... ΑΛΛ ΕΝ ΑΖΥΜΟΙΣ
panel_griego(['ΚΑΙΓΑΡΤΟΠΑ', 'ϹΧΑΗΜΩΝ', 'ΕΤΥΘΗΧϹ', 'ΩϹΤΕΕΟΡΤΑ', 'ΖΩΜΕΝΜΗΕΝ', 'ΖΥΜΗΠΑΛΑΙΑ', 'ΑΛΛΕΝΑΖΥ', 'ΜΟΙϹ'],
             'panel_1corintios5.jpg', barras=((2, 5, 7),))
# Portada: Lv 23:6b
portada_hebreo(['חג המצות ליהוה', 'שבעת ימים מצות תאכלו'])
print('ok')
