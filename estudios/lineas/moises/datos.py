"""Datos de la línea de tiempo «Moisés, el siervo de YHWH».

Fuente única: de aquí salen estudios/lineas/moises.html (scripts/lineas_generar.py moises) y
estudios/lineas/moises/mapa/atlas.json. Cronología bíblica «temprana» (1 R 6:1; Éxodo c. 1446 a. e. c.).
Los textos bíblicos son traducción propia desde el hebreo (Códice de Leningrado, base de la BHS) y el
griego (SBLGNT); el texto original se lee de los archivos de la app (textos.py), no se transcribe a mano.
"""
import json, sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import textos as T
from atlas_datos import ATLAS
try:
    from voces import COM
except ImportError:
    COM = {}

# ---------------------------------------------------------------------------------------------
# Pasajes bíblicos: clave → (cita, era, traducción propia). El original se toma de textos.py.
# ---------------------------------------------------------------------------------------------
P = {
 "heb11_24": ("Heb 11:23–27", 0, "²³ Por la fe Moisés, al nacer, fue escondido tres meses por sus padres, porque vieron que el niño era hermoso, y no temieron el decreto del rey. ²⁴ Por la fe Moisés, ya grande, rehusó ser llamado hijo de la hija del faraón, ²⁵ prefiriendo ser maltratado con el pueblo de Dios antes que gozar por un tiempo del pecado; ²⁶ consideró mayor riqueza el oprobio de Cristo que los tesoros de Egipto, porque tenía la mirada puesta en la recompensa. ²⁷ Por la fe dejó Egipto sin temer la ira del rey, porque se mantuvo firme como quien ve al Invisible."),
 "1r6_1": ("1 R 6:1", 0, "Y sucedió en el año cuatrocientos ochenta después de la salida de los hijos de Israel de la tierra de Egipto, en el año cuarto del reinado de Salomón sobre Israel, en el mes de Ziv —que es el mes segundo—, que comenzó a edificar la casa de YHWH."),
 "ex12_40": ("Ex 12:40–41", 0, "El tiempo que los hijos de Israel habitaron en Egipto fue de cuatrocientos treinta años. Y al cabo de los cuatrocientos treinta años, en ese mismo día, salieron todos los ejércitos de YHWH de la tierra de Egipto."),
 "jue11_26": ("Jue 11:26", 0, "Mientras Israel habitaba en Hesbón y sus aldeas, en Aroer y sus aldeas y en todas las ciudades que están a la orilla del Arnón, trescientos años, ¿por qué no las recuperaron en ese tiempo?"),
 "ex1_8": ("Ex 1:8–11", 1, "Y se levantó sobre Egipto un rey nuevo, que no había conocido a José. Dijo a su pueblo: «El pueblo de los hijos de Israel es más numeroso y fuerte que nosotros. Vamos, seamos astutos con él, no sea que se multiplique y, si hay guerra, se una a nuestros enemigos, luche contra nosotros y suba de la tierra». Pusieron sobre él jefes de trabajos forzados para oprimirlo con sus cargas, y edificó para el faraón ciudades de almacenes: Pitón y Raamsés."),
 "ex1_13": ("Ex 1:13–14", 1, "Los egipcios hicieron servir a los hijos de Israel con dureza, y les amargaron la vida con dura servidumbre en barro y ladrillos y en toda labor del campo: todo el servicio que les impusieron con dureza."),
 "ex1_15": ("Ex 1:15–17", 1, "El rey de Egipto habló a las parteras de las hebreas —una se llamaba Sifrá y la otra Puá— y les dijo: «Cuando asistan a las hebreas en el parto y las vean sobre las dos piedras, si es niño, mátenlo; si es niña, que viva». Pero las parteras temieron a Dios y no hicieron como les había dicho el rey de Egipto: dejaron vivir a los niños."),
 "ex1_22": ("Ex 1:22", 1, "Entonces el faraón mandó a todo su pueblo: «A todo hijo que nazca, échenlo al Nilo; a toda hija, déjenla vivir»."),
 "ex2_3": ("Ex 2:3", 1, "Y cuando ya no pudo esconderlo más, tomó para él una arquilla (tevá) de papiro, la recubrió de betún y de brea, puso en ella al niño y la puso entre los juncos (suf) a la orilla del Nilo."),
 "ex2_10": ("Ex 2:10", 1, "Cuando el niño creció, ella lo llevó a la hija del faraón, y fue para ella como un hijo. Le puso por nombre Moisés (Moshé), y dijo: «Porque de las aguas lo saqué (meshitihu)»."),
 "ex6_20": ("Ex 6:20", 1, "Amram tomó por mujer a Jocabed, su tía, y ella le dio a luz a Aarón y a Moisés. Los años de la vida de Amram fueron ciento treinta y siete."),
 "nm26_59": ("Nm 26:59", 1, "La mujer de Amram se llamaba Jocabed, hija de Leví, que le nació a Leví en Egipto; y ella dio a luz para Amram a Aarón, a Moisés y a Miriam, su hermana."),
 "ex7_7": ("Ex 7:7", 4, "Moisés tenía ochenta años y Aarón ochenta y tres cuando hablaron al faraón."),
 "hch7_20": ("Hch 7:20–22", 2, "²⁰ En ese tiempo nació Moisés, y era hermoso a los ojos de Dios; fue criado tres meses en la casa de su padre. ²¹ Cuando lo expusieron, la hija del faraón lo recogió y lo crió como hijo suyo. ²² Y Moisés fue instruido en toda la sabiduría de los egipcios, y era poderoso en sus palabras y obras."),
 "ex2_11": ("Ex 2:11–12", 2, "En aquellos días, cuando Moisés ya era grande, salió hacia sus hermanos y vio sus cargas. Vio a un egipcio que golpeaba a un hebreo, uno de sus hermanos. Miró a un lado y a otro, y al ver que no había nadie, mató al egipcio y lo escondió en la arena."),
 "hch7_23": ("Hch 7:23–25", 2, "²³ Cuando cumplía cuarenta años, le vino al corazón visitar a sus hermanos, los hijos de Israel. ²⁴ Al ver que uno era maltratado, lo defendió y vengó al oprimido matando al egipcio. ²⁵ Pensaba que sus hermanos entenderían que Dios les daba la salvación por su mano, pero ellos no lo entendieron."),
 "ex2_15": ("Ex 2:15", 2, "El faraón oyó de este asunto y procuró matar a Moisés. Pero Moisés huyó de la presencia del faraón y se quedó en la tierra de Madián, y se sentó junto al pozo."),
 "ex2_21": ("Ex 2:21–22", 2, "Moisés aceptó quedarse con aquel hombre, y él dio a Moisés a su hija Séfora. Ella dio a luz un hijo, y él le puso por nombre Gersom, porque dijo: «Forastero (ger) he sido en tierra extraña»."),
 "ex2_23": ("Ex 2:23–25", 2, "Pasados muchos días, murió el rey de Egipto. Los hijos de Israel gemían a causa de la servidumbre y clamaron, y su clamor subió a Dios desde la servidumbre. Dios oyó su gemido y se acordó de su pacto con Abraham, con Isaac y con Jacob. Dios miró a los hijos de Israel, y Dios lo supo."),
 "hch7_30": ("Hch 7:29–30", 2, "²⁹ Al oír esta palabra, Moisés huyó y fue forastero en la tierra de Madián, donde engendró dos hijos. ³⁰ Cumplidos cuarenta años, se le apareció en el desierto del monte Sinaí un ángel, en la llama de fuego de una zarza."),
 "ex3_1": ("Ex 3:1–2", 3, "Moisés apacentaba el rebaño de Jetró, su suegro, sacerdote de Madián. Llevó el rebaño más allá del desierto y llegó al monte de Dios, a Horeb. Allí se le apareció el ángel de YHWH en una llama de fuego en medio de una zarza (sené). Miró, y he aquí que la zarza ardía en el fuego, y la zarza no se consumía."),
 "ex3_5": ("Ex 3:5–6", 3, "Y dijo: «No te acerques acá. Quita las sandalias de tus pies, porque el lugar en que estás es tierra santa». Y añadió: «Yo soy el Dios de tu padre, el Dios de Abraham, el Dios de Isaac y el Dios de Jacob». Entonces Moisés cubrió su rostro, porque tuvo miedo de mirar a Dios."),
 "ex3_7": ("Ex 3:7–8", 3, "YHWH dijo: «He visto, he visto la aflicción de mi pueblo que está en Egipto, y he oído su clamor a causa de sus opresores; conozco sus dolores. He descendido para librarlo de la mano de los egipcios y para hacerlo subir de esa tierra a una tierra buena y amplia, a una tierra que mana leche y miel»."),
 "ex3_14": ("Ex 3:13–15", 3, "Moisés dijo a Dios: «Si voy a los hijos de Israel y les digo: “El Dios de sus padres me ha enviado a ustedes”, y me preguntan: “¿Cuál es su nombre?”, ¿qué les responderé?». Y Dios dijo a Moisés: «Ehyé asher ehyé» (Seré el que seré). Y dijo: «Así dirás a los hijos de Israel: “Ehyé me ha enviado a ustedes”». Y dijo además Dios a Moisés: «Así dirás a los hijos de Israel: “YHWH, el Dios de sus padres, el Dios de Abraham, de Isaac y de Jacob, me ha enviado a ustedes”. Este es mi nombre para siempre, y este es mi memorial de generación en generación»."),
 "ex4_10": ("Ex 4:10–12", 3, "Moisés dijo a YHWH: «¡Ay, Señor! Yo no soy hombre de palabras, ni de ayer ni de anteayer, ni desde que hablas a tu siervo, porque soy pesado de boca y pesado de lengua». YHWH le respondió: «¿Quién dio la boca al hombre? ¿Quién hace al mudo o al sordo, al que ve o al ciego? ¿No soy yo, YHWH? Ahora, pues, ve; yo estaré con tu boca y te enseñaré lo que has de decir»."),
 "ex4_27": ("Ex 4:27", 3, "YHWH dijo a Aarón: «Ve al encuentro de Moisés en el desierto». Él fue, lo encontró en el monte de Dios y lo besó."),
 "ex5_1": ("Ex 5:1–2", 4, "Después Moisés y Aarón entraron y dijeron al faraón: «Así dice YHWH, el Dios de Israel: “Deja ir a mi pueblo, para que me celebren fiesta en el desierto”». Pero el faraón respondió: «¿Quién es YHWH para que yo escuche su voz y deje ir a Israel? No conozco a YHWH, y tampoco dejaré ir a Israel»."),
 "ex5_7": ("Ex 5:7", 4, "«No sigan dando paja al pueblo para hacer los ladrillos, como antes; que vayan ellos y recojan la paja por sí mismos»."),
 "ex7_5": ("Ex 7:5", 4, "Y sabrán los egipcios que yo soy YHWH, cuando extienda mi mano sobre Egipto y saque de en medio de ellos a los hijos de Israel."),
 "ex12_12": ("Ex 12:12", 4, "Pasaré por la tierra de Egipto esta noche, heriré a todo primogénito en la tierra de Egipto, desde el hombre hasta la bestia, y ejecutaré juicios contra todos los dioses de Egipto. Yo, YHWH."),
 "ex12_13": ("Ex 12:13", 4, "La sangre les será por señal en las casas donde ustedes estén: veré la sangre y pasaré de largo (pasajti) sobre ustedes, y no habrá entre ustedes plaga destructora cuando yo hiera la tierra de Egipto."),
 "1co5_7": ("1 Co 5:7", 4, "Límpiense de la levadura vieja, para que sean una masa nueva, ya que son panes sin levadura; porque Cristo, nuestra Pascua, ha sido sacrificado."),
 "ex12_37": ("Ex 12:37–38", 5, "Los hijos de Israel partieron de Raamsés hacia Sucot, unos seiscientos mil (shesh meot élef) hombres de a pie, sin contar los niños. Subió también con ellos una multitud mezclada (érev rav), y ovejas y vacas, muchísimo ganado."),
 "ex13_17": ("Ex 13:17–18", 5, "Cuando el faraón dejó ir al pueblo, Dios no los llevó por el camino de la tierra de los filisteos, aunque era el más cercano, porque Dios dijo: «No sea que el pueblo se arrepienta al ver la guerra y se vuelva a Egipto». Dios hizo dar un rodeo al pueblo por el camino del desierto del Yam Suf. Y los hijos de Israel subieron de la tierra de Egipto en orden de batalla."),
 "ex13_21": ("Ex 13:21–22", 5, "YHWH iba delante de ellos: de día en una columna de nube para guiarlos por el camino, y de noche en una columna de fuego para alumbrarlos, a fin de que anduvieran de día y de noche. No se apartaba de delante del pueblo la columna de nube de día ni la columna de fuego de noche."),
 "ex14_2": ("Ex 14:1–2", 5, "YHWH habló a Moisés: «Di a los hijos de Israel que se vuelvan y acampen delante de Pi-hahirot, entre Migdol y el mar, frente a Baal-zefón; frente a él acamparán, junto al mar»."),
 "ex14_13": ("Ex 14:13–14", 5, "Moisés dijo al pueblo: «No teman; estén firmes y vean la salvación de YHWH, que él hará hoy por ustedes; porque a los egipcios que hoy ven, nunca más los volverán a ver. YHWH peleará por ustedes, y ustedes estarán callados»."),
 "ex14_21": ("Ex 14:21–22", 5, "Moisés extendió su mano sobre el mar, y YHWH hizo retroceder el mar con un fuerte viento del este toda la noche; convirtió el mar en tierra seca, y las aguas se dividieron. Los hijos de Israel entraron por en medio del mar en lo seco, y las aguas eran para ellos un muro a su derecha y a su izquierda."),
 "1co10_1": ("1 Co 10:1–2", 5, "No quiero, hermanos, que ignoren que nuestros padres estuvieron todos bajo la nube y todos atravesaron el mar, y todos fueron bautizados en Moisés en la nube y en el mar."),
 "ex15_11": ("Ex 15:11", 5, "¿Quién como tú entre los dioses, YHWH? ¿Quién como tú, magnífico en santidad, temible en alabanzas, hacedor de maravillas?"),
 "ex15_20": ("Ex 15:20–21", 5, "Miriam la profetisa, hermana de Aarón, tomó un pandero en su mano, y todas las mujeres salieron tras ella con panderos y danzas. Y Miriam les respondía: «Canten a YHWH, porque se ha engrandecido gloriosamente: caballo y jinete ha arrojado al mar»."),
 "ex15_25": ("Ex 15:25–26", 6, "Él clamó a YHWH, y YHWH le mostró un árbol; lo echó en las aguas, y las aguas se endulzaron. Allí le dio estatuto y ordenanza, y allí lo probó. Y dijo: «Si escuchas atentamente la voz de YHWH tu Dios… ninguna de las enfermedades que puse sobre Egipto pondré sobre ti, porque yo soy YHWH, tu sanador»."),
 "ex15_27": ("Ex 15:27", 6, "Llegaron a Elim, donde había doce manantiales de agua y setenta palmeras, y acamparon allí junto a las aguas."),
 "ex16_15": ("Ex 16:14–15", 6, "Cuando se evaporó la capa de rocío, sobre la superficie del desierto había una cosa menuda, como escamas, menuda como la escarcha sobre la tierra. Al verla, los hijos de Israel se dijeron unos a otros: «¿Man hu?» (¿Qué es esto?), porque no sabían qué era. Y Moisés les dijo: «Es el pan que YHWH les da para comer»."),
 "jn6_32": ("Jn 6:32–33", 6, "Jesús les dijo: «De cierto, de cierto les digo: no fue Moisés quien les dio el pan del cielo, sino mi Padre les da el verdadero pan del cielo. Porque el pan de Dios es el que desciende del cielo y da vida al mundo»."),
 "ex17_6": ("Ex 17:6–7", 6, "«He aquí que yo estaré delante de ti allí, sobre la peña, en Horeb; golpearás la peña, y saldrán de ella aguas, y beberá el pueblo». Moisés lo hizo así a la vista de los ancianos de Israel. Y llamó el nombre del lugar Masá y Meribá, por la contienda de los hijos de Israel y porque tentaron a YHWH, diciendo: «¿Está YHWH en medio de nosotros, o no?»."),
 "ex17_11": ("Ex 17:11–12", 6, "Mientras Moisés alzaba su mano, Israel prevalecía; pero cuando bajaba su mano, prevalecía Amalec. Las manos de Moisés se cansaban; entonces tomaron una piedra y la pusieron debajo de él, y se sentó sobre ella; Aarón y Hur sostenían sus manos, uno de un lado y otro del otro. Así sus manos estuvieron firmes hasta la puesta del sol."),
 "ex17_15": ("Ex 17:15–16", 6, "Moisés edificó un altar y lo llamó YHWH-nisí (YHWH es mi estandarte), y dijo: «Porque una mano se alzó contra el trono de Yah: guerra tendrá YHWH con Amalec de generación en generación»."),
 "ex18_21": ("Ex 18:21–22", 6, "«Escoge tú de entre todo el pueblo hombres capaces, temerosos de Dios, hombres de verdad que aborrezcan la ganancia injusta, y ponlos sobre ellos como jefes de mil, de cien, de cincuenta y de diez. Ellos juzgarán al pueblo en todo tiempo… Así se aliviará tu carga, y la llevarán contigo»."),
 "ex19_4": ("Ex 19:4–6", 7, "«Ustedes vieron lo que hice a los egipcios, y cómo los llevé sobre alas de águila y los traje a mí. Ahora, pues, si de verdad escuchan mi voz y guardan mi pacto, serán mi tesoro especial (segulá) entre todos los pueblos, porque mía es toda la tierra. Ustedes serán para mí un reino de sacerdotes y una nación santa»."),
 "ex19_18": ("Ex 19:18–19", 7, "Todo el monte Sinaí humeaba, porque YHWH había descendido sobre él en fuego; su humo subía como el humo de un horno, y todo el monte temblaba en gran manera. El sonido del shofar iba aumentando mucho; Moisés hablaba, y Dios le respondía con una voz."),
 "ex20_2": ("Ex 20:2–3", 7, "«Yo soy YHWH tu Dios, que te saqué de la tierra de Egipto, de la casa de servidumbre. No tendrás otros dioses delante de mí»."),
 "ex24_4": ("Ex 24:4", 7, "Moisés escribió todas las palabras de YHWH. Se levantó de mañana y edificó un altar al pie del monte, y doce estelas según las doce tribus de Israel."),
 "ex24_7": ("Ex 24:7–8", 7, "Tomó el libro del pacto y lo leyó a oídos del pueblo, y ellos dijeron: «Todo lo que YHWH ha dicho haremos y obedeceremos (naasé venishmá)». Entonces Moisés tomó la sangre, la roció sobre el pueblo y dijo: «He aquí la sangre del pacto que YHWH ha hecho con ustedes sobre todas estas palabras»."),
 "mt26_28": ("Mt 26:27–28", 7, "Tomó la copa, dio gracias y se la dio, diciendo: «Beban de ella todos, porque esto es mi sangre del pacto, que es derramada por muchos para perdón de los pecados»."),
 "ex25_8": ("Ex 25:8–9", 7, "«Que me hagan un santuario, y habitaré (shajantí) en medio de ellos. Conforme a todo lo que yo te muestre, el modelo (tavnit) del tabernáculo (mishkán) y el modelo de todos sus utensilios, así lo harán»."),
 "ex32_4": ("Ex 32:4", 7, "Él los tomó de sus manos, le dio forma con buril e hizo de ello un becerro de fundición. Y dijeron: «Estos son tus dioses, Israel, que te sacaron de la tierra de Egipto»."),
 "ex32_32": ("Ex 32:31–32", 7, "Moisés volvió a YHWH y dijo: «¡Ay! Este pueblo ha cometido un gran pecado: se han hecho dioses de oro. Ahora, pues, si perdonas su pecado…; y si no, bórrame ahora de tu libro que has escrito»."),
 "ex33_11": ("Ex 33:11", 7, "Y hablaba YHWH a Moisés cara a cara, como habla un hombre con su amigo. Luego él volvía al campamento; pero su ayudante, el joven Josué hijo de Nun, no se apartaba de en medio de la tienda."),
 "ex33_18": ("Ex 33:18–20", 7, "Moisés dijo: «Te ruego que me muestres tu gloria». Y él respondió: «Yo haré pasar toda mi bondad delante de tu rostro y proclamaré el nombre de YHWH delante de ti; tendré misericordia del que tendré misericordia y seré compasivo con quien seré compasivo». Y dijo: «No podrás ver mi rostro, porque no me verá el hombre y vivirá»."),
 "ex34_6": ("Ex 34:6–7", 7, "YHWH pasó delante de él y proclamó: «YHWH, YHWH, Dios compasivo y clemente, lento para la ira y abundante en misericordia (jésed) y verdad; que guarda misericordia por millares, que perdona la iniquidad, la rebelión y el pecado, pero que de ningún modo tendrá por inocente al culpable…»."),
 "ex34_29": ("Ex 34:29", 7, "Al descender Moisés del monte Sinaí con las dos tablas del testimonio en su mano, Moisés no sabía que la piel de su rostro irradiaba (qaran) por haber hablado con él."),
 "2co3_18": ("2 Co 3:18", 7, "Y todos nosotros, mirando a cara descubierta, como en un espejo, la gloria del Señor, somos transformados en la misma imagen, de gloria en gloria, como por el Señor, que es el Espíritu."),
 "ex40_34": ("Ex 40:34–35", 7, "Entonces la nube cubrió la tienda del encuentro, y la gloria de YHWH llenó el tabernáculo. Moisés no podía entrar en la tienda del encuentro, porque la nube reposaba sobre ella y la gloria de YHWH llenaba el tabernáculo."),
 "jn1_14": ("Jn 1:14", 7, "Y el Verbo se hizo carne y habitó (eskēnōsen, «puso su tienda») entre nosotros, y vimos su gloria, gloria como del unigénito del Padre, lleno de gracia y de verdad."),
 "lv16_30": ("Lv 16:30", 7, "Porque en este día se hará expiación por ustedes para purificarlos; de todos sus pecados serán puros delante de YHWH."),
 "lv19_2": ("Lv 19:2", 7, "Habla a toda la congregación de los hijos de Israel y diles: «Sean santos, porque yo, YHWH su Dios, soy santo»."),
 "nm1_46": ("Nm 1:45–46", 7, "Todos los contados de los hijos de Israel según sus casas paternas, de veinte años arriba, todos los que podían salir a la guerra en Israel, fueron seiscientos tres mil quinientos cincuenta."),
 "nm6_24": ("Nm 6:24–26", 9, "YHWH te bendiga y te guarde; YHWH haga resplandecer su rostro sobre ti y tenga de ti misericordia; YHWH alce su rostro sobre ti y ponga en ti paz."),
 "nm10_35": ("Nm 10:35–36", 8, "Cuando el arca partía, Moisés decía: «¡Levántate, YHWH, y sean dispersados tus enemigos, y huyan de tu presencia los que te aborrecen!». Y cuando se detenía, decía: «Vuelve, YHWH, a las miríadas de millares de Israel»."),
 "nm12_3": ("Nm 12:3", 8, "Y aquel hombre, Moisés, era muy humilde (anav), más que todos los hombres que había sobre la faz de la tierra."),
 "nm12_7": ("Nm 12:7–8", 8, "«No así con mi siervo Moisés: en toda mi casa él es fiel. Boca a boca hablo con él, claramente y no en enigmas, y él contempla la figura de YHWH. ¿Por qué, pues, no temieron hablar contra mi siervo, contra Moisés?»."),
 "nm13_27": ("Nm 13:27–28", 8, "Y le contaron: «Fuimos a la tierra a la que nos enviaste; ciertamente mana leche y miel, y este es su fruto. Pero el pueblo que habita la tierra es fuerte, y las ciudades son fortificadas y muy grandes; y también vimos allí a los hijos de Anac»."),
 "nm14_9": ("Nm 14:9", 8, "«Solo que no se rebelen contra YHWH ni teman al pueblo de esta tierra, porque nosotros los comeremos como pan; su amparo se ha apartado de ellos, y YHWH está con nosotros: no los teman»."),
 "nm14_33": ("Nm 14:33–34", 8, "Sus hijos andarán pastoreando en el desierto cuarenta años… Conforme al número de los días en que reconocieron la tierra, cuarenta días, un año por cada día, cargarán con sus iniquidades cuarenta años, y conocerán mi oposición."),
 "nm16_3": ("Nm 16:3", 8, "Se juntaron contra Moisés y contra Aarón y les dijeron: «¡Basta ya de ustedes! Porque toda la congregación, todos ellos, son santos, y YHWH está en medio de ellos. ¿Por qué, pues, se levantan ustedes sobre la asamblea de YHWH?»."),
 "nm17_23": ("Nm 17:23", 8, "Al día siguiente Moisés entró en la tienda del testimonio, y he aquí que la vara de Aarón, de la casa de Leví, había brotado: había echado brotes, producido flores y dado almendras."),
 "nm33_1": ("Nm 33:1–2", 8, "Estas son las jornadas de los hijos de Israel, que salieron de la tierra de Egipto por sus ejércitos, bajo la mano de Moisés y Aarón. Moisés escribió sus salidas, jornada por jornada, por mandato de YHWH."),
 "nm20_11": ("Nm 20:11–12", 8, "Moisés alzó su mano y golpeó la peña con su vara dos veces, y salieron muchas aguas, y bebió la congregación y su ganado. Y YHWH dijo a Moisés y a Aarón: «Por cuanto no creyeron en mí para santificarme a los ojos de los hijos de Israel, por tanto, no introducirán a esta asamblea en la tierra que les he dado»."),
 "nm20_17": ("Nm 20:17", 8, "«Te ruego que nos dejes pasar por tu tierra. No pasaremos por campo ni por viña, ni beberemos agua de pozos; iremos por el Camino del Rey (dérej ha-mélej), sin apartarnos ni a la derecha ni a la izquierda, hasta que hayamos pasado tu territorio»."),
 "nm33_38": ("Nm 33:38–39", 8, "Y el sacerdote Aarón subió al monte Hor por mandato de YHWH, y murió allí, en el año cuarenta de la salida de los hijos de Israel de la tierra de Egipto, en el mes quinto, el primero del mes. Aarón tenía ciento veintitrés años cuando murió en el monte Hor."),
 "nm21_8": ("Nm 21:8–9", 9, "YHWH dijo a Moisés: «Hazte un serafín (saraf) y ponlo sobre un asta; y todo el que haya sido mordido y lo mire, vivirá». Moisés hizo una serpiente de bronce (nejash nejóshet) y la puso sobre un asta; y cuando una serpiente mordía a alguno, miraba a la serpiente de bronce y vivía."),
 "jn3_14": ("Jn 3:14–15", 9, "Y como Moisés levantó la serpiente en el desierto, así es necesario que sea levantado el Hijo del Hombre, para que todo el que cree tenga en él vida eterna."),
 "2r18_4": ("2 R 18:4", 9, "Él quitó los lugares altos, quebró las estelas, cortó la Asherá e hizo pedazos la serpiente de bronce que había hecho Moisés, porque hasta aquellos días los hijos de Israel le quemaban incienso; y la llamaban Nejushtán."),
 "nm21_24": ("Nm 21:24", 9, "E Israel lo hirió a filo de espada y tomó posesión de su tierra desde el Arnón hasta el Jaboc, hasta los hijos de Amón; porque la frontera de los hijos de Amón era fuerte."),
 "nm24_17": ("Nm 24:17", 9, "Lo veo, mas no ahora; lo contemplo, mas no de cerca: una estrella saldrá de Jacob, y un cetro se levantará de Israel, y quebrantará las sienes de Moab y el cráneo de todos los hijos de Set."),
 "dt1_3": ("Dt 1:3–5", 9, "En el año cuarenta, en el mes undécimo, el primero del mes, Moisés habló a los hijos de Israel conforme a todo lo que YHWH le había mandado para ellos… Al otro lado del Jordán, en la tierra de Moab, comenzó Moisés a explicar esta Torá."),
 "dt6_4": ("Dt 6:4–5", 9, "Escucha (Shemá), Israel: YHWH nuestro Dios, YHWH uno es. Y amarás a YHWH tu Dios con todo tu corazón, con toda tu alma y con todas tus fuerzas."),
 "dt30_19": ("Dt 30:19–20", 9, "Pongo hoy por testigos contra ustedes a los cielos y a la tierra: he puesto delante de ti la vida y la muerte, la bendición y la maldición. Escoge, pues, la vida, para que vivas tú y tu descendencia, amando a YHWH tu Dios, escuchando su voz y aferrándote a él, porque él es tu vida."),
 "dt31_7": ("Dt 31:7–8", 9, "Moisés llamó a Josué y le dijo a la vista de todo Israel: «Esfuérzate y sé valiente, porque tú entrarás con este pueblo en la tierra… YHWH es el que va delante de ti; él estará contigo, no te dejará ni te desamparará: no temas ni te acobardes»."),
 "dt34_1": ("Dt 34:1–4", 9, "Subió Moisés de las llanuras de Moab al monte Nebo, a la cumbre del Pisgá, que está frente a Jericó, y YHWH le mostró toda la tierra: Galaad hasta Dan, todo Neftalí, la tierra de Efraín y de Manasés, toda la tierra de Judá hasta el mar occidental, el Neguev y la llanura del valle de Jericó, ciudad de las palmeras, hasta Zoar. Y YHWH le dijo: «Esta es la tierra que juré a Abraham, a Isaac y a Jacob… Te la he hecho ver con tus ojos, pero no pasarás allá»."),
 "dt34_5": ("Dt 34:5–7", 9, "Y murió allí Moisés, siervo de YHWH, en la tierra de Moab, conforme a la palabra (al-pi, «por boca») de YHWH. Y lo sepultó en el valle, en la tierra de Moab, frente a Bet-peor; y nadie conoce su sepultura hasta hoy. Moisés tenía ciento veinte años cuando murió; sus ojos no se habían oscurecido ni había perdido su vigor."),
 "dt34_10": ("Dt 34:10–12", 9, "Y nunca más se levantó en Israel un profeta como Moisés, a quien YHWH conociera cara a cara, en todas las señales y prodigios que YHWH lo envió a hacer en la tierra de Egipto… y en toda la mano poderosa y en todo el gran terror que Moisés hizo a los ojos de todo Israel."),
 "dt18_15": ("Dt 18:15", 9, "Profeta como yo te levantará YHWH tu Dios de en medio de ti, de tus hermanos; a él oirán."),
 "hch3_22": ("Hch 3:22", 9, "Moisés dijo: «El Señor su Dios les levantará un profeta como yo de entre sus hermanos; a él escucharán en todo lo que les diga»."),
 "mt17_3": ("Mt 17:2–3", 9, "Y se transfiguró delante de ellos: su rostro resplandeció como el sol y sus vestidos se volvieron blancos como la luz. Y he aquí que se les aparecieron Moisés y Elías, que conversaban con él."),
 "heb3_5": ("Heb 3:5–6", 9, "⁵ Moisés fue fiel en toda la casa de Dios como siervo, para testimonio de lo que se iba a decir; ⁶ pero Cristo, como Hijo, sobre su casa. Y esa casa somos nosotros, si retenemos firme la confianza y la gloria de la esperanza."),
 "jn1_17": ("Jn 1:17", 9, "Porque la ley fue dada por medio de Moisés; la gracia y la verdad vinieron por medio de Jesucristo."),
 "jud9": ("Jud 9", 9, "Pero el arcángel Miguel, cuando contendía con el diablo disputando sobre el cuerpo de Moisés, no se atrevió a pronunciar juicio de maldición, sino que dijo: «El Señor te reprenda»."),
 "ap15_3": ("Ap 15:3", 9, "Y cantan el cántico de Moisés, siervo de Dios, y el cántico del Cordero, diciendo: «Grandes y maravillosas son tus obras, Señor Dios Todopoderoso; justos y verdaderos son tus caminos, Rey de las naciones»."),
}
GRIEGO = {"Mt", "Mc", "Lc", "Jn", "Hch", "Ro", "1 Co", "2 Co", "Heb", "Jud", "Ap"}

def refs_biblicas():
    R = {}
    for k, (lab, era, tr) in P.items():
        lib = lab.rsplit(" ", 1)[0]
        cita = lab.replace("Nm 17:23", "Nm 17:23")
        if lib in GRIEGO:
            R[k] = {"label": lab, "era": era, "he": T.gr(cita), "tr": tr, "lang": "el"}
        else:
            R[k] = {"label": lab, "era": era, "he": T.he(cita), "tr": tr, "lang": "he"}
    R["nm17_23"]["label"] = "Nm 17:23 (17:8 en las versiones castellanas)"
    return R

# ---------------------------------------------------------------------------------------------
# Fuentes (APA 7) con síntesis
# ---------------------------------------------------------------------------------------------
def F(label, era, text, apa, url=""):
    return {"label": label, "era": era, "text": text, "apa": apa, "url": url}

FUENTES = {
 "hoffmeier05": F("Hoffmeier, Ancient Israel in Sinai", 5, "Estudio arqueológico y geográfico del éxodo y del desierto. Identifica Ramsés con Qantir, Pitón con Tell el-Retaba, Sucot con Tjeku y el yam suf con el sistema de lagos Ballah; sitúa el Sinaí en el sur de la península (Ras Safsafah o Jebel Serbal) y lee ʾélef como unidad militar. Trabaja en un marco ramésida (s. XIII), sin defender una fecha.", "Hoffmeier, J. K. (2005). Ancient Israel in Sinai: The evidence for the authenticity of the wilderness tradition. Oxford University Press."),
 "hoffmeier08": F("Hoffmeier, Arqueología de la Biblia", 0, "Manual divulgativo y gráfico. En el capítulo del Éxodo expone las dataciones (c. 1270–1250, 1447/6 y c. 1525) sin decidir entre ellas, y es más prudente que su obra de 2005: dice que ninguno de los topónimos de Ex 14:2 se ha identificado con seguridad.", "Hoffmeier, J. K. (2008). Arqueología de la Biblia. San Pablo."),
 "hoffmeier97": F("Hoffmeier, Israel in Egypt", 1, "Primera parte del trabajo de Hoffmeier: la estancia en Egipto y el éxodo a la luz de la egiptología (nombres, oficios, geografía del delta oriental).", "Hoffmeier, J. K. (1997). Israel in Egypt: The evidence for the authenticity of the Exodus tradition. Oxford University Press."),
 "baker": F("Baker, Trasfondo arqueológico del santuario", 7, "Tesis doctoral sobre el tabernáculo. Compara la Morada con el campamento de Ramsés II en Qadesh y con los santuarios portátiles egipcios; concluye que el diseño refleja el Egipto del Imperio Nuevo. Es una lectura apologética, que expone también la datación temprana y la tardía.", "Baker, L. S., Jr. (2019). Archaeological backgrounds of the sanctuary [Tesis doctoral, Andrews University]."),
 "hillel": F("Hillel, Historia natural de la Biblia", 6, "Lectura ambiental y naturalista de la Biblia hebrea. Explica plagas, cruce del mar, codornices y agua de la roca con fenómenos naturales; es escéptico sobre las cifras y sobre el maná. Se usa para el medio físico, separando sus datos de sus conjeturas.", "Hillel, D. (2006). The natural history of the Bible: An environmental exploration of the Hebrew scriptures. Columbia University Press."),
 "curso": F("Curso «Explorando la Tierra Bíblica de Israel»", 0, "Curso de geografía bíblica (clases 4 y 5: la narración del Éxodo, de Egipto a Cades y de Cades al monte Nebo). Presenta las dos fechas del éxodo y varias rutas, y prefiere la laguna de Bardawil para el cruce.", "Curso «Explorando la Tierra Bíblica de Israel» [Apuntes de clase, clases 4 y 5]. (s. f.)."),
 "kitchen": F("Kitchen, Fiabilidad del AT", 0, "Kitchen reúne datos egipcios (precio de esclavos, nombres, tratados, el tabernáculo) a favor de un trasfondo del II milenio para el éxodo, que él fecha en el s. XIII.", "Kitchen, K. A. (2003). On the reliability of the Old Testament. Eerdmans."),
 "bietak": F("Bietak, Avaris", 1, "Manfred Bietak excavó Tell el-Dab‘a desde 1966: la Avaris de los hicsos, con población de origen cananeo, y después Perunefer, puerto y base militar de la dinastía XVIII. Junto a ella, en Qantir, estuvo Pi-Ramsés.", "Bietak, M. (1996). Avaris, the capital of the Hyksos: Recent excavations at Tell el-Dab‘a. British Museum Press."),
 "hayes": F("Hayes, Papiro Brooklyn 35.1446", 1, "Lista de sirvientes de una casa egipcia (c. 1800–1740 a. e. c.) con unos cuarenta nombres semitas. Entre las mujeres figura una Šp-ra, que Albright relacionó con Sifrá (Ex 1:15). Es un dato de época anterior que muestra nombres semitas en Egipto, no una mención de la partera.", "Hayes, W. C. (1955). A papyrus of the late Middle Kingdom in the Brooklyn Museum (Papyrus Brooklyn 35.1446). The Brooklyn Museum."),
 "lewis_sargon": F("Lewis, La leyenda de Sargón", 1, "Edición del relato acadio en que la madre de Sargón lo pone en una cesta de juncos sellada con betún y lo echa al río. Lewis estudia el motivo del héroe expuesto al nacer en muchas culturas.", "Lewis, B. (1980). The Sargon legend: A study of the Akkadian text and the tale of the hero who was exposed at birth. American Schools of Oriental Research."),
 "davies_rekh": F("Davies, La tumba de Rejmira", 2, "Rejmira fue visir de Tutmosis III. Su tumba de Tebas (TT100) pinta a extranjeros semitas y nubios fabricando adobes con barro, agua y paja bajo capataces con vara, junto a la leyenda «los cautivos que Su Majestad trajo para las obras del templo de Amón».", "Davies, N. de G. (1943). The tomb of Rekh-mi-Rēʿ at Thebes (Vols. 1–2). The Metropolitan Museum of Art."),
 "giveon": F("Giveon, Los beduinos shasu", 3, "Reúne los textos egipcios sobre los shasu, pastores de Edom y Seír. Las listas de Soleb (Amenhotep III) y Amara Oeste (Ramsés II) nombran una «tierra de los shasu de Yhw», que muchos relacionan con el nombre YHWH.", "Giveon, R. (1971). Les bédouins Shosou des documents égyptiens. Brill."),
 "enmarch": F("Enmarch, Las Admoniciones de Ipuwer", 4, "Edición del poema egipcio de Ipuwer («el río es sangre», un país en desorden). Enmarch lo fecha en el Reino Medio y lo lee como literatura de lamento, no como crónica de las plagas.", "Enmarch, R. (2008). A world upturned: Commentary on and analysis of The Dialogue of Ipuwer and the Lord of All. Oxford University Press."),
 "drews": F("Drews y Han, 2010", 5, "Simulación por computadora: un viento del este de unos 100 km/h durante 12 horas podría haber dejado en seco un banco de unos 3–4 km en la laguna del lago Manzala, en el delta oriental, durante unas cuatro horas. Los autores lo proponen como mecanismo físico compatible con Ex 14:21.", "Drews, C., & Han, W. (2010). Dynamics of wind setdown at Suez and the Eastern Nile Delta. PLoS ONE, 5(8), e12481.", "https://doi.org/10.1371/journal.pone.0012481"),
 "mendenhall": F("Mendenhall, Los censos de Números", 7, "Propone que ʾélef designa en los censos una unidad tribal o militar, no «mil». Así las cifras de Nm 1 y 26 darían unos pocos miles de combatientes.", "Mendenhall, G. E. (1958). The census lists of Numbers 1 and 26. Journal of Biblical Literature, 77(1), 52–66."),
 "humphreys": F("Humphreys, El número del Éxodo", 7, "Lee ʾélef como «tropa» y reconstruye unos 5550 combatientes y unas 20 000 personas en total, a partir de las cifras de Nm 1 y 26. Su propuesta es discutida.", "Humphreys, C. J. (1998). The number of people in the Exodus from Egypt: Decoding mathematically the very large numbers in Numbers I and XXVI. Vetus Testamentum, 48(2), 196–213."),
 "homan": F("Homan, A tus tiendas, Israel", 7, "Estudio de las tiendas del Oriente antiguo. Compara la planta del tabernáculo con la tienda de campaña de Ramsés II en la batalla de Qadesh (relieves de Abu Simbel, Luxor y el Rameseo): mismas proporciones y orientación.", "Homan, M. M. (2002). To your tents, O Israel! The terminology, function, form, and symbolism of tents in the Hebrew Bible and the ancient Near East. Brill."),
 "cohen_kades": F("Cohen y Bernick-Greenberg, Cades-barnea", 8, "Informe final de las excavaciones de Tell el-Qudeirat (1976–1982): fortalezas israelitas de los siglos X a VII a. e. c., sin niveles del Bronce Tardío.", "Cohen, R., & Bernick-Greenberg, H. (2007). Excavations at Kadesh Barnea (Tell el-Qudeirat) 1976–1982 (IAA Reports 34). Israel Antiquities Authority."),
 "rothenberg": F("Rothenberg, Timna", 9, "Rothenberg excavó en el valle de Timna un santuario egipcio de Hathor (ss. XIV–XII a. e. c.). En su última fase lo usaron madianitas como santuario-tienda; allí apareció una pequeña serpiente de cobre con la cabeza dorada.", "Rothenberg, B. (1972). Timna: Valley of the biblical copper mines. Thames and Hudson."),
 "hoftijzer": F("Hoftijzer y van der Kooij, Deir Alla", 9, "Edición de la inscripción pintada en yeso hallada en Tell Deir Alla (1967), c. 800 a. e. c.: «Libro de Balaam hijo de Beor, el hombre que veía a los dioses». Es la única mención extrabíblica de Balaam.", "Hoftijzer, J., & van der Kooij, G. (1976). Aramaic texts from Deir ‘Alla. Brill."),
 "barkay": F("Barkay et al., Ketef Hinom", 9, "Dos laminillas de plata enrolladas, halladas en 1979 en tumbas de Ketef Hinom (Jerusalén), del s. VII–VI a. e. c. Contienen la bendición sacerdotal de Nm 6:24–26: el texto bíblico más antiguo conservado.", "Barkay, G., Vaughn, A. G., Lundberg, M. J., & Zuckerman, B. (2004). The amulets from Ketef Hinnom: A new edition and evaluation. Bulletin of the American Schools of Oriental Research, 334, 41–71."),
 "piccirillo": F("Piccirillo y Alliata, Monte Nebo", 9, "Excavaciones franciscanas en Siyagha (monte Nebo): una iglesia del s. IV ampliada en los ss. V–VI, con mosaicos, en el lugar que la peregrina Egeria visitó como memorial de Moisés.", "Piccirillo, M., & Alliata, E. (Eds.). (1998). Mount Nebo: New archaeological excavations 1967–1997. Studium Biblicum Franciscanum."),
 "petrie": F("Petrie, Investigaciones en el Sinaí", 6, "Petrie excavó en 1904–1905 el templo de Hathor de Serabit el-Jadim y halló las inscripciones protosinaíticas, escritura alfabética temprana usada por mineros semitas.", "Petrie, W. M. F. (1906). Researches in Sinai. John Murray."),
 "albright66": F("Albright, Inscripciones protosinaíticas", 6, "Propuesta de desciframiento de las inscripciones de Serabit el-Jadim como una forma temprana del alfabeto cananeo, escrita por trabajadores semitas de las minas de turquesa.", "Albright, W. F. (1966). The Proto-Sinaitic inscriptions and their decipherment. Harvard University Press."),
 "sarna": F("Sarna, Explorando el Éxodo", 3, "Comentario judío de referencia. Sarna lee el éxodo como el acontecimiento fundante de la fe de Israel y presta atención a su trasfondo egipcio y a su sentido teológico.", "Sarna, N. M. (1986). Exploring Exodus: The heritage of biblical Israel. Schocken Books."),
 "childs": F("Childs, Éxodo", 3, "Comentario crítico y teológico. Childs estudia la historia del texto y su lectura en la sinagoga y la iglesia; para Ex 3:14 subraya que el Nombre promete una presencia activa más que definir un ser.", "Childs, B. S. (1974). The book of Exodus: A critical, theological commentary. Westminster Press."),
 "cassuto": F("Cassuto, Comentario a Éxodo", 7, "Umberto Cassuto (1883–1951) lee Éxodo como una composición unitaria y atiende a sus técnicas literarias y a sus paralelos cananeos y egipcios.", "Cassuto, U. (1967). A commentary on the book of Exodus (I. Abrahams, Trad.). Magnes Press."),
 "milgrom": F("Milgrom, Números (JPS)", 8, "Comentario judío a Números. Para Meribá repasa las explicaciones tradicionales de la falta de Moisés: golpear en lugar de hablar, la ira, o el «nosotros» de «¿sacaremos agua?».", "Milgrom, J. (1990). The JPS Torah commentary: Numbers. Jewish Publication Society."),
 "tigay": F("Tigay, Deuteronomio (JPS)", 9, "Comentario judío a Deuteronomio. Sobre Dt 34 recoge la tradición de la muerte de Moisés «por la boca» de YHWH y la tumba desconocida, que impide su veneración.", "Tigay, J. H. (1996). The JPS Torah commentary: Deuteronomy. Jewish Publication Society."),
 "assmann": F("Assmann, Moisés el egipcio", 0, "Estudio de la memoria cultural de Moisés en Occidente: cómo cada época lo ha imaginado, del Egipto de Akenatón a Freud. No es una biografía histórica.", "Assmann, J. (1997). Moses the Egyptian: The memory of Egypt in Western monotheism. Harvard University Press."),
 "finkelstein": F("Finkelstein y Silberman, 2001", 0, "Sostienen que no hay huellas arqueológicas de un gran grupo en el Sinaí en el Bronce Tardío y que el relato del éxodo se fijó en los siglos VII–VI a. e. c., con la geografía de esa época.", "Finkelstein, I., & Silberman, N. A. (2001). The Bible unearthed: Archaeology's new vision of ancient Israel and the origin of its sacred texts. Free Press."),
 "dever": F("Dever, ¿Quiénes eran los primeros israelitas?", 0, "Dever ve el origen de Israel sobre todo en Canaán, pero admite que un grupo pequeño pudo traer de Egipto la memoria del éxodo.", "Dever, W. G. (2003). Who were the early Israelites and where did they come from? Eerdmans."),
 "ussher": F("Ussher, Anales del mundo", 0, "El arzobispo Ussher fechó el éxodo en 1491 a. C. (año del mundo 2513) y el nacimiento de Moisés en 1571 a. C.", "Ussher, J. (1658). The annals of the world. E. Tyler."),
 "seder_olam": F("Seder Olam Rabá", 0, "Cronología rabínica del s. II e. c. Sitúa el éxodo en el año del mundo 2448, que en el cómputo judío corresponde a 1313 a. e. c.; Moisés nace en 2368 (1393 a. e. c.).", "Guggenheimer, H. W. (Trad.). (1998). Seder Olam: The rabbinic view of biblical chronology. Jason Aronson."),
 "gregorio": F("Gregorio de Nisa, Vida de Moisés", 0, "Gregorio de Nisa (c. 335–395) recorre la vida de Moisés en dos partes: la historia y su contemplación espiritual. La zarza, la nube y la tiniebla del Sinaí son etapas del alma que avanza sin fin hacia Dios (epéktasis).", "Gregorio de Nisa. (1978). The life of Moses (A. J. Malherbe & E. Ferguson, Trads.). Paulist Press. (Obra original del s. IV)."),
 "filon": F("Filón, Vida de Moisés", 0, "Filón de Alejandría (c. 20 a. e. c.–50 e. c.) presenta a Moisés como rey, legislador, sacerdote y profeta, educado por maestros egipcios y griegos.", "Filón de Alejandría. (1935). On the life of Moses (F. H. Colson, Trad.; Philo, Vol. 6, Loeb Classical Library 289). Harvard University Press."),
 "josefo": F("Josefo, Antigüedades judías II–IV", 0, "Josefo (s. I e. c.) narra la vida de Moisés con añadidos de la tradición: un escriba anuncia al faraón el nacimiento del libertador, y Moisés dirige una campaña egipcia contra Etiopía antes de huir a Madián.", "Josefo, F. (1930). Jewish antiquities, books I–IV (H. St. J. Thackeray, Trad.; Loeb Classical Library 242). Harvard University Press."),
 "calvino": F("Calvino, Armonía de los cuatro últimos libros de Moisés", 7, "Calvino (1509–1564) ordena Éxodo–Deuteronomio por temas (historia, ley, ceremonias) y lee a Moisés como ministro de un pacto de gracia que apunta a Cristo.", "Calvino, J. (1852–1855). Commentaries on the four last books of Moses arranged in the form of a harmony (C. W. Bingham, Trad.). Calvin Translation Society. (Obra original de 1563)."),
 "henry": F("Matthew Henry, Comentario", 7, "Henry (1662–1714), pastor presbiteriano inglés. Su comentario devocional recorre cada versículo con aplicaciones prácticas. Síntesis, no cita.", "Henry, M. (1706–1714). Commentary on the whole Bible. Obra de dominio público.", "https://ccel.org/ccel/henry/mhc1"),
 "macarthur": F("MacArthur, Biblia de estudio", 7, "John MacArthur (n. 1939), pastor reformado y dispensacionalista. Sus notas defienden la fecha temprana del éxodo (c. 1445 a. C.) y leen la ley y el tabernáculo como figuras de Cristo. Síntesis de su línea interpretativa, no cita.", "MacArthur, J. (1997). The MacArthur Study Bible. Word Publishing."),
 "jfb": F("Jamieson, Fausset y Brown, Comentario", 7, "Comentario evangélico del s. XIX, crítico y devocional a la vez, con atención a la geografía y a las costumbres orientales.", "Jamieson, R., Fausset, A. R., & Brown, D. (1871). Commentary critical and explanatory on the whole Bible. Obra de dominio público."),
 "salamanca": F("Profesores de Salamanca, Biblia comentada", 7, "Comentario católico español de mediados del s. XX, con notas filológicas, históricas y patrísticas.", "Profesores de Salamanca. (1960). Biblia comentada: Vol. 1. Pentateuco (A. Colunga & M. García Cordero). Biblioteca de Autores Cristianos."),
}

# ---------------------------------------------------------------------------------------------
# Glosario
# ---------------------------------------------------------------------------------------------
GLOS = {
 "teva": ["Tevá (תֵּבָה)", "«Arca», palabra que la Biblia usa solo dos veces para dos objetos: el arca de Noé (Gn 6–9) y la arquilla de Moisés (Ex 2:3). En ambas un justo es salvado de las aguas dentro de un cofre embetunado. Probablemente es un préstamo del egipcio db3t, «cofre»."],
 "moshe": ["Moshé (מֹשֶׁה)", "El texto lo explica por el hebreo mashá, «sacar del agua» (Ex 2:10). La forma Moshé es activa («el que saca»), lo que la tradición leyó como anuncio de que él sacaría a Israel de las aguas. Muchos lo relacionan con el egipcio ms(i), «nacido de», de nombres como Tutmosis («nacido de Tot») o Ahmose."],
 "ehye": ["Ehyé asher ehyé (אֶהְיֶה אֲשֶׁר אֶהְיֶה)", "Primera persona del verbo hayá, «ser, estar, llegar a ser»: «Seré el que seré» o «Soy el que soy». La Septuaginta tradujo egō eimi ho ōn, «Yo soy el que es». El tetragrámaton YHWH se relaciona con ese mismo verbo. Por respeto, la tradición judía no lo pronuncia y lee Adonai."],
 "yhwh": ["YHWH", "El nombre propio de Dios, escrito con cuatro consonantes (tetragrámaton). Esta línea lo transcribe sin vocales. La pronunciación original se perdió porque, por reverencia, se dejó de pronunciar; las versiones castellanas lo traducen «Jehová», «Yahvé» o «el Señor»."],
 "yamsuf": ["Yam Suf (יַם־סוּף)", "Literalmente «mar de Juncos»: suf es el junco o papiro (Ex 2:3) y tiene un equivalente egipcio, twf(y). La Septuaginta tradujo «mar Rojo». La Biblia usa el nombre para los lagos del istmo de Suez y también para los golfos de Suez (Nm 33:10) y de Áqaba (1 R 9:26)."],
 "pesaj": ["Pésaj (פֶּסַח)", "La Pascua. Del verbo pasaj, «pasar de largo, saltar por encima, proteger» (Ex 12:13.23). Designa el cordero sacrificado el 14 de nisán y la fiesta que recuerda la salida de Egipto, unida a los siete días de panes sin levadura (matsot)."],
 "elef": ["ʾÉlef (אֶלֶף)", "Significa «mil», pero también «clan, familia» (Jue 6:15) y quizá «tropa». Por eso se discute si los 600 000 de Ex 12:37 y los 603 550 de Nm 1:46 son cifras literales o unidades: Petrie, Mendenhall, Humphreys y Hoffmeier proponen unos miles o pocas decenas de miles."],
 "mishkan": ["Mishkán (מִשְׁכָּן)", "«Morada», del verbo shajan, «habitar como en tienda» (Ex 25:8). De la misma raíz viene el término rabínico Shejiná, la presencia de Dios que habita. Juan 1:14 dice que el Verbo «puso su tienda» (eskēnōsen) entre nosotros."],
 "kaporet": ["Kapóret (כַּפֹּרֶת)", "La tapa de oro del arca, entre los dos querubines, donde se rociaba la sangre en Yom Kipur. La Septuaginta la llamó hilastērion, «lugar de expiación», palabra que Pablo aplica a Cristo (Ro 3:25). En castellano, «propiciatorio»."],
 "torah": ["Torá (תּוֹרָה)", "Más que «ley»: «instrucción, enseñanza», del verbo yará, «señalar, enseñar». Designa los mandamientos de Moisés y, después, los cinco libros del Pentateuco."],
 "eved": ["ʿÉved YHWH (עֶבֶד יְהוָה)", "«Siervo de YHWH», título que Dt 34:5 da a Moisés al morir y que luego llevan Josué, David y el Siervo de Isaías. Hebreos 3:5 lo retoma: Moisés fue fiel como siervo en la casa de Dios."],
 "qaran": ["Qaran (קָרַן)", "«Irradiar, despedir rayos», verbo emparentado con qéren, «cuerno», y también «rayo» (Hab 3:4). La Vulgata tradujo cornuta esset facies sua, «su rostro tenía cuernos»; de ahí el Moisés con cuernos de Miguel Ángel."],
 "shema": ["Shemá (שְׁמַע)", "«¡Escucha!», primera palabra de Dt 6:4. Nombra la confesión de fe que el judaísmo recita mañana y noche (Dt 6:4–9; 11:13–21; Nm 15:37–41). Jesús la cita como el primer mandamiento (Mc 12:29–30)."],
 "corvee": ["Trabajos forzados (mas)", "Los «jefes de trabajos forzados» (sarei misim, Ex 1:11) organizaban la prestación obligatoria de trabajo para el Estado (en francés, corvée), habitual en Egipto para obras públicas, templos y ciudades."],
 "kap": ["El kap", "La «guardería» o escuela del palacio egipcio, donde se criaban los hijos del rey junto con hijos de la élite y de príncipes extranjeros. Hoffmeier lo propone como marco para la educación de Moisés; el título «niño del kap» aparece en tumbas del Reino Nuevo."],
 "shasu": ["Shasu", "Nombre egipcio de los pastores nómadas de Edom, Seír y el sur de Transjordania. Las listas de Amenhotep III (Soleb) y Ramsés II (Amara Oeste) mencionan una «tierra de los shasu de Yhw»."],
 "migdol": ["Migdol", "Palabra semita para «torre, fortaleza». En el Reino Nuevo nombraba los fuertes de la frontera oriental de Egipto. Varios lugares la llevaban; por eso es difícil saber cuál es el de Ex 14:2."],
 "bhs": ["BHS", "Biblia Hebraica Stuttgartensia: edición crítica del texto hebreo basada en el Códice de Leningrado (1008 e. c.)."],
 "sblgnt": ["SBLGNT", "The Greek New Testament: SBL Edition (Holmes, 2010): edición crítica abierta del texto griego del Nuevo Testamento."],
}

# ---------------------------------------------------------------------------------------------
# Lugares: clave → [lat, lon, nombre, identificación]
# ---------------------------------------------------------------------------------------------
SITES = {
 "ramses": [30.800, 31.835, "Ramsés", "Pi-Ramsés, en Qantir (Egipto), junto a Tell el-Dab‘a (Avaris): capital de Ramsés II en el delta oriental (c. 1270–1120 a. e. c.)."],
 "avaris": [30.787, 31.821, "Avaris", "Tell el-Dab‘a (Egipto): Avaris, capital de los hicsos, y después Perunefer, puerto y base militar de la dinastía XVIII."],
 "piton": [30.546, 31.960, "Pitón", "Tell el-Retaba, en el Wadi Tumilat (Egipto): Per-Atum, «casa de Atum», fortaleza del Reino Nuevo. Otros la identifican con Tell el-Maskhuta."],
 "sucot": [30.553, 32.098, "Sucot", "Tell el-Maskhuta, en el extremo oriental del Wadi Tumilat: la región egipcia de Tjeku (Sucot)."],
 "gosen": [30.66, 31.62, "Gosén", "Tierra de Gosén: el delta oriental del Nilo, en torno al Wadi Tumilat (Gn 47:11 la llama «tierra de Ramsés»)."],
 "tanis": [30.977, 31.880, "Tanis", "San el-Hagar (Egipto): Zoán, capital de las dinastías XXI–XXII; muchos bloques de Pi-Ramsés se reutilizaron allí."],
 "menfis": [29.845, 31.251, "Menfis", "Mit Rahina, al sur de El Cairo: capital administrativa del Egipto antiguo."],
 "etam": [30.585, 32.235, "Etam", "«Al borde del desierto» (Ex 13:20), quizá el egipcio «isla de Atum», en la salida del Wadi Tumilat hacia el lago Timsah. Ubicación aproximada."],
 "pihahirot": [30.79, 32.30, "Pi-hahirot", "«La boca de los canales» o «el canal» (egipcio p3 ḥr): Hoffmeier propone la unión del canal fronterizo con los lagos Ballah. Hipótesis."],
 "migdol": [30.875, 32.465, "Migdol", "Un fuerte de la frontera oriental, quizá unos 5 km al sureste de Tell el-Borg (Hoffmeier). Hipótesis."],
 "baalzefon": [31.14, 33.08, "Baal-zefón", "Monte Casio (Ras Qasrun), en la barra del lago Bardawil, según Eissfeldt; Hoffmeier lo sitúa en las «aguas de Baal» junto a los lagos Ballah. Hipótesis."],
 "hebua": [30.932, 32.378, "Tjaru (Hebua)", "Tell Hebua I: Tjaru (Sile), la gran fortaleza de entrada a Egipto en el Camino de Horus."],
 "borg": [30.902, 32.425, "Tell el-Borg", "Dos fuertes del Reino Nuevo (Tutmosis III y Ramsés II) excavados por Hoffmeier en 1999–2008, al sureste de Tjaru."],
 "ballah": [30.83, 32.29, "Lagos Ballah", "Antiguo sistema de lagos del istmo, drenado con el Canal de Suez: el yam suf del éxodo según Bietak y Hoffmeier."],
 "timsah": [30.565, 32.29, "Lago Timsah", "Lago del istmo de Suez, junto a Ismailía; candidato antiguo al cruce del mar."],
 "amargos": [30.33, 32.38, "Lagos Amargos", "Gran y Pequeño Lago Amargo, hoy atravesados por el Canal de Suez; candidato al cruce (Hillel)."],
 "golfosuez": [29.93, 32.56, "Golfo de Suez", "Extremo norte del golfo de Suez, junto a la ciudad de Suez; candidato tradicional al cruce."],
 "bardawil": [31.15, 33.20, "Lago Bardawil", "Laguna costera del norte del Sinaí (Sirbonis), separada del mar por una barra de arena; candidato al cruce (Eissfeldt; el curso de Tierras Bíblicas)."],
 "nuweiba": [28.975, 34.655, "Nuweiba", "Playa del golfo de Áqaba; la hipótesis que sitúa el Sinaí en Arabia (Jebel al-Lawz) pone allí el cruce."],
 "mara": [29.876, 32.648, "Mara", "‘Ayun Musa («fuentes de Moisés»), al sureste de Suez: una de las propuestas para Mara; otras son Bir el-Mura y ‘Ain Hawara."],
 "elim": [29.27, 32.98, "Elim", "Wadi Gharandel, oasis de palmeras en la costa occidental del Sinaí: identificación tradicional. Ubicación aproximada."],
 "markha": [29.05, 33.12, "Junto al mar", "Llanura de el-Markha, cerca de Abu Zenima: el campamento «junto al Yam Suf» de Nm 33:10 y el desierto de Sin, según varios autores."],
 "serabit": [29.036, 33.459, "Serabit el-Jadim", "Minas egipcias de turquesa con un templo de Hathor; allí aparecieron las inscripciones protosinaíticas."],
 "dofca": [28.90, 33.37, "Dofcá", "Wadi Maghara, minas de turquesa (egipcio mfk3t, «turquesa»): propuesta para Dofcá (Nm 33:12). Hipótesis."],
 "refidim": [28.70, 33.63, "Refidim", "El oasis de Wadi Feirán, el mayor del sur del Sinaí: identificación mayoritaria de Refidim (Ex 17)."],
 "sinai": [28.565, 33.955, "Monte Sinaí (Horeb)", "Macizo de Jebel Musa y Ras Safsafah, con la llanura de er-Raha a sus pies (2285 m): identificación tradicional desde el s. IV."],
 "serbal": [28.646, 33.662, "Jebel Serbal", "Monte de 2070 m junto al oasis de Feirán, con inscripciones nabateas: candidato al Sinaí."],
 "sinbishar": [29.70, 32.95, "Jebel Sin Bishar", "Colina de 618 m al noreste de Ras Sudr: candidato al Sinaí (Har-el). Ubicación aproximada."],
 "karkom": [30.29, 34.735, "Har Karkom", "Meseta del Neguev con miles de grabados rupestres: candidato al Sinaí (Anati)."],
 "lawz": [28.654, 35.306, "Jebel al-Lawz", "Monte de 2580 m en el noroeste de Arabia Saudita: candidato al Sinaí en la hipótesis madianita."],
 "madian": [28.48, 35.02, "Madián", "Al-Bad‘ y Magha‘ir Shu‘ayb, en el noroeste de Arabia: centro tradicional de Madián, frente al golfo de Áqaba."],
 "hazerot": [28.88, 34.42, "Hazerot", "‘Ain Hudra, oasis del este del Sinaí: identificación tradicional (Nm 11:35)."],
 "cades": [30.651, 34.425, "Cades-barnea", "‘Ain el-Qudeirat, el mayor manantial del norte del Sinaí; a menos de 10 km está ‘Ain Qadis, que conserva el nombre."],
 "hebron": [31.53, 35.10, "Hebrón (Escol)", "Hebrón y el valle de Escol («racimo»), adonde llegaron los espías (Nm 13:22–23)."],
 "eziongeber": [29.539, 34.983, "Ezión-geber", "Junto a Elat, en la cabecera del golfo de Áqaba (Tell el-Jeleifeh, identificación discutida)."],
 "timna": [29.785, 34.985, "Timna", "Minas de cobre del Arabá, con un santuario egipcio de Hathor que usaron después los madianitas."],
 "hor": [30.317, 35.407, "Monte Hor", "Jebel Harún, junto a Petra (1350 m), con un santuario de Aarón: identificación tradicional (Josefo). Otros proponen un monte cerca de Cades."],
 "punon": [30.627, 35.493, "Punón", "Feinan, en el Arabá: minas de cobre (Nm 33:42); la tradición sitúa cerca la serpiente de bronce."],
 "dibon": [31.499, 35.777, "Dibón", "Dhiban (Jordania), capital de Mesa de Moab; allí apareció su estela en 1868."],
 "aroer": [31.474, 35.841, "Aroer", "Arair, sobre el borde norte del cañón del Arnón (Dt 2:36)."],
 "hesbon": [31.802, 35.810, "Hesbón", "Tell Hesbán (Jordania): la ciudad de Sehón, rey amorreo (Nm 21:26)."],
 "edrei": [32.618, 36.102, "Edrei", "Deraa (Siria), en Basán: la batalla contra Og (Nm 21:33)."],
 "sitim": [31.840, 35.673, "Sitim", "Abel-sitim, en las llanuras de Moab frente a Jericó: probablemente Tell el-Hammam (Nm 33:49)."],
 "deiralla": [32.197, 35.623, "Deir Alla", "Tell Deir Alla, en el valle del Jordán: inscripción de «Balaam hijo de Beor» (c. 800 a. e. c.)."],
 "nebo": [31.768, 35.725, "Monte Nebo", "Ras Siyagha (Jordania), cumbre del Pisgá (710 m): desde allí se ve el valle del Jordán, Jericó y, en días claros, Jerusalén."],
 "jerico": [31.871, 35.444, "Jericó", "Tell es-Sultan, la «ciudad de las palmeras» (Dt 34:3)."],
 "dan": [33.249, 35.652, "Dan", "Tel Dan, en el extremo norte de la tierra (Dt 34:1)."],
 "zoar": [31.04, 35.47, "Zoar", "Ghor es-Safi, al sureste del mar Muerto (Dt 34:3)."],
 "beerseba": [31.244, 34.840, "Beerseba", "Tel Beerseba: el Neguev (Dt 34:3)."],
 "maroccidental": [32.10, 34.70, "Mar occidental", "El Mediterráneo, «el mar de atrás» (Dt 34:2)."],
}

ALTARS = {
 "refidim": {"n": 1, "he": "יְהוָה נִסִּי", "tr": "YHWH Nisí", "ref": "Ex 17:15–16", "mean": "«YHWH es mi estandarte»: nes es el asta o la bandera que se alza para reunir a la tropa.",
   "attr": "Dios que pelea por su pueblo — el Dios que da la victoria.",
   "theo": "Israel vence a Amalec mientras Moisés mantiene alzadas las manos con la vara de Dios. El altar confiesa que la victoria no vino de la espada de Josué, sino del Dios bajo cuya bandera se combate.",
   "app": "Dependencia en la lucha: orar sostenidos por otros, como Aarón y Hur sostuvieron los brazos de Moisés, y reconocer de quién es la victoria."},
 "sinai": {"n": 2, "he": "מִזְבֵּחַ תַּחַת הָהָר", "tr": "Mizbéaj tájat ha-har", "ref": "Ex 24:4–8", "mean": "«altar al pie del monte», con doce estelas (matsevot), una por cada tribu.",
   "attr": "Dios del pacto — santo y, a la vez, cercano por la sangre.",
   "theo": "Moisés escribe las palabras de YHWH, levanta el altar y rocía la sangre sobre el altar y sobre el pueblo: las dos partes del pacto quedan unidas. Después los ancianos «vieron a Dios, y comieron y bebieron» (Ex 24:11).",
   "app": "Obediencia en comunión: «haremos y escucharemos» (Ex 24:7). La sangre del pacto anticipa la copa de la última cena (Mt 26:28)."},
}

ERAS = {"0": "Contexto y marco", "1": "Esclavitud y nacimiento", "2": "Huida y Madián", "3": "La zarza y el llamado", "4": "Plagas y Pascua",
        "5": "El Éxodo y el mar", "6": "Del mar al Sinaí", "7": "Sinaí: pacto, Ley y Morada", "8": "Cades y los cuarenta años", "9": "Moab y el Nebo"}

BANDS = [[[-1544, -1530, "Marco", 0], [-1530, -1487, "Esclavitud · nacimiento · palacio", 1], [-1487, -1447, "Madián", 2], [-1447, -1446.83, "Zarza", 3],
          [-1446.83, -1446.3, "Plagas", 4], [-1446.3, -1446.13, "Éxodo · mar", 5], [-1446.13, -1445.955, "Al Sinaí", 6], [-1445.955, -1444.9, "Sinaí", 7],
          [-1444.9, -1407.5, "Cades · cuarenta años", 8], [-1407.5, -1403, "Moab · Nebo", 9]],
         [[-1544, -1504, "Egipto: Ahmose I y Amenhotep I (dinastía XVIII)", 0], [-1504, -1479, "Tutmosis I y II", 0],
          [-1479, -1427, "Tutmosis III (con Hatshepsut hasta 1458)", 0], [-1427, -1403, "Amenhotep II", 0]]]

# ---------------------------------------------------------------------------------------------
# Ensamblaje: hitos, voces, biblioteca y atlas → DATA, META y mapa/atlas.json
# ---------------------------------------------------------------------------------------------
import copy, re
from hitos import EVENTS as _EV, GLOS_EXTRA, FUENTES_EXTRA, LABW, META
TRABAJO = Path("/home/claude/work")
def _json(nombre):
    """Datos de investigación (voces de comentaristas y citas de la biblioteca). Si no están en esta
    máquina, se usan los ya volcados en el HTML y en atlas.json (copias en estudios/lineas/moises/)."""
    for f in (TRABAJO / nombre, AQUI / nombre):
        if f.exists(): return json.loads(f.read_text(encoding="utf-8"))
    return {}
VOCES = _json("voces.json"); BIB = _json("bib_atlas.json")
ALIAS = {"Dt 34:10–12": "Dt 34:10–12; Heb 3:5", "Ex 2:11–14": "Ex 2:11–14; Hch 7:23–25", "Ex 12:12": "Ex 7–11; 12:12", "Ex 16:14–15": "Ex 16",
         "Ex 20:1–17": "Ex 19:16–20:17", "Ex 40:34–38": "Ex 25:8–9; 40:34–38", "Nm 24:17": "Nm 22–24 (esp. 24:17)", "Hch 7:29–30": None}

REFS = refs_biblicas(); REFS.update(FUENTES); REFS.update(FUENTES_EXTRA)
GLOS.update(GLOS_EXTRA)
ids = {e["id"]: i + 1 for i, e in enumerate(_EV)}
EVENTS = []
for e in copy.deepcopy(_EV):
    pas = e.pop("pas", None); e.pop("id")
    e["vinc"] = [ids[v] for v in e.get("vinc", [])]
    voz = VOCES.get(ALIAS.get(pas, pas) or "", []) if pas else []
    if voz: e["com"] = voz
    for r in e["refs"]: assert r in REFS, f"falta la referencia {r} ({e['title']})"
    for g in re.findall(r"\[\[glos:([^|\]]+)\|", e.get("text", "") + e.get("det", "")): assert g in GLOS, f"falta el glosario {g}"
    md = e.get("media") or {}
    if md.get("tipo") == "escritura": assert md["ref"] in REFS
    for k in md.get("hl", []) + md.get("altars", []) + [x for p in md.get("route", []) for x in p]: assert k in SITES, f"falta el lugar {k}"
    EVENTS.append(e)
for vs in VOCES.values():
    for _, x in vs:
        for r in re.findall(r"\[\[ref:([^|\]]+)\|", x): assert r in REFS, f"voces: falta {r}"

# atlas: pasajes por clave, citas de la biblioteca
atlas = copy.deepcopy(ATLAS)
for Lg in atlas["lugares"]:
    Lg["biblia"] = [[REFS[b]["label"], REFS[b]["tr"]] if isinstance(b, str) else b for b in Lg["biblia"]]
    if (BIB.get("lugares") or {}).get(Lg["id"]): Lg["bib"] = BIB["lugares"][Lg["id"]]
    if not Lg["fuentes"]: Lg.pop("fuentes")
    if Lg["id"] in SITES: Lg["site"] = Lg["id"]
    else: Lg["site"] = None
for t in atlas["tramos"]:
    if (BIB.get("tramos") or {}).get(str(t["n"])): t["bib"] = BIB["tramos"][str(t["n"])]
    if t.pop("vuelta", False): t["vuelta"] = 1
for r in atlas["rutas"]:
    if (BIB.get("rutas") or {}).get(r["n"]): r.setdefault("bib", BIB["rutas"][r["n"]])
for Lg in atlas["lugares"]:      # lugares solo del atlas (sin ficha de mapa de diapositiva): se agregan a SITES
    if Lg["id"] not in SITES:
        SITES[Lg["id"]] = [Lg["ll"][0], Lg["ll"][1], Lg["n"], Lg["actual"]]
        Lg["site"] = Lg["id"]
(AQUI / "mapa").mkdir(exist_ok=True)
(AQUI / "mapa" / "atlas.json").write_text(json.dumps(atlas, ensure_ascii=False, indent=0), encoding="utf-8")
for nombre, d in (("voces.json", VOCES), ("bib_atlas.json", BIB)):   # copia de respaldo junto a los datos
    if d: (AQUI / nombre).write_text(json.dumps(d, ensure_ascii=False, indent=0), encoding="utf-8")

DATA = {"events": EVENTS, "refs": REFS, "bands": BANDS, "glos": GLOS, "eranames": ERAS, "sites": SITES, "altars": ALTARS,
        "labw": LABW, "portada_spec": META["portada_spec"], "tikz_colores": META["tikz_colores"],
        "portada_tres": [[c, a, l, t, ids[k]] for c, a, l, t, k in META["portada_tres"]], "portada_cap": META["portada_cap"]}
