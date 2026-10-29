# Lector de Versículos: app para celular

Esta carpeta `app/` es la app del sitio Yada. Se instala en el celular como una app (PWA) y funciona sin conexión.

## 1. Copiar la carpeta

Copia esta carpeta `app/` dentro de la carpeta del sitio, al lado de `index.qmd`. Si existe el archivo antiguo `app/lector-versiculos.html`, puedes borrarlo: lo reemplaza `app/index.html`.

## 2. Conectarla al sitio (`_quarto.yml`)

Agrega estas líneas. Lo demás del archivo queda igual.

Dentro de `project:`, para que Quarto copie la app al publicar:

```yaml
project:
  resources:
    - "app/**"
```

En el menú (`website: navbar: left:`), el enlace a la app:

```yaml
      - href: app/index.html
        text: Lector
```

## 3. Instalarla en el celular

- **Android (Chrome):** abre el sitio, entra a «Lector» y toca **Instalar**.
- **iPhone (Safari):** entra a «Lector», toca **Compartir** y luego **Agregar a pantalla de inicio**.

La instalación y el modo sin conexión funcionan cuando el sitio está publicado (GitHub Pages usa https). En la vista previa local (`quarto preview`) la app se ve, pero no se instala.

## 4. Agregar un estudio nuevo

1. Copia `estudios/isaias-57-15.json` con otro nombre, por ejemplo `estudios/nehemias-9-6.json`, y cambia su contenido.
2. Agrega el estudio a la lista `estudios` de `estudios/index.json`:

```json
{ "id": "nehemias-9-6", "referencia": "Nehemías 9:6", "titulo": "Tú solo eres Jehová", "linea": "Atributos de Dios", "atributo": "Soberanía creadora" }
```

3. En `sw.js`, sube la versión (por ejemplo `lector-v8` → `lector-v9`) para que los celulares descarguen lo nuevo.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html` | La app. |
| `manifest.webmanifest` | Nombre, colores e íconos de la app instalada. |
| `sw.js` | Guarda la app y los estudios para usarlos sin conexión. |
| `estudios/index.json` | Lista de estudios por línea. |
| `estudios/*.json` | Un archivo por estudio. |
| `iconos/` | Íconos de la app. |
| `morfo/` | Palabras del original con número Strong y morfología, en paquetes por grupo de libros: hebreo (`he/`, Open Scriptures Hebrew Bible, CC BY 4.0), griego SBL con acentos (`sbl/`, CC BY 4.0), bizantino (`byz/`) y Westcott-Hort (`wh/`). `lex-h.json` y `lex-g.json`: diccionario de Strong completo (lema, transliteración, definición, derivación y raíz, familia de palabras) y palabras con que Reina-Valera traduce cada número. |
| `paralelos/` | Pasajes paralelos del Treasury of Scripture Knowledge (dominio público), en paquetes por grupo de libros. |
| `biblias/` | Textos completos de dominio público, en paquetes por grupo de libros (`g1.json` … `g8.json`): Reina-Valera 1909, Biblia del Oso (1569), Reina-Valera 1862, Versión Moderna (1929), King James, American Standard, Douay-Rheims, Vulgata Clementina, Códice de Leningrado (WLC), Textus Receptus, Texto bizantino y Peshitta. |

## Versiones y textos originales

Casi todo se lee desde la carpeta de la app, sin conexión. Solo el Códice de Alepo, la Septuaginta y Tischendorf se piden a getbible.net. El Nuevo Testamento griego abre por defecto en el SBL Greek New Testament, con acentos. Los códices Vaticano y Sinaítico y el Gran Rollo de Isaías se abren como imágenes en sus bibliotecas. La NVI, la Biblia de Jerusalén y La Biblia de las Américas tienen derechos de autor: la app enlaza a Biblia Paralela para leerlas.

## Estudio de palabras

En «Comparación filológica», toca una palabra del hebreo (Códice de Leningrado) o del griego (bizantino o Westcott-Hort). La app muestra el lema, la transliteración, el número Strong, la forma gramatical en español y cómo la traduce Reina-Valera, y marca sus equivalentes en las columnas en español e inglés. Debajo aparecen los pasajes paralelos agrupados por palabra; al tocar uno se abre su comparación.

Los datos se generan con `tools/build_morfo.py`, `tools/build_extra.py` y `tools/build_lexico.py` (después se agrupan con `tools/empaquetar.py`) a partir de Open Scriptures (morphhb y strongs, en GitHub) y de la biblioteca privada. No se publica el texto de versiones con derechos: de la RV1960 solo se guarda la lista de palabras que usa para cada número Strong.

## Comentarios judíos (Sefaria)

En «Comparación filológica», para los versículos del Antiguo Testamento, la sección «Comentarios judíos clásicos» lee en vivo, desde la API pública de Sefaria, los comentarios registrados para ese versículo (Rashi, Ibn Ezra, Ramban, Radak, Sforno, Metzudat David, Malbim, Targum y otros). Muestra el hebreo y, solo cuando la traducción inglesa tiene licencia libre (dominio público, CC0, CC-BY o CC-BY-SA), también el inglés; cada texto indica su edición y licencia. Necesita conexión: sin internet aparecen los enlaces para abrir cada comentario en Sefaria. Los comentarios que ya se abrieron quedan guardados en el celular.

## Número Strong y raíces

El botón «Strong» de la comparación muestra u oculta el número Strong bajo cada palabra del original. Al tocar una palabra, la ficha muestra además su origen (raíz primitiva, deriva de…, compuesta de…), la cadena hasta la raíz, la familia de palabras de esa raíz y la definición de Strong. Cada raíz y cada palabra de la familia se puede tocar para ver su propia ficha. La definición de Strong está en inglés (las ediciones de dominio público son en inglés); dentro de Claude se puede traducir con la guía.

## Diccionarios por número Strong (públicos, sin modo privado)

En la ficha de cada palabra (Comparación filológica), en las palabras clave de la Lectura filológica y en la ventana Strong del sitio aparece la sección «Diccionarios»: una pestaña por diccionario y, en cada una, el idioma (Español / Inglés). Solo se muestran las definiciones. Los números Strong dentro de un diccionario se pueden tocar.

Todos son de dominio público y se ven sin clave:
- Strong (1890): `../datos/strong-{h,g}-fichas.json` (inglés) y `../datos/strong-{h,g}-es.json` (traducción propia al español).
- BDB (Brown, Driver y Briggs, 1906), hebreo y arameo: `lexicos/bdb/` (inglés, solo los elementos `<def>`, por tronco y acepción) y `lexicos/bdb-es/` (traducción propia).
- Abbott-Smith (1922), griego del NT: `lexicos/abbott/` (inglés, solo los elementos `<gloss>`, por acepción) y `lexicos/abbott-es/` (traducción propia).

El inglés se genera con `scripts/lexicos_publicos.py` desde openscriptures/HebrewLexicon (CC BY 4.0) y translatable-exegetical-tools/Abbott-Smith; el script avisa si falta la traducción de algún número. Los diccionarios con derechos de autor (Strong en español de Caribe, Vine en español, Chávez, Ortiz, Barclay, Strong-PT, NCSE) ya no se muestran. También: Thayer (1889, dominio público; edición «Thayer's Greek Definitions» de e-Sword) para los números G y el Ancient Hebrew Lexicon of the Bible (Benner, 2005; copia permitida con fines educativos sin fines de lucro) para los números H, en `app/lexicos/thayer[-es]/` y `app/lexicos/ahlb[-es]/`, traducidos al español por Yada. El Vine no se publica: el de e-Sword es de pago y con derechos de autor.

