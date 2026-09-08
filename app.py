# app.py — Entrypoint utama SultraTravel.
# Mengatur konfigurasi global & navigasi antar halaman lewat st.navigation/st.Page
# (bukan folder "pages/" otomatis) agar label & ikon sidebar tidak bergantung pada
# nama file - ini mencegah karakter rusak (mojibake) saat file diunggah/di-deploy
# di lingkungan yang berbeda encoding-nya.
import streamlit as st
from utils.database import init_db
from utils.styling import inject_base_css

st.set_page_config(
    page_title="SultraTravel — Manajemen Pariwisata Sulawesi Tenggara",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_base_css()

with st.sidebar:
    st.markdown("## 🏝️ SultraTravel")
    st.caption("Sistem Informasi & Manajemen Pariwisata Provinsi Sulawesi Tenggara")
    st.markdown("---")

beranda = st.Page("views/beranda.py", title="Beranda", icon="🏠", default=True)
direktori = st.Page("views/direktori.py", title="Direktori & Peta", icon="🗺️")
chatbot = st.Page("views/chatbot_ai.py", title="Chatbot AI", icon="💬")
itinerary = st.Page("views/itinerary_planner.py", title="Itinerary Planner", icon="🧭")
admin = st.Page("views/admin_panel.py", title="Panel Admin", icon="🔐")

pg = st.navigation([beranda, direktori, chatbot, itinerary, admin])
pg.run()

with st.sidebar:
    st.markdown("---")
    st.caption("Data destinasi dikompilasi dari sumber resmi Dinas Pariwisata Provinsi Sulawesi Tenggara.")
