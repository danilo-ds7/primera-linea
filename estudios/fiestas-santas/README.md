# Festividades santas — fuentes LaTeX

Serie de estudios (capítulo/artículo y presentación Beamer, XeLaTeX) sobre las solemnidades de Levítico 23,
el año sabático y el Jubileo, escritos en el proyecto de estudio «Fiestas Santas». Misma estructura que
`atributos-de-dios/`. Compilar siempre con **XeLaTeX** (3 pasadas) desde la carpeta del archivo.
Método: lectura histórica, filológica, textual y literaria; la Biblia interpreta la Biblia. Marco de la serie:
el documento «Fiestas» (lecciones 6–14: Reglamento del Culto, memorial → figura → esperanza).

| Carpeta | Estudio |
|---|---|
| `00_Introduccion/` | Las solemnidades del Señor (Lv 23, calendario, moed/mikrá/jag, el Shabat, la arquitectura del siete, ¿para quién son las fiestas?) |
| `01_Pesaj/` | Pésaj: la Pascua del Señor (Éx 12–13; 1 Co 5:7) |
| `02_Matzot/` | Jag haMatsot: la fiesta de los Panes sin Levadura (itinerario del éxodo; la levadura en la Biblia) |
| `03_Primicias/` | Reshit y Bikurim: el Ómer de las primicias (*mimojorat hashabat*; 1 Co 15:20) |
| `04_Shavuot/` | Shavuot: la fiesta de las Semanas (Pentecostés; Sinaí y Hch 2; las lluvias de Jl 2:23) |
| `05_Yom_Terua/` | Yom Teruá: el día del sonido de trompeta (Jericó; la final trompeta) |
| `06_Yom_Kipur/` | Yom haKipurim: el día de las Expiaciones (Lv 16; Azazel; Melquisedec; Hebreos 9) |
| `07_Sukkot/` | Sukkot: la fiesta de las Cabañas y el Octavo día (Jn 7; el Reino) |
| `08_Shemita/` | Shemitá: el año sabático y el ciclo del siete (Lv 25; Dt 15; *áphesis*) |
| `09_Jubileo/` | El Jubileo: proclamaréis libertad en la tierra (Lv 25:10; el *goel*; Lc 4) |

En cada carpeta: `NN_Nombre_capitulo.tex` (article: página web + PDF), `NN_Nombre_presentacion.tex`
(beamer = `head.tex` + `body.tex`), `gen_img.py` + `gen_lib.py` (generan `crops/`: paneles de manuscrito y portada),
`papiro.jpg` y `fonts/`. Paleta de la serie: tierra roja, café rojizo, mostaza y papiro.

## Cómo se agrega un estudio

- Cada estudio va en su propia carpeta `NN_Nombre/` (el número fija el orden; `00` es la introducción).
- El `.tex` con clase `article` es el **capítulo**: se publica como página web y como PDF. El `.tex` con clase
  `beamer` es la **presentación**: se publica como PDF.
- Las figuras TikZ del capítulo se compilan aparte para la web: toda macro o estilo que use una figura debe
  definirse dentro de la figura o en el preámbulo.
- Una carpeta `Libro/` (opcional) se compila como libro completo de la serie.
- Los PDF no se suben al repositorio: se generan solos.

## Publicación en el sitio

Al subir cambios a esta carpeta, GitHub Actions compila los PDF y publica cada estudio en la página
**Festividades santas** del sitio (`scripts/atributos.py`, serie `fiestas-santas` → `festividades/`).
No hay que tocar nada más del sitio.
