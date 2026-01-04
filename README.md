# Clustering_Perikanan
Analisis Klaster Perikanan Tangkap Indonesia (BIRCH, K-Means, OPTICS)Proyek ini merupakan aplikasi berbasis website yang dikembangkan untuk mengelompokkan kabupaten/kota di Indonesia berdasarkan karakteristik perikanan tangkap laut, meliputi volume produksi, nilai produksi, dan tingkat konsumsi per kapita. Sistem ini bertujuan untuk mendukung pemetaan potensi maritim strategis guna mendukung SDG 14 (Life Below Water).🚀 Fitur UtamaKomparasi Algoritma: Implementasi K-Means, BIRCH, dan OPTICS untuk menemukan struktur data terbaik.Analisis Temporal: Pemrosesan data tahunan (2019-2023) untuk akurasi yang lebih tinggi dibanding data gabungan.Evaluasi Matriks: Perhitungan otomatis skor Silhouette Coefficient dan Davies-Bouldin Index (DBI).Visualisasi: Boxplot distribusi fitur dan pemetaan wilayah untuk setiap klaster.🛠️ Panduan InstalasiPastikan Anda telah menginstal Python 3.9+ sebelum memulai.1. Clone RepositoryBashgit clone https://github.com/Ricky2902/Clustering_Perikanan.git
cd Clustering_Perikanan
2. Setup Virtual Environment (Envi)Sangat disarankan untuk menggunakan virtual environment agar tidak terjadi konflik pustaka:Windows:Bashpython -m venv env
.\env\Scripts\activate
macOS/Linux:Bashpython3 -m venv env
source env/bin/activate
3. Instalasi DependensiInstal semua pustaka (libraries) yang diperlukan melalui file requirements.txt:Bashpip install --upgrade pip
pip install -r requirements.txt
💻 Cara Menjalankan ProgramJalankan perintah berikut di terminal Anda untuk membuka aplikasi di browser:Bashstreamlit run app.py
Aplikasi akan secara otomatis terbuka pada alamat: http://localhost:8501.📊 Ringkasan Hasil PenelitianAlgoritma Terbaik: BIRCH terbukti paling unggul dalam memetakan data perikanan nasional.Konfigurasi Optimal: Pengelompokan menjadi $K=2$ klaster.Performa Tertinggi: Pada data tahun 2023, skor Silhouette mencapai 0,722 dan DBI 0,580.Struktur Klaster:Klaster 1 (Anomali): 10 wilayah dengan produktivitas ekstrem (Sentra Produksi Utama).Klaster 0 (Umum): 323 wilayah dengan tingkat produksi rendah-menengah.📦 Tech StackLanguage: Python.Framework: Streamlit.Data Analysis: NumPy, Pandas, Scikit-Learn.Visualization: Matplotlib, Seaborn.
Validasi: Program ini telah lulus uji Black Box 100% dan telah melalui tahap User Acceptance Test (UAT).

