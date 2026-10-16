# Los atributos de Dios — fuentes LaTeX

Serie de presentaciones (Beamer, XeLaTeX) y libro *La gloria de Dios* sobre los atributos de Dios.
Compilar siempre con **XeLaTeX** (3 pasadas) desde la carpeta del archivo.

| Carpeta | Contenido |
|---|---|
| `00_Introduccion/` | `presentacion/Atributos_Introduccion.tex` y `articulo/Introduccion_Libro.tex` |
| `01_Preexistencia/` | `01_Preexistencia_presentacion.tex` y `01_Preexistencia_capitulo.tex` |
| `01_Uno/` | `01_Uno_presentacion.tex` y `01_Uno_capitulo.tex` (Dios es uno: el Shemá, Dt 6:4–5; Zac 14:9; 1 Co 8:6) |
| `02_Amor/` | `02_Amor_presentacion.tex` y `02_Amor_capitulo.tex` (Dios es amor: eterno, soberano e inmutable; 1 Jn 4:7–16) |
| `03_Espiritu/` | `03_Espiritu_presentacion.tex` y `03_Espiritu_capitulo.tex` (Jn 4:24; *rúaj*; «Dios de los espíritus», Nm 16:22; Horeb, voz sin figura) |
| `04_Santo/` | `04_Santo_presentacion.tex` y `04_Santo_capitulo.tex` |
| `06_Soberano/` | `06_Soberano_presentacion.tex` y `06_Soberano_capitulo.tex` (soberanía, nombres *Adonay* y *Elyón*, C. S. Lewis y el dolor) |
| `07_Justo/` | `07_Justo_presentacion.tex` y `07_Justo_capitulo.tex` (la justicia de Dios: Sal 145:17, *tsedaqá* y *mishpat*, Abraham ante Sodoma, Ro 3:26) |
| `08_Inmutable/` | `08_Inmutable_presentacion.tex` y `08_Inmutable_capitulo.tex` |
| `09_Omnipotente/` | `09_Omnipotente_presentacion.tex` y `09_Omnipotente_capitulo.tex` |
| `10_Omnipresente/` | `10_Omnipresente_presentacion.tex` y `10_Omnipresente_capitulo.tex` (Jer 23:23–24; Jehová-sama y Emanuel; Betel y *HaMaqom*) |
| `11_Omnisciente/` | `11_Omnisciente_presentacion.tex` y `11_Omnisciente_capitulo.tex` (omnisciencia y presciencia) |
| `12_Sabiduria/` | `12_Sabiduria_presentacion.tex` y `12_Sabiduria_capitulo.tex` |
| `13_Verdad/` | `13_Verdad_presentacion.tex` y `13_Verdad_capitulo.tex` |
| `14_Misericordia/` | `14_Misericordia_presentacion.tex` y `14_Misericordia_capitulo.tex` |
| `15_Fiel/` | `15_Fiel_presentacion.tex` y `15_Fiel_capitulo.tex` (fidelidad: Jos 21:45, *ha'El hane'emán*, el arroyo y el manantial) |
| `16_Celo/` | `16_Celo_presentacion.tex` y `16_Celo_capitulo.tex` |
| `17_Ira/` | `17_Ira_presentacion.tex` y `17_Ira_capitulo.tex` |
| `20_Gracia/` | `20_Gracia_presentacion.tex` y `20_Gracia_capitulo.tex` (Gn 6:8; *jen*, *jinnam*; Manasés; Pablo) |
| `21_Gloria/` | `21_Gloria_presentacion.tex` y `21_Gloria_capitulo.tex` (conclusión: la gloria de Dios, comunión de todos los atributos en Cristo) |
| `Libro/` | Maestro `La_gloria_de_Dios.tex`, `preambulo.tex`, `capitulos/`, `img/` y `convertir.py` |

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
