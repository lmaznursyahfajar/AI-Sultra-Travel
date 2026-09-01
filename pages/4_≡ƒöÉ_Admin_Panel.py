# pages/4_🔐_Admin_Panel.py — Panel manajemen data destinasi wisata (CRUD)
import streamlit as st
import pandas as pd
from utils.database import (
    init_db, get_all_destinations, get_destination_by_id, add_destination,
    update_destination, delete_destination, restore_destination, get_recent_logs,
    get_stats, KATEGORI_LABELS
)
from utils.styling import inject_base_css, page_header, footer
from utils.auth import require_login, logout_button

st.set_page_config(page_title="Panel Admin — SultraTravel", page_icon="🔐", layout="wide")
init_db()
inject_base_css()
page_header("🔐 Panel Admin — Manajemen Data Wisata", "Kelola data destinasi wisata Sulawesi Tenggara: tambah, ubah, dan hapus.")

if not require_login():
    footer()
    st.stop()

logout_button()

kategori_keys = list(KATEGORI_LABELS.keys())
kategori_display = [f"{emoji} {label}" for emoji, label in KATEGORI_LABELS.values()]
kategori_key_by_display = dict(zip(kategori_display, kategori_keys))
kategori_display_by_key = {k: f"{e} {l}" for k, (e, l) in KATEGORI_LABELS.items()}

tab_dashboard, tab_tambah, tab_kelola, tab_log = st.tabs(
    ["📊 Dashboard", "➕ Tambah Destinasi", "📋 Kelola Data", "🧾 Log Aktivitas"]
)

# ==============================
# Dashboard
# ==============================
with tab_dashboard:
    stats = get_stats()
    df_all = get_all_destinations(only_active=False)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Destinasi Aktif", stats.get("total", 0))
    c2.metric("Kabupaten/Kota Tercakup", df_all["kabupaten_kota"].nunique() if not df_all.empty else 0)
    c3.metric("Rata-rata Rating", stats.get("rata_rating", 0))
    c4.metric("Destinasi Gratis", stats.get("gratis", 0))

    st.markdown("#### Distribusi per Kategori")
    if stats.get("per_kategori"):
        kat_df = pd.DataFrame({
            "Kategori": [kategori_display_by_key.get(k, k) for k in stats["per_kategori"].keys()],
            "Jumlah": list(stats["per_kategori"].values())
        }).set_index("Kategori")
        st.bar_chart(kat_df)

    st.markdown("#### Distribusi per Kabupaten/Kota")
    if stats.get("per_kabupaten"):
        kab_df = pd.DataFrame({
            "Kabupaten/Kota": list(stats["per_kabupaten"].keys()),
            "Jumlah": list(stats["per_kabupaten"].values())
        }).set_index("Kabupaten/Kota")
        st.bar_chart(kab_df)

# ==============================
# Tambah destinasi
# ==============================
with tab_tambah:
    st.markdown("#### Tambah Destinasi Baru")
    with st.form("form_tambah", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nama = st.text_input("Nama Destinasi *")
            kategori_disp = st.selectbox("Kategori *", kategori_display)
            kabupaten_kota = st.text_input("Kabupaten/Kota *", placeholder="mis. Kota Kendari")
            harga_tiket = st.text_input("Harga Tiket", placeholder="mis. Rp 10.000 atau Gratis")
            jam_operasional = st.text_input("Jam Operasional", placeholder="mis. 07:00 - 17:00")
            rating = st.slider("Rating", 1.0, 5.0, 4.0, 0.1)
        with c2:
            fasilitas = st.text_input("Fasilitas", placeholder="mis. Parkir, gazebo, warung")
            latitude = st.number_input("Latitude", value=-3.9985, format="%.6f")
            longitude = st.number_input("Longitude", value=122.5125, format="%.6f")
            kontak = st.text_input("Kontak (opsional)")
            tips = st.text_input("Tips Berkunjung (opsional)")
        st.markdown("**📷 Foto Destinasi (opsional)**")
        fc1, fc2 = st.columns(2)
        with fc1:
            foto_url = st.text_input("URL Foto", placeholder="https://... (kosongkan jika belum ada)",
                                      help="Gunakan foto berlisensi bebas (mis. Wikimedia Commons) atau foto koleksi sendiri. "
                                           "Jika dikosongkan, akan ditampilkan ilustrasi placeholder otomatis.")
        with fc2:
            foto_kredit = st.text_input("Kredit/Sumber Foto", placeholder="mis. Foto: Nama / Wikimedia Commons (CC BY-SA 4.0)")
        deskripsi = st.text_area("Deskripsi", height=100)

        submitted = st.form_submit_button("💾 Simpan Destinasi", type="primary")
        if submitted:
            if not nama or not kabupaten_kota:
                st.error("Nama dan Kabupaten/Kota wajib diisi.")
            else:
                add_destination({
                    "nama": nama,
                    "kategori": kategori_key_by_display[kategori_disp],
                    "kabupaten_kota": kabupaten_kota,
                    "deskripsi": deskripsi,
                    "harga_tiket": harga_tiket,
                    "jam_operasional": jam_operasional,
                    "fasilitas": fasilitas,
                    "rating": rating,
                    "latitude": latitude,
                    "longitude": longitude,
                    "kontak": kontak,
                    "tips": tips,
                    "foto_url": foto_url,
                    "foto_kredit": foto_kredit,
                })
                st.success(f"✅ Destinasi '{nama}' berhasil ditambahkan!")
                st.session_state.pop("chatbot", None)  # paksa refresh index pencarian
                st.rerun()

# ==============================
# Kelola data (edit/hapus)
# ==============================
with tab_kelola:
    st.markdown("#### Kelola Destinasi Tersimpan")
    df_manage = get_all_destinations(only_active=False)

    search_manage = st.text_input("🔍 Cari destinasi untuk dikelola", key="search_manage")
    if search_manage:
        df_manage = df_manage[df_manage["nama"].str.lower().str.contains(search_manage.lower())]

    st.dataframe(
        df_manage[["id", "nama", "kategori", "kabupaten_kota", "harga_tiket", "rating", "status"]],
        use_container_width=True, hide_index=True, height=280
    )

    st.markdown("---")
    st.markdown("#### ✏️ Edit / Hapus Destinasi")
    if df_manage.empty:
        st.info("Belum ada data.")
    else:
        options = {f"#{r['id']} — {r['nama']} ({r['status']})": r["id"] for _, r in df_manage.iterrows()}
        selected_label = st.selectbox("Pilih destinasi", list(options.keys()))
        selected_id = options[selected_label]
        record = get_destination_by_id(selected_id)

        if record:
            preview_col, form_col = st.columns([1, 2.2])
            with preview_col:
                from utils.photo_utils import get_photo
                photo = get_photo(record)
                st.image(photo["url"], use_container_width=True, caption=photo.get("credit") or "Placeholder ilustrasi")

            with form_col:
                with st.form("form_edit"):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_nama = st.text_input("Nama Destinasi", value=record["nama"])
                        current_disp = kategori_display_by_key.get(record["kategori"], kategori_display[0])
                        e_kategori_disp = st.selectbox("Kategori", kategori_display,
                                                        index=kategori_display.index(current_disp) if current_disp in kategori_display else 0)
                        e_kabupaten = st.text_input("Kabupaten/Kota", value=record["kabupaten_kota"])
                        e_harga = st.text_input("Harga Tiket", value=record["harga_tiket"] or "")
                        e_jam = st.text_input("Jam Operasional", value=record["jam_operasional"] or "")
                        e_rating = st.slider("Rating", 1.0, 5.0, float(record["rating"] or 4.0), 0.1)
                    with c2:
                        e_fasilitas = st.text_input("Fasilitas", value=record["fasilitas"] or "")
                        e_lat = st.number_input("Latitude", value=float(record["latitude"] or -3.9985), format="%.6f")
                        e_lon = st.number_input("Longitude", value=float(record["longitude"] or 122.5125), format="%.6f")
                        e_kontak = st.text_input("Kontak", value=record["kontak"] or "")
                        e_tips = st.text_input("Tips", value=record["tips"] or "")
                    st.markdown("**📷 Foto Destinasi**")
                    fc1, fc2 = st.columns(2)
                    with fc1:
                        e_foto_url = st.text_input("URL Foto", value=record.get("foto_url") or "",
                                                    placeholder="https://... (kosongkan untuk placeholder otomatis)")
                    with fc2:
                        e_foto_kredit = st.text_input("Kredit/Sumber Foto", value=record.get("foto_kredit") or "")
                    e_deskripsi = st.text_area("Deskripsi", value=record["deskripsi"] or "", height=100)

                    bcol1, bcol2, bcol3 = st.columns(3)
                    save = bcol1.form_submit_button("💾 Simpan Perubahan", type="primary", use_container_width=True)
                    deactivate = bcol2.form_submit_button(
                        "🚫 Nonaktifkan" if record["status"] == "aktif" else "✅ Aktifkan Kembali",
                        use_container_width=True
                    )
                    hard_delete = bcol3.form_submit_button("🗑️ Hapus Permanen", use_container_width=True)

                    if save:
                        update_destination(selected_id, {
                            "nama": e_nama, "kategori": kategori_key_by_display[e_kategori_disp],
                            "kabupaten_kota": e_kabupaten, "deskripsi": e_deskripsi, "harga_tiket": e_harga,
                            "jam_operasional": e_jam, "fasilitas": e_fasilitas, "rating": e_rating,
                            "latitude": e_lat, "longitude": e_lon, "kontak": e_kontak, "tips": e_tips,
                            "foto_url": e_foto_url, "foto_kredit": e_foto_kredit,
                        })
                        st.success("✅ Perubahan disimpan.")
                        st.session_state.pop("chatbot", None)
                        st.rerun()

                    if deactivate:
                        if record["status"] == "aktif":
                            delete_destination(selected_id, hard_delete=False)
                            st.success("Destinasi dinonaktifkan (tidak tampil ke publik, data tetap tersimpan).")
                        else:
                            restore_destination(selected_id)
                            st.success("Destinasi diaktifkan kembali.")
                        st.session_state.pop("chatbot", None)
                        st.rerun()

                    if hard_delete:
                        delete_destination(selected_id, hard_delete=True)
                        st.warning("🗑️ Destinasi dihapus permanen dari database.")
                        st.session_state.pop("chatbot", None)
                        st.rerun()

    st.markdown("---")
    st.markdown("#### ⬇️ Ekspor Data")
    export_df = get_all_destinations(only_active=False)
    st.download_button(
        "Unduh Seluruh Data (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="data_wisata_sultra.csv",
        mime="text/csv",
    )

# ==============================
# Log aktivitas
# ==============================
with tab_log:
    st.markdown("#### Log Aktivitas Terbaru")
    logs = get_recent_logs(50)
    if logs.empty:
        st.info("Belum ada aktivitas tercatat.")
    else:
        st.dataframe(logs[["waktu", "aksi", "detail"]], use_container_width=True, hide_index=True)

footer()
