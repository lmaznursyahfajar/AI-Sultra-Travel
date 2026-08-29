"""
Modul manajemen foto destinasi SultraTravel.

Strategi:
1. Untuk destinasi unggulan/terkenal, gunakan foto ASLI berlisensi bebas dari
   Wikimedia Commons (CC BY-SA / Domain Publik) yang aman untuk digunakan ulang
   dengan atribusi — bukan hasil scraping sembarang dari web.
2. Untuk destinasi yang belum memiliki foto asli, tampilkan placeholder
   ilustrasi bergradasi (SVG orisinal, dibuat sendiri) sesuai kategori — bukan
   foto berhak cipta pihak lain — sehingga tampilan tetap rapi & profesional.
3. Admin dapat menambahkan/meng-update URL foto asli kapan saja lewat Panel Admin
   (mendukung foto koleksi sendiri, Google Drive, atau sumber berlisensi bebas lain).
"""
import base64
import hashlib

WIKIMEDIA_BASE = "https://commons.wikimedia.org/wiki/Special:FilePath/"

# Foto asli terverifikasi dari Wikimedia Commons (berlisensi bebas / CC BY-SA / PD)
# untuk destinasi unggulan Sulawesi Tenggara.
FLAGSHIP_PHOTOS = {
    "Taman Nasional Wakatobi": {
        "file": "Wakatobi-188.jpg",
        "credit": "Foto: Craig D / Wikimedia Commons (CC BY-SA 2.0)",
    },
    "Benteng Keraton Buton (Benteng Wolio)": {
        "file": "Benteng_Wolio.jpg",
        "credit": "Foto: Wikimedia Commons (Dok. Pemerintah Indonesia, domain publik)",
    },
    "Air Terjun Moramo": {
        "file": "Air_Terjun_Moramo.jpg",
        "credit": "Foto: Firstlab18 / Wikimedia Commons (CC BY-SA 4.0)",
    },
    "Masjid Al-Alam Kendari": {
        "file": "Masjid_Al_Alam_Kendari.jpg",
        "credit": "Foto: Didym / Wikimedia Commons (CC BY-SA 4.0)",
    },
    "Pulau Labengki": {
        "file": "Pulau_Labengki_Besar.jpg",
        "credit": "Foto: Wikimedia Commons (CC BY-SA 4.0)",
    },
}

# Palet gradasi & ikon per kategori untuk placeholder foto (SVG orisinal)
CATEGORY_VISUAL = {
    "bahari": {"c1": "#0E7C86", "c2": "#14919B", "icon": "wave"},
    "alam": {"c1": "#2E7D4F", "c2": "#4CAF6D", "icon": "leaf"},
    "sejarah": {"c1": "#8A5A2B", "c2": "#B8834A", "icon": "arch"},
    "religi": {"c1": "#5B4B8A", "c2": "#7C67B0", "icon": "dome"},
    "kuliner": {"c1": "#C1521F", "c2": "#E08339", "icon": "plate"},
}

_ICON_PATHS = {
    "wave": '<path d="M20 130 Q45 100 70 130 T120 130 T170 130 T220 130" stroke="white" stroke-width="6" fill="none" opacity="0.85"/>'
            '<path d="M20 155 Q45 125 70 155 T120 155 T170 155 T220 155" stroke="white" stroke-width="6" fill="none" opacity="0.55"/>',
    "leaf": '<path d="M120 60 C170 70 185 120 150 165 C115 200 70 190 65 150 C60 105 90 65 120 60 Z" fill="white" opacity="0.85"/>'
            '<path d="M120 60 C110 100 100 140 65 150" stroke="#2E7D4F" stroke-width="4" fill="none" opacity="0.6"/>',
    "arch": '<rect x="60" y="140" width="120" height="14" fill="white" opacity="0.9"/>'
            '<rect x="70" y="80" width="14" height="60" fill="white" opacity="0.85"/>'
            '<rect x="103" y="80" width="14" height="60" fill="white" opacity="0.85"/>'
            '<rect x="136" y="80" width="14" height="60" fill="white" opacity="0.85"/>'
            '<rect x="169" y="80" width="14" height="60" fill="white" opacity="0.85"/>'
            '<polygon points="60,80 120,45 180,80" fill="white" opacity="0.9"/>',
    "dome": '<path d="M75 145 A45 42 0 0 1 165 145 Z" fill="white" opacity="0.9"/>'
            '<rect x="66" y="145" width="108" height="10" fill="white" opacity="0.9"/>'
            '<rect x="112" y="88" width="16" height="30" fill="white" opacity="0.9"/>'
            '<path d="M120 78 a9 9 0 1 0 0.1 0" fill="white" opacity="0.9"/>'
            '<path d="M116 78 a7 7 0 1 0 7 -9 a9 9 0 0 1 -7 9 Z" fill="#5B4B8A" opacity="0.9"/>',
    "plate": '<circle cx="120" cy="120" r="55" fill="none" stroke="white" stroke-width="6" opacity="0.85"/>'
             '<circle cx="120" cy="120" r="30" fill="none" stroke="white" stroke-width="4" opacity="0.6"/>',
}


def _slug(text: str) -> str:
    return "".join(c for c in text.lower().replace(" ", "-") if c.isalnum() or c == "-")


def wikimedia_url(filename: str, width: int = 800) -> str:
    return f"{WIKIMEDIA_BASE}{filename}?width={width}"


def placeholder_data_uri(kategori: str, nama: str) -> str:
    """Menghasilkan placeholder foto berupa SVG orisinal (data URI), bergradasi sesuai kategori."""
    visual = CATEGORY_VISUAL.get(kategori, CATEGORY_VISUAL["alam"])
    icon_svg = _ICON_PATHS.get(visual["icon"], "")
    # variasi kecil sudut gradasi berdasarkan hash nama agar antar kartu tidak identik 100%
    seed = int(hashlib.md5(nama.encode()).hexdigest(), 16) % 4
    angle_map = {0: "0%", 1: "20%", 2: "80%", 3: "100%"}
    x2 = angle_map[seed]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">
<defs>
<linearGradient id="g" x1="0%" y1="0%" x2="{x2}" y2="100%">
<stop offset="0%" stop-color="{visual['c1']}"/>
<stop offset="100%" stop-color="{visual['c2']}"/>
</linearGradient>
</defs>
<rect width="400" height="240" fill="url(#g)"/>
<g transform="translate(80,0)">{icon_svg}</g>
<rect x="0" y="196" width="400" height="44" fill="rgba(0,0,0,0.22)"/>
</svg>"""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def get_photo(row) -> dict:
    """
    Mengembalikan dict {url, credit, is_placeholder} untuk sebuah baris destinasi.
    Prioritas: foto_url dari database (diisi admin) > foto unggulan terverifikasi > placeholder.
    """
    foto_url = str(row.get("foto_url") or "").strip()
    if foto_url and foto_url.lower() != "nan":
        return {"url": foto_url, "credit": str(row.get("foto_kredit") or ""), "is_placeholder": False}

    flagship = FLAGSHIP_PHOTOS.get(row.get("nama"))
    if flagship:
        return {
            "url": wikimedia_url(flagship["file"]),
            "credit": flagship["credit"],
            "is_placeholder": False,
        }

    return {
        "url": placeholder_data_uri(row.get("kategori", "alam"), row.get("nama", "")),
        "credit": "",
        "is_placeholder": True,
    }
