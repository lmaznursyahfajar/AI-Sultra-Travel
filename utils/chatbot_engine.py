"""
Chatbot AI SultraTravel — deteksi intent sederhana berbasis aturan + pencarian TF-IDF/fuzzy.
"""
import datetime
import numpy as np
import pandas as pd
from .search_engine import TourismSearchEngine
from .database import KATEGORI_LABELS

GREETINGS = ["halo", "hai", "hi", "hello", "selamat pagi", "selamat siang", "selamat sore",
             "selamat malam", "pagi", "siang", "sore", "malam", "hey"]
FAREWELLS = ["terima kasih", "makasih", "thanks", "bye", "dadah", "sampai jumpa", "selesai"]
HELP_WORDS = ["bantuan", "help", "tolong", "apa yang bisa kamu bantu", "fitur", "cara menggunakan", "petunjuk"]


class TourismChatbot:
    def __init__(self, df):
        self.df = df
        self.search_engine = TourismSearchEngine(df)

    def refresh(self, df):
        self.df = df
        self.search_engine.refresh(df)

    def detect_intent(self, query: str) -> str:
        q = query.lower().strip()
        if any(g in q for g in GREETINGS) and len(q.split()) <= 4:
            return "greeting"
        if any(f in q for f in FAREWELLS):
            return "farewell"
        if any(h in q for h in HELP_WORDS):
            return "help"
        category = self.search_engine.detect_category(q)
        if category:
            return f"category_{category}"
        if any(w in q for w in ["murah", "hemat", "budget", "gratis", "biaya", "tarif"]):
            return "budget"
        if any(w in q for w in ["keluarga", "anak", "anak-anak", "family", "ramah anak"]):
            return "family"
        if any(w in q for w in ["rute", "jalan", "arah", "petunjuk arah", "jarak", "dimana", "lokasi"]):
            return "route"
        return "search"

    def search(self, query, k=5, category=None):
        return self.search_engine.search(query, k=k, category=category)

    def respond(self, query, intent, results=None, user_location=None):
        if intent == "greeting":
            return self._greeting()
        if intent == "farewell":
            return self._farewell()
        if intent == "help":
            return self._help()
        if intent == "budget":
            return self._budget(results)
        if intent == "family":
            return self._family(results)
        if intent == "route":
            return self._route(results, user_location)
        if intent.startswith("category_"):
            cat = intent.split("_", 1)[1]
            return self._category(cat, results)
        return self._search(query, results)

    def _greeting(self):
        jam = datetime.datetime.now().hour
        waktu = "Pagi" if 5 <= jam < 12 else "Siang" if 12 <= jam < 15 else "Sore" if 15 <= jam < 19 else "Malam"
        return (f"🏝️ Selamat {waktu}! Saya asisten SultraTravel, siap membantu Anda menemukan "
                f"destinasi wisata terbaik di Sulawesi Tenggara. Mau cari wisata apa hari ini?")

    def _farewell(self):
        return ("🙏 Terima kasih sudah menggunakan SultraTravel! Semoga perjalanan Anda di "
                "Sulawesi Tenggara menyenangkan. Sampai jumpa lagi! 🌊")

    def _help(self):
        kategori_list = "\n".join(
            f"{emoji} **{label}**" for emoji, label in KATEGORI_LABELS.values()
        )
        return f"""**🎯 Saya bisa membantu Anda mencari:**

{kategori_list}

**💡 Contoh pertanyaan:**
- "Rekomendasi pantai bagus di Kendari"
- "Wisata alam untuk keluarga"
- "Tempat wisata murah/gratis"
- "Rute ke Air Terjun Moramo"
- "Kuliner khas Sulawesi Tenggara"

Silakan tanyakan apa saja seputar wisata Sulawesi Tenggara! 😊"""

    def _budget(self, results):
        if results is None or results.empty:
            return ("💰 **Tips wisata hemat di Sultra:** kunjungi pantai umum yang gratis, "
                    "manfaatkan transportasi bersama, dan nikmati kuliner kaki lima. "
                    "Coba tanyakan 'destinasi gratis di Kendari'.")
        text = "💰 **Rekomendasi wisata ramah kantong:**\n\n"
        sorted_r = results.copy()
        sorted_r["_gratis"] = sorted_r["harga_tiket"].astype(str).str.lower().str.contains("gratis")
        sorted_r = sorted_r.sort_values("_gratis", ascending=False)
        for i, (_, r) in enumerate(sorted_r.head(3).iterrows(), 1):
            label = "🆓 GRATIS" if r["_gratis"] else "💵 Terjangkau"
            text += f"**{i}. {r['nama']}** — {label}\n📍 {r['kabupaten_kota']} • 💰 {r['harga_tiket']}\n\n"
        return text

    def _family(self, results):
        if results is None or results.empty:
            return "👨‍👩‍👧‍👦 Untuk wisata keluarga, coba tanyakan 'pantai ramah anak' atau 'taman rekreasi keluarga'."
        text = "👨‍👩‍👧‍👦 **Rekomendasi wisata keluarga:**\n\n"
        for i, (_, r) in enumerate(results.head(3).iterrows(), 1):
            text += f"**{i}. {r['nama']}** ⭐ {r['rating']}\n📍 {r['kabupaten_kota']} • {r.get('fasilitas', '-')}\n\n"
        return text

    def _route(self, results, user_location):
        if results is None or results.empty:
            return "🗺️ Sebutkan nama destinasi yang Anda tuju agar saya bisa bantu tampilkan rute dan estimasi jaraknya."
        from .map_utils import haversine_km, estimate_travel_time
        text = "🗺️ **Informasi rute & jarak:**\n\n"
        for i, (_, r) in enumerate(results.head(3).iterrows(), 1):
            text += f"**{i}. {r['nama']}** — {r['kabupaten_kota']}\n"
            if user_location and not pd.isna(r.get("latitude")):
                jarak = haversine_km(user_location, [r["latitude"], r["longitude"]])
                if jarak:
                    text += f"   📏 ±{jarak:.1f} km dari lokasi Anda (~{estimate_travel_time(jarak)})\n"
            text += "\n"
        text += "_Aktifkan peta di bawah untuk melihat rute secara visual._"
        return text

    def _category(self, kategori, results):
        emoji, label = KATEGORI_LABELS.get(kategori, ("📍", kategori.title()))
        if results is None or results.empty:
            return f"{emoji} Maaf, belum ada data untuk kategori {label} sesuai pencarian Anda."
        text = f"{emoji} **Rekomendasi wisata {label}:**\n\n"
        for i, (_, r) in enumerate(results.head(5).iterrows(), 1):
            text += f"**{i}. {r['nama']}** ⭐ {r['rating']}\n📍 {r['kabupaten_kota']} • 💰 {r['harga_tiket']}\n"
            text += f"_{str(r.get('deskripsi',''))[:120]}..._\n\n"
        return text

    def _search(self, query, results):
        if results is None or results.empty:
            return (f"🔍 Maaf, saya belum menemukan destinasi yang cocok untuk \"{query}\". "
                    f"Coba gunakan kata kunci lain, misalnya nama kategori (pantai, air terjun, museum) "
                    f"atau kabupaten/kota tujuan.")
        text = f"🔍 **Hasil pencarian untuk \"{query}\":**\n\n"
        for i, (_, r) in enumerate(results.head(5).iterrows(), 1):
            text += f"**{i}. {r['nama']}** ⭐ {r['rating']}\n📍 {r['kabupaten_kota']} • 💰 {r['harga_tiket']}\n"
            text += f"_{str(r.get('deskripsi',''))[:120]}..._\n\n"
        return text
