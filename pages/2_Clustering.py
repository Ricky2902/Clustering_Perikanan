import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from io import BytesIO
from sklearn.preprocessing import  MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, silhouette_samples
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages 
from matplotlib.ticker import ScalarFormatter
import seaborn as sns
import folium
from streamlit_folium import st_folium
import re
from openpyxl.drawing.image import Image as OpenpyxlImage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from PIL import Image
from datetime import datetime

pd.options.display.float_format = '{:,.2f}'.format
np.set_printoptions(suppress=True)

# =============================================================================
# IMPORT UTILS
# =============================================================================
# Pastikan Anda memiliki file utils.py di folder yang sama

from utils import (
        initialize_clustering_model,
        categorize_clusters,
        FEATURE_PRODUKSI,
        CLUSTER_COLORS,
        CATEGORY_COLORS)

st.set_page_config(page_title="CLUSTER | FISHERY CLUSTER", page_icon="assets/logo1.png", layout="wide")

# === GANTI SELURUH BLOK CSS ANDA DENGAN YANG INI ===
st.markdown("""
<style>
    /* --- 1. SIDEBAR (Biru Gelap) --- */
    [data-testid="stSidebar"] {
        background-color: #00427A !important; /* Biru Laut Gelap */
    }

    /* --- 2. SEMUA TEKS SIDEBAR (Putih) --- */
    /* Ini akan menargetkan header, label, dan semua teks lainnya */
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] li {
        color: #FFFFFF !important;
    }
    
    /* Efek hover link navigasi (opsional) */
    [data-testid="stSidebar"] a:hover {
        color: #E0F7FA !important; /* Biru muda saat di-hover */
    }
    
    /* --- 3. BACKGROUND WIDGET (Biru Gelap) --- */
    /* Ini agar teks putih di dalam widget bisa terbaca */
    
    /* Target st.selectbox */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #00315C !important; /* Biru lebih gelap */
        border-color: #005A9C !important;
    }
    
    /* Target st.multiselect */
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background-color: #00315C !important; /* Biru lebih gelap */
        border-color: #005A9C !important;
    }
    
    /* Target tag di st.multiselect (cth: "Konsumsi") */
    [data-testid="stSidebar"] .st-emotion-cache-p5msec {
         background-color: #005A9C !important; /* Biru medium */
         color: #FFFFFF !important;
         border-radius: 4px !important;
    }
    
    /* Target area 'Drag and drop' st.file_uploader */
    [data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] {
        background-color: #00315C !important; /* Biru lebih gelap */
        border-color: #005A9C !important;
    }
    
    /* Target tombol 'Browse files' (agar kontras) */
    [data-testid="stSidebar"] .st-emotion-cache-1jicfl2 {
        background-color: #E0F7FA !important; /* Latar biru muda */
        color: #00315C !important; /* Teks biru gelap */
        border: none !important;
    }
    /* Hover tombol 'Browse files' */
    [data-testid="stSidebar"] .st-emotion-cache-1jicfl2:hover {
        background-color: #FFFFFF !important; /* Latar putih */
        color: #00315C !important; /* Teks biru gelap */
    }


    /* --- 4. KONTEN UTAMA (Biru Langit, Teks Hitam) --- */
    
    /* Latar belakang konten utama */
    [data-testid="stAppViewContainer"] {
        background-color: #E0F7FA !important;
    }
    
    # /* Target semua teks di konten utama jadi HITAM */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] h4,
    [data-testid="stAppViewContainer"] h5,
    [data-testid="stAppViewContainer"] h6 {
        color: #000000 !important; 
    }
</style>
""", unsafe_allow_html=True)
# === AKHIR BLOK CSS ===

# =============================================================================
# Fungsi Download Excel
# =============================================================================
# Tambahkan fungsi helper ini di bagian atas file (setelah imports)
# GANTI FUNGSI LAMA ANDA DENGAN YANG INI

def convert_dfs_to_multisheet_excel(sheets_dict, chart_figure=None, chart_sheet_name=None):
    """
    Mengkonversi kamus DataFrame DAN sebuah chart Matplotlib
    menjadi satu file Excel multi-sheet.
    
    sheets_dict: {'NamaSheet1': df1, 'NamaSheet2': df2}
    chart_figure: Objek Matplotlib Figure (contoh: fig_bar)
    chart_sheet_name: Nama untuk sheet chart (contoh: 'Grafik')
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # --- Bagian 1: Tulis semua DataFrame ---
        for sheet_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # --- Bagian 2: Tulis chart jika ada ---
        if chart_figure is not None and chart_sheet_name is not None:
            
            # Buat sheet baru yang kosong untuk chart
            # (Kita buat DF kosong agar sheet-nya terbuat)
            pd.DataFrame().to_excel(writer, sheet_name=chart_sheet_name)
            worksheet = writer.sheets[chart_sheet_name]

            # Simpan chart ke buffer memori sebagai gambar PNG
            img_buffer = BytesIO()
            # bbox_inches='tight' untuk memotong whitespace berlebih
            chart_figure.savefig(img_buffer, format='png', bbox_inches='tight')
            
            # Pindahkan pointer buffer ke awal agar bisa dibaca
            img_buffer.seek(0) 
            
            # Buat objek gambar openpyxl dari buffer
            img = OpenpyxlImage(img_buffer)
            
            # Tambahkan gambar ke worksheet di sel 'A1'
            worksheet.add_image(img, 'A1')

    # Ambil data biner final dari file Excel di memori
    processed_data = output.getvalue()
    return processed_data

# =============================================================================
# Fungsi Download PDF
# =============================================================================

def create_multi_page_pdf(figures_list, pdf_file_name="report.pdf"):
    """
    Mengkonversi daftar objek Figure Matplotlib menjadi satu file PDF multi-halaman.
    figures_list: Daftar objek Figure Matplotlib.
    """
    pdf_buffer = BytesIO()
    with PdfPages(pdf_buffer) as pdf:
        for fig in figures_list:
            if fig is not None:
                pdf.savefig(fig, bbox_inches='tight') # Simpan setiap figure ke halaman baru
                plt.close(fig) # Tutup figure setelah disimpan untuk membebaskan memori
    pdf_buffer.seek(0)
    return pdf_buffer

# Fungsi helper baru untuk "memfoto" peta folium
def get_folium_map_as_figure(map_object):
    """
    Menyimpan objek Peta Folium sebagai file HTML sementara,
    merendernya dengan Selenium, mengambil screenshot, 
    dan mengembalikannya sebagai objek Figure Matplotlib.
    
    PENTING: Membutuhkan instalasi:
    pip install selenium webdriver-manager pillow
    
    Dan Google Chrome harus terinstal di mesin.
    """
    
    # 1. Simpan peta ke file HTML sementara
    temp_html = "temp_map_for_pdf.html"
    map_object.save(temp_html)
    
    # 2. Dapatkan path absolut untuk browser
    full_path = 'file://' + os.path.abspath(temp_html)

    # 3. Siapkan opsi browser (headless = tanpa membuka jendela)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Atur ukuran jendela yang cukup besar untuk peta Anda
    options.add_argument('--window-size=1000,700') 
    
    driver = None
    try:
        # === PERUBAHAN DI SINI ===
        # Biarkan Service() kosong. Selenium akan otomatis
        # mengunduh driver yang TEPAT (v141).
        service = Service() 
        # =========================
        
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        st.error(f"Gagal memulai Selenium/WebDriver: {e}")
        st.error("Pastikan Google Chrome terinstal. Coba restart aplikasi setelah instalasi.")
        if os.path.exists(temp_html):
             os.remove(temp_html)
        return None

    try:
        # 5. Ambil screenshot
        driver.get(full_path)
        # Beri waktu (detik) agar peta selesai di-render
        time.sleep(1.5) 
        
        png_data = driver.get_screenshot_as_png()
        
    except Exception as e:
        st.error(f"Gagal mengambil screenshot peta: {e}")
        return None
        
    finally:
        # 6. Selalu tutup driver dan hapus file sementara
        if driver:
            driver.quit()
        if os.path.exists(temp_html):
            os.remove(temp_html)

    # 7. Konversi screenshot (PNG) ke Figure Matplotlib
    try:
        img = Image.open(BytesIO(png_data))
        
        # Buat figure matplotlib untuk menampung gambar
        # Sesuaikan figsize agar proporsional (10:7)
        fig_map, ax_map = plt.subplots(figsize=(20, 15)) 
        ax_map.imshow(img)
        ax_map.axis('off') # Sembunyikan sumbu X/Y
        
        return fig_map
        
    except Exception as e:
        st.error(f"Gagal mengkonversi screenshot peta ke figure: {e}")
        return None
# =================================================================================
# PENGATURAN HALAMAN DAN "MEMORI" (SESSION STATE)
# =================================================================================

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

    params = {}
    mode, year, year_range = None, None, None
    selected_features = []
    available_features = []

    if uploaded_file:
        mode = st.selectbox('Mode Analisis:', ['Range Tahun', 'Per Tahun'],
                            help="Pilih 'Range Tahun' untuk menganalisis beberapa tahun, atau 'Per Tahun' untuk fokus pada satu tahun spesifik.")

        try:
            df_temp = pd.read_excel(uploaded_file)
            df_temp.columns = [c.strip().title() for c in df_temp.columns]

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
                    default=available_features,
                    help="Pilih satu atau lebih fitur yang akan digunakan sebagai dasar pengelompokan."
                )
            else:
                st.warning("Tidak ada kolom fitur berformat 'NamaFitur_Tahun' yang ditemukan di file Anda.")

            years_available = set()
            for col in df_temp.columns:
                match = re.search(r'_(\d{4})$', col)
                if match:
                    try:
                        years_available.add(int(match.group(1)))
                    except ValueError:
                        pass
            years_available = sorted(list(years_available))

            if not years_available:
                st.warning("Tidak ada kolom berformat _YYYY yang valid ditemukan.")
            else:
                if mode == 'Per Tahun':
                    year = st.selectbox('Pilih Tahun:', years_available, help="Pilih tahun untuk analisis per tahun.")
                else:
                    default_range = (years_available[0], years_available[-1])
                    year_range = st.select_slider(
                        'Pilih Rentang Tahun (Range):',
                        options=years_available,
                        value=default_range,
                        help="Pilih dari tahun berapa sampai tahun berapa data akan dianalisis (rata-rata)."
                    )
        except Exception as e:
            st.error(f"Gagal membaca atau memproses file: {e}")
            st.stop()

        if available_features:
            st.subheader("Metode & Parameter")
            method = st.selectbox('Metode Clustering:', ['K-Means', 'BIRCH', 'OPTICS'])

            if method in ['K-Means', 'BIRCH']:
                params['n_clusters'] = st.slider('Jumlah Cluster (K):', min_value=2, max_value=7, value=3, help="Tentukan jumlah kelompok yang ingin dibentuk.")
            if method == 'OPTICS':
                params['min_samples'] = st.slider('Minimum Points (MinPts):', min_value=5, max_value=15, value=5, help="Jumlah minimum tetangga...")

            with st.expander("Parameter Lanjutan (Opsional)"):
                if method == 'BIRCH':
                    # PERBAIKAN: Menggunakan keyword arguments
                    params['threshold'] = st.number_input('Threshold:', min_value=0.1, max_value=1.0, value=0.1, step=0.1, help="Radius maksimum...")
                    params['branching_factor'] = st.number_input('Branching Factor:', min_value=2, max_value=100, value=50, help="Jumlah maksimum sub-cluster...")
                if method == 'OPTICS':
                    use_eps = st.checkbox("Tentukan Epsilon (eps) secara manual")
                    if use_eps:
                        # PERBAIKAN: Menggunakan keyword arguments
                        params['eps'] = st.number_input('Epsilon (eps):', min_value=0.1, max_value=5.0, value=2.0, step=0.1, help="Jarak maksimum...")
                    else:
                        params['eps'] = None

            if st.button('🚀 Mulai Clustering'):
                if not selected_features:
                    st.warning("Harap pilih setidaknya satu fitur untuk clustering.")
                else:
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
assets_path = 'files'
if os.path.exists(assets_path):
    with col2:
        template_file = "Template_Dataset.xlsx"
        template_path = os.path.join(assets_path, template_file)
        if os.path.exists(template_path):
            try:
                with open(template_path, "rb") as f:
                    st.download_button(label="📄 Download Template Dataset", data=f.read(), file_name=template_file)
            except Exception as e:
                st.warning(f"Gagal memuat template: {e}")
        else:
            st.caption("Template tidak ditemukan.")
    with col1:
        dataset_file = "Dataset_tangkaplaut.xlsx"
        dataset_path = os.path.join(assets_path, dataset_file)
        if os.path.exists(dataset_path):
            try:
                with open(dataset_path, "rb") as f:
                    st.download_button(label="💾 Download Contoh Dataset", data=f.read(), file_name="dataset_Tangkap_Laut_Dan_Konsumsi.xlsx")
            except Exception as e:
                st.warning(f"Gagal memuat contoh dataset: {e}")
        else:
            st.caption("Contoh dataset tidak ditemukan.")
    with col3:
        guide_file = "Buku_panduan.pptx"
        guide_path = os.path.join(assets_path, guide_file)
        if os.path.exists(guide_path):
            try:
                with open(guide_path, "rb") as f:
                    st.download_button(label="📘 Download Buku Panduan", data=f.read(), file_name=guide_file)
            except Exception as e:
                st.warning(f"Gagal memuat panduan: {e}")
        else:
            st.caption("Buku panduan tidak ditemukan.")
else:
    st.warning(f"Folder '{assets_path}' tidak ditemukan. Tombol download tidak akan muncul.")

st.markdown("---")

if uploaded_file:
    try:
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = [c.strip().title() for c in df_raw.columns]
    except Exception as e:
        st.error(f"Gagal membaca file Excel: {e}")
        st.stop()

    if st.session_state.run_clustering:
        with st.spinner('⏳ Sedang memproses clustering... Harap tunggu...'):
            try:
                if not selected_features:
                    st.error("❌ Harap pilih minimal satu fitur di sidebar untuk memulai analisis."); st.stop()

                feature_cols = []
                df_process = df_raw.copy()

                if mode == 'Range Tahun':
                    if year_range is None:
                         st.error("Rentang tahun tidak terpilih untuk mode 'Range Tahun'."); st.stop()
                    start_year, end_year = int(year_range[0]), int(year_range[1])
                    years_in_range = list(range(start_year, end_year + 1))

                    for feature in selected_features:
                        cols_yearly = [f"{feature}_{y}" for y in years_in_range if f"{feature}_{y}" in df_process.columns]
                        if cols_yearly:
                            avg_col_name = f"{feature}_Avg"
                            df_process[avg_col_name] = df_process[cols_yearly].apply(pd.to_numeric, errors='coerce').mean(axis=1)
                            feature_cols.append(avg_col_name)

                else: # Mode Per Tahun
                    if year is None:
                        st.error("Tahun tidak terpilih untuk mode 'Per Tahun'."); st.stop()
                    for feature in selected_features:
                        col_name_yearly = f"{feature}_{year}"
                        if col_name_yearly in df_process.columns:
                            feature_cols.append(col_name_yearly)

                if not feature_cols:
                    st.error(f'❌ Tidak ada kolom fitur yang cocok ditemukan.'); st.stop()

                X_df = df_process[feature_cols].apply(pd.to_numeric, errors='coerce')
                mask_valid_rows = X_df.dropna().index
                
                min_samples_needed = params.get('n_clusters', 2) if method != 'OPTICS' else params.get('min_samples', 2)
                if len(mask_valid_rows) < min_samples_needed:
                    st.error(f"❌ Data valid ({len(mask_valid_rows)} baris) tidak cukup untuk clustering (membutuhkan min. {min_samples_needed})."); st.stop()

                df_valid = df_process.loc[mask_valid_rows].reset_index(drop=True)
                X_valid = X_df.loc[mask_valid_rows].reset_index(drop=True)

                scaler = MinMaxScaler()
                X_scaled = scaler.fit_transform(X_valid)

                model = initialize_clustering_model(method, params)
                if model is None:
                    st.error(f"Metode clustering '{method}' tidak dikenali."); st.stop()
                
                model.fit(X_scaled)
                labels = getattr(model, "labels_", np.array([-1] * len(X_scaled)))

                df_valid["Cluster"] = labels
                df_valid = categorize_clusters(df_valid)
                
                if 'Kategori' not in df_valid.columns:
                    df_valid['Kategori'] = 'Cluster ' + df_valid['Cluster'].astype(str)
                    df_valid['Kategori'] = df_valid['Kategori'].replace('Cluster -1', 'Outlier')


                st.session_state.results['df_valid'] = df_valid
                st.session_state.results['df_raw'] = df_raw
                st.session_state.results['X_scaled'] = X_scaled
                st.session_state.results['labels'] = labels
                st.session_state.results['mode'] = mode
                st.session_state.results['year'] = year
                st.session_state.results['year_range'] = year_range
                st.session_state.results['selected_features_info'] = selected_features
                st.session_state.results['feature_cols_used'] = feature_cols
                st.session_state.results['available_features'] = available_features

                st.session_state.run_clustering = False
                st.session_state.results_ready = True
                st.success("✅ Clustering selesai!")
                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"Terjadi kesalahan saat proses clustering: {e}")
                st.exception(e)
                st.session_state.run_clustering = False

if 'results_ready' in st.session_state and st.session_state.results_ready:
    df_valid = st.session_state.results.get('df_valid')
    df_raw = st.session_state.results.get('df_raw')
    X_scaled = st.session_state.results.get('X_scaled')
    labels = st.session_state.results.get('labels')
    result_mode = st.session_state.results.get('mode')
    selected_features_info = st.session_state.results.get('selected_features_info', [])
    feature_cols_used = st.session_state.results.get('feature_cols_used', [])
    available_features = st.session_state.results.get('available_features', [])

    if df_valid is None or X_scaled is None or labels is None:
        st.error("Hasil clustering tidak ditemukan. Coba jalankan ulang.")
        st.stop()

    st.header("📋 Hasil Utama Clustering")
    st.info(f"Analisis berdasarkan fitur: **{', '.join(selected_features_info)}** (Mode: {result_mode})")

    # (Asumsi kode ini ada di dalam 'if 'Kategori' in df_valid.columns:')

    # =================================================================
    # --- [PERUBAHAN] BUAT WADAH KOSONG UNTUK SEMUA SHEET EXCEL ---
    excel_sheets_to_download = {}
    # =================================================================

    # --- 1. TABEL HASIL CLUSTERING UTAMA ---
    st.subheader("Tabel Hasil Clustering Utama")

    # --- LOGIKA BARU UNTUK MEMILIH KOLOM FITUR TAMPILAN ---
    feature_cols_to_display = [] 

    if result_mode == 'Range Tahun':
        st.markdown("Menampilkan **data tahunan individual** (Clustering dilakukan berdasarkan rata-rata).")
        year_range_display = st.session_state.results.get('year_range')
        if year_range_display:
            start_yr, end_yr = int(year_range_display[0]), int(year_range_display[1])
            years_in_r = list(range(start_yr, end_yr + 1))
            
            for feature in selected_features_info:
                for yr in years_in_r:
                    col_name = f"{feature}_{yr}"
                    if col_name in df_valid.columns: 
                        feature_cols_to_display.append(col_name)
            feature_cols_to_display.sort() 
        else:
            st.warning("Rentang tahun tidak ditemukan, fallback ke kolom clustering.")
            feature_cols_to_display = feature_cols_used 

    else: # Mode Per Tahun
        selected_year_display = st.session_state.results.get('year')
        if selected_year_display:
            st.markdown(f"Menampilkan **nilai fitur aktual tahun {selected_year_display}**.")
        feature_cols_to_display = feature_cols_used
    # --- AKHIR LOGIKA BARU ---

    # Gunakan feature_cols_to_display yang baru
    cols_to_show_main = ['Wilayah'] + feature_cols_to_display + ['Kategori']
    cols_to_show_main = [col for col in cols_to_show_main if col in df_valid.columns] 

    # (Kita asumsikan 'if 'Kategori' in df_valid.columns:' sudah TRUE dari luar)

    # 1. Definisikan DataFrame yang akan ditampilkan DAN di-download
    df_to_download_main = df_valid[cols_to_show_main]

    # 2. Tampilkan tabel di aplikasi
    st.dataframe(df_to_download_main, height=300)

    # =================================================================
    # --- [PERUBAHAN] Simpan DataFrame ini ke wadah ---
    excel_sheets_to_download['Hasil_Utama'] = df_to_download_main
    # --- Tombol download yang sebelumnya ada di sini SEKARANG DIHAPUS ---
    # =================================================================


    # --- 2. TABEL ANGGOTA PER CLUSTER ---
    st.subheader("Tabel Anggota per Cluster")

    # Urutkan kategori (Outlier terakhir)
    unique_categories = sorted([c for c in df_valid['Kategori'].unique() if c != 'Outlier'])
    if 'Outlier' in df_valid['Kategori'].unique():
        unique_categories.append('Outlier')

    with st.expander("Lihat Anggota Setiap Cluster", expanded=False):
        for kategori_name in unique_categories:
            
            df_cluster = df_valid[df_valid['Kategori'] == kategori_name][['Wilayah', 'Kategori']] 

            st.markdown(f"**Anggota {kategori_name}**") 
            st.dataframe(df_cluster, hide_index=True, use_container_width=True)
            st.caption(f"Jumlah anggota: {len(df_cluster)}")
            st.write("")

            # =================================================================
            # --- [PERUBAHAN] Simpan setiap DataFrame cluster ke wadah ---
            sheet_name = f"Anggota {kategori_name}"
            excel_sheets_to_download[sheet_name] = df_cluster
            # =================================================================

    st.markdown("---")

    # --- 3. GRAFIK JUMLAH ANGGOTA ---
    st.subheader("📊 Jumlah Anggota per Kategori Cluster")

    # =================================================================
    # --- [PERUBAHAN] Inisialisasi fig_bar sebagai None ---
    fig_bar = None 
    # =================================================================

    counts = df_valid['Kategori'].value_counts()
    # Urutkan kategori untuk grafik (Outlier terakhir)
    ordered_categories_chart = sorted([c for c in counts.index if c != 'Outlier'])
    if 'Outlier' in counts.index:
        ordered_categories_chart.append('Outlier')
    counts = counts.reindex(ordered_categories_chart).dropna()

    bar_colors = [CATEGORY_COLORS.get(cat, '#999999') for cat in counts.index] 

    # ===> Di sini 'fig_bar' akan dibuat <===
    fig_bar, ax_bar = plt.subplots(figsize=(10, 5)) 
    bars = ax_bar.bar(counts.index, counts.values, color=bar_colors)
    ax_bar.bar_label(bars, fmt='%d')
    ax_bar.set_ylabel("Jumlah Anggota")
    ax_bar.set_xlabel("Kategori Cluster")
    plt.xticks(rotation=45, ha='right')
    ax_bar.grid(axis='y', linestyle='--', alpha=0.7)

    # Tampilkan di Streamlit
    st.pyplot(fig_bar) 
    plt.close(fig_bar)


    st.markdown("---")

    # =================================================================
    # --- [PERUBAHAN] TAMBAHKAN SATU TOMBOL DOWNLOAD GABUNGAN DI SINI ---

    st.subheader("Download Laporan Lengkap")
    st.markdown("Download semua tabel dan visualisasi dalam satu file Excel.")

    # Panggil fungsi helper baru kita DENGAN TAMBAHAN 'fig_bar'
    excel_data_gabungan = convert_dfs_to_multisheet_excel(
        sheets_dict=excel_sheets_to_download,  # Kamus DataFrame kita
        chart_figure=fig_bar,                  # <-- TAMBAHAN INI
        chart_sheet_name='Grafik Anggota'      # <-- TAMBAHAN INI
    )

    st.download_button(
        label="📥 Download Laporan Lengkap (.xlsx)",
        data=excel_data_gabungan,
        file_name='Laporan_Hasil_Clustering_Lengkap.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheet.sheet'
    )
    # =================================================================
    st.markdown("---")

    # === [PERUBAHAN] Inisialisasi daftar gabungan untuk SEMUA gambar PDF ===
# (Letakkan ini sebelum Bagian 4, atau di awal blok kode hasil cluster)
    figures_for_pdf = [] 
    # ======================================================================

    # --- 4. BOX PLOT ---
    st.subheader("Karakteristik Cluster (Box Plot)")
    cols_to_plot_all = []

    # ... (Seluruh logika 'if result_mode == 'Range Tahun':' Anda tetap sama) ...
    if result_mode == 'Range Tahun':
        year_range_box = st.session_state.results.get('year_range')
        start_yr, end_yr = None, None
        if year_range_box:
            start_yr, end_yr = int(year_range_box[0]), int(year_range_box[1])
            st.info(f"Distribusi nilai aktual per fitur ({start_yr}-{end_yr}).")
            years_in_r = list(range(start_yr, end_yr + 1))
            for feature in selected_features_info:
                for yr in years_in_r:
                    col = f"{feature}_{yr}"
                    if col in df_valid.columns: 
                        cols_to_plot_all.append(col)
            cols_to_plot_all.sort()
    else:
        selected_year_plot = st.session_state.results.get('year')
        if selected_year_plot:
            st.info(f"Distribusi nilai aktual ({selected_year_plot}).")
            cols_to_plot_all = [f"{f}_{selected_year_plot}" for f in selected_features_info if f"{f}_{selected_year_plot}" in df_valid.columns]

    # ... (Seluruh logika 'title_mapping', 'FEATURE_UNITS', 'ordered_categories' Anda tetap sama) ...
    title_mapping = {'Nilai': 'Nilai Produksi', 'Produksi': 'Nilai Produksi', 'Nelayan': 'Nelayan', 'Volume': 'Volume', 'Konsumsi': 'Konsumsi'}
    for f in selected_features_info:
        if f not in title_mapping: 
            title_mapping[f] = f

    FEATURE_UNITS = {'Volume': 'Ton', 'Nilai': 'Rupiah (Rp)', 'Produksi': 'Rupiah (Rp)', 'Nelayan': 'Orang', 'Konsumsi': 'Kg/Kapita'}
    default_unit = "Nilai"

    ordered_categories = sorted([c for c in df_valid['Kategori'].unique() if c != 'Outlier'])
    if 'Outlier' in df_valid['Kategori'].unique():
        ordered_categories.append('Outlier')


    if cols_to_plot_all and ordered_categories:
        if result_mode == 'Range Tahun':
            st.markdown("*(Perbandingan tahunan untuk setiap fitur)*")
            base_features_to_plot = sorted(list(set(col.split('_')[0] for col in cols_to_plot_all)))

            for base_feature in base_features_to_plot:
                cols_for_this_feature = [col for col in cols_to_plot_all if col.startswith(base_feature + "_")]

                if cols_for_this_feature:
                    clean_base_feature_name = title_mapping.get(base_feature, base_feature)
                    st.markdown(f"#### Fitur: **{clean_base_feature_name}**")

                    n_vars = len(cols_for_this_feature)
                    n_cols = 1 if n_vars == 1 else 2
                    n_rows = (n_vars + n_cols - 1) // n_cols

                    fig_range, axes_range = plt.subplots(n_rows, n_cols, figsize=(8 * n_cols, 7 * n_rows), squeeze=False)
                    axes_range = axes_range.flatten()
                    current_unit = FEATURE_UNITS.get(base_feature, default_unit)

                    for i, var in enumerate(cols_for_this_feature):
                        # ... (Semua logika plot boxplot Anda tetap sama) ...
                        ax = axes_range[i]
                        year_name_plot = ""
                        match_year = re.search(r'_(\d{4})$', var)
                        if match_year: 
                            year_name_plot = f" ({match_year.group(1)})"
                        plot_subplot_title = f"{clean_base_feature_name}{year_name_plot}"

                        if 'Kategori' in df_valid.columns:
                            sns.boxplot(data=df_valid, x="Kategori", y=var, ax=ax, order=ordered_categories, palette=CATEGORY_COLORS)
                            ax.yaxis.set_major_formatter(ScalarFormatter())
                            ax.ticklabel_format(style='plain', axis='y')
                            ax.set_title(plot_subplot_title, fontsize=16, fontweight='bold')
                            ax.set_xlabel("Kategori", fontsize=12)
                            ax.set_ylabel(current_unit, fontsize=12)
                            ax.tick_params(axis='x', rotation=45, labelsize=11)
                            ax.grid(axis='y', linestyle='--', alpha=0.7)
                        else: 
                            ax.text(0.5, 0.5, "'Kategori' hilang", ha='center', va='center')
                            ax.set_xticks([])
                            ax.set_yticks([])

                    for j in range(n_vars, len(axes_range)): 
                        fig_range.delaxes(axes_range[j])
                    plt.subplots_adjust(top=0.9, hspace=0.45, wspace=0.3)
                    
                    # === [PERUBAHAN] Tambahkan figure ke daftar gabungan PDF ===
                    figures_for_pdf.append(fig_range) 
                    # ========================================================
                    
                    st.pyplot(fig_range)
                    plt.close(fig_range) # Tetap tutup setelah ditampilkan

        else: # Mode Per Tahun
            # ... (Logika 'Mode Per Tahun' Anda tetap sama) ...
            selected_year_plot = st.session_state.results.get('year')
            st.markdown(f"*(Semua fitur terpilih untuk tahun {selected_year_plot})*")
            n_vars = len(cols_to_plot_all)
            n_cols = 1 if n_vars == 1 else 2
            n_rows = (n_vars + n_cols - 1) // n_cols

            fig_per_year, axes_per_year = plt.subplots(n_rows, n_cols, figsize=(8 * n_cols, 7 * n_rows), squeeze=False)
            axes_per_year = axes_per_year.flatten()

            for i, var in enumerate(cols_to_plot_all):
                # ... (Semua logika plot boxplot Anda tetap sama) ...
                ax = axes_per_year[i]
                base_feature = var.split('_')[0]
                clean_name = title_mapping.get(base_feature, base_feature)
                current_unit = FEATURE_UNITS.get(base_feature, default_unit)
                plot_subplot_title = clean_name

                if 'Kategori' in df_valid.columns:
                    sns.boxplot(data=df_valid, x="Kategori", y=var, ax=ax, order=ordered_categories, palette=CATEGORY_COLORS)
                    ax.yaxis.set_major_formatter(ScalarFormatter())
                    ax.ticklabel_format(style='plain', axis='y')
                    ax.set_title(plot_subplot_title, fontsize=16, fontweight='bold')
                    ax.set_xlabel("Kategori", fontsize=12)
                    ax.set_ylabel(current_unit, fontsize=12)
                    ax.tick_params(axis='x', rotation=45, labelsize=11)
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                else: 
                    ax.text(0.5, 0.5, "'Kategori' hilang", ha='center', va='center')
                    ax.set_xticks([])
                    ax.set_yticks([])

            for j in range(n_vars, len(axes_per_year)): 
                fig_per_year.delaxes(axes_per_year[j])
            plt.subplots_adjust(top=0.93, hspace=0.45, wspace=0.3)

            # === [PERUBAHAN] Tambahkan figure ke daftar gabungan PDF ===
            figures_for_pdf.append(fig_per_year)
            # ========================================================

            st.pyplot(fig_per_year)
            plt.close(fig_per_year)

    elif not cols_to_plot_all:
        st.warning("Tidak ada fitur untuk box plot.")

    st.markdown("---")


    # --- 5. PETA ---
    st.subheader("🗺️ Peta Sebaran dan Karakteristik Cluster")
    if "Latitude" in df_valid.columns and "Longitude" in df_valid.columns:
        df_map = df_valid.dropna(subset=['Latitude', 'Longitude'])
        if not df_map.empty:
            # ... (Semua logika pembuatan peta folium 'm' Anda tetap sama) ...
            center_lat = -2.5
            center_lon = 120
            zoom_level = 4.5
            m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)
            # ... (Semua logika loop 'for _, row in df_map.iterrows():' Anda tetap sama) ...
            selected_year_map = st.session_state.results.get('year')
            features_to_show = FEATURE_PRODUKSI
            FEATURE_UNITS_MAP = {'Volume': 'ton', 'Nilai': '(Rp)', 'Produksi': '(Rp)', 'Nelayan': 'orang', 'Konsumsi': 'kg/kapita'}
            for _, row in df_map.iterrows():
                popup_lines = [
                    f"<div style='font-weight:bold;margin-bottom:4px;'>{row.get('Wilayah', 'N/A')}</div>",
                    f"<div style='margin-bottom:6px;'><b>Kategori:</b> {row.get('Kategori', 'N/A')}</div>",
                    "<table style='border-collapse:collapse;'>"
                ]
                for feat in features_to_show:
                    val_str = "N/A"
                    if result_mode == 'Range Tahun':
                        year_range_map = st.session_state.results.get('year_range')
                        if year_range_map:
                            start_year_map, end_year_map = int(year_range_map[0]), int(year_range_map[1])
                            year_cols_map = [f"{feat}_{y}" for y in range(start_year_map, end_year_map + 1) if f"{feat}_{y}" in df_map.columns]
                            if year_cols_map:
                                values_map = [row.get(col) for col in year_cols_map if pd.notna(row.get(col))]
                                numeric_values = [v for v in values_map if isinstance(v, (int, float))]
                                if numeric_values:
                                    try: 
                                        val_map = sum(numeric_values) / len(numeric_values)
                                        unit_map = FEATURE_UNITS_MAP.get(feat, '')
                                        val_str = f"{val_map:,.2f}"
                                        if unit_map: 
                                            val_str = f"{val_str} {unit_map}"
                                    except ZeroDivisionError:
                                        val_str = "N/A"
                    else: # Mode Per Tahun
                        if selected_year_map:
                            col_name_map = f"{feat}_{selected_year_map}"
                            val_map = row.get(col_name_map)
                            if pd.notna(val_map):
                                try:
                                    unit_map = FEATURE_UNITS_MAP.get(feat, '')
                                    val_str = f"{float(val_map):,.2f}"
                                    if unit_map: 
                                        val_str = f"{val_str} {unit_map}"
                                except (ValueError, TypeError):
                                    val_str = str(val_map)
                    popup_lines.append(f"<tr><td style='padding:2px 8px;'><b>{feat}</b></td><td style='padding:2px 8px;'>: {val_str}</td></tr>")
                popup_lines.append("</table>")
                popup_html = "".join(popup_lines)
                
                # ... (Logika 'color_val' dan 'hex_to_name' Anda tetap sama) ...
                color_val = '#999999'
                try:
                    category = row.get('Kategori')
                    if category and category in CATEGORY_COLORS:
                        color_val = CATEGORY_COLORS[category]
                    elif 'Cluster' in row and pd.notna(row['Cluster']):
                        cluster_idx = int(row['Cluster'])
                        color_val = CLUSTER_COLORS.get(cluster_idx, '#999999')
                except (ValueError, TypeError, KeyError):
                    pass
                hex_to_name = {
                    '#ff4d4d': 'red', 
                    '#ff8000': 'orange', 
                    '#ffcc00': 'beige', 
                    '#9933ff': 'purple', 
                    '#3366ff': 'blue', 
                    '#00cccc': 'cadetblue', 
                    '#33cc33': 'green', 
                    '#999999': 'gray'
                }
                color_name = hex_to_name.get(str(color_val).lower(), 'lightgray') if isinstance(color_val, str) and str(color_val).startswith('#') else str(color_val)
                try: 
                    icon = folium.Icon(icon='ship', prefix='fa', color=color_name, icon_color='white')
                except (TypeError, ValueError): 
                    icon = folium.Icon(icon='ship', prefix='fa', color=color_name)
                
                folium.Marker(location=[row['Latitude'], row['Longitude']], popup=folium.Popup(popup_html, max_width=350), icon=icon).add_to(m)

            # LEGEND Peta
            try:
                # ... (Logika 'legend_html' Anda tetap sama) ...
                kategori_unik_map = sorted(df_map['Kategori'].dropna().unique())
                kategori_warna_map = {k: CATEGORY_COLORS.get(k, '#999999') for k in kategori_unik_map if k in CATEGORY_COLORS}
                if kategori_warna_map:
                    legend_html = "<div style='position: absolute; bottom: 20px; right: 20px; z-index: 9999; background-color: rgba(255,255,255,0.95); border-radius: 8px; border: 1px solid #333; padding: 10px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-size: 13px; font-family: Arial, sans-serif; color: #000; max-height: 240px; overflow-y: auto;'><div style='font-weight:bold; font-size:14px; margin-bottom:6px; border-bottom:1px solid #ccc;'>Legenda Kategori</div>"
                    for kategori, color in kategori_warna_map.items():
                        legend_html += f"<div style='display:flex; align-items:center; margin-top:4px; color:#000;'><div style='width:16px; height:12px; background:{color}; border:1px solid #333; margin-right:6px; border-radius:2px;'></div><div>{kategori}</div></div>"
                    legend_html += "</div>"
                    legend_element = folium.Element(legend_html)
                    m.get_root().html.add_child(legend_element)
                
                # Tampilkan Peta Interaktif di Streamlit
                st_folium(m, width=1500, height=600)
                
                # === [PERUBAHAN] Siapkan Peta Statis untuk PDF ===
                st.caption("Memproses peta statis untuk PDF... (mungkin perlu beberapa detik)")
                try:
                    # Panggil helper untuk "memfoto" peta
                    fig_map_static = get_folium_map_as_figure(m)
                    if fig_map_static:
                        figures_for_pdf.append(fig_map_static)
                        st.caption("✔️ Peta statis siap di-download.")
                    else:
                        st.warning("Gagal membuat peta statis untuk PDF.")
                except Exception as e:
                    st.error(f"Error saat memproses peta statis: {e}")
                # ===============================================

            except Exception as e: 
                st.warning(f"Legenda peta tidak dapat ditampilkan: {e}")
        else: 
            st.warning("Data tidak memiliki nilai Latitude/Longitude yang valid.")
    else: 
        st.warning("Kolom 'Latitude' dan 'Longitude' tidak ditemukan.")

    st.markdown("---")

    # ===> AWAL BAGIAN INFO LANJUTAN WILAYAH (MULTI-SELECT, 2 KOLOM, INFO DETAIL) <===
    st.subheader("ℹ️ Info Lanjutan Wilayah")

    # Pastikan df_valid, feature_cols_used, dynamic_category_colors sudah ada dan benar
    if 'Wilayah' in df_valid.columns and 'Cluster' in df_valid.columns and 'Kategori' in df_valid.columns \
       and not df_valid.empty and feature_cols_used and CATEGORY_COLORS:

        # --- Definisikan mapping judul fitur & unit (ambil dari box plot jika konsisten) ---
        title_mapping_info = {
            'Nilai': 'Nilai Produksi', 'Produksi': 'Nilai Produksi', # Produksi sbg fallback
            'Nelayan': 'Nelayan', 'Volume': 'Volume', 'Konsumsi': 'Konsumsi',
        }
        # Tambahkan fitur lain yg mungkin ada secara dinamis
        for f in selected_features_info:
            if f not in title_mapping_info: title_mapping_info[f] = f[:3] # Fallback

        # Kamus unit (sesuaikan dengan FEATURE_UNITS_BOX jika perlu)
        FEATURE_UNITS_INFO = {
            'Volume': 'Ton', 'Nilai': 'Rp', 'Produksi': 'Rp',
            'Nelayan': 'Orang', 'Konsumsi': 'Kg/Kapita'
        }
        default_unit_info = "" # Default tidak ada unit

        # --- Expander untuk detail ---
        with st.expander("Pilih Wilayah untuk Detail", expanded=False):
            # Tentukan Wilayah Awal (Satu per Cluster)
            initial_regions = []
            try:
                # Ambil satu wilayah pertama dari setiap cluster valid (non-outlier)
                # Urutkan berdasarkan cluster number agar tampilan awal konsisten
                initial_regions_df = df_valid[df_valid['Cluster'] != -1].sort_values('Cluster').groupby('Cluster').first()
                initial_regions = initial_regions_df['Wilayah'].tolist()
                # Tambahkan satu outlier jika ada
                if 'Outlier' in df_valid['Kategori'].unique():
                     outlier_region = df_valid[df_valid['Kategori'] == 'Outlier']['Wilayah'].first()
                     if outlier_region and outlier_region not in initial_regions: # Hindari duplikat jika outlier juga cluster pertama
                          initial_regions.append(outlier_region)
            except Exception as e:
                st.warning(f"Gagal menentukan wilayah awal: {e}")
                initial_regions = df_valid['Wilayah'].unique()[:3] # Fallback: 3 wilayah pertama

            list_wilayah_all = sorted(df_valid['Wilayah'].unique())

            # --- MultiSelect untuk memilih wilayah ---
            selected_regions = st.multiselect(
                "Pilih Wilayah (bisa lebih dari satu):",
                options=list_wilayah_all,
                default=initial_regions, # Default menampilkan contoh per cluster
                key='multiselect_wilayah_detail_v5' # Key baru
            )

            st.markdown("---") # Garis pemisah

            if selected_regions:
                st.write(f"Menampilkan detail untuk **{len(selected_regions)}** wilayah terpilih:")
                st.write("") # Spasi

                # --- Buat Layout 2 Kolom ---
                col_left, col_right = st.columns(2)
                cols = [col_left, col_right] # List kolom untuk iterasi

                # Loop melalui setiap wilayah yang dipilih dan distribusikan ke kolom
                for idx, region in enumerate(selected_regions):
                    target_col = cols[idx % 2] # Pilih kolom kiri (0) atau kanan (1)
                    with target_col:
                        # Filter data
                        try:
                            selected_data = df_valid[df_valid['Wilayah'] == region].iloc[0]
                        except IndexError:
                            st.warning(f"Data wilayah '{region}' tidak ditemukan.")
                            continue # Lanjut ke wilayah berikutnya

                        kategori_name = selected_data.get('Kategori', 'N/A')
                        cluster_color = CATEGORY_COLORS.get(kategori_name, '#999999') # Ambil warna

                        # Indikator warna
                        color_indicator = f'<span style="display: inline-block; margin-right: 8px; width: 12px; height: 12px; background-color: {cluster_color}; border-radius: 50%;"></span>'

                        # Tampilkan Nama Wilayah + Warna & Kategori
                        st.markdown(f"<h5>{color_indicator} <b>{region}</b></h5>", unsafe_allow_html=True) # Ukuran h5 agar sedikit lebih kecil
                        st.markdown(f"**Kategori:** {kategori_name}")
                        # Cluster number tidak ditampilkan

                        st.markdown(f"**Nilai Fitur:**")
                        # Tampilkan nilai fitur dengan font lebih kecil dan unit
                        for col_name in feature_cols_used:
                             base_feature_name = col_name.split('_')[0]
                             clean_feature_name = title_mapping_info.get(base_feature_name, base_feature_name)
                             unit = FEATURE_UNITS_INFO.get(base_feature_name, default_unit_info)
                             label_str = f"{clean_feature_name}{f' ({unit})' if unit else ''}" # Tambahkan unit jika ada
                             value = selected_data.get(col_name, 'N/A')
                             value_str = f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)

                             # Gunakan markdown dengan CSS inline untuk font lebih kecil
                             st.markdown(
                                 f"<p style='margin-bottom: 0.1em; font-size: 0.9em;'><b>{label_str}:</b> {value_str}</p>",
                                 unsafe_allow_html=True
                             )
                        st.markdown("---") # Pemisah antar wilayah di kolom yang sama
            else:
                st.info("Pilih satu atau lebih wilayah dari daftar di atas untuk melihat detailnya.")

    # Peringatan jika data/kolom tidak ada
    elif 'Wilayah' not in df_valid.columns or df_valid.empty:
        st.warning("Kolom 'Wilayah' tidak ditemukan atau data hasil kosong.")
    elif not feature_cols_used:
         st.warning("Tidak ada kolom fitur yang digunakan untuk clustering.")
    elif not CATEGORY_COLORS:
         st.warning("Gagal membuat palet warna dinamis.")


    # ===> AKHIR BAGIAN INFO LANJUTAN WILAYAH <===

    st.markdown("---") # Pemisah ke bagian Evaluasi

    # --- 6. EVALUASI KUALITAS ---
    st.subheader("⚙️ Evaluasi Kualitas Clustering")
    n_unique_clusters = df_valid[df_valid['Cluster'] != -1]['Cluster'].nunique() if 'Cluster' in df_valid else 0

    # Inisialisasi fig_eval agar bisa di-handle di 'except'
    fig_eval = None 

    if n_unique_clusters >= 2 and X_scaled is not None and labels is not None:
        valid_mask = labels != -1
        if np.sum(valid_mask) >= 2:
            try:
                # --- [PERUBAHAN 1: Hitung Skor Dulu] ---
                sil_score = silhouette_score(X_scaled[valid_mask], labels[valid_mask])
                dbi_score = davies_bouldin_score(X_scaled[valid_mask], labels[valid_mask])

                # === BLOK KODE UNTUK EXCEL SUDAH DIHAPUS ===
                
                # --- [PERUBAHAN 2: Buat Satu Figure Gabungan] ---
                # Buat 1 baris, 2 kolom subplot. Ukuran (22, 9) agar lebar.
                fig_eval, (ax_sil, ax_pca) = plt.subplots(1, 2, figsize=(22, 9))
                
                # --- Plot 1: Visualisasi Silhouette (di ax_sil) ---
                sample_silhouette_values = silhouette_samples(X_scaled[valid_mask], labels[valid_mask])
                y_lower = 10
                unique_labels_plot = np.unique(labels[valid_mask])
                
                for i in unique_labels_plot:
                    ith_cluster_silhouette_values = sample_silhouette_values[labels[valid_mask] == i]
                    ith_cluster_silhouette_values.sort()
                    size_cluster_i = ith_cluster_silhouette_values.shape[0]
                    y_upper = y_lower + size_cluster_i
                    color = cm.nipy_spectral(float(i) / n_unique_clusters)
                    ax_sil.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values, facecolor=color, edgecolor=color, alpha=0.7)
                    ax_sil.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
                    y_lower = y_upper + 10
                
                ax_sil.set_title("Visualisasi Silhouette per Cluster", fontsize=16)
                ax_sil.set_xlabel("Nilai Koefisien Silhouette")
                ax_sil.set_ylabel("Label Cluster")
                ax_sil.axvline(x=sil_score, color="red", linestyle="--")
                ax_sil.set_yticks([])
                ax_sil.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

                # --- Plot 2: Plot PCA 2D (di ax_pca) ---
                try:
                    # Gunakan PCA pada SEMUA data (X_scaled) agar konsisten
                    pca_all = PCA(n_components=2)
                    X2_all = pca_all.fit_transform(X_scaled)
                    
                    # Buat DataFrame PCA dari semua data
                    df_pca_all = pd.DataFrame(X2_all, columns=['PC1', 'PC2'])
                    
                    # Tambahkan Kategori dari df_valid
                    # (PENTING: pastikan df_valid.index sesuai dengan X_scaled)
                    df_pca_all['Kategori'] = df_valid['Kategori'].values 
                    
                    # Plot semua data sekaligus dengan 'hue'
                    sns.scatterplot(
                        data=df_pca_all, 
                        x='PC1', 
                        y='PC2', 
                        hue='Kategori', 
                        ax=ax_pca, 
                        palette=CATEGORY_COLORS, 
                        s=70, 
                        style='Kategori', 
                        markers=True
                    )
                    
                    ax_pca.set_xlabel("Principal Component 1")
                    ax_pca.set_ylabel("Principal Component 2")
                    ax_pca.set_title("Visualisasi Cluster 2D (PCA)", fontsize=16)
                    ax_pca.legend(title="Kategori Cluster")
                
                except Exception as e_pca:
                    ax_pca.text(0.5, 0.5, f"Gagal membuat plot PCA:\n{e_pca}", ha='center', va='center', wrap=True)

                # --- [PERUBAHAN 3: Tambahkan Judul Utama dan Skor ke Figure] ---
                fig_eval.suptitle("Evaluasi Kualitas Clustering", fontsize=24, fontweight='bold')
                # Tambahkan teks skor di bawah judul utama
                skor_text = f"Silhouette Score: {sil_score:.3f} (Mendekati 1 lebih baik)   |   Davies-Bouldin Index: {dbi_score:.3f} (Mendekati 0 lebih baik)"
                fig_eval.text(0.5, 0.93, skor_text, ha='center', va='top', fontsize=14)
                
                plt.tight_layout(rect=[0, 0.03, 1, 0.9]) # Sesuaikan layout agar judul tidak tumpang tindih
                
                # Tampilkan SATU figure gabungan di Streamlit
                st.pyplot(fig_eval)

                # Tambahkan SATU figure gabungan ini ke PDF
                figures_for_pdf.append(fig_eval)
                # plt.close(fig_eval) # <-- JANGAN DITUTUP. Fungsi PDF helper yang akan menutupnya.

            except ValueError as ve:
                st.warning(f"Evaluasi clustering tidak dapat dihitung: {ve}")
                if fig_eval: plt.close(fig_eval) # Tutup jika gagal
            except Exception as e_eval:
                st.error(f"Terjadi kesalahan saat evaluasi: {e_eval}")
                if fig_eval: plt.close(fig_eval) # Tutup jika gagal
        else:
            st.warning("Evaluasi tidak dapat ditampilkan karena data valid kurang dari 2.")
    else:
        st.warning("Evaluasi tidak dapat ditampilkan karena hanya 1 cluster yang terbentuk.")

    st.markdown("---")

    # === [PERUBAHAN] BUAT COVER PAGE UNTUK PDF ===
    # (Letakkan ini TEPAT SEBELUM Tombol Download PDF Anda)

    try:
        fig_cover, ax_cover = plt.subplots(figsize=(8.5, 11)) # Ukuran kertas potret
        ax_cover.axis('off') # Sembunyikan sumbu X/Y

        # Ambil waktu sekarang
        now = datetime.now().strftime("%d %B %Y, %H:%M") 

        # Tambahkan teks ke tengah halaman
        fig_cover.text(0.5, 0.60, "Laporan Analisis Clustering", ha='center', fontsize=24, fontweight='bold')
        fig_cover.text(0.5, 0.55, "Hasil dan Visualisasi Data Perikanan", ha='center', fontsize=18)
        fig_cover.text(0.5, 0.48, f"Dibuat pada: {now}", ha='center', fontsize=12)
        
        # Masukkan cover page di AWAL daftar
        figures_for_pdf.insert(0, fig_cover) 

    except Exception as e_cover:
        st.warning(f"Gagal membuat cover page PDF: {e_cover}")
    # === AKHIR PERUBAHAN ===

    # === [PERUBAHAN] TOMBOL DOWNLOAD PDF GABUNGAN (Boxplot + Peta) ===
    if figures_for_pdf: # Hanya tampilkan jika ada gambar yang dibuat
        st.subheader("Download Laporan Visual (PDF)")
        st.markdown("Download semua grafik (Box Plot dan Peta Statis) sebagai satu file PDF multi-halaman.")

        # Gunakan fungsi helper PDF yang sudah ada
        pdf_data = create_multi_page_pdf(figures_for_pdf)

        st.download_button(
            label="⬇️ Download Laporan Visual sebagai PDF",
            data=pdf_data,
            file_name='Laporan_Visual_Clustering.pdf',
            mime='application/pdf'
        )
    # =================================================================
        st.markdown("---")

    # --- 7. TREND TAHUNAN ---
    # ========== TREND SECTION (URUTAN DIUBAH: FITUR DULU BARU JUMLAH) ==========
    st.subheader("📈 Tren Tahunan Lokasi Teratas") # Judul umum

    # --- Tentukan opsi fitur (sama seperti sebelumnya) ---
    trend_options = available_features if available_features else (FEATURE_PRODUKSI if 'FEATURE_PRODUKSI' in locals() else [])

    if trend_options:
        # --- 1. Pilih Fitur untuk Tren ---
        # Beri key berbeda tergantung mode agar selectbox tidak konflik
        selectbox_key = 'trend_feature_range_v2' if result_mode == 'Range Tahun' else 'trend_feature_pertahun_v2' # Update key
        selected_feature_trend = st.selectbox(f"Pilih Fitur untuk Tren ({result_mode}):", trend_options, key=selectbox_key)

        # --- 2. Slider untuk memilih jumlah lokasi (setelah fitur dipilih) ---
        n_top_trend = st.slider("Jumlah Lokasi untuk Tren:", min_value=5, max_value=20, value=10, key='n_top_trend_slider_v2') # Update key

        # --- 3. Logika Pengumpulan Data Tren (sama, tapi pakai n_top_trend) ---
        trend_cols_with_year = []
        start_year_trend, end_year_trend = None, None

        if result_mode == 'Range Tahun':
            year_range_trend = st.session_state.results.get('year_range')
            if year_range_trend:
                 start_year_trend, end_year_trend = int(year_range_trend[0]), int(year_range_trend[1])
            else: # Fallback
                 years_available_trend = sorted(list(set(int(y) for c in df_raw.columns if (m:=re.search(r'_(\d{4})$',c)) and (y:=m.group(1)).isdigit() )))
                 if years_available_trend: start_year_trend, end_year_trend = years_available_trend[0], years_available_trend[-1]

            if start_year_trend is not None and end_year_trend is not None:
                for c in sorted(df_raw.columns):
                    m_trend = re.match(rf'{re.escape(selected_feature_trend)}_(\d{{4}})$', c, flags=re.IGNORECASE)
                    if m_trend:
                        try:
                            y_trend = int(m_trend.group(1))
                            if start_year_trend <= y_trend <= end_year_trend: trend_cols_with_year.append((y_trend, c))
                        except ValueError: pass
        else: # Mode Per Tahun
             for c in sorted(df_raw.columns):
                 m_trend = re.match(rf'{re.escape(selected_feature_trend)}_(\d{{4}})$', c, flags=re.IGNORECASE)
                 if m_trend:
                     try: trend_cols_with_year.append((int(m_trend.group(1)), c))
                     except ValueError: pass
             if trend_cols_with_year:
                 all_years_found = [y for y, c in trend_cols_with_year]
                 start_year_trend, end_year_trend = min(all_years_found), max(all_years_found)


        trend_cols_with_year.sort()
        trend_cols = [c for y, c in trend_cols_with_year]

        # --- 4. Plotting Tren (sama, tapi pakai n_top_trend dan judul baru) ---
        if trend_cols:
            try:
                df_raw['average_trend'] = df_raw[trend_cols].apply(pd.to_numeric, errors='coerce').mean(axis=1).fillna(0)
                # Gunakan n_top_trend dari slider
                df_top_trend = df_raw.nlargest(n_top_trend, 'average_trend')
                years_trend_plot = [y for y, c in trend_cols_with_year]

                fig_trend, ax_trend = plt.subplots(figsize=(12, 7))
                for _, row in df_top_trend.iterrows():
                    trend_values = row[trend_cols].apply(pd.to_numeric, errors='coerce')
                    if not trend_values.isnull().all(): ax_trend.plot(years_trend_plot, trend_values, marker='o', linestyle='-', label=row.get('Wilayah', 'N/A'))

                # Update judul plot
                title_suffix = f"({start_year_trend}-{end_year_trend})" if start_year_trend and end_year_trend and result_mode=='Range Tahun' else ""
                trend_title = f"Tren Tahunan {title_suffix} - Top {n_top_trend} Lokasi: '{selected_feature_trend}'"
                ax_trend.set_title(trend_title)

                ax_trend.set_xlabel("Tahun"); ax_trend.set_ylabel(selected_feature_trend)
                ax_trend.yaxis.set_major_formatter(ScalarFormatter()); ax_trend.ticklabel_format(style='plain', axis='y')
                ax_trend.legend(title='Lokasi', bbox_to_anchor=(1.05, 1), loc='upper left'); ax_trend.grid(True, linestyle='--')
                plt.tight_layout(rect=[0, 0, 0.85, 1]); st.pyplot(fig_trend); plt.close(fig_trend)
            except Exception as e_trend: st.error(f"Gagal membuat plot tren: {e_trend}")
        elif start_year_trend is not None:
            st.warning(f"Tidak ditemukan kolom tahunan untuk '{selected_feature_trend}'.") # Pesan disingkat
        # Jangan tampilkan warning jika start_year_trend None

    else:
        st.warning("Tidak ada fitur tersedia untuk menampilkan tren.")

    st.markdown("---") # Pemisah sebelum Top Kota

    # --- 8. TOP KOTA ---
    st.subheader("🏆 Peringkat Lokasi Teratas (Berdasarkan Rata-Rata Semua Tahun)")
    peringkat_options = available_features if available_features else (FEATURE_PRODUKSI if 'FEATURE_PRODUKSI' in locals() else [])
    if peringkat_options:
        selected_feature_top = st.selectbox("Pilih Fitur untuk Peringkat:", peringkat_options, key='top_feature')
        n_top = st.slider("Jumlah Lokasi Ditampilkan:", min_value=5, max_value=20, value=10, key='n_top_slider')

        # PERBAIKAN: Regex diperbaiki (menambahkan '$', menghapus ',')
        top_cols = sorted([c for c in df_raw.columns if re.match(rf'{re.escape(selected_feature_top)}_(\d{{4}})$', c, flags=re.IGNORECASE)])

        if top_cols:
            try:
                df_raw['average_top'] = df_raw[top_cols].apply(pd.to_numeric, errors='coerce').mean(axis=1).fillna(0)
                df_top = df_raw.nlargest(n_top, 'average_top')

                fig_top, ax_top = plt.subplots(figsize=(10, 8))
                sns.barplot(data=df_top.sort_values('average_top', ascending=False), y='Wilayah', x='average_top', palette='viridis', ax=ax_top)
                ax_top.xaxis.set_major_formatter(ScalarFormatter())
                ax_top.ticklabel_format(style='plain', axis='x')
                ax_top.set_title(f"Top {n_top} Lokasi - Rata-Rata '{selected_feature_top}' (Semua Tahun)")
                ax_top.set_xlabel(f" {selected_feature_top}")
                ax_top.set_ylabel("Wilayah")
                plt.tight_layout()
                st.pyplot(fig_top)
                plt.close(fig_top)

            except Exception as e_top:
                st.error(f"Gagal membuat peringkat: {e_top}")
        else:
            st.warning(f"Tidak ditemukan kolom tahunan untuk fitur '{selected_feature_top}'.")
    else:
        st.warning("Tidak ada fitur tersedia untuk menampilkan peringkat.")

else:
    st.info("👋 Selamat datang! Silakan upload file Excel Anda di sidebar untuk memulai analisis.")
    if 'results_ready' in st.session_state:
        del st.session_state.results_ready