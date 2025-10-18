import pandas as pd
from sklearn.cluster import KMeans, Birch, OPTICS
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================================
# KONFIGURASI UTAMA APLIKASI
# =============================================================================

# Fitur yang akan dicari dan dianalisis secara otomatis dari file Excel.
# Pastikan nama kolom di Excel Anda diawali dengan nama-nama ini (contoh: "Produksi_2020").
FEATURE_PRODUKSI = ['Nelayan', 'Volume', 'Produksi', 'Konsumsi']

# Palet warna untuk konsistensi visualisasi di seluruh aplikasi.
COLOR_PALETTE = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink']


# =============================================================================
# FUNGSI-FUNGSI BANTUAN UNTUK CLUSTERING
# =============================================================================

def initialize_clustering_model(method, params):
    """
    Menginisialisasi model clustering berdasarkan pilihan pengguna.
    Fungsi ini memilih model yang sesuai dan mengaturnya dengan parameter standar dan lanjutan.
    
    Args:
        method (str): Nama metode clustering ('K-Means', 'BIRCH', 'OPTICS').
        params (dict): Dictionary berisi parameter yang dipilih pengguna dari sidebar.
        
    Returns:
        model: Objek model scikit-learn yang sudah diinisialisasi.
    """
    if method == 'K-Means':
        return KMeans(
            n_clusters=params.get('n_clusters', 3), 
            random_state=42, 
            n_init='auto'  # Menggunakan nilai default modern untuk menghindari warning
        )
    if method == 'BIRCH':
        return Birch(
            n_clusters=params.get('n_clusters', 3),
            threshold=params.get('threshold', 0.5),
            branching_factor=params.get('branching_factor', 50)
        )
    if method == 'OPTICS':
        # Parameter 'eps' diatur ke None jika tidak di-override, yang berarti tak terbatas (infinity)
        # Ini adalah perilaku default dan direkomendasikan untuk OPTICS.
        return OPTICS(
            min_samples=params.get('min_samples', 5),
            eps=params.get('eps', None) 
        )
    # Jika tidak ada metode yang cocok, kembalikan None untuk penanganan error
    return None

def categorize_clusters(df):
    """
    Memberi label kategori yang dinamis dan mudah dibaca (Rendah, Sedang, Tinggi, dll.) pada setiap cluster.
    Kategori ditentukan berdasarkan skor rata-rata gabungan dari semua fitur dan jumlah total cluster yang terbentuk.
    
    Args:
        df (DataFrame): DataFrame yang sudah memiliki kolom 'Cluster'.
        
    Returns:
        DataFrame: DataFrame yang sama dengan tambahan kolom 'Kategori'.
    """
    if 'Cluster' not in df.columns or df['Cluster'].nunique() == 0:
        return df
        
    feature_cols = [c for c in df.columns if any(f.lower() in c.lower() for f in FEATURE_PRODUKSI)]
    
    if not feature_cols:
        df['Kategori'] = 'Cluster ' + df['Cluster'].astype(str)
        return df
    
    # Pisahkan outlier (cluster -1 dari OPTICS) dari cluster valid untuk perhitungan peringkat
    valid_clusters_df = df[df['Cluster'] != -1]
    
    # Jika semua data ternyata adalah outlier, beri label dan kembalikan
    if valid_clusters_df.empty:
        df['Kategori'] = 'Outlier'
        return df
        
    # Hitung skor rata-rata gabungan untuk setiap cluster yang valid
    cluster_means = valid_clusters_df.groupby('Cluster')[feature_cols].mean()
    cluster_means['agg_score'] = cluster_means.mean(axis=1)
    
    # Urutkan cluster dari skor terendah ke tertinggi
    cluster_means = cluster_means.sort_values('agg_score')
    
    # Kamus (dictionary) untuk pemetaan label berdasarkan jumlah cluster
    label_map_by_k = {
        2: ['Rendah', 'Tinggi'],
        3: ['Rendah', 'Sedang', 'Tinggi'],
        4: ['Sangat Rendah', 'Rendah', 'Sedang', 'Tinggi'],
        5: ['Sangat Rendah', 'Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi'],
        6: ['Sangat Rendah', 'Rendah', 'Cukup Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi'],
        7: ['Sangat Rendah', 'Rendah', 'Cukup Rendah', 'Sedang', 'Cukup Tinggi', 'Tinggi', 'Sangat Tinggi']
    }
    
    num_clusters = len(cluster_means)
    labels = label_map_by_k.get(num_clusters)
    
    # Buat pemetaan dari nomor cluster (misal: 0, 1, 2) ke label kategori ('Rendah', 'Sedang', 'Tinggi')
    mapping = {cluster_id: labels[i] if labels and i < len(labels) else f'Kategori {i+1}' 
               for i, cluster_id in enumerate(cluster_means.index)}
    
    # Tambahkan pemetaan khusus untuk outlier jika ada
    mapping[-1] = 'Outlier'
            
    # Terapkan pemetaan untuk membuat kolom 'Kategori' baru
    df['Kategori'] = df['Cluster'].map(mapping)
    return df

def boxgrid_per_cluster(df: pd.DataFrame, variabel, judul: str):
    """
    Membuat grid box plot untuk setiap fitur guna membandingkan karakteristik antar cluster.
    """
    df = df.copy()

    # Definisikan mapping untuk judul plot yang lebih baik dan deskriptif
    indikator_deskripsi = {
        'Nelayan_Avg': 'Rata-rata Nelayan',
        'Volume_Avg': 'Rata-rata Volume (Ton)',
        'Produksi_Avg': 'Rata-rata Produksi (Ton)',
        'Konsumsi_Avg': 'Rata-rata Konsumsi (Ton)'
    }
    
    mapping = {k: indikator_deskripsi.get(k, k) for k in variabel}
    df_plot = df.rename(columns=mapping)
    variabel_jelas = [mapping.get(v, v) for v in variabel]

    n_vars = len(variabel_jelas)
    n_cols = 2  # Atur 2 kolom per baris agar lebih rapi untuk 4 fitur
    n_rows = (n_vars + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8 * n_cols, 6 * n_rows))
    axes = axes.flatten()

    # Dapatkan urutan kategori yang benar untuk plotting yang konsisten
    category_order = sorted(df_plot['Kategori'].unique())

    for i, var in enumerate(variabel_jelas):
        if var not in df_plot.columns:
            continue
        sns.boxplot(
            data=df_plot, x="Kategori", y=var, hue="Kategori",
            palette="Set2", legend=False, ax=axes[i], order=category_order
        )
        axes[i].set_title(f'Distribusi {var} per Cluster', fontsize=14)
        axes[i].set_xlabel("Kategori Cluster", fontsize=12)
        axes[i].set_ylabel("Nilai Rata-rata", fontsize=12)
        axes[i].tick_params(axis='x', rotation=45)

    # Sembunyikan subplot yang tidak terpakai
    for j in range(len(variabel_jelas), len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(judul, y=1.03, fontsize=18, fontweight='bold')
    plt.tight_layout(pad=3.0)
    return fig

