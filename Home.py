import streamlit as st
import os

st.set_page_config(
    page_title="Home | Analisis Clustering Perikanan",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state='expanded'
)

# --- Konten Halaman ---
st.title("🌊🐟Pengelompokan dan Analisis Clustering Produksi Perikanan Tangkap Laut di Indonesia")
st.markdown("---")
st.sidebar.success("Anda berada di halaman Home. Gunakan menu navigasi untuk menjelajahi fitur lainnya.")

# Menampilkan gambar utama
# Pastikan gambar.png ada di dalam folder Assets
image_path = os.path.join('Assets', 'laut.png')
if os.path.exists(image_path):
    st.image(image_path, caption="perairan Pulau Gunung Api Banda, Salah Satu Ekosistem Laut yang kaya Akan jenis ikan Dan Terumbu Karang di Indonesia")
else:
    st.warning(f"File gambar utama tidak ditemukan di '{image_path}'. Harap periksa path file Anda.")

st.header("Selamat Datang di Website pemetaan dan Analisis Perikanan")

st.write("""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc pellentesque, nunc id tincidunt pretium, libero elit auctor quam, ac scelerisque quam est nec sapien. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Maecenas sed blandit magna. Integer eu dolor eu quam viverra interdum.

Vivamus in massa eu nisi dictum feugiat. Sed et mi eget tellus bibendum venenatis. Suspendisse potenti. Ut ac turpis vitae felis dapibus aliquam. Phasellus nec dolor eu elit tincidunt commodo.
""")

st.info("Gunakan menu navigasi di sebelah kiri untuk memulai analisis di halaman **Clustering** atau untuk melihat informasi lainnya.")

