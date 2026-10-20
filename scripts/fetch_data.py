#!/usr/bin/env python3
"""Unduh ulang data gempa dari dua sumber resmi/terbuka.

1. BMKG (resmi, real-time, tanpa auth):
   - autogempa.json      : gempa terbaru
   - gempaterkini.json   : 15 gempa M5+ terbaru
   - gempadirasakan.json : 15 gempa dirasakan terbaru
2. USGS FDSN Event API (katalog historis): bbox Indonesia,
   2015-01-01 s.d. 2026-10-20, magnitudo >= 4.5.

Output: data/raw/*.json, data/raw/usgs_katalog.geojson
"""
import json
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (portfolio gempa-bumi-indonesia)"}

BMKG = "https://data.bmkg.go.id/DataMKG/TEWS/{}.json"
for name in ["autogempa", "gempaterkini", "gempadirasakan"]:
    req = urllib.request.Request(BMKG.format(name), headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read()
    (RAW / f"bmkg_{name}.json").write_bytes(data)
    print(f"BMKG {name}: {len(data)} bytes")

USGS = (
    "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson"
    "&starttime=2015-01-01&endtime=2026-10-20"
    "&minlatitude=-11&maxlatitude=6&minlongitude=95&maxlongitude=141"
    "&minmagnitude=4.5&orderby=time&limit=20000"
)
req = urllib.request.Request(USGS, headers=UA)
data = urllib.request.urlopen(req, timeout=600).read()
(RAW / "usgs_katalog.geojson").write_bytes(data)
n = len(json.loads(data)["features"])
print(f"USGS katalog: {n} fitur, {len(data)} bytes")
