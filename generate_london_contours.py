#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_PATH = DATA_DIR / "london_contours.geojson"
TILE_CACHE_DIR = DATA_DIR / "terrain_tiles"
MPL_CACHE_DIR = DATA_DIR / ".matplotlib"
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import geopandas as gpd
import matplotlib
import numpy as np
from PIL import Image
from shapely.geometry import LineString, MultiLineString, box, mapping
from shapely.ops import unary_union

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ZOOM = 11
TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
CONTOUR_INTERVAL_M = 10
MAJOR_CONTOUR_INTERVAL_M = 50
BOUNDARY_BUFFER_DEGREES = 0.045
SIMPLIFY_TOLERANCE_DEGREES = 0.00011
MIN_SEGMENT_POINTS = 8


def tile_x_from_lon(lon: float, zoom: int) -> float:
    return (lon + 180.0) / 360.0 * (2**zoom)


def tile_y_from_lat(lat: float, zoom: int) -> float:
    lat_rad = math.radians(lat)
    return (
        (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)
        / 2.0
        * (2**zoom)
    )


def lon_from_px(px: np.ndarray, zoom: int) -> np.ndarray:
    return (px / (256.0 * (2**zoom))) * 360.0 - 180.0


def lat_from_py(py: np.ndarray, zoom: int) -> np.ndarray:
    n = math.pi - (2.0 * math.pi * py) / (256.0 * (2**zoom))
    return np.degrees(np.arctan(np.sinh(n)))


def fetch_tile(z: int, x: int, y: int) -> Image.Image:
    TILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = TILE_CACHE_DIR / f"{z}_{x}_{y}.png"
    if not path.exists():
        url = TILE_URL.format(z=z, x=x, y=y)
        subprocess.run(["curl", "-L", "-sS", url, "-o", str(path)], check=True)
    return Image.open(path).convert("RGB")


def decode_terrarium(image: Image.Image) -> np.ndarray:
    rgb = np.asarray(image).astype(np.float32)
    return (rgb[..., 0] * 256.0 + rgb[..., 1] + rgb[..., 2] / 256.0) - 32768.0


def contour_levels(elevation: np.ndarray) -> np.ndarray:
    low = math.floor(np.nanmin(elevation) / CONTOUR_INTERVAL_M) * CONTOUR_INTERVAL_M
    high = math.ceil(np.nanmax(elevation) / CONTOUR_INTERVAL_M) * CONTOUR_INTERVAL_M
    return np.arange(low, high + CONTOUR_INTERVAL_M, CONTOUR_INTERVAL_M)


def build_mosaic(bounds: tuple[float, float, float, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    min_lon, min_lat, max_lon, max_lat = bounds
    x0 = int(math.floor(tile_x_from_lon(min_lon, ZOOM)))
    x1 = int(math.ceil(tile_x_from_lon(max_lon, ZOOM))) - 1
    y0 = int(math.floor(tile_y_from_lat(max_lat, ZOOM)))
    y1 = int(math.ceil(tile_y_from_lat(min_lat, ZOOM))) - 1

    tile_rows = []
    for ty in range(y0, y1 + 1):
        row = []
        for tx in range(x0, x1 + 1):
            row.append(decode_terrarium(fetch_tile(ZOOM, tx, ty)))
        tile_rows.append(np.concatenate(row, axis=1))
    mosaic = np.concatenate(tile_rows, axis=0)

    width = mosaic.shape[1]
    height = mosaic.shape[0]
    px = np.arange(x0 * 256, x0 * 256 + width, dtype=np.float64)
    py = np.arange(y0 * 256, y0 * 256 + height, dtype=np.float64)
    lons = lon_from_px(px, ZOOM)
    lats = lat_from_py(py, ZOOM)
    return mosaic, lons, lats


def london_clip_polygon() -> tuple[box, object]:
    boroughs = gpd.read_file(ROOT / "london_boroughs.geojson").to_crs("EPSG:4326")
    union = unary_union(boroughs.geometry.values)
    minx, miny, maxx, maxy = union.bounds
    clip_bbox = box(
        minx - BOUNDARY_BUFFER_DEGREES,
        miny - BOUNDARY_BUFFER_DEGREES,
        maxx + BOUNDARY_BUFFER_DEGREES,
        maxy + BOUNDARY_BUFFER_DEGREES,
    )
    return clip_bbox, union


def contour_to_features(elevation: np.ndarray, lons: np.ndarray, lats: np.ndarray, clip_geom) -> list[dict]:
    levels = contour_levels(elevation)
    fig, ax = plt.subplots(figsize=(12, 12), dpi=96)
    cs = ax.contour(lons, lats[::-1], elevation[::-1, :], levels=levels)
    plt.close(fig)

    features: list[dict] = []
    for level, segments in zip(cs.levels, cs.allsegs):
        major = int(level) % MAJOR_CONTOUR_INTERVAL_M == 0
        for segment in segments:
            if len(segment) < MIN_SEGMENT_POINTS:
                continue
            geom = LineString(segment)
            if geom.length == 0:
                continue
            clipped = geom.intersection(clip_geom)
            if clipped.is_empty:
                continue

            parts = list(clipped.geoms) if isinstance(clipped, MultiLineString) else [clipped]
            for part in parts:
                simplified = part.simplify(SIMPLIFY_TOLERANCE_DEGREES, preserve_topology=False)
                if simplified.is_empty or simplified.length == 0:
                    continue
                if isinstance(simplified, MultiLineString):
                    split_parts = simplified.geoms
                else:
                    split_parts = [simplified]
                for split_part in split_parts:
                    if len(split_part.coords) < 2:
                        continue
                    features.append(
                        {
                            "type": "Feature",
                            "properties": {
                                "elev": int(level),
                                "major": major,
                            },
                            "geometry": mapping(split_part),
                        }
                    )
    return features


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
    clip_bbox, _ = london_clip_polygon()
    bounds = clip_bbox.bounds
    elevation, lons, lats = build_mosaic(bounds)
    features = contour_to_features(elevation, lons, lats, clip_bbox)
    fc = {"type": "FeatureCollection", "features": features}
    OUTPUT_PATH.write_text(json.dumps(fc, separators=(",", ":")))
    print(f"Wrote {len(features)} contours to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
