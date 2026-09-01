# pages/1_🗺️_Direktori.py — Direktori destinasi wisata dengan filter & peta interaktif
import streamlit as st
import pandas as pd
from utils.database import init_db, get_all_destinations, KATEGORI_LABELS
from utils.styling import inject_base_css, page_header, footer, destination_card
from utils.leaflet_map import render_interactive_map
from utils.map_utils import haversine_km, estimate_travel_time

st.set_page_config(page_title="Direktori — SultraTravel", page_icon="🗺️", layout="wide")
init_db()
inject_base_css()
page_header("🗺️ Direktori Destinasi Wisata", "Cari, saring, dan jelajahi seluruh destinasi wisata Sulawesi Tenggara.")

df = get_all_destinations()

if df.empty:
    st.warning("Belum ada data destinasi. Silakan tambahkan data melalui Panel Admin.")
    st.stop()

# ==============================
# Filter
# ==============================
with st.container():
    f1, f2, f3, f4 = st.columns([1.4, 1, 1, 1])
    with f1:
        keyword = st.text_input("🔍 Cari nama/deskripsi destinasi", placeholder="mis. pantai, air terjun, benteng...")
    with f2:
        kategori_opsi = ["Semua"] + [label for _, label in KATEGORI_LABELS.values()]
        kategori_pilih = st.selectbox("Kategori", kategori_opsi)
    with f3:
        kab_opsi = ["Semua"] + sorted(df["kabupaten_kota"].unique().tolist())
        kab_pilih = st.selectbox("Kabupaten/Kota", kab_opsi)
    with f4:
        harga_opsi = st.selectbox("Biaya Masuk", ["Semua", "Gratis saja", "Berbayar saja"])

filtered = df.copy()
if keyword:
    kw = keyword.lower()
    filtered = filtered[
        filtered["nama"].str.lower().str.contains(kw, na=False)
        | filtered["deskripsi"].str.lower().str.contains(kw, na=False)
    ]
if kategori_pilih != "Semua":
    key_map = {label: key for key, (_, label) in KATEGORI_LABELS.items()}
    filtered = filtered[filtered["kategori"] == key_map[kategori_pilih]]
if kab_pilih != "Semua":
    filtered = filtered[filtered["kabupaten_kota"] == kab_pilih]
if harga_opsi == "Gratis saja":
    filtered = filtered[filtered["harga_tiket"].str.lower().str.contains("gratis", na=False)]
elif harga_opsi == "Berbayar saja":
    filtered = filtered[~filtered["harga_tiket"].str.lower().str.contains("gratis", na=False)]

st.markdown(f"**{len(filtered)}** destinasi ditemukan dari total {len(df)} destinasi.")

# ==============================
# Lokasi user (opsional, untuk info jarak)
# ==============================
with st.expander("📍 Atur lokasi Anda (opsional, untuk menghitung jarak & rute)"):
    loc_col1, loc_col2 = st.columns([2, 1])
    with loc_col1:
        loc_text = st.text_input("Koordinat Anda (lat,lon)", placeholder="mis. -3.9985,122.5125")
    with loc_col2:
        if st.button("📍 Gunakan Pusat Kota Kendari"):
            st.session_state["user_location"] = [-3.9985, 122.5125]
    if loc_text:
        try:
            lat, lon = [float(x.strip()) for x in loc_text.split(",")]
            st.session_state["user_location"] = [lat, lon]
        except Exception:
            st.error("Format koordinat tidak valid. Gunakan format: latitude,longitude")

user_location = st.session_state.get("user_location")

# ==============================
# Tampilan: Grid + Peta
# ==============================
tab_grid, tab_map = st.tabs(["📋 Daftar Destinasi", "🗺️ Peta Interaktif"])

with tab_grid:
    if filtered.empty:
        st.info("Tidak ada destinasi yang sesuai dengan filter saat ini.")
    else:
        cols = st.columns(3)
        for i, (_, r) in enumerate(filtered.sort_values("rating", ascending=False).iterrows()):
            jarak_txt = ""
            if user_location and pd.notna(r["latitude"]):
                jarak = haversine_km(user_location, [r["latitude"], r["longitude"]])
                if jarak is not None:
                    jarak_txt = f" • 📏 ±{jarak:.1f} km (~{estimate_travel_time(jarak)})"
            with cols[i % 3]:
                destination_card(
                    r, KATEGORI_LABELS,
                    extra_info_html=f" • 🕒 {r['jam_operasional']}{jarak_txt}"
                )
                with st.expander("💡 Tips berkunjung"):
                    st.write(r.get("tips", "-"))
                    if r.get("kontak"):
                        st.caption(f"📞 Kontak: {r['kontak']}")

with tab_map:
    st.caption("🧭 Klik marker untuk detail, cari destinasi lewat kotak pencarian, "
               "atau aktifkan '📍 Lokasi Saya' untuk mendapatkan rute jalan langsung ke tujuan.")
    render_interactive_map(filtered, user_location=user_location, height=580)

footer()
