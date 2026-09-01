# pages/2_💬_Chatbot_AI.py — Chatbot AI pencarian wisata
import datetime
import streamlit as st
from utils.database import init_db, get_all_destinations, KATEGORI_LABELS
from utils.styling import inject_base_css, page_header, footer
from utils.chatbot_engine import TourismChatbot
from utils.leaflet_map import render_interactive_map
from utils.photo_utils import get_photo

st.set_page_config(page_title="Chatbot AI — SultraTravel", page_icon="💬", layout="wide")
init_db()
inject_base_css()
page_header("💬 Chatbot AI SultraTravel", "Tanyakan rekomendasi wisata dengan bahasa sehari-hari.")

df = get_all_destinations()

if df.empty:
    st.warning("Belum ada data destinasi. Silakan tambahkan data melalui Panel Admin.")
    st.stop()

# ==============================
# Inisialisasi state
# ==============================
if "chatbot" not in st.session_state or st.session_state.get("chatbot_data_len") != len(df):
    st.session_state["chatbot"] = TourismChatbot(df)
    st.session_state["chatbot_data_len"] = len(df)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "quick_query" not in st.session_state:
    st.session_state["quick_query"] = ""
if "show_map_chat" not in st.session_state:
    st.session_state["show_map_chat"] = True

chatbot: TourismChatbot = st.session_state["chatbot"]
user_location = st.session_state.get("user_location")

# ==============================
# Pertanyaan cepat
# ==============================
st.markdown("##### 🚀 Pertanyaan Cepat")
suggestions = [
    ("🏖️ Pantai Terkenal", "Rekomendasi pantai terkenal di Sulawesi Tenggara"),
    ("🌳 Wisata Alam", "Tempat wisata alam dan air terjun yang indah"),
    ("👨‍👩‍👧‍👦 Untuk Keluarga", "Wisata yang cocok untuk keluarga dan anak-anak"),
    ("🍽️ Kuliner Khas", "Makanan khas dan tempat kuliner terbaik di Sultra"),
    ("🏛️ Sejarah & Budaya", "Destinasi sejarah dan budaya Sulawesi Tenggara"),
    ("💰 Budget Terbatas", "Rekomendasi wisata murah dan gratis"),
]
cols = st.columns(6)
for i, (label, q) in enumerate(suggestions):
    with cols[i]:
        if st.button(label, key=f"sugg_{i}", use_container_width=True):
            st.session_state["quick_query"] = q

st.markdown("---")

# ==============================
# Riwayat percakapan
# ==============================
chat_box = st.container()
with chat_box:
    if not st.session_state["chat_history"]:
        st.info("👋 Mulai percakapan dengan mengetik pertanyaan di bawah, atau klik salah satu pertanyaan cepat di atas.")
    for chat in st.session_state["chat_history"]:
        if chat["role"] == "user":
            st.markdown(
                f"""<div class="chat-bubble-user"><b>Anda</b> • {chat['time']}<br>{chat['content']}</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""<div class="chat-bubble-bot"><b>🏝️ SultraTravel AI</b> • {chat['time']}<br>{chat['content']}</div>""",
                unsafe_allow_html=True,
            )
            if chat.get("results") is not None and not chat["results"].empty:
                thumb_cols = st.columns(min(4, len(chat["results"])))
                for i, (_, r) in enumerate(chat["results"].head(4).iterrows()):
                    photo = get_photo(r)
                    emoji, _ = KATEGORI_LABELS.get(r["kategori"], ("📍", r["kategori"]))
                    with thumb_cols[i]:
                        st.markdown(
                            f"""<div class="dest-card" style="margin-bottom:6px;">
                            <img class="dest-card-photo" src="{photo['url']}" style="height:90px;"
                                 onerror="this.style.display='none'"/>
                            <div class="dest-card-body" style="padding:8px 10px;">
                            <div style="font-size:0.82rem;font-weight:700;color:#0F3D3E;">{emoji} {r['nama']}</div>
                            <div style="font-size:0.75rem;color:#667;">⭐ {r['rating']} • {r['kabupaten_kota']}</div>
                            </div></div>""",
                            unsafe_allow_html=True,
                        )
                if st.session_state["show_map_chat"]:
                    with st.expander("🗺️ Lihat di peta", expanded=False):
                        render_interactive_map(chat["results"], user_location=user_location, height=420)

# ==============================
# Input pengguna
# ==============================
st.markdown("---")
in_col1, in_col2, in_col3 = st.columns([5, 1, 1])
with in_col1:
    query = st.text_input(
        "Tulis pertanyaan Anda",
        value=st.session_state["quick_query"],
        key="query_input",
        label_visibility="collapsed",
        placeholder="💭 Contoh: 'Rekomendasi pantai bagus di Kendari' atau 'wisata sejarah di Buton'...",
    )
with in_col2:
    st.session_state["show_map_chat"] = st.checkbox("🗺️ Peta", value=st.session_state["show_map_chat"])
with in_col3:
    send = st.button("Kirim 💬", type="primary", use_container_width=True)

if send and query.strip():
    st.session_state["quick_query"] = ""
    now = datetime.datetime.now().strftime("%H:%M")
    st.session_state["chat_history"].append({"role": "user", "content": query, "time": now, "results": None})

    intent = chatbot.detect_intent(query)
    results = None
    if intent not in ["greeting", "farewell", "help"]:
        category = intent.split("_", 1)[1] if intent.startswith("category_") else None
        results = chatbot.search(query, k=6, category=category)

    response = chatbot.respond(query, intent, results=results, user_location=user_location)
    st.session_state["chat_history"].append({
        "role": "assistant", "content": response,
        "time": datetime.datetime.now().strftime("%H:%M"), "results": results
    })
    st.rerun()

if st.button("🗑️ Bersihkan Riwayat Percakapan"):
    st.session_state["chat_history"] = []
    st.rerun()

footer()
