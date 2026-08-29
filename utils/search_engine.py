"""
Search engine ringan untuk SultraTravel.
Menggabungkan TF-IDF cosine similarity (pemahaman makna & konteks kalimat)
dengan fuzzy matching (toleransi typo pada nama tempat/lokasi).
Didesain agar tidak bergantung pada model AI berukuran besar / koneksi internet saat runtime,
sehingga aplikasi tetap andal untuk kebutuhan demo maupun deployment.
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz

CATEGORY_KEYWORDS = {
    "bahari": ["bahari", "pantai", "pulau", "laut", "snorkel", "diving", "mangrove",
               "pasir putih", "biota laut", "terumbu karang", "wisata laut", "beach", "karang"],
    "religi": ["religi", "masjid", "gereja", "vihara", "klenteng", "makam", "ziarah",
               "tempat ibadah", "keagamaan", "islam", "kristen", "buddha", "hindu", "katedral"],
    "sejarah": ["sejarah", "budaya", "museum", "benteng", "istana", "adat", "tradisional",
                "peninggalan", "warisan", "keraton", "kesultanan", "situs", "goa purba"],
    "alam": ["alam", "air terjun", "gua", "bukit", "panorama", "taman nasional", "danau",
             "hotspring", "hutan", "pemandangan", "gunung", "sungai", "waterfall", "puncak"],
    "kuliner": ["kuliner", "makanan", "minuman", "masakan", "khas", "restoran", "warung",
                "makanan tradisional", "food", "makan", "minum", "sinonggi", "kasoami"],
}


class TourismSearchEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True) if df is not None else pd.DataFrame()
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()

    def _combined_text(self, row) -> str:
        parts = [
            str(row.get("nama", "")),
            str(row.get("kategori", "")),
            str(row.get("kabupaten_kota", "")),
            str(row.get("deskripsi", "")),
            str(row.get("fasilitas", "")),
        ]
        return " ".join(parts).lower()

    def _build_index(self):
        if self.df.empty:
            return
        corpus = self.df.apply(self._combined_text, axis=1).tolist()
        self.vectorizer = TfidfVectorizer(
            lowercase=True, ngram_range=(1, 2), min_df=1, max_df=0.95
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def refresh(self, df: pd.DataFrame):
        """Bangun ulang index ketika data berubah (mis. setelah admin menambah data)."""
        self.df = df.reset_index(drop=True) if df is not None else pd.DataFrame()
        self._build_index()

    def detect_category(self, query: str):
        q = query.lower()
        best_cat, best_hits = None, 0
        for cat, kws in CATEGORY_KEYWORDS.items():
            hits = sum(1 for kw in kws if kw in q)
            if hits > best_hits:
                best_cat, best_hits = cat, hits
        return best_cat

    def search(self, query: str, k=5, category=None, kabupaten=None, max_price_free_only=False):
        """Cari destinasi paling relevan berdasarkan query, dengan filter opsional."""
        if self.df.empty:
            return pd.DataFrame()

        candidates = self.df.copy()
        if category:
            candidates = candidates[candidates["kategori"] == category]
        if kabupaten:
            candidates = candidates[candidates["kabupaten_kota"] == kabupaten]
        if max_price_free_only:
            candidates = candidates[candidates["harga_tiket"].astype(str).str.lower().str.contains("gratis")]

        if candidates.empty:
            return candidates

        idx_pool = candidates.index.tolist()

        # Skor semantik via TF-IDF cosine similarity
        query_vec = self.vectorizer.transform([query.lower()])
        sims = cosine_similarity(query_vec, self.tfidf_matrix[idx_pool]).flatten()

        # Skor fuzzy matching pada nama tempat (menangkap typo / nama parsial)
        fuzzy_scores = np.array([
            fuzz.partial_ratio(query.lower(), str(self.df.loc[i, "nama"]).lower()) / 100.0
            for i in idx_pool
        ])

        combined = 0.7 * sims + 0.3 * fuzzy_scores
        order = np.argsort(-combined)

        result_indices = [idx_pool[i] for i in order[:k] if combined[i] > 0.03]
        if not result_indices:
            # fallback: tampilkan berdasarkan rating tertinggi dalam kandidat yang ada
            result_indices = candidates.sort_values("rating", ascending=False).index[:k].tolist()

        results = self.df.loc[result_indices].copy()
        results["skor_relevansi"] = [round(float(combined[idx_pool.index(i)]), 3) for i in result_indices]
        return results
