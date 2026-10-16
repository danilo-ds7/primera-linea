# Festividades santas — fuentes LaTeX

Serie de estudios (artículo/capítulo y presentación Beamer, XeLaTeX) sobre las fiestas de Levítico 23,
escritos en el proyecto de estudio «Fiestas Santas». Misma estructura que `atributos-de-dios/`.
Compilar siempre con **XeLaTeX** (3 pasadas) desde la carpeta del archivo.

## Cómo se agrega un estudio

- Cada fiesta va en su propia carpeta `NN_Nombre/` (el número fija el orden; `00` es la introducción).
  Por ejemplo: `00_Introduccion/`, `01_Pesaj/`, `02_Matzot/`, `03_Primicias/`, `04_Shavuot/`,
  `05_Yom_Terua/`, `06_Yom_Kipur/`, `07_Sukkot/`.
- Dentro, el `.tex` con clase `article` (u otra que no sea `beamer`) es el **capítulo**: se publica como
  página web y como PDF. El `.tex` con clase `beamer` es la **presentación**: se publica como PDF.
- Junto a los `.tex` van sus piezas (`head.tex`, `body.tex`), imágenes (`crops/`, `papiro*.jpg`) y `fonts/`.
- Una carpeta `Libro/` (opcional) se compila como libro completo de la serie.
- Los PDF no se suben al repositorio: se generan solos.

## Publicación en el sitio

Al subir cambios a esta carpeta, GitHub Actions compila los PDF y publica cada estudio en la página
**Festividades santas** del sitio (`scripts/atributos.py`, serie `fiestas-santas` → `festividades/`).
No hay que tocar nada más del sitio.
