#!/usr/bin/env python3
import json
import sys
from pathlib import Path


CLASS_MAP = {
    "Cycle Superhighways": ("major", 3),
    "Cycleways": ("primary", 2),
    "Quietways": ("connector", 1),
}


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: prepare_london_cycle_network.py <input_json> <output_geojson>", file=sys.stderr)
        return 1

    source_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with source_path.open() as f:
        raw = json.load(f)

    features = raw.get("features", [])
    cleaned = []
    for feature in features:
        props = feature.get("properties") or {}
        geom = feature.get("geometry") or {}
        if geom.get("type") != "MultiLineString" or not geom.get("coordinates"):
            continue

        programme = props.get("Programme")
        route_class, class_rank = CLASS_MAP.get(programme, ("primary", 2))
        label = (props.get("Label") or "").strip()
        route_name = (props.get("Route_Name") or label or programme or "Cycle route").strip()

        cleaned.append({
            "type": "Feature",
            "properties": {
                "route_name": route_name,
                "route_label": label or route_name,
                "programme": programme,
                "route_class": route_class,
                "class_rank": class_rank,
                "length_m": round(float(props.get("Shape_Leng") or 0), 1),
            },
            "geometry": geom,
        })

    output = {
        "type": "FeatureCollection",
        "name": "london_cycle_network",
        "features": cleaned,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(output, f, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
