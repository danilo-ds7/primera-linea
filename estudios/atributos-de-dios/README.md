# Los atributos de Dios — fuentes LaTeX

Serie de presentaciones (Beamer, XeLaTeX) y libro *La gloria de Dios* sobre los atributos de Dios.
Compilar siempre con **XeLaTeX** (3 pasadas) desde la carpeta del archivo.

| Carpeta | Contenido |
|---|---|
| `00_Introduccion/` | `presentacion/Atributos_Introduccion.tex` y `articulo/Introduccion_Libro.tex` |
| `04_Santo/` | `04_Santo_presentacion.tex` y `04_Santo_capitulo.tex` |
| `09_Omnipotente/` | `09_Omnipotente_presentacion.tex` y `09_Omnipotente_capitulo.tex` |
| `12_Sabiduria/` | `12_Sabiduria_presentacion.tex` y `12_Sabiduria_capitulo.tex` |
| `13_Verdad/` | `13_Verdad_presentacion.tex` y `13_Verdad_capitulo.tex` |
| `14_Misericordia/` | `14_Misericordia_presentacion.tex` y `14_Misericordia_capitulo.tex` |
| `16_Celo/` | `16_Celo_presentacion.tex` y `16_Celo_capitulo.tex` |
| `17_Ira/` | `17_Ira_presentacion.tex` y `17_Ira_capitulo.tex` |
| `Libro/` | Maestro `La_gloria_de_Dios.tex`, `preambulo.tex`, `capitulos/` y `convertir.py` |

En cada atributo, `head.tex` y `body.tex` son piezas que usa la presentación. `crops/` y `papiro*.jpg` son las imágenes, y `fonts/` las fuentes hebreas y griegas.
Las referencias (APA 7) van dentro de cada `.tex`; no hay archivo `.bib`.

## Publicación en el sitio

Al subir cambios a esta carpeta, GitHub Actions compila los PDF y publica cada estudio en la sección
**Atributos de Dios** del sitio (`scripts/atributos.py`). No hay que tocar nada del sitio:

- Cada atributo va en su propia carpeta `NN_Nombre/` (el número fija el orden; `00` es la introducción).
- El `.tex` con clase `article` (u otra que no sea `beamer`) es el **capítulo**: se publica como página web y como PDF.
- El `.tex` con clase `beamer` es la **presentación**: se publica como PDF descargable.
- `Libro/` se compila como el libro completo *La gloria de Dios*.
- Los PDF no se suben al repositorio: se generan solos.
