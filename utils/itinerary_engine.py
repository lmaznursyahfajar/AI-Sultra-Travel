"""
Itinerary Planner untuk SultraTravel.

Pendekatan: algoritma berbasis aturan (rule-based) yang menyusun rencana perjalanan
multi-hari dengan mempertimbangkan minat wisata, budget, rating, dan jarak antar lokasi
(nearest-neighbor heuristic memakai jarak Haversine) agar rute tidak bolak-balik jauh.
Tidak bergantung pada API AI eksternal berbayar sehingga selalu siap digunakan.
"""
import pandas as pd
from .map_utils import haversine_km, estimate_travel_time

BUDGET_MAP = {
    "hemat": 0,      # prioritas gratis / murah
    "menengah": 1,   # campuran
    "mewah": 2,      # tidak membatasi harga, prioritas rating tertinggi
}

PACE_STOPS_PER_DAY = {
    "santai": 2,
    "normal": 3,
    "padat": 4,
}

TIME_SLOTS = ["08:00 (Pagi)", "12:00 (Siang)", "15:30 (Sore)", "18:30 (Malam)"]


def _price_is_free(harga: str) -> bool:
    return "gratis" in str(harga).lower()


def _score_candidate(row, interests, budget_level):
    score = float(row.get("rating", 4.0))
    if interests and row.get("kategori") in interests:
        score += 1.5
    if budget_level == "hemat" and _price_is_free(row.get("harga_tiket", "")):
        score += 1.0
    return score


def generate_itinerary(df: pd.DataFrame, days: int, interests: list, budget_level: str,
                        start_location: list, pace: str = "normal"):
    """
    Menyusun itinerary N hari.
    Mengembalikan dict: {
        "days": [ {"day": 1, "stops": [ {...}, ... ], "total_distance_km": x }, ... ],
        "total_destinations": n,
        "estimasi_total_jarak_km": x
    }
    """
    if df is None or df.empty:
        return {"days": [], "total_destinations": 0, "estimasi_total_jarak_km": 0}

    pool = df.dropna(subset=["latitude", "longitude"]).copy()
    if interests:
        filtered = pool[pool["kategori"].isin(interests)]
        # jika filter terlalu ketat & hasil sedikit, tambahkan destinasi lain sebagai pelengkap
        if len(filtered) < days * PACE_STOPS_PER_DAY.get(pace, 3):
            extra = pool[~pool.index.isin(filtered.index)]
            pool = pd.concat([filtered, extra])
        else:
            pool = filtered

    if budget_level == "hemat":
        pool = pool.sort_values(
            by=["harga_tiket"], key=lambda s: s.astype(str).str.lower().str.contains("gratis"),
            ascending=False
        )

    pool["_skor"] = pool.apply(lambda r: _score_candidate(r, interests, budget_level), axis=1)
    pool = pool.sort_values("_skor", ascending=False)

    stops_per_day = PACE_STOPS_PER_DAY.get(pace, 3)
    total_needed = days * stops_per_day

    # Ambil kandidat terbaik (dengan sedikit buffer) lalu urutkan berdasar rute terdekat (nearest neighbor)
    candidates = pool.head(min(total_needed * 3, len(pool))).copy()

    ordered = []
    current_loc = start_location
    remaining = candidates.copy()
    while not remaining.empty and len(ordered) < total_needed:
        remaining["_jarak"] = remaining.apply(
            lambda r: haversine_km(current_loc, [r["latitude"], r["longitude"]]) or 999999, axis=1
        )
        # Gabungkan jarak terdekat dengan skor preferensi agar tetap relevan, bukan cuma dekat
        remaining["_gabungan"] = remaining["_jarak"] * 0.6 - remaining["_skor"] * 15
        best_idx = remaining["_gabungan"].idxmin()
        best_row = remaining.loc[best_idx]
        ordered.append(best_row)
        current_loc = [best_row["latitude"], best_row["longitude"]]
        remaining = remaining.drop(index=best_idx)

    # Bagi ke hari-hari
    result_days = []
    total_distance = 0.0
    cursor = start_location
    idx = 0
    for d in range(1, days + 1):
        day_stops = []
        for slot_i in range(stops_per_day):
            if idx >= len(ordered):
                break
            row = ordered[idx]
            coords = [row["latitude"], row["longitude"]]
            jarak = haversine_km(cursor, coords)
            waktu_tempuh = estimate_travel_time(jarak) if jarak is not None else "-"
            day_stops.append({
                "waktu": TIME_SLOTS[slot_i] if slot_i < len(TIME_SLOTS) else f"Slot {slot_i+1}",
                "nama": row["nama"],
                "kategori": row["kategori"],
                "kabupaten_kota": row["kabupaten_kota"],
                "harga_tiket": row["harga_tiket"],
                "deskripsi": row.get("deskripsi", ""),
                "jarak_dari_sebelumnya_km": round(jarak, 1) if jarak is not None else None,
                "estimasi_waktu_tempuh": waktu_tempuh,
                "rating": row.get("rating"),
            })
            if jarak:
                total_distance += jarak
            cursor = coords
            idx += 1
        if day_stops:
            result_days.append({"day": d, "stops": day_stops})

    return {
        "days": result_days,
        "total_destinations": sum(len(d["stops"]) for d in result_days),
        "estimasi_total_jarak_km": round(total_distance, 1),
    }


def itinerary_to_markdown(itinerary: dict, judul="Rencana Perjalanan Wisata Sulawesi Tenggara") -> str:
    lines = [f"# {judul}", ""]
    lines.append(f"Total destinasi: {itinerary['total_destinations']} | "
                 f"Estimasi total jarak tempuh: {itinerary['estimasi_total_jarak_km']} km")
    lines.append("")
    for day in itinerary["days"]:
        lines.append(f"## Hari ke-{day['day']}")
        for stop in day["stops"]:
            lines.append(f"**{stop['waktu']} — {stop['nama']}** ({stop['kategori'].title()}, {stop['kabupaten_kota']})")
            lines.append(f"- Tiket: {stop['harga_tiket']}")
            if stop["jarak_dari_sebelumnya_km"] is not None:
                lines.append(f"- Jarak dari titik sebelumnya: {stop['jarak_dari_sebelumnya_km']} km (~{stop['estimasi_waktu_tempuh']})")
            if stop.get("deskripsi"):
                lines.append(f"- {stop['deskripsi']}")
            lines.append("")
        lines.append("")
    return "\n".join(lines)
