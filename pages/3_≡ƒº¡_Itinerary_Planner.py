# pages/3_🧭_Itinerary_Planner.py — Penyusun rencana perjalanan otomatis
import streamlit as st
import pandas as pd
from utils.database import init_db, get_all_destinations, KATEGORI_LABELS
from utils.styling import inject_base_css, page_header, footer
from utils.itinerary_engine import generate_itinerary, itinerary_to_markdown
from utils.leaflet_map import render_interactive_map
from utils.photo_utils import get_photo

st.set_page_config(page_title="Itinerary Planner — SultraTravel", page_icon="🧭", layout="wide")
init_db()
inject_base_css()
page_header("🧭 AI Itinerary Planner", "Sebutkan durasi, minat, dan budget — sistem akan menyusun rute perjalanan harian secara otomatis.")

df = get_all_destinations()
if df.empty:
    st.warning("Belum ada data destinasi. Silakan tambahkan data melalui Panel Admin.")
    st.stop()

KAB_KOTA_CENTER = {
    "Kota Kendari": [-3.9985, 122.5125],
    "Kota Baubau": [-5.4700, 122.6100],
}

# ==============================
# Form input
# ==============================
with st.form("itinerary_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        days = st.slider("📅 Durasi perjalanan (hari)", 1, 7, 3)
        pace = st.selectbox("🚶 Ritme perjalanan", ["santai", "normal", "padat"], index=1,
                             help="Menentukan jumlah destinasi yang dikunjungi per hari")
    with c2:
        kategori_opsi = [label for _, label in KATEGORI_LABELS.values()]
        pilih_label = st.multiselect("🎯 Minat wisata", kategori_opsi, default=kategori_opsi[:2])
        key_map = {label: key for key, (_, label) in KATEGORI_LABELS.items()}
        interests = [key_map[l] for l in pilih_label]
    with c3:
        budget_level = st.selectbox("💰 Level budget", ["hemat", "menengah", "mewah"], index=1)
        start_kab = st.selectbox("📍 Titik keberangkatan", list(KAB_KOTA_CENTER.keys()) + ["Kustom (koordinat)"])

    start_location = KAB_KOTA_CENTER.get(start_kab)
    if start_kab == "Kustom (koordinat)":
        coord_text = st.text_input("Masukkan koordinat keberangkatan (lat,lon)", "-3.9985,122.5125")
        try:
            lat, lon = [float(x.strip()) for x in coord_text.split(",")]
            start_location = [lat, lon]
        except Exception:
            st.error("Format koordinat tidak valid.")
            start_location = KAB_KOTA_CENTER["Kota Kendari"]

    submitted = st.form_submit_button("✨ Susun Itinerary Saya", type="primary", use_container_width=True)

# ==============================
# Hasil itinerary
# ==============================
if submitted:
    with st.spinner("🧭 Menyusun rute perjalanan optimal..."):
        itinerary = generate_itinerary(
            df, days=days, interests=interests, budget_level=budget_level,
            start_location=start_location, pace=pace
        )
    st.session_state["last_itinerary"] = itinerary

itinerary = st.session_state.get("last_itinerary")

if itinerary and itinerary["days"]:
    st.markdown("---")
    m1, m2 = st.columns(2)
    m1.metric("📍 Total Destinasi", itinerary["total_destinations"])
    m2.metric("🛣️ Estimasi Total Jarak", f"{itinerary['estimasi_total_jarak_km']} km")

    tab_plan, tab_map = st.tabs(["📋 Rencana Harian", "🗺️ Peta Rute"])

    with tab_plan:
        day_tabs = st.tabs([f"Hari {d['day']}" for d in itinerary["days"]])
        for tab, day in zip(day_tabs, itinerary["days"]):
            with tab:
                for stop in day["stops"]:
                    emoji, label = KATEGORI_LABELS.get(stop["kategori"], ("📍", stop["kategori"]))
                    photo = get_photo(stop)
                    jarak_info = ""
                    if stop["jarak_dari_sebelumnya_km"] is not None:
                        jarak_info = (f"🚗 {stop['jarak_dari_sebelumnya_km']} km dari titik sebelumnya "
                                      f"(~{stop['estimasi_waktu_tempuh']})")
                    st.markdown(
                        f"""<div class="dest-card">
                        <img class="dest-card-photo" src="{photo['url']}" onerror="this.style.display='none'"/>
                        <div class="dest-card-body">
                        <span class="badge badge-amber">{stop['waktu']}</span>
                        <h4>{emoji} {stop['nama']}</h4>
                        <span class="badge">{label}</span>
                        <p style="margin-top:8px; color:#445; font-size:0.9rem;">
                        📍 {stop['kabupaten_kota']} • 💰 {stop['harga_tiket']} • ⭐ {stop['rating']}<br>
                        {jarak_info}</p>
                        <p style="color:#556; font-size:0.87rem;">{str(stop['deskripsi'])[:140]}...</p>
                        </div></div>""",
                        unsafe_allow_html=True,
                    )

    with tab_map:
        all_stops = [s for d in itinerary["days"] for s in d["stops"]]
        stops_df = df[df["nama"].isin([s["nama"] for s in all_stops])]
        st.caption("🧭 Rute berurutan sesuai jadwal harian di atas — gunakan tombol 'Rute ke sini' pada setiap marker untuk arahan jalan.")
        render_interactive_map(stops_df, user_location=start_location, height=520)

    st.markdown("---")
    md_text = itinerary_to_markdown(itinerary)
    st.download_button(
        "⬇️ Unduh Itinerary (Markdown/Teks)",
        data=md_text,
        file_name="itinerary_sultratravel.md",
        mime="text/markdown",
        use_container_width=True,
    )
elif itinerary and not itinerary["days"]:
    st.warning("Tidak ditemukan destinasi yang sesuai dengan preferensi Anda. Coba ubah filter minat atau budget.")
else:
    st.info("Isi formulir di atas lalu klik **Susun Itinerary Saya** untuk mendapatkan rencana perjalanan otomatis.")

footer()
