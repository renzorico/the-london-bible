#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
GEOJSON_PATH = ROOT / "london_msoa_density.geojson"
WORKBOOK_2011_2022 = Path("/tmp/sapemsoaquinaryage20112022.xlsx")
WORKBOOK_2022_2024 = Path("/tmp/sapemsoaquinaryage20222024.xlsx")


def load_year_populations(path: Path, years: list[int], valid_codes: set[str]) -> dict[int, dict[str, int]]:
    series: dict[int, dict[str, int]] = {}
    for year in years:
        sheet = f"Mid-{year} MSOA 2021"
        frame = pd.read_excel(path, sheet_name=sheet, header=3, usecols=["MSOA 2021 Code", "Total"])
        frame = frame.rename(columns={"MSOA 2021 Code": "code", "Total": "population"})
        frame["code"] = frame["code"].astype(str).str.strip()
        frame["population"] = pd.to_numeric(frame["population"], errors="coerce")
        subset = frame[frame["code"].isin(valid_codes)].copy()
        found_codes = set(subset["code"])
        missing = sorted(valid_codes - found_codes)
        if missing:
            raise RuntimeError(f"Year {year} is missing {len(missing)} London MSOA codes; sample: {missing[:10]}")
        series[year] = {code: int(population) for code, population in zip(subset["code"], subset["population"])}
    return series


def main() -> None:
    data = json.loads(GEOJSON_PATH.read_text())
    features = data["features"]
    codes = {feature["properties"]["msoa_code"] for feature in features}

    yearly_population = load_year_populations(WORKBOOK_2011_2022, list(range(2011, 2023)), codes)
    yearly_population.update(load_year_populations(WORKBOOK_2022_2024, [2022, 2023, 2024], codes))

    for feature in features:
        props = feature["properties"]
        code = props["msoa_code"]
        area = float(props["area_km2"])
        for year in sorted(yearly_population):
            population = yearly_population[year][code]
            props[f"population_{year}"] = population
            props[f"density_{year}"] = population / area

    GEOJSON_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print(f"Updated {GEOJSON_PATH.name} with years {sorted(yearly_population)} for {len(features)} MSOAs")


if __name__ == "__main__":
    main()
