import pandas as pd
from sklearn.cluster import KMeans, Birch, OPTICS
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================================
# KONFIGURASI UTAMA APLIKASI
# =============================================================================

# Fitur yang akan dicari dan dianalisis secara otomatis dari file Excel.
# Pastikan nama kolom di Excel Anda diawali dengan nama-nama ini (contoh: "Produksi_2020").
FEATURE_PRODUKSI = ['Volume', 'Nilai', 'Konsumsi', 'Nelayan']

# Skema warna konsisten untuk setiap jumlah cluster (2-7)
# Pola: Merah → Orange → Kuning → Ungu → Biru → Cyan → Hijau
CLUSTER_COLOR_SCHEMES = {
    2: ['#ff4d4d', '#33cc33'],  # Merah, Hijau
    3: ['#ff4d4d', '#9933ff', '#33cc33'],  # Merah, Ungu, Hijau
    4: ['#ff4d4d', '#ff8000', '#3366ff', '#33cc33'],  # Merah, Orange, Biru, Hijau
    5: ['#ff4d4d', '#ff8000', '#9933ff', '#3366ff', '#33cc33'],  # Merah, Orange, Ungu, Biru, Hijau
    6: ['#ff4d4d', '#ff8000', '#ffcc00', '#9933ff', '#3366ff', '#33cc33'],  # Merah, Orange, Kuning, Ungu, Biru, Hijau
    7: ['#ff4d4d', '#ff8000', '#ffcc00', '#9933ff', '#3366ff', '#00cccc', '#33cc33']  # Merah, Orange, Kuning, Ungu, Biru, Cyan, Hijau
}

# Warna default untuk cluster individual (backward compatibility)
CLUSTER_COLORS = {
    0: '#ff4d4d',  # Merah
    1: '#ff8000',  # Orange
    2: '#ffcc00',  # Kuning
    3: '#9933ff',  # Ungu
    4: '#3366ff',  # Biru
    5: '#00cccc',  # Cyan
    6: '#33cc33',  # Hijau
    -1: '#999999'  # Abu-abu (untuk outlier)
}

# Mapping kategori ke warna (sekarang menggunakan label "Cluster N")
CATEGORY_COLORS = {}  # Akan diisi secara dinamis oleh fungsi categorize_clusters


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
            n_init='auto'
        )
    if method == 'BIRCH':
        return Birch(
            n_clusters=params.get('n_clusters', 3),
            threshold=params.get('threshold', 0.1),
            branching_factor=params.get('branching_factor', 50)
        )
    if method == 'OPTICS':
        return OPTICS(
            min_samples=params.get('min_samples', 5),
            eps=params.get('eps', None) 
        )
    return None

def get_color_for_k_clusters(k):
    """
    Mengembalikan skema warna yang sesuai untuk jumlah cluster tertentu.
    
    Args:
        k (int): Jumlah cluster (2-7)
        
    Returns:
        list: Daftar warna hex untuk setiap cluster
    """
    if k in CLUSTER_COLOR_SCHEMES:
        return CLUSTER_COLOR_SCHEMES[k]
    # Fallback untuk k > 7 atau k < 2
    return [CLUSTER_COLORS.get(i, '#999999') for i in range(k)]

def categorize_clusters(df):
    """
    Memberi label "Cluster 0", "Cluster 1", dst pada setiap cluster.
    Cluster diurutkan berdasarkan skor rata-rata gabungan dari terendah (Cluster 0) ke tertinggi.
    Warna ditentukan secara dinamis berdasarkan jumlah cluster yang terbentuk.
    
    Args:
        df (DataFrame): DataFrame yang sudah memiliki kolom 'Cluster'.
        
    Returns:
        DataFrame: DataFrame yang sama dengan tambahan kolom 'Kategori'.
    """
    global CATEGORY_COLORS
    
    if 'Cluster' not in df.columns or df['Cluster'].nunique() == 0:
        return df
        
    feature_cols = [c for c in df.columns if any(f.lower() in c.lower() for f in FEATURE_PRODUKSI)]
    
    if not feature_cols:
        df['Kategori'] = 'Cluster ' + df['Cluster'].astype(str)
        return df
    
    # Pisahkan outlier (cluster -1 dari OPTICS) dari cluster valid
    valid_clusters_df = df[df['Cluster'] != -1]
    
    # Jika semua data adalah outlier
    if valid_clusters_df.empty:
        df['Kategori'] = 'Outlier'
        CATEGORY_COLORS = {'Outlier': '#999999'}
        return df
        
    # Hitung skor rata-rata gabungan untuk setiap cluster yang valid
    cluster_means = valid_clusters_df.groupby('Cluster')[feature_cols].mean()
    cluster_means['agg_score'] = cluster_means.mean(axis=1)
    
    # Urutkan cluster dari skor terendah ke tertinggi
    cluster_means = cluster_means.sort_values('agg_score')
    
    num_clusters = len(cluster_means)
    
    # Dapatkan skema warna yang sesuai
    color_scheme = get_color_for_k_clusters(num_clusters)
    
    # Buat pemetaan dari nomor cluster asli ke "Cluster 0", "Cluster 1", dst
    # Dan mapping warna yang sesuai
    mapping = {}
    color_mapping = {}
    
    for i, cluster_id in enumerate(cluster_means.index):
        new_label = f'Cluster {i}'
        mapping[cluster_id] = new_label
        color_mapping[new_label] = color_scheme[i] if i < len(color_scheme) else '#999999'
    
    # Tambahkan pemetaan untuk outlier jika ada
    if -1 in df['Cluster'].values:
        mapping[-1] = 'Outlier'
        color_mapping['Outlier'] = '#999999'
    
    # Update CATEGORY_COLORS global
    CATEGORY_COLORS = color_mapping
            
    # Terapkan pemetaan untuk membuat kolom 'Kategori' baru
    df['Kategori'] = df['Cluster'].map(mapping)
    return df

def boxgrid_per_cluster(df: pd.DataFrame, variabel, judul: str):
    """
    Membuat grid box plot untuk setiap fitur guna membandingkan karakteristik antar cluster.
    """
    df = df.copy()

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
    n_cols = 2
    n_rows = (n_vars + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8 * n_cols, 6 * n_rows))
    axes = axes.flatten()

    # Urutkan kategori: Cluster 0, Cluster 1, ..., Outlier (jika ada)
    categories = sorted([c for c in df_plot['Kategori'].unique() if c != 'Outlier'])
    if 'Outlier' in df_plot['Kategori'].unique():
        categories.append('Outlier')

    for i, var in enumerate(variabel_jelas):
        if var not in df_plot.columns:
            continue
        sns.boxplot(
            data=df_plot, x="Kategori", y=var, hue="Kategori",
            palette=CATEGORY_COLORS, legend=False, ax=axes[i], order=categories
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