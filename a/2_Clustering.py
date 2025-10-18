import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from io import BytesIO
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, silhouette_samples
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import folium
from streamlit_folium import folium_static
import re

# Mengimpor fungsi bantuan dari utils.py
# Pastikan file utils.py ada di direktori root proyek Anda
from utils import initialize_clustering_model, categorize_clusters, FEATURE_PRODUKSI, COLOR_PALETTE

# =================================================================================
# PENGATURAN HALAMAN DAN "MEMORI" (SESSION STATE)
# =================================================================================
st.set_page_config(page_title="Clustering", page_icon="📈", layout="wide")

# Inisialisasi 'memori' untuk menyimpan status dan hasil agar tidak hilang saat rerun
if 'run_clustering' not in st.session_state:
    st.session_state.run_clustering = False
if 'results' not in st.session_state:
    st.session_state.results = {}

# =================================================================================
# SIDEBAR - KONTROL PENGGUNA
# =================================================================================
with st.sidebar:
    st.header('⚙️ Pengaturan Clustering')
    uploaded_file = st.file_uploader('📂 Upload File Excel Anda', type=['xlsx'])
    
    # Dictionary untuk menampung semua parameter
    params = {}
    mode, year = None, None
    selected_features = [] # Inisialisasi list kosong
    
    if uploaded_file:
        # PENGATURAN MODE
        mode = st.selectbox('Mode Analisis:', ['Keseluruhan', 'Per Tahun'], help="Pilih 'Keseluruhan' untuk menganalisis tren semua tahun, atau 'Per Tahun' untuk fokus pada satu tahun spesifik.")
        
        try:
            df_temp = pd.read_excel(uploaded_file)
            df_temp.columns = [c.strip().title() for c in df_temp.columns]
            
            # Deteksi fitur dasar yang tersedia (e.g., 'Produksi', 'Volume') dari nama kolom
            base_features = set()
            for col in df_temp.columns:
                match = re.match(r'(.+)_(\d{4})$', col)
                if match:
                    base_features.add(match.group(1))
            available_features = sorted(list(base_features))
            
            if available_features:
                st.subheader("Fitur Analisis")
                selected_features = st.multiselect(
                    'Pilih Fitur untuk Clustering:',
                    options=available_features,
                    default=available_features, # Default memilih semua fitur yang ada
                    help="Pilih satu atau lebih fitur yang akan digunakan sebagai dasar pengelompokan."
                )
            else:
                st.warning("Tidak ada kolom fitur berformat 'NamaFitur_Tahun' yang ditemukan di file Anda.")

            if mode == 'Per Tahun':
                years_available = sorted(list(set(int(re.search(r'_(\d{4})$', c).group(1))
                                                    for c in df_temp.columns if re.search(r'_(\d{4})$', c))), reverse=True)
                if years_available:
                    year = st.selectbox('Pilih Tahun:', years_available)
                else:
                    st.warning("Tidak ada kolom berformat _YYYY yang ditemukan.")
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
            
        # PENGATURAN METODE
        st.subheader("Metode & Parameter")
        method = st.selectbox('Metode Clustering:', ['K-Means', 'BIRCH', 'OPTICS'])
        
        # PENGATURAN PARAMETER UTAMA
        if method in ['K-Means', 'BIRCH']:
            params['n_clusters'] = st.slider('Jumlah Cluster (K):', 2, 7, 3, help="Tentukan jumlah kelompok yang ingin dibentuk.")
        if method == 'OPTICS':
            params['min_samples'] = st.slider('Minimum Points (MinPts):', 2, 20, 5, help="Jumlah minimum tetangga yang diperlukan untuk sebuah titik dianggap sebagai titik inti (core point).")

        # PENGATURAN PARAMETER LANJUTAN (OPSIONAL)
        with st.expander("Parameter Lanjutan (Opsional)"):
            if method == 'BIRCH':
                params['threshold'] = st.number_input('Threshold:', min_value=0.1, max_value=1.0, value=0.5, step=0.1, help="Radius maksimum dari sub-cluster.")
                params['branching_factor'] = st.number_input('Branching Factor:', min_value=2, max_value=100, value=50, help="Jumlah maksimum sub-cluster di setiap node pada CF-Tree.")
            if method == 'OPTICS':
                use_eps = st.checkbox("Tentukan Epsilon (eps) secara manual")
                if use_eps:
                    params['eps'] = st.number_input('Epsilon (eps):', min_value=0.1, max_value=5.0, value=2.0, step=0.1, help="Jarak maksimum antara dua sampel untuk dianggap sebagai tetangga.")
                else:
                    params['eps'] = None 
        
        # TOMBOL AKSI
        if st.button('🚀 Mulai Clustering'):
            st.session_state.run_clustering = True
            st.session_state.results = {}

# =================================================================================
# AREA KONTEN UTAMA
# =================================================================================
st.title("📊 Dasbor Analisis Clustering Hasil Tangkapan Laut dan Konsumsi")

st.markdown("""
Aplikasi ini memungkinkan Anda untuk melakukan analisis clustering pada data perikanan tangkap laut. Unggah dataset Anda, pilih metode dan parameter di sidebar, lalu klik **"Mulai Clustering"** untuk melihat hasilnya.
""")

st.title("📂 Dataset")
col1, col2, col3 = st.columns(3)
assets_path = 'Files' 
if os.path.exists(assets_path):
    with col1:
        template_file = "Template_Dataset.xlsx"
        template_path = os.path.join(assets_path, template_file)
        if os.path.exists(template_path):
            with open(template_path, "rb") as f:
                st.download_button(label="📥 Download Template Dataset", data=f.read(), file_name=template_file)
    with col2:
        dataset_file = "Dataset_tangkaplaut.xlsx"
        dataset_path = os.path.join(assets_path, dataset_file)
        if os.path.exists(dataset_path):
            with open(dataset_path, "rb") as f:
                st.download_button(label="📂 Download Contoh Dataset", data=f.read(), file_name="dataset_Tangkap_Laut_Dan_Konsumsi.xlsx")
    with col3:
        guide_file = "Buku_panduan.pptx"
        guide_path = os.path.join(assets_path, guide_file)
        if os.path.exists(guide_path):
            with open(guide_path, "rb") as f:
                st.download_button(label="📘 Download Buku Panduan", data=f.read(), file_name=guide_file)
else:
    st.warning(f"Folder '{assets_path}' tidak ditemukan. Tombol download tidak akan muncul.")

st.markdown("---")


# --- Logika Pemrosesan dan Penampilan Hasil ---
if uploaded_file:
    df_raw = pd.read_excel(uploaded_file)
    df_raw.columns = [c.strip().title() for c in df_raw.columns]
    
    if st.session_state.run_clustering:
        with st.spinner('⏳ Sedang memproses clustering... Harap tunggu...'):
            try:
                if not selected_features:
                    st.error("❌ Harap pilih minimal satu fitur di sidebar untuk memulai analisis.")
                    st.stop()
                
                if mode == 'Keseluruhan':
                    feature_cols = sorted([c for f in selected_features for c in df_raw.columns if c.lower().startswith(f.lower() + '_')])
                else: # Per Tahun
                    if year is None: st.error("Tahun tidak terpilih atau tidak ditemukan."); st.stop()
                    feature_cols = [f"{f}_{year}" for f in selected_features if f"{f}_{year}" in df_raw.columns]
                
                if not feature_cols: st.error('❌ Tidak ada kolom fitur yang cocok ditemukan untuk mode/tahun yang dipilih.'); st.stop()
                
                # 2. PROSES DATA & CLUSTERING
                X_df = df_raw[feature_cols].copy().apply(pd.to_numeric, errors='coerce')
                mask_valid = X_df.dropna().index
                if len(mask_valid) < params.get('n_clusters', 2) or len(mask_valid) < params.get('min_samples', 2):
                    st.error(f"❌ Data valid setelah dibersihkan ({len(mask_valid)} baris) tidak cukup. Periksa isi file Anda."); st.stop()

                df_valid = df_raw.loc[mask_valid].reset_index(drop=True)
                scaler = MinMaxScaler(); X_scaled = scaler.fit_transform(X_df.loc[mask_valid])
                
                model = initialize_clustering_model(method, params); 
                model.fit(X_scaled)
                labels = getattr(model, "labels_", np.array([-1] * len(X_scaled)))
                
                df_valid["Cluster"] = labels
                df_valid = categorize_clusters(df_valid)
                
                # 3. SIMPAN SEMUA HASIL PENTING KE "MEMORI"
                st.session_state.results['df_valid'] = df_valid
                st.session_state.results['df_raw'] = df_raw
                st.session_state.results['X_scaled'] = X_scaled
                st.session_state.results['labels'] = labels
                st.session_state.results['mode'] = mode
                st.session_state.results['year'] = year # <-- TAMBAHAN PENTING
                st.session_state.results['selected_features_info'] = selected_features 
                
                st.session_state.run_clustering = False
                st.session_state.results_ready = True # Flag baru untuk menandakan hasil siap
                st.experimental_rerun() # Paksa rerun untuk menampilkan hasil dengan bersih
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat clustering: {e}"); st.exception(e)
                st.session_state.run_clustering = False

# --- Tampilkan hasil dari "memori" jika ada ---
if 'results_ready' in st.session_state and st.session_state.results_ready:
    df_valid = st.session_state.results['df_valid']
    df_raw = st.session_state.results['df_raw']
    X_scaled = st.session_state.results['X_scaled']
    labels = st.session_state.results['labels']
    result_mode = st.session_state.results['mode']
    selected_features_info = st.session_state.results['selected_features_info']

    st.header("🎉 Hasil Utama Clustering")
    st.info(f"Analisis dilakukan berdasarkan fitur: **{', '.join(selected_features_info)}**")

    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.subheader("Tabel Hasil Cluster")
        st.dataframe(df_valid[['Wilayah', 'Cluster', 'Kategori']])
    with col2:
        st.subheader("Jumlah Anggota per Cluster")
        counts = df_valid['Kategori'].value_counts()
        st.bar_chart(counts)
    
    # ===============================================================
    # UPDATE BAGIAN BOX PLOT
    # ===============================================================
    st.subheader("📦 Karakteristik Cluster (Box Plot)")

    cols_to_plot = []
    plot_title = ""
    plot_ylabel = ""
    
    if result_mode == 'Keseluruhan':
        st.info("Menampilkan distribusi **rata-rata** setiap fitur di dalam masing-masing cluster.")
        plot_title = "Perbandingan Karakteristik Rata-rata Fitur antar Cluster"
        plot_ylabel = "Nilai Rata-rata"
        # Hitung rata-rata untuk setiap fitur yang dipilih
        for feature in selected_features_info:
            yearly_cols = [c for c in df_valid.columns if c.lower().startswith(feature.lower() + "_")]
            if yearly_cols:
                avg_col_name = f"{feature}_Avg"
                df_valid[avg_col_name] = df_valid[yearly_cols].mean(axis=1)
                cols_to_plot.append(avg_col_name)
    else: # Mode 'Per Tahun'
        selected_year = st.session_state.results.get('year')
        st.info(f"Menampilkan distribusi nilai **aktual** untuk tahun **{selected_year}**.")
        plot_title = f"Perbandingan Karakteristik Fitur untuk Tahun {selected_year}"
        plot_ylabel = "Nilai Aktual"
        # Gunakan kolom aktual untuk tahun yang dipilih
        cols_to_plot = [f"{f}_{selected_year}" for f in selected_features_info if f"{f}_{selected_year}" in df_valid.columns]

    if cols_to_plot:
        # Mapping untuk judul plot yang lebih deskriptif
        title_mapping = {
            'Nelayan_Avg': 'Rata-rata Nelayan',
            'Volume_Avg': 'Rata-rata Volume',
            'Produksi_Avg': 'Rata-rata Produksi',
            'Konsumsi_Avg': 'Rata-rata Konsumsi',
        }
        
        n_vars = len(cols_to_plot)
        n_cols = 2  # Atur 2 plot per baris
        n_rows = (n_vars + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(8 * n_cols, 6 * n_rows), squeeze=False)
        axes = axes.flatten()
        
        # Urutkan kategori untuk plotting yang konsisten (misalnya: Rendah, Sedang, Tinggi)
        # Ini penting agar plot tidak acak urutannya
        try:
            category_order = ['Outlier', 'Sangat Rendah', 'Rendah', 'Cukup Rendah', 'Sedang', 'Cukup Tinggi', 'Tinggi', 'Sangat Tinggi']
            ordered_categories = [cat for cat in category_order if cat in df_valid['Kategori'].unique()]
            if not ordered_categories: # Fallback jika tidak ada kategori yang cocok
                ordered_categories = sorted(df_valid['Kategori'].unique())
        except Exception:
            ordered_categories = sorted(df_valid['Kategori'].unique())

        for i, var in enumerate(cols_to_plot):
            ax = axes[i]
            # Dapatkan judul yang lebih baik dari mapping, atau gunakan nama kolom jika tidak ada
            # Juga hapus '_Avg' atau '_YYYY' untuk judul yang lebih bersih
            clean_title = title_mapping.get(var, var.rsplit('_', 1)[0])
            
            sns.boxplot(data=df_valid, x="Kategori", y=var, ax=ax, order=ordered_categories, palette="viridis")
            ax.set_title(f'Distribusi {clean_title}', fontsize=16, fontweight='bold')
            ax.set_xlabel("Kategori Cluster", fontsize=12)
            ax.set_ylabel(plot_ylabel, fontsize=12)
            ax.tick_params(axis='x', rotation=45, labelsize=11)
            ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Sembunyikan subplot yang tidak terpakai
        for j in range(n_vars, len(axes)):
            fig.delaxes(axes[j])

        fig.suptitle(plot_title, y=1.03, fontsize=22, fontweight='bold')
        plt.tight_layout(pad=4.0, h_pad=5.0) # Beri lebih banyak ruang antar plot
        st.pyplot(fig)
    else:
        st.warning("Tidak ada fitur yang dapat divisualisasikan untuk box plot.")
    # ===============================================================
    
    st.subheader("🗺️ Peta Sebaran dan Karakteristik Cluster")
    if "Latitude" in df_valid.columns and "Longitude" in df_valid.columns:
        df_map = df_valid.dropna(subset=['Latitude', 'Longitude'])
        if not df_map.empty:
            m = folium.Map(location=[df_map["Latitude"].mean(), df_map["Longitude"].mean()], zoom_start=5)
            for _, row in df_map.iterrows():
                popup_html = f"<b>{row.get('Wilayah', 'N/A')}</b><br><b>Kategori: {row.get('Kategori', 'N/A')}</b>"
                folium.Marker(location=[row['Latitude'], row['Longitude']],
                              popup=folium.Popup(popup_html, max_width=300),
                              icon=folium.Icon(color=COLOR_PALETTE[int(row['Cluster']) % len(COLOR_PALETTE)], icon='ship', prefix='fa')).add_to(m)
            folium_static(m, width=1200, height=500)
        else:
            st.warning("Data tidak memiliki nilai Latitude/Longitude yang valid untuk ditampilkan di peta.")
    else:
        st.warning("Kolom 'Latitude' dan 'Longitude' tidak ditemukan di dataset Anda.")

    st.subheader("⚙️ Evaluasi Kualitas Clustering")
    n_unique_clusters = df_valid[df_valid['Cluster'] != -1]['Cluster'].nunique()
    if n_unique_clusters >= 2:
        valid_mask = labels != -1
        sil_score = silhouette_score(X_scaled[valid_mask], labels[valid_mask])
        dbi_score = davies_bouldin_score(X_scaled[valid_mask], labels[valid_mask])
        
        col1_eval, col2_eval = st.columns(2)
        col1_eval.metric("Silhouette Score", f"{sil_score:.3f}", help="Mengukur seberapa mirip sebuah objek dengan clusternya sendiri dibandingkan dengan cluster lain. Semakin mendekati 1, semakin baik.")
        col2_eval.metric("Davies-Bouldin Index", f"{dbi_score:.3f}", help="Mengukur rata-rata 'kemiripan' antara setiap cluster dengan cluster yang paling mirip dengannya. Semakin mendekati 0, semakin baik.")

        plot_col1, plot_col2 = st.columns(2)
        with plot_col1:
            st.subheader("📊 Visualisasi Silhouette")
            fig, ax = plt.subplots(figsize=(10, 8))
            sample_silhouette_values = silhouette_samples(X_scaled[valid_mask], labels[valid_mask])
            y_lower = 10
            unique_labels = np.unique(labels[valid_mask])
            for i in unique_labels:
                ith_cluster_silhouette_values = sample_silhouette_values[labels[valid_mask] == i]
                ith_cluster_silhouette_values.sort()
                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                y_upper = y_lower + size_cluster_i
                color = cm.nipy_spectral(float(i) / n_unique_clusters)
                ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values, facecolor=color, edgecolor=color, alpha=0.7)
                ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
                y_lower = y_upper + 10
            ax.set_title("Visualisasi Silhouette untuk Setiap Cluster")
            ax.set_xlabel("Nilai Koefisien Silhouette")
            ax.set_ylabel("Label Cluster")
            ax.axvline(x=sil_score, color="red", linestyle="--")
            ax.set_yticks([])
            ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
            st.pyplot(fig)

        with plot_col2:
            st.subheader("🌀 Plot PCA 2D")
            pca = PCA(n_components=2); X2 = pca.fit_transform(X_scaled)
            fig, ax = plt.subplots(figsize=(10, 8)); 
            sns.scatterplot(x=X2[:,0], y=X2[:,1], hue=df_valid['Kategori'], ax=ax, palette='viridis', s=70, style=df_valid['Kategori'], markers=True)
            ax.set_xlabel("Principal Component 1"); ax.set_ylabel("Principal Component 2"); ax.set_title("Visualisasi Cluster dalam Ruang 2D (PCA)")
            ax.legend(title="Kategori Cluster")
            st.pyplot(fig)
    else:
        st.warning("Evaluasi dan Plot PCA tidak dapat ditampilkan karena hanya 1 cluster yang terbentuk (atau semua data adalah outlier).")

    st.markdown("---")
    
    st.subheader("🏆 Peringkat Lokasi Teratas")
    peringkat_options = available_features if 'available_features' in locals() else FEATURE_PRODUKSI
    selected_feature_top = st.selectbox("Pilih Fitur untuk Peringkat:", peringkat_options, key='top_feature')
    n_top = st.slider("Jumlah Lokasi:", 5, 20, 10)
    top_cols = sorted([c for c in df_raw.columns if c.lower().startswith(selected_feature_top.lower() + "_")])
    if top_cols:
        df_raw['average'] = df_raw[top_cols].mean(axis=1).fillna(0)
        df_top = df_raw.nlargest(n_top, 'average')
        fig, ax = plt.subplots(figsize=(10, 8)); 
        sns.barplot(data=df_top, y='Wilayah', x='average', palette='viridis', ax=ax)
        ax.set_title(f"Top {n_top} Lokasi - Berdasarkan Rata-rata {selected_feature_top}")
        st.pyplot(fig)
        
    if result_mode == 'Keseluruhan':
        st.subheader("📈 Tren Tahunan 10 Lokasi Teratas")
        trend_options = available_features if 'available_features' in locals() else FEATURE_PRODUKSI
        selected_feature_trend = st.selectbox("Pilih Fitur untuk Tren:", trend_options, key='trend_feature')
        trend_cols = sorted([c for c in df_raw.columns if c.lower().startswith(selected_feature_trend.lower() + "_")])
        if trend_cols:
            df_raw['average_trend'] = df_raw[trend_cols].mean(axis=1).fillna(0)
            df_top_trend = df_raw.nlargest(10, 'average_trend')
            years = [int(re.search(r'(\d{4})', c).group(1)) for c in trend_cols]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            for _, row in df_top_trend.iterrows():
                ax.plot(years, row[trend_cols].values, marker='o', linestyle='-', label=row['Wilayah'])
            ax.set_title(f"Tren Tahunan 10 Lokasi Teratas untuk Fitur '{selected_feature_trend}'")
            ax.legend(title='Lokasi', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, linestyle='--')
            st.pyplot(fig)

# Jika tidak ada file, tampilkan pesan awal
else:
    st.info("Selamat datang! Silakan upload file Excel Anda di sidebar untuk memulai analisis.")
    if 'results_ready' in st.session_state:
        del st.session_state.results_ready # Hapus flag jika file di-unload

