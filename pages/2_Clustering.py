import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import re
from io import BytesIO
from PIL import Image
from datetime import datetime

# Import Sklearn
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, silhouette_samples

# Import Visualisasi
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import ScalarFormatter
import seaborn as sns

# Import Peta (Folium)
import folium
from streamlit_folium import st_folium

# Import Laporan (Excel/PDF/Web)
from openpyxl.drawing.image import Image as OpenpyxlImage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Import dari file utils.py Anda
try:
    from utils import (
        initialize_clustering_model,
        categorize_clusters,
        FEATURE_PRODUKSI,
        CLUSTER_COLORS,
        CATEGORY_COLORS
    )
except ImportError:
    st.error("Gagal mengimpor file 'utils.py'. Pastikan file tersebut ada.")
    # Fallback default jika utils tidak ada (agar aplikasi tidak crash)
    FEATURE_PRODUKSI = ['Produksi', 'Volume', 'Nilai', 'Nelayan', 'Konsumsi']
    CLUSTER_COLORS = {0: '#3366ff', 1: '#ff4d4d', 2: '#ff8000', 3: '#33cc33', 4: '#9933ff', 5: '#00cccc', 6: '#ffcc00', -1: '#999999'}
    CATEGORY_COLORS = {'Cluster 0': '#3366ff', 'Cluster 1': '#ff4d4d', 'Cluster 2': '#ff8000', 'Cluster 3': '#33cc33', 'Cluster 4': '#9933ff', 'Cluster 5': '#00cccc', 'Cluster 6': '#ffcc00', 'Outlier': '#999999'}
    
    def initialize_clustering_model(method, params):
        # Placeholder jika utils.py tidak ada
        from sklearn.cluster import KMeans, Birch, OPTICS
        if method == 'K-Means':
            return KMeans(n_clusters=params.get('n_clusters', 3), random_state=42, n_init=10)
        if method == 'BIRCH':
            return Birch(n_clusters=params.get('n_clusters', 3), threshold=params.get('threshold', 0.1), branching_factor=params.get('branching_factor', 50))
        if method == 'OPTICS':
            return OPTICS(min_samples=params.get('min_samples', 8), xi=params.get('xi', 0.01), min_cluster_size=params.get('min_cluster_size', 5))
        return None

    def categorize_clusters(df):
        # Placeholder jika utils.py tidak ada
        if 'Cluster' in df.columns:
            df['Kategori'] = 'Cluster ' + df['Cluster'].astype(str)
            df['Kategori'] = df['Kategori'].replace('Cluster -1', 'Outlier')
        return df

# =============================================================================
# PENGATURAN AWAL HALAMAN
# =============================================================================

st.set_page_config(page_title="CLUSTER | FISHERY CLUSTER", page_icon="assets/logo1.png", layout="wide")

# Pengaturan format angka
pd.options.display.float_format = '{:,.2f}'.format
np.set_printoptions(suppress=True)

# =============================================================================
# FUNGSI SETUP: STYLING DAN SESSION STATE
# =============================================================================

def setup_styling():
    """Menerapkan CSS kustom untuk tema aplikasi."""
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

def inisialisasi_session_state():
    """Menginisialisasi variabel session state yang diperlukan."""
    if 'run_clustering' not in st.session_state:
        st.session_state.run_clustering = False
    if 'results' not in st.session_state:
        st.session_state.results = {}
    if 'results_ready' not in st.session_state:
        st.session_state.results_ready = False

# =============================================================================
# FUNGSI HELPER: DOWNLOAD (Excel, PDF, Peta)
# =============================================================================

def convert_dfs_to_multisheet_excel(sheets_dict, chart_figure=None, chart_sheet_name=None):
    """
    Mengkonversi kamus DataFrame DAN sebuah chart Matplotlib
    menjadi satu file Excel multi-sheet.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # --- Bagian 1: Tulis semua DataFrame ---
        for sheet_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # --- Bagian 2: Tulis chart jika ada ---
        if chart_figure is not None and chart_sheet_name is not None:
            
            # Buat sheet baru yang kosong untuk chart
            pd.DataFrame().to_excel(writer, sheet_name=chart_sheet_name)
            worksheet = writer.sheets[chart_sheet_name]

            # Simpan chart ke buffer memori sebagai gambar PNG
            img_buffer = BytesIO()
            chart_figure.savefig(img_buffer, format='png', bbox_inches='tight')
            
            # Pindahkan pointer buffer ke awal agar bisa dibaca
            img_buffer.seek(0) 
            
            # Buat objek gambar openpyxl dari buffer
            img = OpenpyxlImage(img_buffer)
            
            # Tambahkan gambar ke worksheet di sel 'A1'
            worksheet.add_image(img, 'A1')

    processed_data = output.getvalue()
    return processed_data

def create_multi_page_pdf(figures_list):
    """
    Mengkonversi daftar objek Figure Matplotlib menjadi satu file PDF multi-halaman.
    """
    pdf_buffer = BytesIO()
    with PdfPages(pdf_buffer) as pdf:
        for fig in figures_list:
            if fig is not None:
                pdf.savefig(fig, bbox_inches='tight') # Simpan setiap figure ke halaman baru
                plt.close(fig) # Tutup figure setelah disimpan untuk membebaskan memori
    pdf_buffer.seek(0)
    return pdf_buffer

def get_folium_map_as_figure(map_object):
    """
    Menyimpan objek Peta Folium sebagai file HTML sementara,
    merendernya dengan Selenium, mengambil screenshot, 
    dan mengembalikannya sebagai objek Figure Matplotlib.
    
    PENTING: Dikonfigurasi untuk Streamlit Cloud (membutuhkan packages.txt)
    """
    
    temp_html = "temp_map_for_pdf.html"
    try:
        # 1. Simpan peta ke file HTML sementara
        map_object.save(temp_html)
        # 2. Dapatkan path absolut untuk browser
        full_path = 'file://' + os.path.abspath(temp_html)
    except Exception as e:
        st.error(f"Gagal menyimpan peta sementara ke HTML: {e}")
        if os.path.exists(temp_html):
             os.remove(temp_html)
        return None
    # ======================

    # 1. Siapkan semua options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-sh-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1000,700")

    # 2. Tentukan path driver secara EKSPLISIT
    service = Service(executable_path="/usr/bin/chromedriver")
    
    driver = None
    png_data = None # Inisialisasi png_data di luar try

    try:
        # 3. Pastikan Anda memasukkan KEDUA argumen: 
        driver = webdriver.Chrome(service=service, options=options)
    
    except Exception as e:
        if os.path.exists(temp_html):
             os.remove(temp_html)
        return None

    try:
        # 5. Ambil screenshot
        driver.get(full_path)
        # Beri waktu (detik) agar peta selesai di-render
        time.sleep(2) 
        
        png_data = driver.get_screenshot_as_png()
        
    except Exception as e:
        st.error(f"Gagal mengambil screenshot peta: {e}")
        # png_data akan tetap None
        
    finally:
        # 6. Selalu tutup driver dan hapus file sementara
        if driver:
            driver.quit()
        if os.path.exists(temp_html):
            os.remove(temp_html)
            
    # --- Blok 3: Konversi Gambar (HANYA JIKA SCREENSHOT BERHASIL) ---
    if png_data:
        try:
            # 7. Konversi screenshot (PNG) ke Figure Matplotlib
            img = Image.open(BytesIO(png_data))
            
            fig_map, ax_map = plt.subplots(figsize=(20, 15)) 
            ax_map.imshow(img)
            ax_map.axis('off') # Sembunyikan sumbu X/Y
            
            return fig_map
            
        except Exception as e:
            st.error(f"Gagal mengkonversi screenshot peta ke figure: {e}")
            return None
    else:
        # Jika png_data masih None (karena screenshot gagal)
        st.warning("Tidak ada data gambar yang berhasil diambil.")
        return None

# =============================================================================
# FUNGSI HELPER: EVALUASI
# =============================================================================

def get_silhouette_indicator(score):
    """Memberikan interpretasi teks untuk Silhouette Score."""
    if score > 0.7:
        return "Sangat Baik (Struktur Kuat)"
    elif score > 0.5:
        return "Baik (Struktur Wajar)"
    elif score > 0.25:
        return "Cukup (Struktur Lemah)"
    else:
        return "Buruk (Struktur Tidak Ditemukan)"

def get_dbi_indicator(score):
    """Memberikan interpretasi teks untuk Davies-Bouldin Index."""
    if score < 0.5:
        return "Sangat Baik (Cluster Terpisah Jelas)"
    elif score < 0.8:
        return "Baik (Cluster Cukup Terpisah)"
    elif score < 1.2:
        return "Cukup (Cluster Agak Tumpang Tindih)"
    else:
        return "Buruk (Cluster Sangat Tumpang Tindih)"

# =============================================================================
# FUNGSI UTAMA APLIKASI: SIDEBAR
# =============================================================================

def tampilkan_sidebar():
    """Menampilkan semua widget di sidebar dan mengembalikan pengaturannya."""
    with st.sidebar:
        st.header('⚙️ Pengaturan Clustering')
        uploaded_file = st.file_uploader('📂 Upload File Excel Anda', type=['xlsx'])

        if not uploaded_file:
            return None # Keluar jika tidak ada file

        # Inisialisasi variabel
        pengaturan = {
            "uploaded_file": uploaded_file,
            "params": {},
            "mode": None,
            "year": None,
            "year_range": None,
            "selected_features": [],
            "available_features": []
        }

        pengaturan['mode'] = st.selectbox('Mode Analisis:', ['Range Tahun', 'Per Tahun'],
                                          help="Pilih 'Range Tahun' untuk menganalisis beberapa tahun, atau 'Per Tahun' untuk fokus pada satu tahun spesifik.")

        try:
            df_temp = pd.read_excel(uploaded_file)
            df_temp.columns = [c.strip().title() for c in df_temp.columns]

            # Ekstrak Fitur (NamaFitur)
            base_features = set()
            for col in df_temp.columns:
                match = re.match(r'(.+)_(\d{4})$', col)
                if match:
                    base_features.add(match.group(1))
            pengaturan['available_features'] = sorted(list(base_features))

            if pengaturan['available_features']:
                st.subheader("Fitur Analisis")
                pengaturan['selected_features'] = st.multiselect(
                    'Pilih Fitur untuk Clustering:',
                    options=pengaturan['available_features'],
                    default=pengaturan['available_features'],
                    help="Pilih satu atau lebih fitur yang akan digunakan sebagai dasar pengelompokan."
                )
            else:
                st.warning("Tidak ada kolom fitur berformat 'NamaFitur_Tahun' yang ditemukan. Tolong Upload FIle yang Benar")
                return None

            # Ekstrak Tahun (YYYY)
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
                st.warning("Tidak ada kolom berformat _YYYY yang valid ditemukan. Tolong Upload FIle yang Benar")
                return None

            if pengaturan['mode'] == 'Per Tahun':
                pengaturan['year'] = st.selectbox('Pilih Tahun:', years_available, help="Pilih tahun untuk analisis per tahun.")
            else:
                default_range = (years_available[0], years_available[-1])
                pengaturan['year_range'] = st.select_slider(
                    'Pilih Rentang Tahun (Range):',
                    options=years_available,
                    value=default_range,
                    help="Pilih dari tahun berapa sampai tahun berapa data akan dianalisis (rata-rata)."
                )

        except Exception as e:
            st.error(f"Gagal membaca atau memproses file: {e}")
            st.stop()

        # Parameter Metode
        if pengaturan['available_features']:
            st.subheader("Metode & Parameter")
            method = st.selectbox('Metode Clustering:', ['K-Means', 'BIRCH', 'OPTICS'])
            pengaturan['method'] = method

            if method in ['K-Means', 'BIRCH']:
                pengaturan['params']['n_clusters'] = st.slider('Jumlah Cluster (K):', min_value=2, max_value=7, value=3, help="Tentukan jumlah kelompok yang ingin dibentuk.")
            if method == 'OPTICS':
                pengaturan['params']['min_samples'] = st.slider('Minimum Points (MinPts):', min_value=2, max_value=50, value=8, help="Jumlah minimum tetangga, Aturan praktis: 2 * jumlah fitur. Naikkan jika hasil 'Range Tahun'")

            with st.expander("Parameter Lanjutan (Opsional)"):
                if method == 'BIRCH':
                    pengaturan['params']['threshold'] = st.number_input('Threshold:', min_value=0.01, max_value=1.0, value=0.1, step=0.1, help="Radius maksimum...")
                    pengaturan['params']['branching_factor'] = st.number_input('Branching Factor:', min_value=2, max_value=100, value=50, help="Jumlah maksimum sub-cluster...")
                if method == 'OPTICS':
                    pengaturan['params']['xi'] = st.slider('Xi (Sensitivitas Cluster):',
                                                           min_value=0.01, max_value=0.05, value=0.01, step=0.01,
                                                           help="Nilai 0.05 (5%) adalah default yang baik. Turunkan (mis: 0.001) untuk mendeteksi lebih banyak cluster kecil.")

            if st.button('Mulai Clustering'):
                if not pengaturan['selected_features']:
                    st.warning("Harap pilih setidaknya satu fitur untuk Memulai clustering.")
                else:
                    st.session_state.run_clustering = True
                    st.session_state.results = {} # Hapus hasil lama
                    st.session_state.results_ready = False
        
        return pengaturan

# =============================================================================
# FUNGSI UTAMA APLIKASI: HALAMAN AWAL
# =============================================================================

def tampilkan_halaman_utama_info():
    """Menampilkan judul, deskripsi, dan tombol download aset."""
    st.title("Dasbor Analisis Clustering Hasil Tangkapan Laut dan Konsumsi")
    st.markdown("""
    Aplikasi ini memungkinkan Anda untuk melakukan analisis clustering pada data perikanan tangkap laut. Unggah dataset Anda, pilih metode dan parameter di sidebar, lalu klik **"Mulai Clustering"** untuk melihat hasilnya.
    """)

    st.title("📂 Dataset")
    col1, col2, col3 = st.columns(3)
    assets_path = 'files'

    def buat_tombol_download(kolom, file_name, label, download_name):
        """Helper untuk membuat tombol download di kolom."""
        with kolom:
            file_path = os.path.join(assets_path, file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        st.download_button(label=label, data=f.read(), file_name=download_name)
                except Exception as e:
                    st.warning(f"Gagal memuat {file_name}: {e}")
            else:
                st.caption(f"{label} tidak ditemukan.")

    if os.path.exists(assets_path):
        buat_tombol_download(col1, "Dataset_tangkaplaut.xlsx", "💾 Download Dataset Perikanan", "dataset_Tangkap_Laut_Dan_Konsumsi_2019-2023.xlsx")
        buat_tombol_download(col2, "Template_Dataset.xlsx", "📄 Download Template Dataset", "Template_Dataset.xlsx")
        buat_tombol_download(col3, "Manual_Book_Clustering_Perikanan_535220059.pdf", "📘 Download Buku Panduan", "Manual_Book_Fishery_Cluster.pdf")
    else:
        st.warning(f"Folder '{assets_path}' tidak ditemukan. Tombol download tidak akan muncul.")

    st.markdown("---")

# =============================================================================
# FUNGSI UTAMA APLIKASI: LOGIKA CLUSTERING (BACKEND)
# =============================================================================

def jalankan_proses_clustering(pengaturan):
    """Menjalankan seluruh logika pemrosesan data dan clustering."""
    with st.spinner('⏳ Sedang memproses clustering... Harap tunggu...'):
        try:
            df_raw = pd.read_excel(pengaturan['uploaded_file'])
            df_raw.columns = [c.strip().title() for c in df_raw.columns]
            
            selected_features = pengaturan['selected_features']
            if not selected_features:
                st.error("❌ Harap pilih minimal satu fitur di sidebar untuk memulai analisis."); st.stop()

            feature_cols = []
            df_process = df_raw.copy()
            mode = pengaturan['mode']
            
            if mode == 'Range Tahun':
                year_range = pengaturan['year_range']
                if year_range is None:
                    st.error("Rentang tahun tidak terpilih untuk mode 'Range Tahun'."); st.stop()
                start_year, end_year = int(year_range[0]), int(year_range[1])
                years_in_range = list(range(start_year, end_year + 1))

                for feature in selected_features:
                    for y in years_in_range:
                        col_name_yearly = f"{feature}_{y}"
                        if col_name_yearly in df_process.columns:
                            feature_cols.append(col_name_yearly)

            else: # Mode Per Tahun
                year = pengaturan['year']
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
            
            params = pengaturan['params']
            method = pengaturan['method']
            min_samples_needed = params.get('n_clusters', 2) if method != 'OPTICS' else params.get('min_samples', 2)
            if len(mask_valid_rows) < min_samples_needed:
                st.error(f"❌ Data valid ({len(mask_valid_rows)} baris) tidak cukup untuk clustering (membutuhkan min. {min_samples_needed})."); st.stop()

            df_valid = df_process.loc[mask_valid_rows].reset_index(drop=True)
            X_valid = X_df.loc[mask_valid_rows].reset_index(drop=True)

            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(X_valid)
            
            num_dimensions = X_scaled.shape[1]
            
            if mode == 'Range Tahun' and method == 'OPTICS' and num_dimensions > 10:
                saran_min_pts = 2 * num_dimensions
                user_min_pts = params.get('min_samples', 40) # Ambil nilai dari user
                
                # Cek apakah nilai user lebih rendah dari yang disarankan
                if user_min_pts < saran_min_pts:
                    # Tampilkan peringatan, TAPI JANGAN UBAH NILAI params
                    st.warning(f"PERINGATAN: Data dimensi tinggi ({num_dimensions} fitur) terdeteksi. "
                            f"Nilai MinPts Anda ({user_min_pts}) sangat rendah. "
                            f"Direkomendasikan MinPts >= {saran_min_pts} untuk hasil yang lebih baik. "
                            f"Eksperimen tetap dijalankan dengan nilai Anda.")
                        
            model = initialize_clustering_model(method, params)
            if model is None:
                st.error(f"Metode clustering '{method}' tidak dikenali."); st.stop()
            
            model.fit(X_scaled)
            labels = getattr(model, "labels_", np.array([-1] * len(X_scaled)))

            df_valid["Cluster"] = labels
            df_valid = categorize_clusters(df_valid) # Dari utils.py
            
            if 'Kategori' not in df_valid.columns:
                df_valid['Kategori'] = 'Cluster ' + df_valid['Cluster'].astype(str)
                df_valid['Kategori'] = df_valid['Kategori'].replace('Cluster -1', 'Outlier')

            # Simpan semua hasil ke session state
            st.session_state.results = {
                'df_valid': df_valid,
                'df_raw': df_raw,
                'X_scaled': X_scaled,
                'labels': labels,
                'mode': mode,
                'year': pengaturan.get('year'),
                'year_range': pengaturan.get('year_range'),
                'selected_features_info': selected_features,
                'feature_cols_used': feature_cols,
                'available_features': pengaturan['available_features']
            }

            st.session_state.run_clustering = False
            st.session_state.results_ready = True
            st.success("✅ Clustering selesai!")
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"Terjadi kesalahan saat proses clustering: {e}")
            st.exception(e)
            st.session_state.run_clustering = False

# =============================================================================
# FUNGSI TAMPILAN HASIL: TABEL
# =============================================================================

def tampilkan_tabel_hasil(df_valid, result_mode, year_range, year, selected_features, feature_cols_used):
    """Menampilkan tabel hasil utama dan tabel anggota cluster."""
    st.header("📋 Hasil Utama Clustering")
    st.info(f"Analisis berdasarkan fitur: **{', '.join(selected_features)}** (Mode: {result_mode})")
    
    excel_sheets_to_download = {}
    
    # --- 1. TABEL HASIL CLUSTERING UTAMA ---
    st.subheader("Tabel Hasil Clustering Utama")

    feature_cols_to_display = []
    if result_mode == 'Range Tahun':
        st.markdown("Menampilkan **data tahunan individual**.")
        if year_range:
            start_yr, end_yr = int(year_range[0]), int(year_range[1])
            years_in_r = list(range(start_yr, end_yr + 1))
            for feature in selected_features:
                for yr in years_in_r:
                    col_name = f"{feature}_{yr}"
                    if col_name in df_valid.columns:
                        feature_cols_to_display.append(col_name)
            feature_cols_to_display.sort()
        else:
            feature_cols_to_display = feature_cols_used
    else: # Mode Per Tahun
        if year:
            st.markdown(f"Menampilkan **nilai fitur aktual tahun {year}**.")
        feature_cols_to_display = feature_cols_used

    cols_to_show_main = ['Wilayah'] + feature_cols_to_display + ['Kategori']
    cols_to_show_main = [col for col in cols_to_show_main if col in df_valid.columns]
    
    df_to_download_main = df_valid[cols_to_show_main]
    st.dataframe(df_to_download_main, height=300)
    excel_sheets_to_download['Hasil_Utama'] = df_to_download_main

    # --- 2. TABEL ANGGOTA PER CLUSTER ---
    st.subheader("Tabel Anggota per Cluster")
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
            
            sheet_name = f"Anggota {kategori_name.replace(':', '')[:30]}" # Nama sheet aman
            excel_sheets_to_download[sheet_name] = df_cluster
            
    st.markdown("---")
    return excel_sheets_to_download

# =============================================================================
# FUNGSI TAMPILAN HASIL: GRAFIK ANGGOTA
# =============================================================================

def tampilkan_grafik_anggota(df_valid):
    """Menampilkan bar chart jumlah anggota dan mengembalikan figure-nya."""
    st.subheader("Jumlah Anggota per Kategori Cluster")
    fig_bar = None
    
    counts = df_valid['Kategori'].value_counts()
    ordered_categories_chart = sorted([c for c in counts.index if c != 'Outlier'])
    if 'Outlier' in counts.index:
        ordered_categories_chart.append('Outlier')
    counts = counts.reindex(ordered_categories_chart).dropna()

    bar_colors = [CATEGORY_COLORS.get(cat, '#999999') for cat in counts.index]

    fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
    bars = ax_bar.bar(counts.index, counts.values, color=bar_colors)
    ax_bar.bar_label(bars, fmt='%d')
    ax_bar.set_ylabel("Jumlah Anggota")
    ax_bar.set_xlabel("Kategori Cluster")
    plt.xticks(rotation=45, ha='right')
    ax_bar.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig_bar)
    st.markdown("---")
    # JANGAN plt.close(fig_bar) di sini, karena akan dipakai untuk Excel
    return fig_bar

# =============================================================================
# FUNGSI TAMPILAN HASIL: TOMBOL DOWNLOAD EXCEL
# =============================================================================

def tampilkan_download_excel(excel_sheets_dict, fig_bar):
    """Menampilkan tombol download laporan Excel gabungan."""
    st.subheader("Download Laporan Lengkap")
    st.markdown("Download semua tabel dan visualisasi dalam satu file Excel.")

    excel_data_gabungan = convert_dfs_to_multisheet_excel(
        sheets_dict=excel_sheets_dict,
        chart_figure=fig_bar,
        chart_sheet_name='Grafik Anggota'
    )
    
    st.download_button(
        label="📥 Download Laporan Lengkap (.xlsx)",
        data=excel_data_gabungan,
        file_name='Laporan_Hasil_Clustering_Lengkap.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheet.sheet'
    )
    plt.close(fig_bar) # Tutup figure setelah selesai dipakai
    st.markdown("---")

# =============================================================================
# FUNGSI TAMPILAN HASIL: BOXPLOT
# =============================================================================

def tampilkan_boxplot_karakteristik(df_valid, result_mode, year_range, year, selected_features):
    """Menampilkan visualisasi boxplot dan mengembalikan daftar figures."""
    st.subheader("Karakteristik Cluster (Box Plot)")
    
    figures_for_pdf_boxplot = []
    cols_to_plot_all = []

    if result_mode == 'Range Tahun':
        if year_range:
            start_yr, end_yr = int(year_range[0]), int(year_range[1])
            st.info(f"Distribusi nilai aktual per fitur ({start_yr}-{end_yr}).")
            years_in_r = list(range(start_yr, end_yr + 1))
            for feature in selected_features:
                for yr in years_in_r:
                    col = f"{feature}_{yr}"
                    if col in df_valid.columns:
                        cols_to_plot_all.append(col)
            cols_to_plot_all.sort()
    else: # Mode Per Tahun
        if year:
            st.info(f"Distribusi nilai aktual ({year}).")
            cols_to_plot_all = [f"{f}_{year}" for f in selected_features if f"{f}_{year}" in df_valid.columns]

    title_mapping = {'Nilai': 'Nilai Produksi', 'Produksi': 'Nilai Produksi', 'Nelayan': 'Nelayan', 'Volume': 'Volume', 'Konsumsi': 'Konsumsi'}
    for f in selected_features:
        if f not in title_mapping: title_mapping[f] = f
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
                        ax = axes_range[i]
                        year_name_plot = ""
                        match_year = re.search(r'_(\d{4})$', var)
                        if match_year: year_name_plot = f" ({match_year.group(1)})"
                        plot_subplot_title = f"{clean_base_feature_name}{year_name_plot}"

                        sns.boxplot(data=df_valid, x="Kategori", y=var, ax=ax, order=ordered_categories, palette=CATEGORY_COLORS)
                        ax.yaxis.set_major_formatter(ScalarFormatter())
                        ax.ticklabel_format(style='plain', axis='y')
                        ax.set_title(plot_subplot_title, fontsize=16, fontweight='bold')
                        ax.set_xlabel("Kategori", fontsize=12)
                        ax.set_ylabel(current_unit, fontsize=12)
                        ax.tick_params(axis='x', rotation=45, labelsize=11)
                        ax.grid(axis='y', linestyle='--', alpha=0.7)

                    for j in range(n_vars, len(axes_range)): fig_range.delaxes(axes_range[j])
                    plt.subplots_adjust(top=0.9, hspace=0.45, wspace=0.3)
                    
                    figures_for_pdf_boxplot.append(fig_range)
                    st.pyplot(fig_range)
                    # plt.close(fig_range) # Ditutup oleh create_multi_page_pdf

        else: # Mode Per Tahun
            st.markdown(f"*(Semua fitur terpilih untuk tahun {year})*")
            n_vars = len(cols_to_plot_all)
            n_cols = 1 if n_vars == 1 else 2
            n_rows = (n_vars + n_cols - 1) // n_cols

            fig_per_year, axes_per_year = plt.subplots(n_rows, n_cols, figsize=(8 * n_cols, 7 * n_rows), squeeze=False)
            axes_per_year = axes_per_year.flatten()

            for i, var in enumerate(cols_to_plot_all):
                ax = axes_per_year[i]
                base_feature = var.split('_')[0]
                clean_name = title_mapping.get(base_feature, base_feature)
                current_unit = FEATURE_UNITS.get(base_feature, default_unit)
                plot_subplot_title = clean_name

                sns.boxplot(data=df_valid, x="Kategori", y=var, ax=ax, order=ordered_categories, palette=CATEGORY_COLORS)
                ax.yaxis.set_major_formatter(ScalarFormatter())
                ax.ticklabel_format(style='plain', axis='y')
                ax.set_title(plot_subplot_title, fontsize=16, fontweight='bold')
                ax.set_xlabel("Kategori", fontsize=12)
                ax.set_ylabel(current_unit, fontsize=12)
                ax.tick_params(axis='x', rotation=45, labelsize=11)
                ax.grid(axis='y', linestyle='--', alpha=0.7)

            for j in range(n_vars, len(axes_per_year)): fig_per_year.delaxes(axes_per_year[j])
            plt.subplots_adjust(top=0.93, hspace=0.45, wspace=0.3)

            figures_for_pdf_boxplot.append(fig_per_year)
            st.pyplot(fig_per_year)
            # plt.close(fig_per_year) # Ditutup oleh create_multi_page_pdf

    elif not cols_to_plot_all:
        st.warning("Tidak ada fitur untuk box plot.")
        
    st.markdown("---")
    return figures_for_pdf_boxplot

# =============================================================================
# FUNGSI TAMPILAN HASIL: analisis Boxplot
# =============================================================================

def tampilkan_profil_statistik(df_valid, result_mode, year_range, year, selected_features):
    """
    Menampilkan tabel statistik deskriptif (Min, Q1, Median, Q3, Max) 
    untuk setiap kategori cluster.
    """
    st.subheader("📊 Profil Statistik Detail per Cluster")
    st.info("Tabel ini merangkum sebaran data (Min, Q1, Median, Q3, Max) untuk setiap fitur di dalam masing-masing kategori cluster.")

    # 1. Tentukan kolom fitur yang relevan (logika yang sama dari boxplot)
    relevant_feature_cols = []
    if result_mode == 'Range Tahun':
        if year_range:
            start_yr, end_yr = int(year_range[0]), int(year_range[1])
            years_in_r = list(range(start_yr, end_yr + 1))
            for feature in selected_features:
                for yr in years_in_r:
                    col = f"{feature}_{yr}"
                    if col in df_valid.columns:
                        relevant_feature_cols.append(col)
        relevant_feature_cols.sort()
    else: # Mode Per Tahun
        if year:
            relevant_feature_cols = [f"{f}_{year}" for f in selected_features if f"{f}_{year}" in df_valid.columns]

    if not relevant_feature_cols:
        st.warning("Tidak dapat membuat profil statistik, kolom fitur tidak ditemukan.")
        st.markdown("---")
        return

    # 2. Dapatkan daftar kategori/cluster yang terurut
    try:
        ordered_categories_stats = sorted([c for c in df_valid['Kategori'].unique() if c != 'Outlier'])
        if 'Outlier' in df_valid['Kategori'].unique():
            ordered_categories_stats.append('Outlier')
    except KeyError:
        st.error("Kolom 'Kategori' tidak ditemukan di hasil. Gagal membuat profil.")
        st.markdown("---")
        return

    # 3. Buat tab untuk setiap cluster agar rapi
    tabs = st.tabs(ordered_categories_stats)
    
    for i, category in enumerate(ordered_categories_stats):
        with tabs[i]:
            
            # Ambil data HANYA untuk kategori ini
            df_category = df_valid[df_valid['Kategori'] == category]
            
            # Hitung describe() HANYA pada fitur yang relevan
            stats = df_category[relevant_feature_cols].describe()
            
            # <-- PERUBAHAN DI SINI: Memilih statistik yang sesuai dengan boxplot
            # Kita memilih min, 25% (Q1), 50% (Median), 75% (Q3), dan max
            stats_keys = ['min', '25%', '50%', '75%', 'max']
            
            # Pastikan semua keys ada sebelum mencoba mengambilnya
            valid_keys = [key for key in stats_keys if key in stats.index]
            stats_display = stats.loc[valid_keys].rename(
                index={
                    'min': 'Lower Extreme (Batas Bawah)',
                    '25%': 'Q1 (Kuartil Bawah)',
                    '50%': 'Median (Q2)',
                    '75%': 'Q3 (Kuartil Atas)',
                    'max': 'Upper Extreme (Batas Atas)'
                }
            )
            # <-- AKHIR PERUBAHAN
            
            # Tampilkan tabel statistik
            st.dataframe(stats_display.style.format("{:,.2f}"))

    # Beri pemisah sebelum peta
    st.markdown("---")
# =============================================================================
# FUNGSI TAMPILAN HASIL: PETA
# =============================================================================

def tampilkan_peta_sebaran(df_valid, result_mode, year_range, year):
    """Menampilkan peta Folium interaktif dan mengembalikan figure statis."""
    st.subheader("Peta Sebaran dan Karakteristik Cluster")
    fig_map_static = None # Inisialisasi

    if "Latitude" not in df_valid.columns or "Longitude" not in df_valid.columns:
        st.warning("Kolom 'Latitude' dan 'Longitude' tidak ditemukan. Peta tidak dapat ditampilkan.")
        st.markdown("---")
        return None

    df_map = df_valid.dropna(subset=['Latitude', 'Longitude'])
    if df_map.empty:
        st.warning("Data tidak memiliki nilai Latitude/Longitude yang valid. Peta tidak dapat ditampilkan.")
        st.markdown("---")
        return None

    # Pembuatan Peta
    m = folium.Map(location=[-2.5, 120], zoom_start=4.5)
    
    FEATURE_UNITS_MAP = {'Volume': 'ton', 'Nilai': '(Rp)', 'Produksi': '(Rp)', 'Nelayan': 'orang', 'Konsumsi': 'kg/kapita'}
    
    for _, row in df_map.iterrows():
        # Buat Popup
        popup_lines = [
            f"<div style='font-weight:bold;margin-bottom:4px;'>{row.get('Wilayah', 'N/A')}</div>",
            f"<div style='margin-bottom:6px;'><b>Kategori:</b> {row.get('Kategori', 'N/A')}</div>",
            "<table style='border-collapse:collapse;'>"
        ]
        
        for feat in FEATURE_PRODUKSI: # Dari utils.py
            val_str = "N/A"
            if result_mode == 'Range Tahun':
                if year_range:
                    start_year_map, end_year_map = int(year_range[0]), int(year_range[1])
                    year_cols_map = [f"{feat}_{y}" for y in range(start_year_map, end_year_map + 1) if f"{feat}_{y}" in df_map.columns]
                    if year_cols_map:
                        values_map = [row.get(col) for col in year_cols_map if pd.notna(row.get(col))]
                        numeric_values = [v for v in values_map if isinstance(v, (int, float))]
                        if numeric_values:
                            try:
                                val_map = sum(numeric_values) / len(numeric_values)
                                unit_map = FEATURE_UNITS_MAP.get(feat, '')
                                val_str = f"{val_map:,.2f}"
                                if unit_map: val_str = f"{val_str} {unit_map}"
                            except ZeroDivisionError: val_str = "N/A"
            else: # Mode Per Tahun
                if year:
                    col_name_map = f"{feat}_{year}"
                    val_map = row.get(col_name_map)
                    if pd.notna(val_map):
                        try:
                            unit_map = FEATURE_UNITS_MAP.get(feat, '')
                            val_str = f"{float(val_map):,.2f}"
                            if unit_map: val_str = f"{val_str} {unit_map}"
                        except (ValueError, TypeError): val_str = str(val_map)
            
            popup_lines.append(f"<tr><td style='padding:2px 8px;'><b>{feat}</b></td><td style='padding:2px 8px;'>: {val_str}</td></tr>")
        
        popup_lines.append("</table>")
        popup_html = "".join(popup_lines)

        # Tentukan Warna Ikon
        color_val = '#999999'
        try:
            category = row.get('Kategori')
            if category and category in CATEGORY_COLORS:
                color_val = CATEGORY_COLORS[category]
            elif 'Cluster' in row and pd.notna(row['Cluster']):
                color_val = CLUSTER_COLORS.get(int(row['Cluster']), '#999999')
        except (ValueError, TypeError, KeyError): pass

        hex_to_name = {'#ff4d4d': 'red', '#ff8000': 'orange', '#ffcc00': 'beige', '#9933ff': 'purple', '#3366ff': 'blue', '#00cccc': 'cadetblue', '#33cc33': 'green', '#999999': 'gray'}
        color_name = hex_to_name.get(str(color_val).lower(), 'lightgray') if isinstance(color_val, str) and str(color_val).startswith('#') else str(color_val)
        
        try:
            icon = folium.Icon(icon='ship', prefix='fa', color=color_name, icon_color='white')
        except (TypeError, ValueError):
            icon = folium.Icon(icon='ship', prefix='fa', color=color_name)
        
        folium.Marker(location=[row['Latitude'], row['Longitude']], popup=folium.Popup(popup_html, max_width=350), icon=icon).add_to(m)

    # Tambahkan Legenda
    try:
        kategori_unik_map = sorted(df_map['Kategori'].dropna().unique())
        kategori_warna_map = {k: CATEGORY_COLORS.get(k, '#999999') for k in kategori_unik_map if k in CATEGORY_COLORS}
        if kategori_warna_map:
            legend_html = "<div style='position: absolute; bottom: 20px; right: 20px; z-index: 9999; background-color: rgba(255,255,255,0.95); border-radius: 8px; border: 1px solid #333; padding: 10px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-size: 13px; font-family: Arial, sans-serif; color: #000; max-height: 240px; overflow-y: auto;'><div style='font-weight:bold; font-size:14px; margin-bottom:6px; border-bottom:1px solid #ccc;'>Legenda Kategori</div>"
            for kategori, color in kategori_warna_map.items():
                legend_html += f"<div style='display:flex; align-items:center; margin-top:4px; color:#000;'><div style='width:16px; height:12px; background:{color}; border:1px solid #333; margin-right:6px; border-radius:2px;'></div><div>{kategori}</div></div>"
            legend_html += "</div>"
            legend_element = folium.Element(legend_html)
            m.get_root().html.add_child(legend_element)
    except Exception as e:
        st.warning(f"Legenda peta tidak dapat ditampilkan: {e}")

    # Tampilkan Peta Interaktif
    st_folium(m, width=1500, height=600)
    
    # Siapkan Peta Statis untuk PDF
    st.caption("Memproses peta statis untuk PDF... (mungkin perlu beberapa detik)")
    try:
        fig_map_static = get_folium_map_as_figure(m)
        if fig_map_static:
            st.caption("✔️ Peta statis siap di-download.")
        else:
            st.warning("Gagal membuat peta statis untuk PDF.")
    except Exception as e:
        st.error(f"Error saat memproses peta statis: {e}")

    st.markdown("---")
    return fig_map_static

# =============================================================================
# FUNGSI TAMPILAN HASIL: INFO WILAYAH
# =============================================================================
def tampilkan_info_lanjutan_wilayah(df_valid, feature_cols_used, selected_features):
    """Menampilkan expander dengan detail per wilayah yang dipilih."""
    st.subheader("Info Lanjutan Wilayah")

    if 'Wilayah' not in df_valid.columns or df_valid.empty or not feature_cols_used:
        st.warning("Data tidak lengkap untuk menampilkan info lanjutan wilayah.")
        st.markdown("---")
        return

    # Definisikan mapping judul fitur & unit
    title_mapping_info = {'Nilai': 'Nilai Produksi', 'Produksi': 'Nilai Produksi', 'Nelayan': 'Nelayan', 'Volume': 'Volume', 'Konsumsi': 'Konsumsi'}
    for f in selected_features:
        if f not in title_mapping_info: title_mapping_info[f] = f
    FEATURE_UNITS_INFO = {'Volume': 'Ton', 'Nilai': 'Rp', 'Produksi': 'Rp', 'Nelayan': 'Orang', 'Konsumsi': 'Kg/Kapita'}
    default_unit_info = ""

    with st.expander("Pilih Wilayah untuk Detail", expanded=False):
        # Tentukan Wilayah Awal (Satu per Cluster)
        initial_regions = []
        try:
            initial_regions_df = df_valid[df_valid['Cluster'] != -1].sort_values('Cluster').groupby('Cluster').first()
            initial_regions = initial_regions_df['Wilayah'].tolist()
            if 'Outlier' in df_valid['Kategori'].unique():
                # Pastikan ada outlier sebelum mencoba mengambilnya
                if not df_valid[df_valid['Kategori'] == 'Outlier'].empty:
                    outlier_region = df_valid[df_valid['Kategori'] == 'Outlier']['Wilayah'].iloc[0]
                    if outlier_region and outlier_region not in initial_regions:
                        initial_regions.append(outlier_region)
        except Exception:
            initial_regions = list(df_valid['Wilayah'].unique()[:3]) # Fallback

        list_wilayah_all = sorted(df_valid['Wilayah'].unique())
        selected_regions = st.multiselect(
            "Pilih Wilayah (bisa lebih dari satu):",
            options=list_wilayah_all,
            default=initial_regions,
            key='multiselect_wilayah_detail'
        )
        st.markdown("---")

        if selected_regions:
            st.write(f"Menampilkan detail untuk **{len(selected_regions)}** wilayah terpilih:")
            st.write("")
            col_left, col_right = st.columns(2)
            cols = [col_left, col_right]

            for idx, region in enumerate(selected_regions):
                target_col = cols[idx % 2]
                with target_col:
                    try:
                        selected_data = df_valid[df_valid['Wilayah'] == region].iloc[0]
                    except IndexError:
                        st.warning(f"Data wilayah '{region}' tidak ditemukan.")
                        continue

                    kategori_name = selected_data.get('Kategori', 'N/A')
                    cluster_color = CATEGORY_COLORS.get(kategori_name, '#999999')
                    color_indicator = f'<span style="display: inline-block; margin-right: 8px; width: 12px; height: 12px; background-color: {cluster_color}; border-radius: 50%;"></span>'

                    st.markdown(f"<h5>{color_indicator} <b>{region}</b></h5>", unsafe_allow_html=True)
                    st.markdown(f"**Kategori:** {kategori_name}")
                    st.markdown(f"**Nilai Fitur:**")

                    # --- [MULAI PERUBAHAN] ---
                    for col_name in feature_cols_used:
                        # Ambil nama dasar fitur (logika Anda)
                        base_feature_name = col_name.split('_')[0]
                        
                        # [BARU] Ekstrak sufiks tahun
                        year_suffix = ""
                        parts = col_name.split('_')
                        if len(parts) > 1 and parts[-1].isdigit() and len(parts[-1]) == 4:
                            year_suffix = f" ({parts[-1]})" # Hasil: " (2019)"
                        
                        # Ambil nama bersih dan unit (logika Anda)
                        clean_feature_name = title_mapping_info.get(base_feature_name, base_feature_name)
                        unit = FEATURE_UNITS_INFO.get(base_feature_name, default_unit_info)
                        
                        # [BARU] Susun label string dengan menyisipkan tahun
                        # Hasil: "Volume (2019) (Ton)"
                        label_str = f"{clean_feature_name}{year_suffix}{f' ({unit})' if unit else ''}"
                        
                        # Sisa kode Anda tidak berubah
                        value = selected_data.get(col_name, 'N/A')
                        value_str = f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
                        
                        st.markdown(
                            f"<p style='margin-bottom: 0.1em; font-size: 0.9em;'><b>{label_str}:</b> {value_str}</p>",
                            unsafe_allow_html=True
                        )
                    # --- [AKHIR PERUBAHAN] ---
                    
                    st.markdown("---")
        else:
            st.info("Pilih satu atau lebih wilayah dari daftar di atas untuk melihat detailnya.")
    st.markdown("---")
# =============================================================================
# FUNGSI TAMPILAN HASIL: EVALUASI
# =============================================================================

def tampilkan_evaluasi_clustering(X_scaled, labels, df_valid):
    """Menampilkan metrik dan plot evaluasi (Silhouette, PCA)."""
    st.subheader("⚙️ Evaluasi Kualitas Clustering")
    
    fig_eval_pdf = None # Figure gabungan untuk PDF
    n_unique_clusters = df_valid[df_valid['Cluster'] != -1]['Cluster'].nunique() if 'Cluster' in df_valid else 0

    if n_unique_clusters < 2:
        st.warning("Evaluasi tidak dapat ditampilkan karena hanya 1 cluster yang terbentuk.")
        st.markdown("---")
        return None

    valid_mask = labels != -1
    if np.sum(valid_mask) < 2:
        st.warning("Evaluasi tidak dapat ditampilkan karena data valid kurang dari 2.")
        st.markdown("---")
        return None

    try:
        num_features = X_scaled.shape[1]
        
        # --- Hitung Skor ---
        sil_score = silhouette_score(X_scaled[valid_mask], labels[valid_mask])
        dbi_score = davies_bouldin_score(X_scaled[valid_mask], labels[valid_mask])
        
        sample_silhouette_values = silhouette_samples(X_scaled[valid_mask], labels[valid_mask])
        unique_labels_plot = np.unique(labels[valid_mask])
        
        # --- Hitung PCA ---
        df_pca_all = None
        if num_features > 1:
            try:
                pca_all = PCA(n_components=2)
                X2_all = pca_all.fit_transform(X_scaled)
                df_pca_all = pd.DataFrame(X2_all, columns=['PC1', 'PC2'])
                
                # --- PERBAIKAN 1 ---
                # Ambil SEMUA kategori (termasuk 'Outlier')
                # .values akan mengubahnya jadi array numpy, memastikan indeksnya selaras
                df_pca_all['Kategori'] = df_valid['Kategori'].values # <-- PERBAIKAN DI SINI
                
            except Exception as e_pca_init:
                st.warning(f"Gagal menginisialisasi PCA: {e_pca_init}")

        # --- Tampilkan Metrik di Web ---
        sil_indicator = get_silhouette_indicator(sil_score)
        dbi_indicator = get_dbi_indicator(dbi_score)
        
        st.markdown("##### Hasil Metrik Evaluasi")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Silhouette Score", value=f"{sil_score:.3f}", help="Rentang [-1, 1]. Makin tinggi makin baik.")
            st.caption(f"**Indikator:** {sil_indicator}")
        with col2:
            st.metric(label="Davies-Bouldin Index", value=f"{dbi_score:.3f}", help="Rentang [0, ∞]. Makin rendah makin baik.")
            st.caption(f"**Indikator:** {dbi_indicator}")
        st.markdown("---")

        # --- Tampilkan Visualisasi di Web ---
        st.markdown("##### Visualisasi Hasil Clustering")
        col_web_1, col_web_2 = st.columns(2)
        
        # Plot 1: Silhouette (Web)
        with col_web_1:
            fig_sil_web, ax_sil_web = plt.subplots(figsize=(10, 8))
            y_lower = 10
            
            sorted_unique_labels = sorted(unique_labels_plot)

            for i_label in sorted_unique_labels: # Iterasi berdasarkan label integer
                ith_cluster_silhouette_values = sample_silhouette_values[labels[valid_mask] == i_label]
                ith_cluster_silhouette_values.sort()
                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                y_upper = y_lower + size_cluster_i
                
                category_name = f'Cluster {i_label}' if i_label != -1 else 'Outlier'
                
                color = CATEGORY_COLORS.get(category_name, '#999999') # Menggunakan palet CATEGORY_COLORS Anda
                
                ax_sil_web.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values, facecolor=color, edgecolor=color, alpha=0.7)
                ax_sil_web.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i_label))
                y_lower = y_upper + 10
            
            ax_sil_web.set_title("Visualisasi Silhouette per Cluster", fontsize=16)
            ax_sil_web.set_xlabel("Nilai Koefisien Silhouette")
            ax_sil_web.set_ylabel("Label Cluster")
            ax_sil_web.axvline(x=sil_score, color="red", linestyle="--")
            ax_sil_web.set_yticks([])
            ax_sil_web.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
            st.pyplot(fig_sil_web)
            plt.close(fig_sil_web)

        # Plot 2: PCA (Web)
        with col_web_2:
            fig_pca_web, ax_pca_web = plt.subplots(figsize=(10, 8))
            if df_pca_all is not None:
                
                # --- PERBAIKAN 2 ---
                # Hapus .dropna() agar 'Outlier' (yang tidak lagi NaN) ikut terbaca
                categories_from_pca = df_pca_all['Kategori'].unique() # <-- PERBAIKAN DI SINI
                
                ordered_categories = sorted([c for c in categories_from_pca if c != 'Outlier'])
                if 'Outlier' in categories_from_pca:
                    ordered_categories.append('Outlier')
                
                sns.scatterplot(data=df_pca_all, x='PC1', y='PC2', hue='Kategori', ax=ax_pca_web, 
                                palette=CATEGORY_COLORS, s=70, style='Kategori', markers=True, 
                                hue_order=ordered_categories) # Gunakan 'ordered_categories' yang sudah bersih
                ax_pca_web.set_title("Visualisasi Cluster 2D (PCA)", fontsize=16)
            elif num_features == 1:
                ax_pca_web.text(0.5, 0.5, "Plot tidak ada karena hanya 1 fitur yang dipilih.", ha='center', va='center', wrap=True, fontsize=12)
                ax_pca_web.set_title("Visualisasi Cluster 2D (PCA)", fontsize=16)
                ax_pca_web.set_xticks([]); ax_pca_web.set_yticks([])
            else:
                ax_pca_web.text(0.5, 0.5, "Gagal membuat plot PCA.", ha='center', va='center', wrap=True)
                ax_pca_web.set_title("Visualisasi Cluster 2D (PCA)", fontsize=16)
            st.pyplot(fig_pca_web)
            plt.close(fig_pca_web)

        # --- Buat Figure Gabungan untuk PDF ---
        fig_eval_pdf, (ax_sil_pdf, ax_pca_pdf) = plt.subplots(1, 2, figsize=(22, 9))
        
        # Plot 1: Silhouette (PDF)
        y_lower_pdf = 10
        sorted_unique_labels_pdf = sorted(unique_labels_plot) # Pastikan urutan sama

        for i_label_pdf in sorted_unique_labels_pdf:
            ith_cluster_silhouette_values = sample_silhouette_values[labels[valid_mask] == i_label_pdf]
            ith_cluster_silhouette_values.sort()
            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper_pdf = y_lower_pdf + size_cluster_i
            
            category_name_pdf = f'Cluster {i_label_pdf}' if i_label_pdf != -1 else 'Outlier'
            color_pdf = CATEGORY_COLORS.get(category_name_pdf, '#999999') # Menggunakan palet CATEGORY_COLORS Anda
            
            ax_sil_pdf.fill_betweenx(np.arange(y_lower_pdf, y_upper_pdf), 0, ith_cluster_silhouette_values, facecolor=color_pdf, edgecolor=color_pdf, alpha=0.7)
            ax_sil_pdf.text(-0.05, y_lower_pdf + 0.5 * size_cluster_i, str(i_label_pdf))
            y_lower_pdf = y_upper_pdf + 10
            
        ax_sil_pdf.set_title("Visualisasi Silhouette per Cluster", fontsize=16)
        ax_sil_pdf.set_xlabel("Nilai Koefisien Silhouette"); ax_sil_pdf.set_ylabel("Label Cluster")
        ax_sil_pdf.axvline(x=sil_score, color="red", linestyle="--"); ax_sil_pdf.set_yticks([])
        ax_sil_pdf.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        # Plot 2: PCA (PDF)
        if df_pca_all is not None:
            
            # --- PERBAIKAN 3 ---
            # Hapus .dropna() agar 'Outlier' ikut terbaca
            categories_from_pca_pdf = df_pca_all['Kategori'].unique() # <-- PERBAIKAN DI SINI
            
            ordered_categories_pdf = sorted([c for c in categories_from_pca_pdf if c != 'Outlier'])
            if 'Outlier' in categories_from_pca_pdf:
                ordered_categories_pdf.append('Outlier')

            sns.scatterplot(data=df_pca_all, x='PC1', y='PC2', hue='Kategori', ax=ax_pca_pdf, 
                            palette=CATEGORY_COLORS, s=70, style='Kategori', markers=True,
                            hue_order=ordered_categories_pdf) # Gunakan 'ordered_categories_pdf' yang sudah bersih
            ax_pca_pdf.set_title("Visualisasi Cluster 2D (PCA)", fontsize=16)
        elif num_features == 1:
            ax_pca_pdf.text(0.5, 0.5, "Plot tidak ada (hanya 1 fitur).", ha='center', va='center', wrap=True, fontsize=12)
            ax_pca_pdf.set_title("Visualisasi Cluster 2D (PCA)", fontsize=16)
            ax_pca_pdf.set_xticks([]); ax_pca_pdf.set_yticks([])
        else:
            ax_pca_pdf.text(0.5, 0.5, "Gagal membuat plot PCA.", ha='center', va='center', wrap=True)
            ax_pca_pdf.set_title("Visualisasi Cluster 2D (PCA)", fontsize=16)

        fig_eval_pdf.suptitle("Evaluasi Kualitas Clustering", fontsize=24, fontweight='bold')
        skor_text = f"Silhouette Score: {sil_score:.3f} ({sil_indicator})     |     Davies-Bouldin Index: {dbi_score:.3f} ({dbi_indicator})"
        fig_eval_pdf.text(0.5, 0.93, skor_text, ha='center', va='top', fontsize=14)
        plt.tight_layout(rect=[0, 0.03, 1, 0.9])

    except ValueError as ve:
        st.warning(f"Evaluasi clustering tidak dapat dihitung: {ve}")
    except Exception as e_eval:
        st.error(f"Terjadi kesalahan saat evaluasi: {e_eval}")
        if fig_eval_pdf: plt.close(fig_eval_pdf)
        fig_eval_pdf = None # Pastikan tidak ada figure rusak yang dikembalikan
        
    st.markdown("---")
    return fig_eval_pdf
# =============================================================================
# FUNGSI TAMPILAN HASIL: DOWNLOAD PDF
# =============================================================================

def tampilkan_download_pdf(figures_list):
    """Membuat cover, menggabungkan semua figure, dan menampilkan tombol download PDF."""
    if not figures_list:
        st.warning("Tidak ada visualisasi yang dihasilkan untuk laporan PDF.")
        st.markdown("---")
        return

    # Buat Cover Page
    try:
        fig_cover, ax_cover = plt.subplots(figsize=(8.5, 11))
        ax_cover.axis('off')
        now = datetime.now().strftime("%d %B %Y, %H:%M")
        fig_cover.text(0.5, 0.60, "Laporan Analisis Clustering", ha='center', fontsize=24, fontweight='bold')
        fig_cover.text(0.5, 0.55, "Hasil dan Visualisasi Data Perikanan", ha='center', fontsize=18)
        fig_cover.text(0.5, 0.48, f"Dibuat pada: {now}", ha='center', fontsize=12)
        # Masukkan cover page di AWAL daftar
        figures_list.insert(0, fig_cover)
    except Exception as e_cover:
        st.warning(f"Gagal membuat cover page PDF: {e_cover}")
        
    st.subheader("Download Laporan Visual (PDF)")
    st.markdown("Download semua grafik (Box Plot dan Peta Statis) sebagai satu file PDF multi-halaman.")
    
    pdf_data = create_multi_page_pdf(figures_list)

    st.download_button(
        label="⬇️ Download Laporan Visual sebagai PDF",
        data=pdf_data,
        file_name='Laporan_Visual_Clustering.pdf',
        mime='application/pdf'
    )
    st.markdown("---")

# =============================================================================
# FUNGSI TAMPILAN HASIL: TREN & PERINGKAT
# =============================================================================

def tampilkan_tren_tahunan(df_raw, result_mode, year_range, selected_features):
    """Menampilkan plot tren tahunan jika mode 'Range Tahun'."""
    if result_mode != 'Range Tahun':
        return # Hanya tampilkan jika mode range

    st.subheader("📈 Tren Tahunan Lokasi Teratas")
    if not selected_features:
        st.warning("Tidak ada fitur yang dipilih untuk menampilkan tren.")
        st.markdown("---")
        return
        
    selected_feature_trend = st.selectbox(
        "Pilih Fitur untuk Tren:",
        selected_features,
        key='trend_feature_selectbox',
        help="Hanya fitur yang Anda pilih untuk analisis clustering yang ditampilkan di sini."
    )
    n_top_trend = st.slider("Jumlah Lokasi untuk Tren:", min_value=5, max_value=20, value=10, key='n_top_trend_slider')

    # Logika Pengumpulan Data Tren
    start_year_trend, end_year_trend = None, None
    if year_range:
        start_year_trend, end_year_trend = int(year_range[0]), int(year_range[1])
    else: # Fallback jika year_range None
        years_available_trend = sorted(list(set(int(y) for c in df_raw.columns if (m:=re.search(r'_(\d{4})$',c)) and (y:=m.group(1)).isdigit() )))
        if years_available_trend: start_year_trend, end_year_trend = years_available_trend[0], years_available_trend[-1]

    if start_year_trend is None:
        st.warning("Tidak dapat menentukan rentang tahun untuk tren.")
        st.markdown("---")
        return

    trend_cols_with_year = []
    for c in sorted(df_raw.columns):
        m_trend = re.match(rf'{re.escape(selected_feature_trend)}_(\d{{4}})$', c, flags=re.IGNORECASE)
        if m_trend:
            try:
                y_trend = int(m_trend.group(1))
                if start_year_trend <= y_trend <= end_year_trend:
                    trend_cols_with_year.append((y_trend, c))
            except ValueError: pass
    
    trend_cols_with_year.sort()
    trend_cols = [c for y, c in trend_cols_with_year]

    if trend_cols:
        try:
            df_raw['average_trend'] = df_raw[trend_cols].apply(pd.to_numeric, errors='coerce').mean(axis=1).fillna(0)
            df_top_trend = df_raw.nlargest(n_top_trend, 'average_trend')
            years_trend_plot = [y for y, c in trend_cols_with_year]

            fig_trend, ax_trend = plt.subplots(figsize=(12, 7))
            for _, row in df_top_trend.iterrows():
                trend_values = row[trend_cols].apply(pd.to_numeric, errors='coerce')
                if not trend_values.isnull().all():
                    ax_trend.plot(years_trend_plot, trend_values, marker='o', linestyle='-', label=row.get('Wilayah', 'N/A'))

            title_suffix = f"({start_year_trend}-{end_year_trend})"
            trend_title = f"Tren Tahunan {title_suffix} - Top {n_top_trend} Lokasi: '{selected_feature_trend}'"
            ax_trend.set_title(trend_title)
            ax_trend.set_xlabel("Tahun"); ax_trend.set_ylabel(selected_feature_trend)
            ax_trend.yaxis.set_major_formatter(ScalarFormatter()); ax_trend.ticklabel_format(style='plain', axis='y')
            ax_trend.legend(title='Lokasi', bbox_to_anchor=(1.05, 1), loc='upper left'); ax_trend.grid(True, linestyle='--')
            plt.tight_layout(rect=[0, 0, 0.85, 1]); st.pyplot(fig_trend); plt.close(fig_trend)
        except Exception as e_trend:
            st.error(f"Gagal membuat plot tren: {e_trend}")
    else:
        st.warning(f"Tidak ditemukan kolom tahunan untuk '{selected_feature_trend}'.")
        
    st.markdown("---")

def tampilkan_peringkat_lokasi(df_raw, selected_features):
    """Menampilkan bar chart peringkat lokasi teratas."""
    st.subheader("🏆 Peringkat Lokasi Teratas (Berdasarkan Rata-Rata Semua Tahun)")

    if not selected_features:
        st.warning("Tidak ada fitur tersedia untuk menampilkan peringkat.")
        return

    selected_feature_top = st.selectbox("Pilih Fitur untuk Peringkat:", selected_features, key='top_feature_selectbox')
    n_top = st.slider("Jumlah Lokasi Ditampilkan:", min_value=5, max_value=20, value=10, key='n_top_slider')

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

# =============================================================================
# FUNGSI MAIN() PENGENDALI UTAMA
# =============================================================================

def main():
    """Fungsi utama yang menjalankan alur aplikasi Streamlit."""
    
    # Tampilkan Sidebar dan dapatkan pengaturan
    pengaturan = tampilkan_sidebar()
    
    # Tampilkan halaman utama (Judul, Deskripsi, Download Aset)
    tampilkan_halaman_utama_info()

    # Logika 1: Jika tombol "Mulai" ditekan
    if st.session_state.run_clustering and pengaturan:
        jalankan_proses_clustering(pengaturan) # Fungsi ini akan menyimpan hasil ke state & rerun
    
    # Logika 2: Jika hasil sudah siap
    elif st.session_state.get('results_ready', False):
        # Ambil semua data hasil dari session state
        results = st.session_state.results
        df_valid = results.get('df_valid')
        df_raw = results.get('df_raw')
        X_scaled = results.get('X_scaled')
        labels = results.get('labels')
        result_mode = results.get('mode')
        year = results.get('year')
        year_range = results.get('year_range')
        selected_features = results.get('selected_features_info', [])
        feature_cols_used = results.get('feature_cols_used', [])

        if df_valid is None or df_raw is None or labels is None:
            st.error("Gagal memuat hasil clustering. Coba jalankan ulang.")
            st.session_state.results_ready = False
            st.stop()

        # Daftar untuk menampung semua figure PDF
        figures_for_pdf = []

        # 1. Tampilkan Tabel (dan dapatkan data Excel)
        excel_sheets = tampilkan_tabel_hasil(df_valid, result_mode, year_range, year, selected_features, feature_cols_used)
        
        # 2. Tampilkan Grafik Anggota (dan dapatkan figure-nya)
        fig_bar = tampilkan_grafik_anggota(df_valid)
        
        # 3. Tampilkan Tombol Download Excel (menggunakan data dari #1 dan #2)
        tampilkan_download_excel(excel_sheets, fig_bar)
        
        # 4. Tampilkan Boxplot (dan dapatkan daftar figure-nya)
        boxplot_figs = tampilkan_boxplot_karakteristik(df_valid, result_mode, year_range, year, selected_features)
        figures_for_pdf.extend(boxplot_figs)
        
        # 5. Tampilkan Profil Statistik (Mean, Median, dll)
        tampilkan_profil_statistik(df_valid, result_mode, year_range, year, selected_features)

        # 6. Tampilkan Peta (dan dapatkan figure statisnya)
        fig_map_static = tampilkan_peta_sebaran(df_valid, result_mode, year_range, year)
        if fig_map_static:
            figures_for_pdf.append(fig_map_static)
            
        # 7. Tampilkan Info Wilayah (Expander)
        tampilkan_info_lanjutan_wilayah(df_valid, feature_cols_used, selected_features)
        
        # 8. Tampilkan Evaluasi (dan dapatkan figure gabungannya)
        fig_eval = tampilkan_evaluasi_clustering(X_scaled, labels, df_valid)
        if fig_eval:
            figures_for_pdf.append(fig_eval)
            
        # 9. Tampilkan Tombol Download PDF (menggunakan semua figure)
        tampilkan_download_pdf(figures_for_pdf)
        
        # 10. Tampilkan Tren Tahunan
        tampilkan_tren_tahunan(df_raw, result_mode, year_range, selected_features)
        
        # 11. Tampilkan Peringkat Lokasi
        tampilkan_peringkat_lokasi(df_raw, selected_features)

    # Logika 3: Halaman default (jika tidak sedang running dan hasil tidak siap)
    else:
        st.info("Selamat datang! Silakan upload file Excel Anda di sidebar untuk memulai analisis.")
        # Membersihkan state jika pengguna mengunggah file baru tapi belum klik 'mulai'
        if 'results_ready' in st.session_state:
            del st.session_state.results_ready
            del st.session_state.results

# =============================================================================
# EKSEKUSI APLIKASI
# =============================================================================

if __name__ == "__main__":
    setup_styling()
    inisialisasi_session_state()
    main()