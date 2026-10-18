# Predicaciones — fuentes

Predicaciones listas para publicar: el **PDF** para descargar y el **audio** para escuchar.
Al subir cambios a esta carpeta, GitHub Actions publica cada predicación en la página
**Predicaciones** del sitio (`scripts/predicaciones.py` → `predicaciones/`). No hay que tocar nada más del sitio.

## Dónde va cada predicación

| Carpeta | Tipo |
|---|---|
| `biograficas/` | La vida de un personaje bíblico (Abraham, David, Pablo…) |
| `tematicas/` | Un tema recorrido por toda la Escritura |
| `autoayuda/` | La Palabra aplicada a la vida diaria |
| `otras/` | Exposiciones de un pasaje y predicaciones de ocasión |
| `series/` | Series de predicaciones: una carpeta por serie y, dentro, una por predicación |

Cada predicación va en su propia carpeta `NN_Nombre/` (el número fija el orden):

```
biograficas/
  01_Abraham_el_peregrino/
    Abraham_el_peregrino.pdf      ← la predicación (PDF). Si en vez de PDF hay un .tex, se compila con XeLaTeX.
    Abraham_el_peregrino.mp3      ← el audio (también .m4a, .ogg o .wav)
    ficha.txt                     ← opcional: título, pasaje, fecha, lugar y descripción
series/
  01_De_Josue_a_David/
    serie.txt                     ← opcional: título y descripción de la serie
    01_Josue_y_la_conquista/
      ...pdf, ...mp3, ficha.txt
    02_Los_jueces/
      ...
```

- Basta con el PDF, con el audio o con ambos. Sin `ficha.txt`, el título sale del nombre de la carpeta
  (`01_Abraham_el_peregrino` → «Abraham el peregrino»).
- Modelo de `ficha.txt` y `serie.txt` en `_plantilla/` (las carpetas que empiezan con `_` no se publican).
- La fecha de `ficha.txt` (AAAA-MM-DD) es el día en que se predicó; sin ella se usa la fecha en que se subió.
- **Audio liviano**: GitHub no acepta archivos de más de 100 MB. Un MP3 mono a 64 kbps ocupa ~30 MB por hora.
  Si el audio está en otro lugar (Spotify, Drive), en vez de subirlo se pone su enlace en `ficha.txt`
  con la línea `audio: https://…`.
- Mientras no haya predicaciones, la página muestra «en preparación». Cada tipo aparece en la página
  solo cuando tiene al menos una predicación.
