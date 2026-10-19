# Guía de reescritura: una redacción más humana

Objetivo: que cada capítulo y cada presentación de la serie «Festividades santas» suene escrito por una
persona —Danilo Gómez Correa, profesor y estudiante de teología que enseña a adultos— y no por una máquina.
No se cambia el contenido, la estructura ni la exégesis; se cambia la voz.

## Qué suena a máquina (y hay que quitar)

1. **La frase-sentencia al cierre de cada párrafo.** Remates como «La restricción crea el día», «El enlace es
   deliberado», «La simetría es clara». Uno cada tanto está bien; uno por párrafo es un tic. Si el remate no
   agrega nada, se borra; si agrega, se integra a la frase anterior.
2. **El patrón «no X, sino Y» / «no es X; es Y».** Aparece docenas de veces. Dejar unos pocos, reescribir el resto
   de forma directa.
3. **Las tríadas y el paralelismo mecánico.** «una fecha, a una persona y a un procedimiento»; «la sangre, el
   incienso y las suertes». Cuando sea una enumeración real, se mantiene; cuando sea ritmo decorativo, se rompe.
4. **Los dos puntos como muletilla** («La tesis es clara: …», «Lo notable: …»). Reducir a la mitad por lo menos.
5. **Conectores de plantilla**: «Lo notable es que», «Conviene», «Cabe señalar», «Es decir», «En otras palabras»,
   «Nótese», «Obsérvese», «En suma», «En síntesis», «Más aún», «Con todo», «Así pues», «en clave de».
   Usar cada uno como mucho una o dos veces por documento; preferir transiciones que nazcan del argumento.
6. **Las frases de longitud uniforme.** Alternar: una frase larga que desarrolla, otra corta que fija. Que haya
   respiración, no metrónomo.
7. **El exceso de señalización meta** («La tesis de este estudio es que…», «La ruta es la misma de toda la
   serie…», «Este apartado mostrará…»). Un párrafo de orientación al inicio basta; el resto, fuera.
8. **Adjetivos valorativos sueltos** («incómoda», «deliberado», «notable», «decisivo», «central») usados para
   dar énfasis sin explicar. Si se afirma que algo es notable, hay que decir por qué o quitarlo.
9. **Lenguaje de informe**: «se observa», «se constata», «resulta evidente», «es preciso», «permite», «evidencia
   que», «en el marco de», «a nivel de». Fuera.
10. **Referencias al autor en tercera persona.** El sitio publica bajo el nombre de Danilo, así que «las
    presentaciones de Danilo», «las láminas de Danilo» quedan raras. Reemplazar por primera persona
    («en mis presentaciones anteriores», «cuando preparé las láminas de esta fiesta») o neutro
    («las presentaciones de esta serie»). Lo mismo en títulos de subsección y en notas de tablas
    («a partir de las presentaciones de Danilo» → «a partir de mis presentaciones anteriores»).

## Cómo suena una persona — SIEMPRE en registro académico

Esto es prosa académica (artículo de estudio bíblico serio), no divulgación ni sermón. «Humano» aquí
significa: un académico real escribiendo con su propia voz, no un generador. Por tanto:

- **Registro académico sostenido.** Nada de «usted», nada de apelaciones directas al lector, nada de
  coloquialismos ni exclamaciones. Se argumenta, se documenta, se matiza.
- **Primera persona con medida**, como en un artículo firmado: plural académico para conducir el argumento
  («leamos el versículo en su contexto», «volvamos a Lv 16:21»), y singular solo en juicios propios y escasos
  («sigo aquí a Milgrom», «mi lectura es que…»). Nunca más de un par de singulares por sección.
- **Decir las cosas una vez y bien.** Si un párrafo repite lo que ya dijo otro, se funde o se acorta.
- **Precisión antes que énfasis.** Las afirmaciones se sostienen con el texto, con la filología o con un autor;
  no con adjetivos.
- **Imágenes concretas cuando aclaran**, no como adorno: una comparación breve y sobria puede explicar el
  recorrido de la sangre «de dentro hacia fuera»; no hace falta más de una por sección.
- **Preguntas verdaderas**, escasas: la pregunta que el propio texto plantea, no la pregunta-gancho.
- **Admitir incertidumbre** con honestidad académica: «la evidencia no permite decidirlo», «el texto no lo
  afirma», «esta lectura es interpretativa».
- **Transiciones que razonan**: la frase que une dos secciones explica por qué el argumento pasa de una a otra.
- Español cuidado y neutro, con la terminología técnica que la serie ya usa (jatat, kapóret, moed, etc.).

## Qué NO se toca

- Toda cita bíblica (RVR1960 con \SENOR), todo texto hebreo (\heb, \hebverso) y griego (\grc), las referencias,
  los nombres de autores y obras, las fechas, los números de versículo. Ni una letra.
- Las tablas, las figuras TikZ, los recuadros `filologia`, `nota`, `cita`, `precision`, las macros, el preámbulo,
  los `\label`, los `\input`, las rutas de imágenes, los `\fotolado`, los comandos de Beamer.
- La estructura de secciones y de láminas (mismo número y mismo orden). Los títulos pueden ajustarse si suenan
  a máquina, pero sin perder lo que anuncian.
- La extensión total: puede bajar hasta un 10–15 % por eliminar redundancias, nunca subir. No se añade contenido
  nuevo ni se quita ningún argumento, cita o precisión.
- Las «Precisiones» (distinción entre texto explícito y tradición) se conservan íntegras en su sentido.

## En las presentaciones (Beamer)

- Las láminas ya son breves; aquí el problema es el remate aforístico en cada lámina y el patrón «no X, sino Y».
  Suavizar, variar, y que el texto de apoyo suene a lo que uno diría en voz alta al explicar la lámina.
- Las viñetas pueden ser frases incompletas; no hace falta convertirlas en prosa.
- Los recuadros `\precision{...}` se dejan como están salvo las referencias a «Danilo» (regla 10).

## Procedimiento

1. Leer este documento entero. Leer entero el capítulo y el `body.tex` (o el `_presentacion.tex`) antes de
   tocar nada, para captar la voz del estudio y sus repeticiones.
2. Reescribir con `Edit`, sección por sección (o bloque de láminas), sin reescribir el archivo entero de una vez.
3. Al terminar, compilar tres veces con XeLaTeX desde la carpeta del estudio:
   `cd <carpeta> && for i in 1 2 3; do xelatex -interaction=nonstopmode -halt-on-error NN_Nombre_capitulo.tex >/dev/null; done`
   y lo mismo para `NN_Nombre_presentacion.tex`. Revisar el `.log` (cero errores; sin `Overfull` nuevos graves).
   Comparar el número de páginas antes y después (`pdfinfo`): la presentación debe conservar el mismo número de
   láminas; el capítulo puede perder alguna página, no ganar.
4. Borrar los auxiliares (`.aux .log .out .nav .snm .toc .vrb` y los PDF) para dejar la carpeta limpia. No usar git.
5. Reportar en diez líneas: qué patrones se corrigieron más, cuántas palabras antes/después, páginas antes/después,
   y cualquier frase sobre la que haya duda.
