#!/usr/bin/env python3
import json
from pathlib import Path


BBOX = (-0.51, 51.28, 0.33, 51.70)


POI_CONFIG = {
    "coffee": {"label": "Coffee", "min_zoom": 11.6, "priority": 1, "source_type": "OpenStreetMap"},
    "nightlife": {"label": "Nightlife", "min_zoom": 11.0, "priority": 2, "source_type": "London Datastore Cultural Infrastructure Map"},
    "culture": {"label": "Culture", "min_zoom": 10.15, "priority": 3, "source_type": "London Datastore Cultural Infrastructure Map"},
    "sport": {"label": "Urban sport", "min_zoom": 10.9, "priority": 2, "source_type": "London Datastore Cultural Infrastructure Map"},
    "landmarks": {"label": "Landmarks", "min_zoom": 9.85, "priority": 3, "source_type": "London Datastore Cultural Infrastructure Map"},
}


ROOT = Path(__file__).resolve().parent
TMP = Path("/tmp")


def in_bbox(lon: float, lat: float) -> bool:
    return BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]


def norm_name(value: str) -> str:
    return " ".join((value or "").split())


def add_feature(store, *, key, lon, lat, name, category, subcategory, source_type, min_zoom, priority):
    if not name or not in_bbox(lon, lat):
        return
    store[key] = {
        "type": "Feature",
        "properties": {
            "name": name,
            "category": category,
            "category_label": POI_CONFIG[category]["label"],
            "subcategory": subcategory,
            "source_type": source_type,
            "min_zoom": min_zoom,
            "priority": priority,
        },
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
    }


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def load_cafes(store):
    data = load_json(TMP / "pois_cafe.json")
    for element in data.get("elements", []):
        tags = element.get("tags") or {}
        name = norm_name(tags.get("name"))
        add_feature(
            store,
            key=f"osm-cafe-{element['id']}",
            lon=float(element["lon"]),
            lat=float(element["lat"]),
            name=name,
            category="coffee",
            subcategory="Cafe",
            source_type="OpenStreetMap amenity=cafe",
            min_zoom=POI_CONFIG["coffee"]["min_zoom"],
            priority=POI_CONFIG["coffee"]["priority"],
        )


def load_cim_layer(store, filename: str, category: str, subcategory: str, source_type: str):
    data = load_json(TMP / filename)
    for feature in data.get("features", []):
        geometry = feature.get("geometry") or {}
        if geometry.get("type") != "Point":
            continue
        props = feature.get("properties") or {}
        object_id = props.get("objectid") or props.get("OBJECTID") or props.get("uniqueid") or props.get("vid")
        lon, lat = geometry.get("coordinates", [None, None])
        if lon is None or lat is None:
            continue
        add_feature(
            store,
            key=f"cim-{subcategory.lower().replace(' ', '-')}-{object_id}",
            lon=float(lon),
            lat=float(lat),
            name=norm_name(props.get("name")),
            category=category,
            subcategory=subcategory,
            source_type=source_type,
            min_zoom=POI_CONFIG[category]["min_zoom"],
            priority=POI_CONFIG[category]["priority"],
        )


def main() -> int:
    features = {}

    load_cafes(features)

    load_cim_layer(features, "cim_pubs.geojson", "nightlife", "Pub", "Cultural Infrastructure Map · Pubs")
    load_cim_layer(features, "cim_pubs_2.geojson", "nightlife", "Pub", "Cultural Infrastructure Map · Pubs")
    load_cim_layer(features, "cim_pubs_3.geojson", "nightlife", "Pub", "Cultural Infrastructure Map · Pubs")
    load_cim_layer(features, "cim_nightclubs.geojson", "nightlife", "Nightclub", "Cultural Infrastructure Map · Nightclubs")

    load_cim_layer(features, "cim_theatres.geojson", "culture", "Theatre", "Cultural Infrastructure Map · Theatres")
    load_cim_layer(features, "cim_cinemas.geojson", "culture", "Cinema", "Cultural Infrastructure Map · Cinemas")
    load_cim_layer(features, "cim_museums.geojson", "culture", "Museum / gallery", "Cultural Infrastructure Map · Museums and public galleries")
    load_cim_layer(features, "cim_music_venues.geojson", "culture", "Music venue", "Cultural Infrastructure Map · Music venues")
    load_cim_layer(features, "cim_arts_centres.geojson", "culture", "Arts centre", "Cultural Infrastructure Map · Arts centres")

    load_cim_layer(features, "cim_skateparks.geojson", "sport", "Skate park", "Cultural Infrastructure Map · Skate parks")
    load_cim_layer(features, "cim_monuments.geojson", "landmarks", "Scheduled monument", "Cultural Infrastructure Map · Scheduled monuments")

    output = {
        "type": "FeatureCollection",
        "name": "london_pois",
        "features": list(features.values()),
    }

    output_path = ROOT / "data" / "london_pois.geojson"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(output, f, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
