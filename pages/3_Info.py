import streamlit as st

st.set_page_config(
    page_title="INFO | FISHERY CLUSTER", 
    page_icon="assets/logo1.png", 
    layout="wide"
)

# === [KODE CSS ANDA] ===
# (Ini dipertahankan untuk membuat sidebar gelap)

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
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Konten Halaman ---
st.title("Pusat Informasi")
st.write("Temukan jawaban atas pertanyaan umum mengenai aplikasi, data, dan metode yang digunakan di bawah ini.")
st.markdown("---")

# --- Bagian Tanya Jawab menggunakan Expander ---

# === 1. HEADER UMUM ===
st.header("Umum")

with st.expander("Alasan Aplikasi Web ini dibuat?"):
    st.write("""
        Website ini dibuat sebagai alat bantu untuk **mengelompokkan dan menganalisis data produksi perikanan tangkap laut di Indonesia**. 
        
        Analisis data perikanan secara manual seringkali rumit dan sulit untuk menemukan pola tersembunyi. Aplikasi ini menyederhanakan proses tersebut dengan menerapkan metode *clustering* dan **menghasilkan hasil analisis secara visual**, terutama melalui visualisasi peta interaktif dan grafik.
    """)

with st.expander("Apa tujuan dan manfaat dari website ini?"):
    st.write("""
        Tujuan utama dari aplikasi ini adalah untuk menjawab beberapa pertanyaan penelitian kunci terkait data perikanan tangkap laut di Indonesia. Manfaatnya adalah menyediakan wawasan berbasis data untuk berbagai pemangku kepentingan.
        
        Secara spesifik, tujuan dan manfaat aplikasi ini adalah:
        
        1.  **Menerapkan Metode Clustering**: Menunjukkan bagaimana metode K-Means, BIRCH, dan OPTICS dapat digunakan untuk mengelompokkan kabupaten/kota di Indonesia berdasarkan data volume dan nilai produksi perikanan.
        
        2.  **Menemukan Jumlah Cluster Optimal**: Membantu menentukan berapa jumlah klaster optimal dari masing-masing metode melalui evaluasi *validity index* (Silhouette Coefficient dan Davies-Bouldin Index) untuk merepresentasikan kondisi produksi perikanan secara akurat.
        
        3.  **Membandingkan Performa Metode**: Menyajikan data perbandingan performa antara K-Means, BIRCH, dan OPTICS dalam hal kualitas hasil pengelompokan (berdasarkan skor evaluasi) dan efisiensi komputasi.
        
        4.  **Memberikan Wawasan (Insight)**: Menjabarkan karakteristik unik dari setiap klaster yang terbentuk dan bagaimana hasil pengelompokan ini dapat digunakan untuk memberikan wawasan dalam pencapaian *Sustainable Development Goals (SDG) 14* (Ekosistem Lautan).
        
        Bagi masyarakat umum, aplikasi ini diharapkan dapat **membantu memahami peta cluster wilayah produksi perikanan** di Indonesia. Bagi peneliti atau mahasiswa, aplikasi ini diharapkan bisa menjadi alat bantu untuk **mengetahui dan menganalisis *clustering* perikanan** di Indonesia secara lebih mudah.
    """)

# === 2. HEADER DATA ===
st.header("Data")

with st.expander("Fitur apa saja yang digunakan?"):
    st.write("""
        Aplikasi ini menggunakan beberapa fitur (kolom) kunci dari data perikanan tangkap laut untuk melakukan analisis:
        
        - **Nelayan**: Jumlah total nelayan yang terdata di suatu wilayah.
        - **Volume**: Total berat ikan yang didaratkan/diproduksi (satuan: Ton).
        - **Produksi**: Nilai moneter/ekonomi dari hasil tangkapan (satuan: Rupiah).
        - **Konsumsi**: Angka konsumsi ikan per kapita di wilayah tersebut.
        
        Data pendukung yang wajib ada di dataset Anda:
        - **Wilayah**: Nama kabupaten/kota atau provinsi.
        - **Tahun**: Tahun pencatatan data.
        - **Latitude**: Koordinat garis lintang.
        - **Longitude**: Koordinat garis bujur.
    """)

with st.expander("Sumber data berasal dari mana?"):
    st.write("""
        Sumber data utama yang digunakan untuk dataset demo pada aplikasi ini berasal dari portal **Satu Data Kementerian Kelautan dan Perikanan (KKP)**, yang merupakan situs resmi statistik Kementrian Kelautan dan Perikanan.
        
        - Portal Satu Data KKP: [https://statistik.kkp.go.id/](https://statistik.kkp.go.id/)
    """)

with st.expander("Apa isi dataset yang sudah tersedia (dataset demo)?"):
    st.write("""
        Dataset demo yang sudah tersedia di aplikasi ini adalah data gabungan dari beberapa tahun (misalnya: 2018-2022) yang mencakup seluruh provinsi/kabupaten/kota di Indonesia.
        
        Isi fiturnya adalah:
        - `Tahun`
        - `Wilayah`
        - `Latitude`
        - `Longitude`
        - `Nelayan` (Jumlah nelayan)
        - `Volume` (dalam Ton)
        - `Nilai` (dalam Rupiah)
        - `Konsumsi` (per kapita)
    """)

with st.expander("Bagaimana cara mengisi template dataset?"):
    st.write("""
        Template dataset (file `.xlsx` atau `.csv`) adalah fondasi agar aplikasi ini dapat membaca data Anda. Berikut adalah langkah-langkah untuk mengisinya:

        1.  **Unduh Template**: Di halaman "Clustering", unduh file template yang disediakan.
        2.  **Buka di Excel/Spreadsheet**: Buka file tersebut di Microsoft Excel atau Google Sheets.
        3.  **Wajib Diisi**: Pastikan Anda mengisi kolom-kolom berikut untuk setiap baris data:
            - `Tahun`: Tahun pencatatan data didalam kolom fitur (misal: Volume_2020).
            - `Wilayah`: Nama wilayah (misal: "Kabupaten Aceh Besar").
            - `Latitude`: Koordinat latitude (misal: 5.5485).
            - `Longitude`: Koordinat longitude (misal: 95.3238).
            - `Nelayan`: Jumlah nelayan (wajib angka, misal: 1500).
            - `Volume`: Jumlah volume dalam Ton (wajib angka, misal: 3000.5).
            - `Nilai`: Nilai produksi dalam Rp (wajib angka, misal: 5000000000).
            - `Konsumsi`: Angka konsumsi (wajib angka, misal: 45.3).
        4.  **Tanpa Sel Kosong**: **Sangat Penting!** Pastikan tidak ada sel yang kosong (missing value / NaN) di kolom angka (`Nelayan`, `Volume`, `Produksi`, `Konsumsi`). Jika data tidak ada, isi dengan `0`.
        5.  **Simpan File**: Simpan file Anda dalam format `.xlsx` atau `.csv`.
        6.  **Unggah**: Kembali ke aplikasi dan unggah file yang sudah Anda isi.
    """)

# === 3. HEADER METODOLOGI ===
st.header("Metodologi")

with st.expander("Metode apa saja yang digunakan?"):
    st.write("""
        Aplikasi ini menyediakan tiga algoritma *clustering* populer dari pustaka `scikit-learn` Python. Anda dapat memilih salah satu tergantung pada karakteristik data dan tujuan Anda:
        
        1.  **K-Means**
        2.  **BIRCH**
        3.  **OPTICS**
    """)

with st.expander("Apa itu metode K-Means?"):
    st.write("""
        **Apa itu K-Means?**
        K-Means adalah algoritma *clustering* berbasis **centroid (titik pusat)**. Ini adalah metode yang paling umum dan paling sederhana. Ia mencoba membagi data Anda ke dalam **'K'** jumlah cluster.
        
        **Nilai Wajib Diisi:**
        - **Nilai 'K' (Jumlah Cluster)**: Ini adalah parameter **wajib** dan paling penting.
        - **Apa itu Nilai 'K'?**: 'K' adalah **jumlah cluster yang Anda ingin temukan**. Anda harus memberi tahu algoritma berapa banyak kelompok yang Anda cari (misal: 3 kelompok 'Rendah', 'Sedang', 'Tinggi').
        - **Saran Pengisian**: Memilih 'K' yang tepat adalah kunci. Jika Anda tidak yakin, **mulailah dengan K=3 atau K=4** untuk melihat pengelompokan dasar. Anda dapat mencoba nilai K yang berbeda dan membandingkan **Skor Evaluasi** (Silhouette Score) untuk melihat nilai K mana yang memberikan hasil terbaik.
    """)

with st.expander("Apa itu metode BIRCH?"):
    st.write("""
        **Apa itu BIRCH?**
        BIRCH (Balanced Iterative Reducing and Clustering using Hierarchies) adalah algoritma yang dirancang khusus untuk menangani dataset yang **sangat besar** dengan cepat. Ia meringkas data ke dalam struktur pohon (CF-Tree) sebelum melakukan clustering.
        
        **Nilai Wajib Diisi:**
        - **Nilai 'K' (Jumlah Cluster)**: Sama seperti K-Means, ini adalah parameter **wajib** untuk menentukan jumlah cluster final yang Anda inginkan.
        - **Saran Pengisian**: Mulailah dengan **K=3 atau K=4**.
        
        **Nilai Opsional (Bisa Diisi Manual atau Otomatis):**
        Aplikasi ini akan mengatur nilai *default* terbaik jika Anda tidak mengisinya. Namun, Anda bisa mengaturnya manual:
        - **Threshold (Ambang Batas)**: Radius maksimum dari sub-cluster di pohon CF.
            - *Saran Manual*: Nilai **0.1** adalah titik awal yang umum untuk data yang sudah di normalisasi.
        - **Branching Factor (Faktor Percabangan)**: Jumlah maksimum entri di setiap node pohon.
            - *Saran Manual*: Nilai *default* **50** biasanya sudah baik.
    """)

with st.expander("Apa itu metode OPTICS?"):
    st.write("""
        **Apa itu OPTICS?**
       OPTICS (Ordering Points To Identify the Clustering Structure) adalah algoritma clustering berbasis kepadatan (density-based). Metode ini sangat baik untuk menemukan cluster dengan bentuk yang tidak beraturan dan mengidentifikasi outlier (data pencilan, ditandai -1).

Nilai Wajib Diisi:

Min Samples (MinPts): Ini adalah parameter wajib.

Apa itu Min Samples?: Ini adalah jumlah minimum data/titik yang harus berkumpul berdekatan agar dianggap sebagai wilayah padat (inti cluster).

Saran Pengisian: Aturan umum yang baik adalah mengaturnya menjadi 2 kali jumlah fitur yang Anda gunakan. Jika Anda menggunakan 4 fitur (Nelayan, Volume, Produksi, Konsumsi), maka Min Samples = 8 adalah titik awal yang sangat baik.

Nilai Opsional (Bisa Diisi Manual atau Otomatis):

Epsilon (eps): Ini adalah parameter yang menentukan jarak pencarian maksimum untuk mencari tetangga.

Sistem Otomatis (Sangat Disarankan): Secara default, sistem akan menggunakan nilai Tak Terhingga (Infinity) jika Anda tidak mencentang box "Tentukan Epsilon (eps) secara manual".

Mengapa Otomatis Lebih Baik?: Ini adalah cara kerja OPTICS yang sesungguhnya. Dengan membiarkannya tak terhingga, algoritma dapat menemukan cluster dengan tingkat kepadatan yang berbeda-beda (ada yang padat, ada yang renggang).

Saran Manual (Tidak Disarankan): Jika Anda tetap ingin mengisinya secara manual, ingat bahwa data Anda sudah dinormalisasi (skala 0-1).

Saran Nilai: Gunakan nilai yang sangat kecil. Titik awal yang baik adalah antara 0.1 dan 1.0 (misalnya, coba 0.5).
    """)

# === 4. HEADER HASIL CLUSTERING ===
st.header("Hasil Clustering")

with st.expander("Apa saja hasil clustering yang ditampilkan?"):
    st.write("""
        Setelah Anda menjalankan proses analisis, aplikasi akan menampilkan beberapa output secara berurutan:
        
        1.  **Tabel Cluster Utama**: Ringkasan statistik (rata-rata, min, max) dari setiap fitur untuk setiap cluster yang terbentuk.
        2.  **Tabel Cluster Anggota**: Daftar lengkap wilayah/data dan penetapan clusternya (`Cluster` dan `Kategori`).
        3.  **Visualisasi Barchart Cluster**: Grafik batang yang membandingkan nilai rata-rata setiap fitur antar cluster (sangat berguna untuk melihat profil cluster).
        4.  **Boxplot**: Menunjukkan sebaran dan variasi data (termasuk outlier) untuk setiap fitur di dalam setiap cluster.
        5.  **Peta Interaktif**: Visualisasi geografis yang menunjukkan sebaran lokasi setiap cluster di peta Indonesia.
        6.  **Info Lanjutan Wilayah**: (Tergantung implementasi) Detail spesifik per wilayah.
        7.  **Hasil Evaluasi Silhouette dan DBI Score**: Angka metrik utama untuk menilai kualitas cluster (Silhouette mendekati 1, DBI mendekati 0).
        8.  **Visualisasi Silhouette dan Plot PCA**: Grafik visual dari skor Silhouette per cluster dan plot PCA 2D untuk melihat pemisahan cluster.
        9.  **Tren per Fitur**: Grafik garis (jika data time-series) yang menunjukkan tren (misal: volume) dari tahun ke tahun untuk setiap cluster.
        10. **Top Data per Fitur**: Daftar data teratas (misal: 5 wilayah dengan volume tertinggi) di dalam setiap cluster.
    """)

with st.expander("Bagaimana cara membaca hasil Clustering?"):
    st.write("""
        Berikut adalah panduan untuk menginterpretasi hasil Anda secara berurutan:
        
        1.  **Lihat Evaluasi (Silhouette/DBI Score)**: Pertama, cek skor ini. Jika Silhouette Score Anda rendah (misal: di bawah 0.25) atau DBI tinggi (misal: di atas 1.5), hasil clustering mungkin kurang valid. Jika skornya baik (Silhouette > 0.5, DBI < 1.0), lanjutkan.
        
        2.  **Pahami Profil Cluster (Barchart/Radar Chart & Tabel Utama)**: Lihat Barchart. Cluster mana yang `Volume` dan `Produksi`-nya tinggi? Cluster mana yang `Nelayan`-nya banyak tapi produksinya rendah? Ini adalah "profil" atau "DNA" dari setiap cluster. `Tabel Cluster Utama` memberi Anda angka pastinya.
        
        3.  **Tentukan Kategori**: Berdasarkan profil tadi, Anda bisa menamai cluster Anda. Misal: Cluster 2 (yang `Volume` dan `Produksi`-nya tinggi) Anda sebut "Potensi Tinggi". Cluster 0 (yang semuanya rendah) Anda sebut "Potensi Rendah".
        
        4.  **Lihat Sebaran (Peta Interaktif)**: Sekarang lihat petanya. Di mana cluster "Potensi Tinggi" Anda berada? Apakah mereka berkumpul di Indonesia Timur? Apakah cluster "Potensi Rendah" ada di Jawa? Ini menunjukkan pola geografis.
        
        5.  **Periksa Anggota (Tabel Anggota)**: Cari wilayah spesifik yang Anda kenal di `Tabel Cluster Anggota` untuk melihat dia masuk ke cluster/kategori apa.
        
        6.  **Analisis Tren & Detail (Grafik Tren & Boxplot)**: Terakhir, lihat grafik tren untuk melihat apakah performa cluster "Potensi Tinggi" naik atau turun dari tahun ke tahun. Gunakan `Boxplot` untuk melihat seberapa bervariasi data di dalam satu cluster.
    """)

with st.expander("Hasil yang bisa Di-download?"):
    st.write("""
        Aplikasi ini memungkinkan Anda mengunduh hasil analisis dalam dua format utama:
        
        1.  **File Excel (`.xlsx`)**:
            - Berisi data mentah hasil clustering.
            - Termasuk **Tabel Cluster Utama** (statistik per cluster).
            - Termasuk **Tabel Cluster Anggota** (daftar lengkap data dan clusternya).
            - (Terkadang) menyertakan data untuk **Visualisasi Cluster (Barchart)**.
            
        2.  **File PDF (`.pdf`)**:
            - Berisi laporan visual ringkas dari hasil analisis.
            - Termasuk **Boxplot** per fitur.
            - Termasuk gambar **Peta Sebaran Cluster**.
            - Mencantumkan **Nilai Silhouette dan DBI Score**.
            - Termasuk gambar **Visualisasi Silhouette** dan **Plot PCA**.
    """)

