#!/usr/bin/env python3
import csv
import json
from pathlib import Path

from pyproj import Transformer


ROOT = Path(__file__).resolve().parent
TMP = Path("/tmp")
OUT = ROOT / "data" / "london_schools_ofsted.geojson"

GIAS_PATH = TMP / "edubasealldata.csv"
OFSTED_PATH = TMP / "ofsted_latest_schools.csv"

LONDON_BOROUGHS = {
    "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley", "Camden",
    "City of London", "Croydon", "Ealing", "Enfield", "Greenwich", "Hackney",
    "Hammersmith and Fulham", "Haringey", "Harrow", "Havering", "Hillingdon",
    "Hounslow", "Islington", "Kensington and Chelsea", "Kingston upon Thames",
    "Lambeth", "Lewisham", "Merton", "Newham", "Redbridge",
    "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets",
    "Waltham Forest", "Wandsworth", "Westminster",
}

MAINSTREAM_TYPES = {
    "Community school",
    "Academy converter",
    "Voluntary aided school",
    "Academy sponsor led",
    "Free schools",
    "Foundation school",
    "Voluntary controlled school",
    "City technology college",
}

MAINSTREAM_PHASES = {"Primary", "Secondary", "All-through"}

RATING_MAP = {
    "1": "Outstanding",
    "2": "Good",
    "3": "Requires improvement",
    "4": "Inadequate",
}

TRANSFORMER = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)


def clean(value):
    value = (value or "").strip()
    return None if not value or value == "NULL" else value


def grade_from_ofsted(row):
    direct = clean(row.get("Latest OEIF overall effectiveness"))
    if direct in RATING_MAP:
        return RATING_MAP[direct], "graded"

    ungraded = clean(row.get("Ungraded inspection overall outcome"))
    if ungraded in {
        "School remains Outstanding",
        "School remains Outstanding (Concerns) - S5 Next",
    }:
        return "Outstanding", "ungraded"
    if ungraded in {
        "School remains Good",
        "School remains Good (Improving) - S5 Next",
        "School remains Good (Concerns) - S5 Next",
    }:
        return "Good", "ungraded"
    return "Ungraded", "ungraded"


def rating_sort_value(label):
    return {
        "Outstanding": 1,
        "Good": 2,
        "Requires improvement": 3,
        "Inadequate": 4,
        "Ungraded": 5,
    }.get(label, 6)


def inspection_date_for(row):
    direct = clean(row.get("Inspection start date of latest OEIF graded inspection"))
    if direct:
        return direct
    return clean(row.get("Date of latest ungraded inspection")) or clean(row.get("Inspection start date"))


def rating_detail_for(row):
    direct = clean(row.get("Latest OEIF overall effectiveness"))
    if direct in RATING_MAP:
        return "Latest OEIF graded inspection"
    return clean(row.get("Ungraded inspection overall outcome")) or "Latest inspection not currently graded"


def load_ofsted():
    by_urn = {}
    with OFSTED_PATH.open("r", encoding="latin1", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urn = clean(row.get("URN"))
            if not urn or clean(row.get("Region")) != "London":
                continue
            by_urn[urn] = row
    return by_urn


def load_gias(ofsted_rows):
    features = []
    with GIAS_PATH.open("r", encoding="latin1", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if clean(row.get("EstablishmentStatus (name)")) != "Open":
                continue
            borough = clean(row.get("DistrictAdministrative (name)"))
            if borough not in LONDON_BOROUGHS:
                continue
            school_type = clean(row.get("TypeOfEstablishment (name)"))
            if school_type not in MAINSTREAM_TYPES:
                continue
            phase = clean(row.get("PhaseOfEducation (name)"))
            if phase not in MAINSTREAM_PHASES:
                continue
            urn = clean(row.get("URN"))
            if not urn:
                continue
            ofsted = ofsted_rows.get(urn)
            if not ofsted:
                continue
            easting = clean(row.get("Easting"))
            northing = clean(row.get("Northing"))
            if not easting or not northing:
                continue
            lon, lat = TRANSFORMER.transform(float(easting), float(northing))
            rating, rating_basis = grade_from_ofsted(ofsted)
            features.append({
                "type": "Feature",
                "properties": {
                    "school_name": clean(row.get("EstablishmentName")) or clean(ofsted.get("School name")) or "School",
                    "urn": urn,
                    "phase": phase,
                    "type": school_type,
                    "ofsted_rating": rating,
                    "rating_basis": rating_basis,
                    "rating_sort": rating_sort_value(rating),
                    "inspection_date": inspection_date_for(ofsted),
                    "inspection_detail": rating_detail_for(ofsted),
                    "borough": borough,
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            })
    return features


def main():
    ofsted_rows = load_ofsted()
    features = load_gias(ofsted_rows)
    output = {"type": "FeatureCollection", "name": "london_schools_ofsted", "features": features}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, separators=(",", ":")))
    print(f"Wrote {len(features)} schools to {OUT}")


if __name__ == "__main__":
    main()
