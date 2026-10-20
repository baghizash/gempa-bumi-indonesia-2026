#!/usr/bin/env python3
"""Rakit CSV bersih dari data mentah BMKG + USGS.

Output:
  data/gempa_katalog_2015_2026.csv  katalog USGS yang sudah difilter Indonesia
  data/bmkg_terkini.csv             snapshot BMKG 15 gempa M5+ terbaru
  data/bmkg_dirasakan.csv           snapshot BMKG 15 gempa dirasakan terbaru

Aturan wilayah (didokumentasikan juga di data/SOURCES.md):
  1. Kejadian berlabel negara lain pada kolom place USGS (Philippines,
     Malaysia, Papua New Guinea, Palau) dikeluarkan dari katalog. Kejadian
     berlabel "Timor Leste" dipertahankan: episentrumnya berada di perairan
     Indonesia utara/timur Pulau Timor, kota acuannya saja yang di Timor Leste.
  2. Jika place menyebut nama laut/selat, wilayah = nama laut itu.
  3. Jika tidak, wilayah ditentukan dari kotak koordinat pulau terdekat.
  4. Sisanya masuk "Lainnya/Lepas Pantai".
Kelas kedalaman: Dangkal < 70 km, Menengah 70-300 km, Dalam > 300 km.
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

EXCLUDE_COUNTRY = ["philippines", "malaysia", "papua new guinea", "palau"]
# Catatan: kejadian berlabel "Timor Leste" TIDAK dikeluarkan. USGS memberi
# label kota terdekat; episentrumnya banyak berada di perairan Indonesia di
# utara/timur Pulau Timor (Selat Wetar, Laut Banda, sekitar P. Kisar/Wetar/
# Romang yang masuk NTT). Jumlahnya dihitung dan dilaporkan di SOURCES.md.

SEA_RULES = [
    ("banda sea", "Laut Banda"),
    ("molucca sea", "Laut Maluku"),
    ("ceram sea", "Laut Seram"),
    ("arafura sea", "Laut Arafura"),
    ("timor sea", "Laut Timor"),
    ("sunda strait", "Selat Sunda"),
    ("java sea", "Laut Jawa"),
    ("flores sea", "Laut Flores"),
    ("savu sea", "Laut Sawu"),
    ("celebes sea", "Laut Sulawesi"),
    ("indian ocean", "Samudra Hindia"),
]

# (nama, lon_min, lon_max, lat_min, lat_max) — kotak pulau terdekat,
# diperiksa berurutan; kotak spesifik ditaruh lebih dulu.
ISLAND_BOXES = [
    ("Halmahera & Maluku Utara", 126.0, 130.6, -1.2, 5.8),
    ("Maluku (Seram & Buru)", 125.0, 131.5, -4.2, -0.4),
    ("Sulawesi", 118.5, 128.0, -6.0, 5.8),
    ("Bali & Nusa Tenggara", 114.4, 121.0, -11.0, -7.4),
    ("Nusa Tenggara Timur", 121.0, 131.0, -11.0, -7.4),
    ("Jawa", 105.0, 114.4, -11.0, -5.4),
    ("Sumatera", 94.9, 106.0, -8.0, 5.8),
    ("Kalimantan", 108.9, 119.6, -3.6, 4.6),
    ("Papua", 130.6, 141.0, -9.0, 3.0),
]


def derive_region(place: str, lon: float, lat: float) -> str:
    p = (place or "").lower()
    for key, label in SEA_RULES:
        if key in p:
            return label
    for name, lo0, lo1, la0, la1 in ISLAND_BOXES:
        if lo0 <= lon <= lo1 and la0 <= lat <= la1:
            return name
    return "Lainnya/Lepas Pantai"


def depth_class(d: float) -> str:
    if d < 70:
        return "Dangkal (<70 km)"
    if d <= 300:
        return "Menengah (70-300 km)"
    return "Dalam (>300 km)"


def main():
    geo = json.loads((RAW / "usgs_katalog.geojson").read_text())
    rows, excluded = [], 0
    for f in geo["features"]:
        pr = f["properties"]
        place = pr.get("place") or ""
        low = place.lower()
        if any(c in low for c in EXCLUDE_COUNTRY):
            excluded += 1
            continue
        lon, lat, depth = f["geometry"]["coordinates"]
        t = pd.to_datetime(pr["time"], unit="ms", utc=True).tz_convert("Asia/Jakarta")
        rows.append(
            {
                "waktu_wib": t.strftime("%Y-%m-%d %H:%M:%S"),
                "tanggal": t.strftime("%Y-%m-%d"),
                "tahun": t.year,
                "bulan": t.strftime("%Y-%m"),
                "magnitudo": pr["mag"],
                "tipe_magnitudo": pr.get("magType"),
                "kedalaman_km": round(float(depth), 1),
                "kelas_kedalaman": depth_class(float(depth)),
                "lintang": lat,
                "bujur": lon,
                "lokasi_usgs": place,
                "wilayah": derive_region(place, lon, lat),
                "flag_tsunami_usgs": int(pr.get("tsunami") or 0),
                "dirasakan_mmi_maks": pr.get("mmi"),
                "id_usgs": f["id"],
            }
        )
    df = pd.DataFrame(rows).sort_values("waktu_wib").reset_index(drop=True)
    df.to_csv(ROOT / "data" / "gempa_katalog_2015_2026.csv", index=False)
    print(f"Katalog USGS mentah : {len(geo['features'])} kejadian")
    print(f"Dikeluarkan (negara lain): {excluded}")
    print(f"Katalog Indonesia   : {len(df)} kejadian")
    print("Berlabel Timor Leste (dipertahankan):", int(df["lokasi_usgs"].str.contains("Timor Leste").sum()))
    print(df["wilayah"].value_counts().to_string())

    # ---- BMKG gempaterkini ----
    def parse_bmkg(path):
        d = json.loads(Path(path).read_text())
        g = d["Infogempa"]["gempa"]
        return g if isinstance(g, list) else [g]

    def bmkg_rows(items):
        out = []
        for g in items:
            lat_s, lon_s = g["Coordinates"].split(",")
            out.append(
                {
                    "tanggal": g["Tanggal"],
                    "jam": g["Jam"],
                    "datetime_utc": g["DateTime"],
                    "lintang": float(lat_s),
                    "bujur": float(lon_s),
                    "magnitudo": float(g["Magnitude"]),
                    "kedalaman": g["Kedalaman"],
                    "wilayah": g["Wilayah"],
                    "potensi": g.get("Potensi", "-"),
                    "dirasakan": g.get("Dirasakan", "-"),
                }
            )
        return pd.DataFrame(out)

    tk = bmkg_rows(parse_bmkg(RAW / "bmkg_gempaterkini.json"))
    tk.to_csv(ROOT / "data" / "bmkg_terkini.csv", index=False)
    dr = bmkg_rows(parse_bmkg(RAW / "bmkg_gempadirasakan.json"))
    dr.to_csv(ROOT / "data" / "bmkg_dirasakan.csv", index=False)
    auto = parse_bmkg(RAW / "bmkg_autogempa.json")[0]
    pd.DataFrame([auto]).to_csv(ROOT / "data" / "bmkg_autogempa.csv", index=False)
    print(f"BMKG terkini: {len(tk)} baris | dirasakan: {len(dr)} baris")


if __name__ == "__main__":
    main()
