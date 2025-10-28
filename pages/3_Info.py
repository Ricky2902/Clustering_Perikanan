import streamlit as st

st.set_page_config(
    page_title="INFO | FISHERY CLUSTER", 
    page_icon="assets/logo1.png", 
    layout="wide"
)

# === [PERUBAHAN] TAMBAHKAN BLOK KODE CSS INI ===
# Ini adalah "hack" untuk membuat sidebar gelap secara paksa

st.markdown("""
<style>
    /* Target sidebar */
    [data-testid="stSidebar"] {
        background-color: #00427A !important; /* Biru Laut Gelap */
    }

    /* Target semua teks di dalam sidebar */
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p {
        color: #FFFFFF !important; /* Paksa teks jadi putih */
    }
    
    /* Target judul di sidebar (jika ada) */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #E0F7FA !important; /* Teks judul jadi biru muda */
    }

    /* Target link/menu navigasi di sidebar */
    [data-testid="stSidebar"] a {
        color: #FFFFFF !important; /* Teks link jadi putih */
    }

    /* Target ikon panah expander di sidebar (jika ada) */
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
        color: #FFFFFF !importan;
    }
</style>
""", unsafe_allow_html=True)

# --- Konten Halaman ---
st.title("ℹ️ Pusat Informasi")
st.write("Temukan jawaban atas pertanyaan umum mengenai aplikasi, data, dan metode yang digunakan di bawah ini.")
st.markdown("---")

# --- Bagian Tanya Jawab menggunakan Expander ---

st.header("Umum")
with st.expander("Apa tujuan utama dari aplikasi web ini?"):
    st.write("""
        Tujuan utama aplikasi ini adalah untuk menyediakan sebuah alat bantu (decision support tool) yang interaktif dan visual bagi para pemangku kepentingan di sektor perikanan. 
        
        Dengan menerapkan algoritma *clustering*, aplikasi ini dapat:
        - **Mengelompokkan** wilayah-wilayah perikanan tangkap laut di Indonesia ke dalam beberapa kategori (misalnya: 'Rendah', 'Sedang', 'Tinggi') berdasarkan karakteristiknya.
        - **Mengidentifikasi pola** geografis dan tren dari data perikanan dari tahun ke tahun.
        - **Menyediakan dasar** untuk pengambilan kebijakan yang lebih tepat sasaran, seperti alokasi sumber daya, program bantuan, atau fokus pengembangan wilayah.
    """)

st.header("Data")
with st.expander("Data apa saja yang digunakan dalam analisis ini?"):
    st.write("""
        Aplikasi ini dirancang untuk menganalisis data time-series (data dari tahun ke tahun) dari sektor perikanan tangkap laut. Fitur utama yang dianalisis adalah:
        - **Nelayan**: Jumlah nelayan yang terdata di suatu wilayah.
        - **Volume**: Total volume ikan yang didaratkan (dalam ton).
        - **Produksi**: Nilai produksi dari hasil tangkapan (biasanya dalam Rupiah atau Dolar).
        - **Konsumsi**: Tingkat konsumsi ikan per kapita di wilayah tersebut.

        Selain itu, data geografis juga dibutuhkan:
        - **Wilayah**: Nama kabupaten/kota atau provinsi.
        - **Latitude & Longitude**: Koordinat geografis untuk pemetaan.
    """)

with st.expander("Dari mana sumber data ini didapatkan?"):
    st.write("""
        Data yang digunakan dalam aplikasi ini bersumber dari basis data statistik publik yang disediakan oleh lembaga pemerintah terkait. Sumber utamanya adalah:
        - **Kementerian Kelautan dan Perikanan (KKP)**: Sebagai penyedia utama data statistik perikanan nasional.
        - **Badan Pusat Statistik (BPS)**: Untuk data pendukung seperti demografi atau data ekonomi regional.
        
        Pengguna juga dapat mengunggah dataset mereka sendiri selama formatnya sesuai dengan template yang disediakan di halaman **Clustering**.
    """)

st.header("Metodologi")
with st.expander("Metode clustering apa saja yang tersedia?"):
    st.write("""
        Aplikasi ini menyediakan beberapa algoritma clustering populer yang memiliki karakteristik berbeda:
        
        - **K-Means**: Algoritma yang paling umum digunakan. Ia mengelompokkan data dengan mencari titik pusat (centroid) untuk setiap cluster dan memasukkan data ke cluster dengan pusat terdekat. Cepat dan efisien untuk dataset besar.
        
        - **BIRCH**: (Balanced Iterative Reducing and Clustering using Hierarchies). Sangat efisien untuk dataset yang sangat besar karena ia meringkas data ke dalam struktur pohon (CF-Tree) sebelum melakukan clustering.
        
        - **OPTICS**: (Ordering Points To Identify the Clustering Structure). Algoritma berbasis kepadatan (density-based) yang sangat baik dalam menemukan cluster dengan bentuk yang tidak beraturan dan juga mampu mengidentifikasi *outlier* (data pencilan) yang tidak termasuk dalam cluster manapun.
    """)

with st.expander("Bagaimana cara membaca hasil clustering?"):
    st.write("""
        Setelah proses clustering selesai, Anda akan mendapatkan beberapa hasil utama:
        - **Tabel Hasil**: Menunjukkan setiap wilayah masuk ke 'Cluster' nomor berapa dan apa 'Kategori'-nya (misal: 'Rendah', 'Tinggi'). Kategori ini ditentukan dari skor rata-rata gabungan semua fitur.
        - **Peta Sebaran**: Memberikan gambaran visual tentang letak geografis setiap cluster. Ini membantu Anda melihat apakah ada pola regional.
        - **Grafik Evaluasi**: Membantu Anda (sebagai analis) untuk menilai seberapa "baik" atau valid pengelompokan yang dihasilkan.
        - **Analisis Lanjutan**: Tab ini berisi visualisasi detail untuk memahami karakteristik setiap cluster (misalnya, cluster 'Tinggi' unggul di fitur apa saja) dan melihat tren dari waktu ke waktu.
    """)

