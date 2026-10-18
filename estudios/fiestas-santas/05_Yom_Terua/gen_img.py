# Genera los paneles de manuscrito y la portada de la presentación (texto real BHS / NA28)
from gen_lib import panel_hebreo, panel_griego, portada_hebreo

# Lv 23:24b (BHS, consonántico)
panel_hebreo(['בחדש השביעי', 'באחד לחדש', 'יהיה לכם', 'שבתון', 'זכרון תרועה', 'מקרא קדש'], 'panel_levitico23.jpg', tam=80, paso=150)
# Nm 29:1 (BHS, consonántico)
panel_hebreo(['ובחדש השביעי', 'באחד לחדש', 'מקרא קדש', 'יהיה לכם', 'כל מלאכת', 'עבדה לא', 'תעשו יום', 'תרועה יהיה', 'לכם'], 'panel_numeros29.jpg', tam=66, paso=104)
# Jos 6:5 (BHS, consonántico; qere כשמעכם)
panel_hebreo(['והיה במשך', 'בקרן היובל', 'כשמעכם את', 'קול השופר', 'יריעו כל', 'העם תרועה', 'גדולה ונפלה', 'חומת העיר', 'תחתיה'], 'panel_josue6.jpg', tam=66, paso=104)
# 1 Co 15:52 en uncial (NA28): EN ATOMW EN RIPH OFQALMOU EN TH ESCATH SALPIGGI SALPISEI GAR KAI OI NEKROI EGERQHSONTAI AFQARTOI
gr = 'ΕΝΑΤΟΜΩΕΝΡΙΠΗΟΦΘΑΛΜΟΥΕΝΤΗΕϹΧΑΤΗϹΑΛΠΙΓΓΙϹΑΛΠΙϹΕΙΓΑΡΚΑΙΟΙΝΕΚΡΟΙΕΓΕΡΘΗϹΟΝΤΑΙΑΦΘΑΡΤΟΙ'
lineas = [gr[i:i + 11] for i in range(0, len(gr), 11)]
panel_griego(lineas, 'panel_1corintios15.jpg', tam=52, paso=112)
# Portada: Lv 23:24 (zijrón teruá mikrá kódesh) y Nm 29:1 (yom teruá yihyé lajem)
portada_hebreo(['זכרון תרועה מקרא קדש', 'יום תרועה יהיה לכם'])
print('ok', len(lineas))
