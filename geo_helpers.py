"""
Kerangka kode untuk choropleth kab/kota level (~500 unit) memakai GeoJSON
batas wilayah digital. Isi GEOJSON_PATH dengan file yang sudah kamu unduh,
lalu panggil `build_choropleth()` dari app.py menggantikan proportional
symbol contoh di Tab 2.

Sumber GeoJSON kab/kota yang bisa dicoba:
- Portal Satu Data Indonesia / tanahair.indonesia.go.id (batas administrasi)
- Kemendagri Permendagri kode wilayah (untuk cocokkan kode_wilayah)
- Repositori GeoJSON komunitas (verifikasi lisensi & akurasi sebelum dipakai)
"""

import json
import plotly.express as px

GEOJSON_PATH = "data/indonesia_kabkota.geojson"  # <- ganti dengan file asli
GEOJSON_ID_PROPERTY = "kode_wilayah"  # <- sesuaikan nama field di GeoJSON-mu


def build_choropleth(df, value_col, geojson_path=GEOJSON_PATH,
                      id_property=GEOJSON_ID_PROPERTY):
    """
    df harus punya kolom 'kode_wilayah' (str, cocok dengan properti GeoJSON)
    dan kolom `value_col` (numerik) yang mau divisualisasikan.
    """
    with open(geojson_path) as f:
        geojson = json.load(f)

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="kode_wilayah",
        featureidkey=f"properties.{id_property}",
        color=value_col,
        color_continuous_scale="Viridis",
        mapbox_style="open-street-map",
        zoom=3.5,
        center={"lat": -2.5, "lon": 118},
        opacity=0.75,
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig
