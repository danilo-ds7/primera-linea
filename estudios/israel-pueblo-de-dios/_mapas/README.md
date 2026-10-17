# Mapas de la serie Israel

`mapas.py` dibuja los mapas con cartografía real (costas, lagos y ríos GSHHS/WDB de Basemap y relieve sombreado), con la paleta café ladrillo de la serie. `mapas_datos.py` define cada mapa.

    pip install basemap basemap-data-hires pillow numpy matplotlib
    python3 mapas.py patriarcas --out ../01_Abraham_Exodo

Genera `crops/mapa_<id>.pdf` y `crops/mapa_<id>_leyenda.tex` (presentación) y `mapa_<id>.png` (capítulo y web). La carpeta empieza con `_`: el sitio no la publica como estudio.
