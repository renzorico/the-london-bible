#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

import geopandas as gpd
import requests
from pyogrio import list_layers
from shapely.geometry import LineString
from tqdm import tqdm


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "_data_cache"
OUTPUT_CRS = "EPSG:27700"
WGS84 = "EPSG:4326"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "map-maker-london-pop/1.0"})

KONTUR_URLS = [
    "https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/kontur_population_GB_20231101.gpkg.gz",
    "https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/kontur_population_GB_latest.gpkg.gz",
    "https://data.kontur.io/kontur_population_gb_20231101.gpkg.gz",
    "https://data.kontur.io/kontur_population_gb_latest.gpkg.gz",
]

LONDON_BOUNDARY_URLS = [
    "https://data.london.gov.uk/download/statistical-gis-boundary-files-london/9ba8c833-6370-4b11-abdc-314aa020d5e0/statistical-gis-boundaries-london.zip",
]

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

THAMES_FALLBACK_GEOJSON = (
    "https://gis2.london.gov.uk/server/rest/services/apps/webmap_context_layer/MapServer/1/"
    "query?where=1%3D1&outFields=*&f=geojson"
)


def download_file(url: str, dest: Path) -> Path:
    if dest.exists():
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    with SESSION.get(url, stream=True, timeout=180) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        with dest.open("wb") as handle, tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            desc=f"Downloading {dest.name}",
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                handle.write(chunk)
                bar.update(len(chunk))
    return dest


def first_successful_download(urls: list[str], dest_name: str) -> Path:
    errors: list[str] = []
    for url in urls:
        try:
            return download_file(url, DATA_DIR / dest_name)
        except Exception as exc:  # pragma: no cover - network behavior
            errors.append(f"{url}: {exc}")
    raise RuntimeError("All downloads failed:\n" + "\n".join(errors))


def gunzip_file(src: Path, dest: Path) -> Path:
    if dest.exists():
        return dest
    with gzip.open(src, "rb") as in_file, dest.open("wb") as out_file:
        shutil.copyfileobj(in_file, out_file)
    return dest


def unzip_file(src: Path, dest_dir: Path) -> Path:
    marker = dest_dir / ".unzipped"
    if marker.exists():
        return dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zf:
        zf.extractall(dest_dir)
    marker.write_text("ok\n")
    return dest_dir


def detect_population_column(frame: gpd.GeoDataFrame) -> str:
    preferred = [
        "population",
        "population_sum",
        "pop",
        "population_cnt",
        "population_count",
    ]
    lowered = {column.lower(): column for column in frame.columns}
    for name in preferred:
        if name in lowered:
            return lowered[name]

    candidates = [
        column
        for column in frame.columns
        if "pop" in column.lower() and column != frame.geometry.name
    ]
    if candidates:
        return candidates[0]
    raise RuntimeError(f"Could not detect population column in {list(frame.columns)}")


def read_first_layer(path: Path) -> gpd.GeoDataFrame:
    layers = list_layers(path)
    if len(layers) == 0:
        raise RuntimeError(f"No layers found in {path}")
    return gpd.read_file(path, layer=layers[0][0])


def choose_boundary_file(extract_dir: Path, kind: str) -> Path:
    patterns = {
        "boroughs": ["borough", "bor", "london_borough"],
        "wards": ["ward"],
    }
    suffixes = {".geojson", ".json", ".gpkg", ".shp"}
    candidates: list[tuple[int, Path]] = []
    for path in extract_dir.rglob("*"):
        if path.suffix.lower() not in suffixes:
            continue
        name = path.name.lower()
        if "label" in name or "point" in name:
            continue
        score = sum(token in name for token in patterns[kind])
        if score == 0:
            continue
        if kind == "boroughs" and "ward" in name:
            continue
        if kind == "wards" and "borough" in name:
            continue
        score += int("geojson" in name) + int("pol" in name) + int("bound" in name)
        candidates.append((score, path))
    if not candidates:
        raise RuntimeError(f"Unable to find {kind} file in {extract_dir}")
    candidates.sort(key=lambda item: (-item[0], len(item[1].name)))
    return candidates[0][1]


def normalize_name_columns(frame: gpd.GeoDataFrame, fallback_prefix: str) -> gpd.GeoDataFrame:
    name_columns = [
        column
        for column in frame.columns
        if column != frame.geometry.name and "name" in column.lower()
    ]
    if not name_columns:
        code_columns = [
            column
            for column in frame.columns
            if column != frame.geometry.name and column.lower().endswith(("cd", "code"))
        ]
        if code_columns:
            frame["name"] = frame[code_columns[0]].astype(str)
        else:
            frame["name"] = [f"{fallback_prefix} {i + 1}" for i in range(len(frame))]
    else:
        frame["name"] = frame[name_columns[0]].astype(str)
    return frame


def load_boroughs(boundary_dir: Path) -> gpd.GeoDataFrame:
    path = choose_boundary_file(boundary_dir, "boroughs")
    if path.suffix.lower() == ".gpkg":
        frame = read_first_layer(path)
    else:
        frame = gpd.read_file(path)
    frame = frame.to_crs(OUTPUT_CRS)
    frame = normalize_name_columns(frame, "Borough")
    frame = frame[~frame.geometry.is_empty & frame.geometry.notna()].copy()
    frame["name"] = frame["name"].str.replace(r"\s+", " ", regex=True).str.strip()
    frame = frame[["name", "geometry"]].dissolve(by="name").reset_index()
    return frame


def load_wards(boundary_dir: Path, london_outline: gpd.GeoDataFrame) -> gpd.GeoDataFrame | None:
    try:
        path = choose_boundary_file(boundary_dir, "wards")
    except RuntimeError:
        return None

    if path.suffix.lower() == ".gpkg":
        frame = read_first_layer(path)
    else:
        frame = gpd.read_file(path)
    frame = frame.to_crs(OUTPUT_CRS)
    frame = normalize_name_columns(frame, "Ward")
    frame = frame[~frame.geometry.is_empty & frame.geometry.notna()].copy()
    clip_mask = london_outline[["geometry"]].copy()
    clipped = gpd.overlay(frame[["name", "geometry"]], clip_mask, how="intersection")
    if clipped.empty:
        return None
    return clipped[["name", "geometry"]]


def load_kontur_hexes(gpkg_path: Path) -> gpd.GeoDataFrame:
    hexes = read_first_layer(gpkg_path)
    population_column = detect_population_column(hexes)
    if hexes.crs is None:
        hexes = hexes.set_crs(WGS84)
    hexes = hexes.to_crs(OUTPUT_CRS)
    hexes = hexes.rename(columns={population_column: "population"})
    keep_columns = ["population", hexes.geometry.name]
    hexes = hexes[keep_columns].copy()
    hexes["population"] = hexes["population"].fillna(0).astype(float)
    return hexes


def spatially_assign_population(
    source_hexes: gpd.GeoDataFrame,
    target_areas: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    centroids = source_hexes.copy()
    centroids["geometry"] = centroids.geometry.centroid
    joined = gpd.sjoin(
        centroids[["population", "geometry"]],
        target_areas.reset_index(drop=True),
        how="inner",
        predicate="within",
    )
    population = joined.groupby("index_right")["population"].sum()
    result = target_areas.copy()
    result["population"] = population.reindex(result.index, fill_value=0).astype(float)
    result["area_km2"] = result.geometry.area / 1_000_000
    result["density"] = result["population"] / result["area_km2"]
    return result


def prepare_hex_outputs(hexes: gpd.GeoDataFrame, london_outline: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    clipped = gpd.overlay(hexes, london_outline, how="intersection")
    if clipped.empty:
        raise RuntimeError("No Kontur hexes intersected the London boundary")
    clipped["area_km2"] = clipped.geometry.area / 1_000_000
    clipped["density"] = clipped["population"] / clipped["area_km2"]
    centroids = gpd.GeoSeries(clipped.geometry.centroid, crs=OUTPUT_CRS).to_crs(WGS84)
    clipped["centroid_lon"] = centroids.x
    clipped["centroid_lat"] = centroids.y
    clipped["hex_id"] = [f"hex_{index}" for index in range(len(clipped))]
    return clipped


def fetch_thames(london_outline_wgs84: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    minx, miny, maxx, maxy = london_outline_wgs84.total_bounds
    query = f"""
    [out:json][timeout:25];
    (
      way["waterway"="river"]["name"~"Thames|River Thames", i]({miny},{minx},{maxy},{maxx});
    );
    out geom;
    """
    errors: list[str] = []
    data = None
    for url in OVERPASS_URLS:
        try:
            response = SESSION.post(
                url,
                data={"data": query},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            break
        except Exception as exc:  # pragma: no cover - network behavior
            errors.append(f"{url}: {exc}")
    if data is None:
        temp_geojson = DATA_DIR / "london_thames_fallback.geojson"
        if not temp_geojson.exists():
            response = SESSION.get(THAMES_FALLBACK_GEOJSON, timeout=120)
            response.raise_for_status()
            temp_geojson.write_text(response.text)
        fallback = gpd.read_file(temp_geojson).to_crs(WGS84)
        fallback["name"] = "River Thames"
        fallback["geometry"] = fallback.geometry.boundary
        clip_mask = london_outline_wgs84[["geometry"]].copy()
        clipped = gpd.overlay(fallback[["name", "geometry"]], clip_mask, how="intersection")
        if clipped.empty:
            clipped = fallback[["name", "geometry"]]
        return clipped.dissolve(by="name").reset_index()

    lines = []
    for element in data.get("elements", []):
        geometry = element.get("geometry")
        if element.get("type") == "way" and geometry and len(geometry) >= 2:
            coords = [(point["lon"], point["lat"]) for point in geometry]
            lines.append(LineString(coords))

    if not lines:
        raise RuntimeError("No Thames geometry returned from Overpass")

    thames = gpd.GeoDataFrame({"name": ["River Thames"] * len(lines)}, geometry=lines, crs=WGS84)
    clip_mask = london_outline_wgs84[["geometry"]].copy()
    clipped = gpd.overlay(thames, clip_mask, how="intersection")
    if clipped.empty:
        clipped = thames
    return clipped.dissolve(by="name").reset_index()


def write_geojson(frame: gpd.GeoDataFrame, filename: str) -> None:
    output = ROOT / filename
    frame.to_crs(WGS84).to_file(output, driver="GeoJSON")
    print(f"Wrote {output.name}")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    kontur_archive = first_successful_download(KONTUR_URLS, "kontur_population_gb.gpkg.gz")
    kontur_gpkg = gunzip_file(kontur_archive, DATA_DIR / "kontur_population_gb.gpkg")

    london_zip = first_successful_download(LONDON_BOUNDARY_URLS, "statistical-gis-boundaries-london.zip")
    boundary_dir = unzip_file(london_zip, DATA_DIR / "london_boundaries")

    boroughs = load_boroughs(boundary_dir)
    london_outline = boroughs.dissolve().reset_index(drop=True)
    london_outline["name"] = "Greater London"

    hexes = load_kontur_hexes(kontur_gpkg)
    london_hexes = prepare_hex_outputs(hexes, london_outline)

    boroughs_with_population = spatially_assign_population(london_hexes, boroughs)

    wards = load_wards(boundary_dir, london_outline)
    wards_with_population = None
    if wards is not None and not wards.empty:
        wards_with_population = spatially_assign_population(london_hexes, wards)

    thames = fetch_thames(london_outline.to_crs(WGS84))

    write_geojson(london_hexes, "london_hexes.geojson")
    write_geojson(boroughs_with_population, "london_boroughs.geojson")
    if wards_with_population is not None:
        write_geojson(wards_with_population, "london_wards.geojson")
    write_geojson(thames, "london_thames.geojson")

    summary = {
        "hexes": int(len(london_hexes)),
        "boroughs": int(len(boroughs_with_population)),
        "wards": int(len(wards_with_population)) if wards_with_population is not None else 0,
        "population_total": float(london_hexes["population"].sum()),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
