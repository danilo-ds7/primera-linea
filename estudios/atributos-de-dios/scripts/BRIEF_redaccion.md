# Revisión de redacción de un capítulo (regla 10 del proyecto, 19-10-2026)

Eres el editor de estilo de un capítulo en LaTeX (XeLaTeX) de la serie *La gloria de Dios: los atributos de Dios*, un estudio bíblico académico escrito en español. El autor pidió, para todos los capítulos: **"procura una redacción más humana, pero siempre en redacción académica"**. Tu trabajo es un pulido editorial de la prosa, no una reescritura del contenido.

## Qué significa "más humana, siempre académica"

**Humana:** la prosa debe leerse como la escribiría un autor que domina el texto y expone con naturalidad, no como un informe técnico ni como un texto generado.
- Párrafos con ritmo variado: frases largas y cortas, no una sucesión de oraciones del mismo molde.
- Transiciones naturales entre ideas; cada párrafo retoma algo del anterior y avanza.
- Verbos activos y lenguaje concreto.
- Se eliminan: las fórmulas mecánicas repetidas al abrir párrafos o secciones ("El verso dice…", "El texto muestra…", "Este pasaje…", una y otra vez); las listas disfrazadas de párrafo (tres o cuatro elementos pegados con punto y coma); los conectores de relleno ("en este sentido", "cabe destacar", "es importante señalar", "como se ha dicho", "en definitiva" usado como muletilla); las cadenas de paréntesis técnicos (si una frase trae tres o cuatro paréntesis seguidos, integra los datos en la oración cuando se lea mejor, **sin perder ninguno**); el tono de resumen o de ficha.
- La filología, los conteos, las referencias bíblicas y las citas de autores se conservan completos, pero integrados en la explicación.

**Académica:** registro de estudio bíblico universitario.
- Tercera persona, o primera del plural expositiva ("veamos", "observemos", "conviene notar"). **Nunca** tuteo al lector, nunca "usted", nunca "yo".
- Sin exclamaciones, sin anécdotas personales, sin giros de sermón ("hermanos", "¿no es maravilloso?", "¡qué consuelo!"), sin coloquialismos.
- Las preguntas se admiten solo como preguntas de investigación que ordenan el razonamiento ("¿Qué significa, entonces, que la palabra no caiga?"), no como recurso retórico ni emocional.
- Terminología técnica exacta, explicada cuando se introduce; afirmaciones sostenidas con texto bíblico y referencias APA, tal como ya están.
- Las interpretaciones propias o rabínicas siguen marcadas como *precisión* (los entornos `nota` y las `\precision{}` se mantienen como tales).

## Qué puedes editar

- Los párrafos de prosa corrida.
- El resumen (`abstract`).
- El texto dentro de `\begin{nota}[...] ... \end{nota}` (precisiones y notas).
- El texto de los `\item` en `itemize`, `enumerate` y `description`, con cuidado y sin cambiar su contenido.
- El texto de las cajas de definición (`tcolorbox` con la definición del atributo): solo pulido de estilo; la definición debe seguir diciendo exactamente lo mismo.
- Los `\caption{}` de figuras y tablas.

## Qué NO puedes tocar (invariantes; un script los verifica)

- Nada dentro de `\begin{cita}…\end{cita}`, `\begin{verso}…\end{verso}`, `\hebverso{…}`, `\begin{filologia}…\end{filologia}`, `\begin{tabular}…\end{tabular}`, `\begin{tikzpicture}…\end{tikzpicture}`, `\includegraphics`. Ni una letra.
- Los títulos de `\section`, `\subsection`, `\subsubsection` (se conservan textualmente, también sus `\label`).
- Los archivos `00_cabeza.tex` (preámbulo) y `99_cola.tex` (referencias): no se editan.
- Todo `\heb{…}`, `\hebl{…}`, `\grc{…}`, `\SENOR{}`, `\label{…}`, `\ref{…}`, `\emph{término}` de palabras hebreas/griegas transliteradas.
- Todas las referencias bíblicas (Gn 12:7, Sal 36:5 [36:6], Jos 21:43--45…), todas las cifras y conteos, todas las citas de autores con año y página (Pink, 2020, p. 54), (Carson, 1991), (HALOT), (BDAG), etc. Puedes mover una referencia dentro de la oración, pero no omitirla ni cambiarla.
- El orden de las secciones y de los párrafos entre secciones. Dentro de un párrafo puedes reordenar, unir o dividir oraciones.
- Las comillas LaTeX `` '' , los guiones `--`, `\ldots{}`, `~`, `\emph{}`, `\textbf{}`: conserva la sintaxis LaTeX válida (llaves balanceadas). No introduzcas comandos nuevos ni paquetes.
- Donde la RVR1960 dice "Jehová" el capítulo escribe `\SENOR{}`: no cambies eso.

## Lo que no debes hacer

- No agregues contenido, versículos, datos, interpretaciones ni referencias nuevas. No quites información. No "mejores" la teología. No resumas.
- No cambies el sentido de ninguna frase. Si una oración afirma algo con cautela ("lectura propia", "se señala como paralelo, no como dependencia"), la cautela se conserva.
- No alargues ni acortes el capítulo más de un 10 %.
- No menciones la Trinidad ni introduzcas términos que el proyecto evita.
- No cambies el nombre de los archivos ni crees archivos nuevos en el directorio de trozos.

## Procedimiento

1. Lee este brief y luego los trozos `NN_*.tex` del directorio de trabajo que se te indica, en orden. El capítulo está partido por `\section`: cada trozo es una sección completa.
2. Para cada trozo (salvo `00_cabeza.tex` y `99_cola.tex`), reescribe el archivo completo con la herramienta Write, con la prosa pulida y todo lo demás intacto. Un trozo puede quedar igual si ya está bien; lo normal es que cada trozo tenga varios párrafos mejorables. Trabaja de a un trozo por vez.
3. Al terminar todos los trozos, une y verifica:
   ```
   python3 -I scripts/redaccion.py join <dir_trozos> <dir_trozos>/../<nombre>_nuevo.tex
   python3 -I scripts/redaccion.py check <capitulo_original.tex> <dir_trozos>/../<nombre>_nuevo.tex
   ```
   (se ejecuta desde `/home/claude/primera-linea/estudios/atributos-de-dios`). Si el check reporta DIFERENCIAS, corrige el trozo correspondiente hasta que diga "OK: invariantes conservados". Un aviso sobre `emphterm` solo exige revisar que no se haya perdido un término en cursiva por error.
4. Compila el capítulo nuevo para comprobar que el LaTeX sigue siendo válido: copia `<nombre>_nuevo.tex` a la carpeta del atributo con el nombre que se te indica y corre `xelatex -interaction=nonstopmode -halt-on-error` allí (una pasada basta para detectar errores). Si falla, corrige y repite. Al final deja el .tex corregido en la carpeta del atributo (reemplazando el original) y borra los archivos auxiliares (.aux, .log, .out, .toc) que hayas generado.
5. Informa en pocas líneas: trozos editados, resultado del check, resultado de la compilación (páginas), y **tres ejemplos** breves de "antes → después" representativos de lo que cambiaste. No pegues el capítulo entero en el informe.
