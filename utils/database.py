"""
Modul database untuk SultraTravel - Aplikasi Manajemen Pariwisata Sulawesi Tenggara
Menggunakan SQLite sebagai penyimpanan lokal yang ringan dan tanpa perlu server terpisah.
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "sultra_tourism.db")
SEED_CSV_PATH = os.path.join(BASE_DIR, "data", "seed_wisata_sultra.csv")

KATEGORI_LABELS = {
    "bahari": ("🏖️", "Bahari"),
    "alam": ("🌳", "Alam"),
    "sejarah": ("🏛️", "Sejarah & Budaya"),
    "religi": ("🕌", "Religi"),
    "kuliner": ("🍽️", "Kuliner"),
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS destinasi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    kategori TEXT NOT NULL,
    kabupaten_kota TEXT NOT NULL,
    deskripsi TEXT,
    harga_tiket TEXT,
    jam_operasional TEXT,
    fasilitas TEXT,
    rating REAL DEFAULT 4.0,
    latitude REAL,
    longitude REAL,
    kontak TEXT,
    tips TEXT,
    foto_url TEXT,
    foto_kredit TEXT,
    status TEXT DEFAULT 'aktif',
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS log_aktivitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aksi TEXT,
    detail TEXT,
    waktu TEXT
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate_schema(conn):
    """Menambahkan kolom baru ke database lama agar tetap kompatibel (idempotent)."""
    existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(destinasi)").fetchall()}
    migrations = {
        "foto_url": "ALTER TABLE destinasi ADD COLUMN foto_url TEXT",
        "foto_kredit": "ALTER TABLE destinasi ADD COLUMN foto_kredit TEXT",
    }
    for col, ddl in migrations.items():
        if col not in existing_cols:
            conn.execute(ddl)


def _row_to_tuple(r, now):
    return (
        r["nama"], r["kategori"], r["kabupaten_kota"], r.get("deskripsi", ""),
        r.get("harga_tiket", ""), r.get("jam_operasional", ""), r.get("fasilitas", ""),
        float(r.get("rating", 4.0)) if not pd.isna(r.get("rating", 4.0)) else 4.0,
        float(r.get("latitude")) if not pd.isna(r.get("latitude")) else None,
        float(r.get("longitude")) if not pd.isna(r.get("longitude")) else None,
        r.get("kontak", ""), r.get("tips", ""),
        r.get("foto_url", "") if not pd.isna(r.get("foto_url", "")) else "",
        r.get("foto_kredit", "") if not pd.isna(r.get("foto_kredit", "")) else "",
        "aktif", now, now
    )


_INSERT_SQL = """INSERT INTO destinasi
   (nama, kategori, kabupaten_kota, deskripsi, harga_tiket, jam_operasional,
    fasilitas, rating, latitude, longitude, kontak, tips, foto_url, foto_kredit,
    status, created_at, updated_at)
   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""


def init_db():
    """
    Inisialisasi database. Jika kosong, isi penuh dengan data awal (seed) dari CSV.
    Jika database SUDAH ADA ISINYA (misalnya dari deployment sebelumnya dengan dataset
    yang lebih sedikit), fungsi ini tetap mengecek dan menambahkan destinasi seed yang
    BELUM ada (dicocokkan berdasarkan nama) — sehingga pembaruan dataset otomatis
    tersinkron tanpa menghapus atau menimpa data yang sudah diedit/ditambahkan admin.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        _migrate_schema(conn)

        if not os.path.exists(SEED_CSV_PATH):
            return

        seed_df = pd.read_csv(SEED_CSV_PATH)
        now = datetime.now().isoformat(timespec="seconds")

        existing_names = {
            row["nama"] for row in conn.execute("SELECT nama FROM destinasi").fetchall()
        }

        if not existing_names:
            # Database benar-benar kosong -> muat seluruh seed data
            rows = [_row_to_tuple(r, now) for _, r in seed_df.iterrows()]
            conn.executemany(_INSERT_SQL, rows)
            log_activity(conn, "seed_data", f"Memuat {len(rows)} destinasi awal dari dataset seed")
        else:
            # Database sudah ada isinya -> hanya tambahkan destinasi seed yang belum ada
            missing = seed_df[~seed_df["nama"].isin(existing_names)]
            if not missing.empty:
                rows = [_row_to_tuple(r, now) for _, r in missing.iterrows()]
                conn.executemany(_INSERT_SQL, rows)
                log_activity(
                    conn, "sinkronisasi_seed",
                    f"Menyinkronkan {len(rows)} destinasi baru dari pembaruan dataset seed"
                )


def log_activity(conn, aksi, detail):
    conn.execute(
        "INSERT INTO log_aktivitas (aksi, detail, waktu) VALUES (?,?,?)",
        (aksi, detail, datetime.now().isoformat(timespec="seconds"))
    )


def get_all_destinations(only_active=True) -> pd.DataFrame:
    with get_connection() as conn:
        query = "SELECT * FROM destinasi"
        if only_active:
            query += " WHERE status = 'aktif'"
        query += " ORDER BY nama ASC"
        df = pd.read_sql_query(query, conn)
    return df


def get_destination_by_id(dest_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM destinasi WHERE id = ?", (dest_id,)).fetchone()
        return dict(row) if row else None


def add_destination(data: dict):
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO destinasi
               (nama, kategori, kabupaten_kota, deskripsi, harga_tiket, jam_operasional,
                fasilitas, rating, latitude, longitude, kontak, tips, foto_url, foto_kredit,
                status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data["nama"], data["kategori"], data["kabupaten_kota"], data.get("deskripsi", ""),
             data.get("harga_tiket", ""), data.get("jam_operasional", ""), data.get("fasilitas", ""),
             data.get("rating", 4.0), data.get("latitude"), data.get("longitude"),
             data.get("kontak", ""), data.get("tips", ""), data.get("foto_url", ""),
             data.get("foto_kredit", ""), "aktif", now, now)
        )
        log_activity(conn, "tambah", f"Menambahkan destinasi '{data['nama']}'")
        return cur.lastrowid


def update_destination(dest_id: int, data: dict):
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            """UPDATE destinasi SET nama=?, kategori=?, kabupaten_kota=?, deskripsi=?,
               harga_tiket=?, jam_operasional=?, fasilitas=?, rating=?, latitude=?, longitude=?,
               kontak=?, tips=?, foto_url=?, foto_kredit=?, updated_at=? WHERE id=?""",
            (data["nama"], data["kategori"], data["kabupaten_kota"], data.get("deskripsi", ""),
             data.get("harga_tiket", ""), data.get("jam_operasional", ""), data.get("fasilitas", ""),
             data.get("rating", 4.0), data.get("latitude"), data.get("longitude"),
             data.get("kontak", ""), data.get("tips", ""), data.get("foto_url", ""),
             data.get("foto_kredit", ""), now, dest_id)
        )
        log_activity(conn, "ubah", f"Memperbarui destinasi id={dest_id} ('{data['nama']}')")


def delete_destination(dest_id: int, hard_delete=False):
    with get_connection() as conn:
        if hard_delete:
            conn.execute("DELETE FROM destinasi WHERE id=?", (dest_id,))
            log_activity(conn, "hapus_permanen", f"Menghapus permanen destinasi id={dest_id}")
        else:
            conn.execute("UPDATE destinasi SET status='nonaktif' WHERE id=?", (dest_id,))
            log_activity(conn, "nonaktifkan", f"Menonaktifkan destinasi id={dest_id}")


def restore_destination(dest_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE destinasi SET status='aktif' WHERE id=?", (dest_id,))
        log_activity(conn, "aktifkan", f"Mengaktifkan kembali destinasi id={dest_id}")


def get_recent_logs(limit=20) -> pd.DataFrame:
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM log_aktivitas ORDER BY id DESC LIMIT ?", conn, params=(limit,)
        )
    return df


def get_stats() -> dict:
    df = get_all_destinations()
    if df.empty:
        return {"total": 0}
    return {
        "total": len(df),
        "per_kategori": df["kategori"].value_counts().to_dict(),
        "per_kabupaten": df["kabupaten_kota"].value_counts().to_dict(),
        "rata_rating": round(df["rating"].mean(), 2),
        "gratis": int(df["harga_tiket"].astype(str).str.lower().str.contains("gratis").sum()),
    }
