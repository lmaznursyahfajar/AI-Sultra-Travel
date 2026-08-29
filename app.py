# app.py — SultraTravel: Sistem Informasi & Manajemen Pariwisata Sulawesi Tenggara
import streamlit as st
import pandas as pd
from utils.database import init_db, get_all_destinations, get_stats, KATEGORI_LABELS
from utils.styling import inject_base_css, page_header, footer, destination_card
from utils.leaflet_map import render_interactive_map

st.set_page_config(
    page_title="SultraTravel — Manajemen Pariwisata Sulawesi Tenggara",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_base_css()

# ==============================
# Sidebar
# ==============================
with st.sidebar:
    st.markdown("## 🏝️ SultraTravel")
    st.caption("Sistem Informasi & Manajemen Pariwisata Provinsi Sulawesi Tenggara")
    st.markdown("---")
    st.markdown(
        "**Navigasi:**\n\n"
        "🏠 Beranda\n\n"
        "🗺️ Direktori & Peta *(menu Pages)*\n\n"
        "💬 Chatbot AI *(menu Pages)*\n\n"
        "🧭 Itinerary Planner *(menu Pages)*\n\n"
        "🔐 Panel Admin *(menu Pages)*"
    )
    st.markdown("---")
    st.caption("Gunakan menu di sidebar (atas) untuk berpindah halaman.")

# ==============================
# Header
# ==============================
page_header(
    "🏝️ SultraTravel",
    "Jelajahi, rencanakan, dan kelola data pariwisata Sulawesi Tenggara dalam satu platform terpadu."
)

df = get_all_destinations()
stats = get_stats()

# ==============================
# Ringkasan Statistik
# ==============================
st.markdown("### 📊 Ringkasan Data Pariwisata")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card"><h3>{stats.get('total', 0)}</h3>
                <p>Total Destinasi Terdata</p></div>""", unsafe_allow_html=True)
with c2:
    n_kab = df["kabupaten_kota"].nunique() if not df.empty else 0
    st.markdown(f"""<div class="metric-card"><h3>{n_kab}</h3>
                <p>Kabupaten/Kota Tercakup</p></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card"><h3>{stats.get('gratis', 0)}</h3>
                <p>Destinasi Tanpa Biaya Masuk</p></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card"><h3>⭐ {stats.get('rata_rating', 0)}</h3>
                <p>Rata-rata Rating</p></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================
# Kategori wisata
# ==============================
st.markdown("### 🎯 Jelajahi Berdasarkan Kategori")
cat_cols = st.columns(5)
per_kategori = stats.get("per_kategori", {})
for i, (key, (emoji, label)) in enumerate(KATEGORI_LABELS.items()):
    with cat_cols[i]:
        jumlah = per_kategori.get(key, 0)
        st.markdown(
            f"""<div class="dest-card" style="text-align:center;">
            <div style="font-size:2rem;">{emoji}</div>
            <h4>{label}</h4>
            <span class="badge">{jumlah} destinasi</span>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================
# Destinasi unggulan
# ==============================
left, right = st.columns([1.15, 1])
with left:
    st.markdown("### ✨ Destinasi Rating Tertinggi")
    if not df.empty:
        top = df.sort_values("rating", ascending=False).head(6)
        for _, r in top.iterrows():
            destination_card(r, KATEGORI_LABELS)
    else:
        st.info("Belum ada data destinasi.")

with right:
    st.markdown("### 🗺️ Peta Sebaran Destinasi")
    if not df.empty:
        render_interactive_map(df, height=520)
    else:
        st.info("Belum ada data untuk ditampilkan di peta.")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================
# Ajakan aksi ke fitur lain
# ==============================
st.markdown("### 🚀 Mulai Jelajahi")
a1, a2, a3 = st.columns(3)
with a1:
    st.markdown(
        """<div class="dest-card"><h4>💬 Tanya Chatbot AI</h4>
        <p style="color:#556; font-size:0.9rem;">Tanyakan rekomendasi wisata dengan bahasa sehari-hari,
        lengkap dengan info jarak dan peta.</p></div>""",
        unsafe_allow_html=True,
    )
with a2:
    st.markdown(
        """<div class="dest-card"><h4>🧭 Susun Itinerary</h4>
        <p style="color:#556; font-size:0.9rem;">Buat rencana perjalanan otomatis berdasarkan durasi,
        minat, dan budget Anda.</p></div>""",
        unsafe_allow_html=True,
    )
with a3:
    st.markdown(
        """<div class="dest-card"><h4>🗺️ Buka Direktori</h4>
        <p style="color:#556; font-size:0.9rem;">Cari & saring seluruh destinasi lengkap dengan peta
        interaktif dan detail lengkap.</p></div>""",
        unsafe_allow_html=True,
    )

footer()
