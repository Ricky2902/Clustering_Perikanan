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


# Menampilkan gambar utama
# Pastikan gambar.png ada di dalam folder Assets
image_path = os.path.join('assets', 'laut.png')
if os.path.exists(image_path):
    st.image(image_path, caption="perairan Pulau Gunung Api Banda, Salah Satu Ekosistem Laut yang kaya Akan jenis ikan Dan Terumbu Karang di Indonesia")
else:
    st.warning(f"File gambar utama tidak ditemukan di '{image_path}'. Harap periksa path file Anda.")

st.header("Selamat Datang di Website pemetaan dan Analisis Perikanan")

st.write("""
Indonesia, sebagai negara kepulauan terbesar di dunia, dianugerahi garis pantai yang sangat panjang dan wilayah laut yang luas. Posisi geografis ini menjadikan Indonesia sebagai poros maritim global dengan kekayaan sumber daya kelautan dan perikanan yang luar biasa. Potensi ini bukan hanya menjadi tulang punggung bagi ekonomi biru nasional, tetapi juga merupakan bagian krusial dari warisan alam yang harus dikelola dengan bijak dan berkelanjutan untuk generasi mendatang.

Kekayaan maritim Indonesia tercermin dari keanekaragaman hayati lautnya yang tak tertandingi. Wilayah perairan kita merupakan rumah bagi ekosistem vital seperti terumbu karang, hutan mangrove, dan padang lamun yang paling beragam di planet ini. Sebagai jantung dari Segitiga Terumbu Karang, laut Indonesia menjadi pusat biodiversitas global, menopang ribuan spesies ikan dan biota laut lainnya. Ekosistem ini tidak hanya penting secara ekologis, tetapi juga memberikan jasa lingkungan yang esensial, mulai dari penyediaan pangan hingga perlindungan pesisir.

Di tengah melimpahnya data dari sektor perikanan, seringkali sulit untuk melihat pola yang jelas tanpa alat yang tepat. Oleh karena itu, website ini hadir sebagai platform untuk menganalisis dan mengelompokkan (clustering) data produksi perikanan di seluruh Indonesia. Dengan menerapkan beberapa metode clustering populer seperti K-Means, Birch, dan OPTICS , platform ini secara otomatis mengidentifikasi wilayah-wilayah dengan karakteristik serupa, sehingga membantu mengungkap wawasan baru yang tersembunyi di dalam data.

Tujuan utama dari platform ini adalah menjadi sarana edukasi bagi mahasiswa, akademisi, dan masyarakat umum yang tertarik untuk mempelajari penerapan ilmu data, khususnya clustering, dalam konteks sektor perikanan Indonesia. Lebih jauh lagi, proyek ini berupaya mendukung pencapaian Tujuan Pembangunan Berkelanjutan atau SDGs, terutama SDG 14: Kehidupan di Bawah Air (Life Below Water). Dengan menyediakan analisis berbasis data, diharapkan platform ini dapat menyumbangkan wawasan yang berguna untuk pengelolaan sumber daya laut yang lebih efektif dan berkelanjutan.
""")

st.info("Gunakan menu navigasi di sebelah kiri untuk memulai analisis di halaman **Clustering** atau untuk melihat informasi lainnya.")

