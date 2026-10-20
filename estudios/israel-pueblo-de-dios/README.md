# Israel y su restauración — fuentes LaTeX

Serie de estudios (artículo/capítulo y presentación Beamer, XeLaTeX) sobre Israel, el pueblo de Dios:
las promesas a los patriarcas y la restauración que anuncian los profetas. Se escriben en el proyecto
de estudio «Israel». Misma estructura que `atributos-de-dios/` y `fiestas-santas/`.
Compilar siempre con **XeLaTeX** (3 pasadas) desde la carpeta del archivo.

## Regla de redacción

En todos los capítulos y presentaciones de la serie: **redacción humana, siempre en registro académico**.
Voz de autor que domina el tema, frases de largo variado y transiciones naturales; sin andamiaje mecánico
en la prosa (listas numeradas dentro del párrafo, «primero… segundo…», tres frases paralelas seguidas,
cierres de síntesis en cada párrafo, muletillas como «cabe señalar» o «en este sentido»). Nada coloquial.
En las presentaciones, enunciados breves de lámina, no párrafos copiados del capítulo. Rigor, citas bíblicas,
referencias, estructura y paleta no cambian.

## Cómo se agrega un estudio

- Cada estudio va en su propia carpeta `NN_Nombre/` (el número fija el orden; `00` es la introducción).
  Por ejemplo: `00_Introduccion/`, `01_Abraham/`, `02_Isaac/`, `03_Jacob/`…
- Dentro, el `.tex` con clase `article` (u otra que no sea `beamer`) es el **capítulo**: se publica como
  página web y como PDF. El `.tex` con clase `beamer` es la **presentación**: se publica como PDF.
- Junto a los `.tex` van sus piezas (`head.tex`, `body.tex`), imágenes (`crops/`, `papiro*.jpg`) y `fonts/`.
- Una carpeta `Libro/` (opcional) se compila como libro completo de la serie.
- Los PDF no se suben al repositorio: se generan solos.

## Publicación en el sitio

Al subir cambios a esta carpeta, GitHub Actions compila los PDF y publica cada estudio en la página
**Israel y su restauración** del sitio (`scripts/atributos.py`, serie `israel-pueblo-de-dios` → `israel/`).
No hay que tocar nada más del sitio.
