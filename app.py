"""
Dashboard UAS Visualisasi Data dan Informasi
Tema: Daya Saing dan Sebaran Produksi Perikanan Tangkap Indonesia (BPS)
Topik: Multivariat (profil perikanan 34 provinsi) + Geospasial (produksi
       perikanan per kab/kota) + Aliran (ekspor perikanan menurut negara tujuan)

PENTING: Beberapa nilai pada file data/multivariat_provinsi.csv masih
bertanda "TODO", dan file *_SAMPLE.csv baru berisi data parsial / contoh.
Lengkapi/ganti sebelum deployment final -- lihat README.md.
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="Dashboard Perikanan Tangkap Indonesia", layout="wide")

# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------

@st.cache_data
def load_multivariat():
    return pd.read_csv("data/multivariat_provinsi.csv")

@st.cache_data
def load_geospasial():
    return pd.read_csv("data/geospasial_kabkota_SAMPLE.csv", comment="#")

@st.cache_data
def load_aliran():
    return pd.read_csv("data/aliran_ekspor_perikanan_SAMPLE.csv", comment="#")

st.title("Dashboard Produksi dan Ekspor Perikanan Tangkap Indonesia")
st.caption("Sumber: BPS (Badan Pusat Statistik) | Diakses: [isi tanggal akses]")

tab1, tab2, tab3 = st.tabs([
    "1. Data Berdimensi Tinggi (Multivariat)",
    "2. Data Geospasial",
    "3. Data Aliran (Ekspor)"
])

# ---------------------------------------------------------------------------
# TAB 1 — MULTIVARIAT: PCA + Parallel Coordinates + Heatmap Terklaster
#          dengan brushing & linking (Altair interval selection)
# ---------------------------------------------------------------------------
with tab1:
    st.header("Profil Perikanan 34 Provinsi (Multivariat)")
    df = load_multivariat()

    numeric_cols = [c for c in df.columns if c != "provinsi"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    missing = df[numeric_cols].isna().sum().sum()
    if missing > 0:
        st.warning(
            f"Ada {missing} sel data yang masih kosong/TODO dari total "
            f"{df.shape[0]*len(numeric_cols)} sel. Baris tidak lengkap "
            "disembunyikan sementara dari PCA/klaster. Lengkapi "
            "data/multivariat_provinsi.csv sebelum submit final."
        )

    df_complete = df.dropna(subset=numeric_cols)

    if len(df_complete) < 3:
        st.info(
            "Belum cukup baris lengkap (minimal 3) untuk menghitung PCA. "
            "Lengkapi CSV dari sumber BPS yang tercantum di README.md dulu."
        )
    else:
        X_scaled = StandardScaler().fit_transform(df_complete[numeric_cols].values)

        n_clusters = st.slider("Jumlah klaster (K-Means)", 2, 8, 4)
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_complete = df_complete.copy()
        df_complete["klaster"] = km.fit_predict(X_scaled).astype(str)

        pca = PCA(n_components=2)
        pcs = pca.fit_transform(X_scaled)
        df_complete["PC1"], df_complete["PC2"] = pcs[:, 0], pcs[:, 1]
        var_exp = pca.explained_variance_ratio_

        st.caption(
            f"PC1 menjelaskan {var_exp[0]*100:.1f}% varians, "
            f"PC2 menjelaskan {var_exp[1]*100:.1f}% varians."
        )

        brush = alt.selection_interval(name="brush")

        scatter = (
            alt.Chart(df_complete)
            .mark_circle(size=90)
            .encode(
                x=alt.X("PC1:Q", title=f"PC1 ({var_exp[0]*100:.0f}%)"),
                y=alt.Y("PC2:Q", title=f"PC2 ({var_exp[1]*100:.0f}%)"),
                color=alt.condition(brush, "klaster:N", alt.value("lightgray")),
                tooltip=["provinsi"] + numeric_cols,
            )
            .add_params(brush)
            .properties(title="PCA Biplot (per provinsi)", width=380, height=380)
        )

        pc_df = df_complete.melt(
            id_vars=["provinsi", "klaster"], value_vars=numeric_cols,
            var_name="variabel", value_name="nilai"
        )
        parallel = (
            alt.Chart(pc_df)
            .transform_filter(brush)
            .mark_line(opacity=0.6)
            .encode(
                x=alt.X("variabel:N", title=None),
                y=alt.Y("nilai:Q"),
                color=alt.Color("klaster:N"),
                detail="provinsi:N",
                tooltip=["provinsi:N"],
            )
            .properties(title="Parallel Coordinates (terhubung dgn seleksi di kiri)",
                        width=380, height=380)
        )

        st.altair_chart(scatter | parallel, use_container_width=False)
        st.caption(
            "Interaksi: drag/blok pada scatter PCA (brushing) untuk menyorot "
            "provinsi yang sama pada parallel coordinates (linking)."
        )

        st.subheader("Heatmap Terklaster")
        heat_df = df_complete.set_index("provinsi")[numeric_cols]
        heat_df = heat_df.loc[df_complete.sort_values("klaster")["provinsi"]]
        fig = px.imshow(heat_df.T, aspect="auto", color_continuous_scale="Viridis",
                         labels=dict(color="Nilai (asli)"))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Lihat pencilan (outlier) berdasarkan jarak ke centroid klaster"):
            centroid_dist = np.linalg.norm(
                X_scaled - km.cluster_centers_[km.labels_], axis=1
            )
            out_df = df_complete[["provinsi", "klaster"]].copy()
            out_df["jarak_ke_centroid"] = centroid_dist
            st.dataframe(
                out_df.sort_values("jarak_ke_centroid", ascending=False).head(10),
                use_container_width=True,
            )

# ---------------------------------------------------------------------------
# TAB 2 — GEOSPASIAL: Produksi perikanan per kab/kota
# ---------------------------------------------------------------------------
with tab2:
    st.header("Sebaran Produksi Perikanan Tangkap per Kab/Kota")
    st.warning(
        "Data pada tab ini **data BPS asli tapi baru 19 kab/kota** (Sulawesi "
        "Selatan, 2021) sebagai contoh. Ketentuan minimal ujian: level "
        "kab/kota (±500 unit) seluruh Indonesia. Tambahkan tabel sejenis dari "
        "33 provinsi lain (lihat README.md) dan GeoJSON batas wilayah untuk "
        "choropleth penuh."
    )
    geo_df = load_geospasial()
    metric = st.selectbox(
        "Pilih indikator",
        ["produksi_total_ton", "produksi_laut_ton", "produksi_perairan_umum_ton"],
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Peringkat Kab/Kota (proxy sebelum choropleth penuh)")
        rank_df = geo_df.sort_values(metric, ascending=True)
        fig = px.bar(
            rank_df, x=metric, y="kabupaten_kota", orientation="h",
            color=metric, color_continuous_scale="Viridis",
        )
        fig.update_layout(height=480, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Tabel data (ganti dgn ~500 kab/kota se-Indonesia)")
        st.dataframe(geo_df.drop(columns=[c for c in geo_df.columns if c.startswith("#")]),
                     use_container_width=True, height=480)

    st.info(
        "Untuk choropleth kab/kota se-Indonesia: unduh GeoJSON batas wilayah "
        "(mis. dari Portal Satu Data Indonesia / tanahair.indonesia.go.id), "
        "gabungkan dengan `kode_wilayah`, lalu panggil "
        "`geo_helpers.build_choropleth()` menggantikan bar chart di atas. "
        "Tambahkan juga 1 jenis peta lain (mis. proportional symbol) agar "
        "memenuhi 'minimal 2 jenis peta berbeda'."
    )

# ---------------------------------------------------------------------------
# TAB 3 — ALIRAN: Ekspor perikanan menurut negara tujuan (Sankey)
# ---------------------------------------------------------------------------
with tab3:
    st.header("Ekspor Komoditas Perikanan Indonesia menurut Negara Tujuan")
    st.warning(
        "Data pada tab ini **data contoh (SAMPLE)**, bukan data BPS asli. "
        "Ganti dengan data ekspor BPS (kode HS 03) sebelum submit final — "
        "lihat README.md."
    )
    flow_df = load_aliran()

    min_vol = st.slider(
        "Filter: tampilkan hanya negara dgn volume ekspor minimal (ton)",
        int(flow_df.volume_ekspor_ton.min()), int(flow_df.volume_ekspor_ton.max()),
        int(flow_df.volume_ekspor_ton.min()),
    )
    flow_filtered = flow_df[flow_df.volume_ekspor_ton >= min_vol].copy()
    flow_filtered["asal"] = "Indonesia"

    nodes = ["Indonesia"] + list(flow_filtered["negara_tujuan"])
    node_idx = {n: i for i, n in enumerate(nodes)}

    sankey = go.Figure(go.Sankey(
        node=dict(label=nodes, pad=12, thickness=14),
        link=dict(
            source=[0] * len(flow_filtered),
            target=[node_idx[n] for n in flow_filtered["negara_tujuan"]],
            value=flow_filtered["volume_ekspor_ton"],
            customdata=flow_filtered["nilai_ekspor_ribu_usd"],
            hovertemplate="Indonesia → %{target.label}<br>Volume: %{value} ton<br>"
                          "Nilai: %{customdata} ribu USD<extra></extra>",
        ),
    ))
    sankey.update_layout(
        title="Sankey: Volume Ekspor Perikanan Indonesia per Negara Tujuan",
        height=550,
    )
    st.plotly_chart(sankey, use_container_width=True)

    st.subheader("Volume vs Nilai Ekspor per Negara")
    fig2 = px.scatter(
        flow_filtered, x="volume_ekspor_ton", y="nilai_ekspor_ribu_usd",
        text="negara_tujuan", color="nilai_ekspor_ribu_usd",
        color_continuous_scale="Blues",
    )
    fig2.update_traces(textposition="top center")
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.caption(
    "Dibuat untuk UAS Visualisasi Data dan Informasi, Politeknik Statistika STIS. "
    "Palet warna: Viridis/Blues (ramah buta warna)."
)
