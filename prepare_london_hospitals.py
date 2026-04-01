#!/usr/bin/env python3
import csv
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "london_hospitals.geojson"
TMP = Path("/tmp")
DIRECTORY_PATH = TMP / "cqc_directory.csv"
RATING_CACHE_PATH = TMP / "cqc_hospital_rating_cache.json"

DIRECTORY_URL = "https://www.cqc.org.uk/sites/default/files/2026-04/01_April_2026_CQC_directory.csv"
POSTCODE_BATCH_URL = "https://api.postcodes.io/postcodes"

LONDON_BOROUGHS = {
    "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley", "Camden",
    "City of London", "Croydon", "Ealing", "Enfield", "Greenwich", "Hackney",
    "Hammersmith and Fulham", "Haringey", "Harrow", "Havering", "Hillingdon",
    "Hounslow", "Islington", "Kensington and Chelsea", "Kingston upon Thames",
    "Lambeth", "Lewisham", "Merton", "Newham", "Redbridge",
    "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets",
    "Waltham Forest", "Wandsworth", "Westminster",
}

HOSPITAL_SERVICE_TYPES = {
    "Hospital",
    "Hospitals - Mental health/capacity",
}

RATING_ORDER = {
    "Outstanding": 1,
    "Good": 2,
    "Requires improvement": 3,
    "Inadequate": 4,
    "Not rated": 5,
}

USER_AGENT = "LondonBibleHospitals/1.0 (+https://github.com/renzorico/map-maker)"


def clean(value):
    value = (value or "").strip()
    return value or None


def ensure_directory_csv():
    if DIRECTORY_PATH.exists() and DIRECTORY_PATH.stat().st_size > 1000:
        return
    response = requests.get(DIRECTORY_URL, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    DIRECTORY_PATH.write_bytes(response.content)


def load_rating_cache():
    if not RATING_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(RATING_CACHE_PATH.read_text())
    except Exception:
        return {}


def save_rating_cache(cache):
    RATING_CACHE_PATH.write_text(json.dumps(cache, separators=(",", ":")))


def load_hospital_rows():
    ensure_directory_csv()
    with DIRECTORY_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[4]
    idx = {name: i for i, name in enumerate(header)}
    hospitals = []
    for row in rows[5:]:
        if len(row) < len(header):
            row += [""] * (len(header) - len(row))
        region = clean(row[idx["Region"]])
        borough = clean(row[idx["Local authority"]])
        service_types = [part.strip() for part in (row[idx["Service types"]] or "").split("|") if part.strip()]
        if region != "London" or borough not in LONDON_BOROUGHS:
            continue
        if not any(service_type in HOSPITAL_SERVICE_TYPES for service_type in service_types):
            continue
        hospitals.append({
            "hospital_name": clean(row[idx["Name"]]) or "Hospital",
            "also_known_as": clean(row[idx["Also known as"]]),
            "address": clean(row[idx["Address"]]),
            "postcode": clean(row[idx["Postcode"]]),
            "type": service_types[0] if service_types else "Hospital",
            "service_types": service_types,
            "inspection_date": clean(row[idx["Date of latest check"]]),
            "operator": clean(row[idx["Provider name"]]),
            "borough": borough,
            "location_url": clean(row[idx["Location URL"]]),
            "cqc_location_id": clean(row[idx["CQC Location ID (for office use only)"]]),
            "cqc_provider_id": clean(row[idx["CQC Provider ID (for office use only)"]]),
        })
    return hospitals


def extract_rating(page_html):
    soup = BeautifulSoup(page_html, "html.parser")
    rating_node = soup.select_one(".overall-rating__value--value")
    if rating_node:
        rating = rating_node.get_text(" ", strip=True)
        if rating in {"Insufficient evidence to rate", "Not rated"}:
            return "Not rated"
        return rating
    meta = soup.find(string=re.compile(r"\b(Outstanding|Good|Requires improvement|Inadequate|Not rated)\b", re.I))
    if meta:
        match = re.search(r"(Outstanding|Good|Requires improvement|Inadequate|Not rated)", meta, re.I)
        if match:
            return match.group(1)
    return "Not rated"


def fetch_ratings(hospitals):
    cache = load_rating_cache()
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    dirty = False
    for hospital in hospitals:
        location_id = hospital["cqc_location_id"]
        location_url = hospital["location_url"]
        if not location_id or not location_url:
            hospital["cqc_rating"] = "Not rated"
            continue
        cached = cache.get(location_id)
        if cached:
            hospital["cqc_rating"] = cached["cqc_rating"]
            continue
        response = session.get(location_url, timeout=60)
        response.raise_for_status()
        rating = extract_rating(response.text)
        hospital["cqc_rating"] = rating
        cache[location_id] = {"cqc_rating": rating}
        dirty = True
        time.sleep(0.12)
    if dirty:
        save_rating_cache(cache)


def geocode_postcodes(hospitals):
    unique = []
    seen = set()
    for hospital in hospitals:
        postcode = hospital["postcode"]
        if postcode and postcode not in seen:
            seen.add(postcode)
            unique.append(postcode)

    coords = {}
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    for start in range(0, len(unique), 100):
        batch = unique[start:start + 100]
        response = session.post(POSTCODE_BATCH_URL, json={"postcodes": batch}, timeout=60)
        response.raise_for_status()
        payload = response.json()
        for item in payload.get("result", []):
            query = item.get("query")
            result = item.get("result") or {}
            lon = result.get("longitude")
            lat = result.get("latitude")
            if query and lon is not None and lat is not None:
                coords[query] = [lon, lat]
        time.sleep(0.08)
    return coords


def make_features(hospitals, coords):
    features = []
    for hospital in hospitals:
        coord = coords.get(hospital["postcode"])
        if not coord:
            continue
        rating = hospital.get("cqc_rating") or "Not rated"
        if rating not in RATING_ORDER:
            rating = "Not rated"
        features.append({
            "type": "Feature",
            "properties": {
                "hospital_name": hospital["hospital_name"],
                "site_code": hospital["cqc_location_id"],
                "provider_id": hospital["cqc_provider_id"],
                "type": hospital["type"],
                "operator": hospital["operator"],
                "cqc_rating": rating,
                "rating_sort": RATING_ORDER.get(rating, 6),
                "inspection_date": hospital["inspection_date"],
                "borough": hospital["borough"],
                "postcode": hospital["postcode"],
                "location_url": hospital["location_url"],
            },
            "geometry": {"type": "Point", "coordinates": coord},
        })
    return features


def main():
    hospitals = load_hospital_rows()
    fetch_ratings(hospitals)
    coords = geocode_postcodes(hospitals)
    features = make_features(hospitals, coords)
    output = {"type": "FeatureCollection", "name": "london_hospitals", "features": features}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, separators=(",", ":")))
    print(f"Wrote {len(features)} hospitals to {OUT}")


if __name__ == "__main__":
    main()
