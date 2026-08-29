"""
Utilitas perhitungan jarak untuk SultraTravel.
Peta interaktif kini ditangani oleh utils/leaflet_map.py (Leaflet.js, ala Google Maps).
Modul ini hanya menyisakan fungsi perhitungan jarak yang dipakai bersama oleh
itinerary_engine, chatbot_engine, dan halaman-halaman lain.
"""
import math


def haversine_km(coord1, coord2):
    """Menghitung jarak antara dua koordinat (lat, lon) dalam kilometer (garis lurus)."""
    if not coord1 or not coord2:
        return None
    try:
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return 6371 * c
    except Exception:
        return None


def estimate_travel_time(distance_km, avg_speed_kmh=35):
    if distance_km is None:
        return None
    hours = distance_km / avg_speed_kmh
    if hours < 1:
        return f"{hours * 60:.0f} menit"
    return f"{hours:.1f} jam"
