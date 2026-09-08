"""
Styling bersama (tema navy - teal - amber) agar tampilan konsisten & profesional
di seluruh halaman aplikasi SultraTravel.
"""
import streamlit as st

PRIMARY = "#0F3D3E"       # navy-teal gelap
SECONDARY = "#14919B"     # teal
ACCENT = "#F2A541"        # amber
BG_LIGHT = "#F7FAFA"
TEXT_DARK = "#132A2C"

BASE_CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    h1, h2, h3, .main-header h1 {{
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }}
    .stApp {{
        background-color: {BG_LIGHT};
    }}
    .main-header {{
        background: linear-gradient(120deg, {PRIMARY} 0%, {SECONDARY} 100%);
        padding: 28px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 4px 18px rgba(15,61,62,0.18);
    }}
    .main-header h1 {{
        margin: 0;
        font-size: 1.9rem;
        font-weight: 700;
    }}
    .main-header p {{
        margin: 6px 0 0 0;
        opacity: 0.92;
        font-size: 1.02rem;
    }}
    .metric-card {{
        background: white;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 5px solid {ACCENT};
    }}
    .metric-card h3 {{
        margin: 0;
        font-size: 1.6rem;
        color: {PRIMARY};
    }}
    .metric-card p {{
        margin: 2px 0 0 0;
        color: #667;
        font-size: 0.88rem;
    }}
    .dest-card {{
        background: white;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        display: flex;
        flex-direction: column;
        height: 100%;
    }}
    .dest-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 22px rgba(15,61,62,0.16);
    }}
    .dest-card-photo {{
        width: 100%;
        height: 150px;
        object-fit: cover;
        display: block;
        background: #e5ecec;
        flex-shrink: 0;
    }}
    .dest-card-body {{
        padding: 14px 18px 16px 18px;
        border-top: 3px solid {SECONDARY};
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }}
    .dest-card-body h4 {{
        margin: 0 0 6px 0;
        color: {PRIMARY};
        font-size: 1.02rem;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .dest-card-desc {{
        color: #556;
        font-size: 0.87rem;
        margin-top: 6px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        flex-grow: 1;
    }}
    .photo-credit {{
        font-size: 0.68rem;
        color: #9aabab;
        padding: 3px 18px 0 18px;
    }}
    .badge {{
        display: inline-block;
        background: {SECONDARY}22;
        color: {SECONDARY};
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
    }}
    .badge-amber {{
        background: {ACCENT}22;
        color: #96650f;
    }}
    .cat-chip {{
        display: inline-block;
        padding: 7px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 3px 6px 3px 0;
        border: 1.5px solid {SECONDARY}55;
        color: {PRIMARY};
        background: white;
    }}
    .cat-chip-active {{
        background: {PRIMARY};
        color: white;
        border-color: {PRIMARY};
    }}
    .results-count {{
        color: #667;
        font-size: 0.88rem;
        margin: 4px 0 12px 0;
    }}
    .kab-pill {{
        display: inline-flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        border-radius: 10px;
        padding: 9px 14px;
        margin-bottom: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        font-size: 0.86rem;
        color: {TEXT_DARK};
    }}
    .kab-pill b {{
        color: {SECONDARY};
    }}
    .chat-bubble-user {{
        background: {PRIMARY};
        color: white;
        padding: 12px 16px;
        border-radius: 14px 14px 2px 14px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
    }}
    .chat-bubble-bot {{
        background: white;
        border: 1px solid #e2e8e8;
        padding: 12px 16px;
        border-radius: 14px 14px 14px 2px;
        margin: 8px 0;
        max-width: 90%;
    }}
    .footer-pro {{
        text-align: center;
        padding: 22px;
        margin-top: 30px;
        color: #6b7f80;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8e8;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {PRIMARY};
    }}
    section[data-testid="stSidebar"] * {{
        color: #eaf4f4 !important;
    }}
</style>
"""


def inject_base_css():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""<div class="main-header"><h1>{title}</h1><p>{subtitle}</p></div>""",
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """<div class="footer-pro">
        🏝️ <strong>SultraTravel</strong> — Sistem Informasi & Manajemen Pariwisata Sulawesi Tenggara<br>
        Dibangun untuk mendukung promosi pariwisata daerah secara digital.
        </div>""",
        unsafe_allow_html=True,
    )


def destination_card(row, kategori_labels, extra_info_html: str = "", show_tips: bool = False):
    """Merender satu kartu destinasi (foto + info) dengan gaya konsisten. Dipakai lintas halaman."""
    from .photo_utils import get_photo

    emoji, label = kategori_labels.get(row.get("kategori"), ("📍", row.get("kategori", "-")))
    photo = get_photo(row)
    deskripsi = str(row.get("deskripsi", "") or "")

    st.markdown(
        f"""<div class="dest-card">
        <img class="dest-card-photo" src="{photo['url']}" loading="lazy"
             onerror="this.style.display='none'"/>
        <div class="dest-card-body">
        <h4 title="{row.get('nama','')}">{emoji} {row.get('nama','')}</h4>
        <span class="badge">{label}</span>
        <span class="badge badge-amber">⭐ {row.get('rating','-')}</span>
        <p style="margin-top:8px; color:#445; font-size:0.9rem;">
        📍 {row.get('kabupaten_kota','-')} • 💰 {row.get('harga_tiket','-')}{extra_info_html}</p>
        <p class="dest-card-desc">{deskripsi}</p>
        </div></div>""",
        unsafe_allow_html=True,
    )
    if photo.get("credit"):
        st.markdown(f"""<div class="photo-credit">{photo['credit']}</div>""", unsafe_allow_html=True)


def category_chips_html(kategori_labels: dict, counts: dict, active_key: str = None) -> str:
    """Menghasilkan HTML baris chip kategori (indikator visual, bukan tombol interaktif)."""
    chips = [
        f'<span class="cat-chip{" cat-chip-active" if active_key == "__all__" else ""}">🗺️ Semua ({sum(counts.values())})</span>'
    ]
    for key, (emoji, label) in kategori_labels.items():
        active = " cat-chip-active" if key == active_key else ""
        chips.append(f'<span class="cat-chip{active}">{emoji} {label} ({counts.get(key, 0)})</span>')
    return '<div style="margin-bottom:10px;">' + "".join(chips) + "</div>"


def paginate(items_count: int, page_size: int, state_key: str) -> tuple:
    """
    Komponen pagination sederhana. Mengembalikan (start_index, end_index, current_page).
    Menyimpan halaman aktif di st.session_state[state_key].
    """
    total_pages = max(1, (items_count + page_size - 1) // page_size)
    current = st.session_state.get(state_key, 1)
    current = min(max(1, current), total_pages)

    if total_pages > 1:
        col_prev, col_mid, col_next = st.columns([1, 3, 1])
        with col_prev:
            if st.button("⬅️ Sebelumnya", disabled=(current <= 1), key=f"{state_key}_prev", use_container_width=True):
                current -= 1
        with col_mid:
            st.markdown(
                f"<div style='text-align:center; padding-top:8px; color:#667;'>Halaman {current} dari {total_pages}</div>",
                unsafe_allow_html=True,
            )
        with col_next:
            if st.button("Berikutnya ➡️", disabled=(current >= total_pages), key=f"{state_key}_next", use_container_width=True):
                current += 1

    st.session_state[state_key] = current
    start = (current - 1) * page_size
    end = start + page_size
    return start, end, current
