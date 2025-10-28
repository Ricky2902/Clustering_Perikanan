import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="ABOUT | FISHERY CLUSTER", 
    page_icon="assets/logo1.png", 
    layout="centered"
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
st.title("👨‍💻 Profil Saya")
st.markdown("---")

# Mengatur layout menjadi dua kolom: satu untuk foto, satu untuk teks
col1, col2 = st.columns([1, 2], gap="medium")

with col1:
    # Path ke gambar profil Anda
    # Ganti 'profil.png' dengan nama file foto Anda jika berbeda
    profile_image_path = os.path.join('assets', 'Profile.jpg')
    
    if os.path.exists(profile_image_path):
        profile_image = Image.open(profile_image_path)
        st.image(profile_image, caption="Mahasiswa")
    else:
        # Pesan jika gambar tidak ditemukan
        st.warning("Letakkan foto Anda di folder 'Assets' dengan nama 'profil.png'")

with col2:
    st.header("Ricky Fernando JF")
    st.write("**Teknik Informatika**")
    st.write("**Universitas Tarumanagara**")    
    st.markdown("---")
    
    st.write("📧 **Email**: RickyBong2902@gmail.com")
    st.write("🔗 **LinkedIn**: https://www.linkedin.com/in/ricky-fernando-jf")
    st.write("깃 **GitHub**: https://github.com/Ricky2902")

st.markdown("---")
st.header("Tentang Proyek Ini")
st.write("""
Aplikasi ini dikembangkan sebagai bagian dari **Tugas Akhir Skripsi** dengan judul **"Pengelompok dan Analisis Clustering Produksi Perikanan Tangkap laut di Indonesia Dengan Mengunakan Metode K-Means, BIRCH dan OPTICS"**. 

Fokus utama proyek ini adalah untuk menerapkan dan membandingkan beberapa algoritma clustering untuk menganalisis pola dalam data perikanan tangkap laut di Indonesia lalu mevisualisasikan melalui pemetaan. Tujuannya adalah untuk memberikan informasi bagi setiap orang akan potensi kelautan di indonesia dengan memberikan analasis yang interaktif, visual, dan mudah digunakan bagi masyarakat  untuk mempelajari Clustering di sektor perikanan di Indonesia.
""")

