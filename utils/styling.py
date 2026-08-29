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
    }}
    .dest-card-body {{
        padding: 14px 18px 16px 18px;
        border-top: 3px solid {SECONDARY};
    }}
    .dest-card-body h4 {{
        margin: 0 0 6px 0;
        color: {PRIMARY};
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
    deskripsi = str(row.get("deskripsi", "") or "")[:130]

    st.markdown(
        f"""<div class="dest-card">
        <img class="dest-card-photo" src="{photo['url']}" loading="lazy"
             onerror="this.style.display='none'"/>
        <div class="dest-card-body">
        <h4>{emoji} {row.get('nama','')}</h4>
        <span class="badge">{label}</span>
        <span class="badge badge-amber">⭐ {row.get('rating','-')}</span>
        <p style="margin-top:8px; color:#445; font-size:0.9rem;">
        📍 {row.get('kabupaten_kota','-')} • 💰 {row.get('harga_tiket','-')}{extra_info_html}</p>
        <p style="color:#556; font-size:0.87rem;">{deskripsi}{'...' if deskripsi else ''}</p>
        </div></div>""",
        unsafe_allow_html=True,
    )
    if photo.get("credit"):
        st.markdown(f"""<div class="photo-credit">{photo['credit']}</div>""", unsafe_allow_html=True)
