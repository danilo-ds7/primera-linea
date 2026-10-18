# Genera las imágenes de la presentación «Yom haKipurim» (crops/) con gen_lib.py.
# Texto hebreo consonántico según la BHS (Westminster Leningrad Codex); griego según NA28.
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 16:30 — כי ביום הזה יכפר עליכם לטהר אתכם מכל חטאתיכם לפני יהוה תטהרו
panel_hebreo(['כי ביום הזה', 'יכפר עליכם', 'לטהר אתכם', 'מכל', 'חטאתיכם', 'לפני יהוה', 'תטהרו'],
             'panel_lv16_30.jpg')

# Lv 16:8 — ונתן אהרן על שני השעירם גורלות גורל אחד ליהוה וגורל אחד לעזאזל
panel_hebreo(['ונתן אהרן', 'על שני', 'השעירם', 'גורלות', 'גורל אחד', 'ליהוה', 'וגורל אחד', 'לעזאזל'],
             'panel_lv16_8.jpg', tam=76, paso=128)

# Lv 16:21 (parte) — והתודה עליו את כל עונת בני ישראל ואת כל פשעיהם לכל חטאתם
panel_hebreo(['והתודה עליו', 'את כל עונת', 'בני ישראל', 'ואת כל', 'פשעיהם', 'לכל', 'חטאתם'],
             'panel_lv16_21.jpg')

# He 9:28b — ἐκ δευτέρου χωρὶς ἁμαρτίας ὀφθήσεται τοῖς αὐτὸν ἀπεκδεχομένοις εἰς σωτηρίαν
panel_griego(['ΕΚΔΕΥΤΕΡΟΥ', 'ΧΩΡΙϹΑΜΑΡ', 'ΤΙΑϹΟΦΘΗϹΕ', 'ΤΑΙΤΟΙϹΑΥ', 'ΤΟΝΑΠΕΚΔΕ', 'ΧΟΜΕΝΟΙϹΕΙϹ', 'ϹΩΤΗΡΙΑΝ'],
             'panel_he9_28.jpg')

# Portada: Lv 16:30a
portada_hebreo(['כי ביום הזה יכפר עליכם', 'לטהר אתכם מכל חטאתיכם'])
print('ok')
