#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
GEOJSON_PATH = ROOT / "london_msoa_density.geojson"
WORKBOOK_2011_2022 = Path("/tmp/sapemsoaquinaryage20112022.xlsx")
WORKBOOK_2022_2024 = Path("/tmp/sapemsoaquinaryage20222024.xlsx")


def load_year_population_and_sex(path: Path, years: list[int], valid_codes: set[str]) -> dict[int, dict[str, dict[str, float]]]:
    series: dict[int, dict[str, dict[str, float]]] = {}
    for year in years:
        sheet = f"Mid-{year} MSOA 2021"
        frame = pd.read_excel(path, sheet_name=sheet, header=3)
        frame = frame.rename(columns={"MSOA 2021 Code": "code", "Total": "population"})
        frame["code"] = frame["code"].astype(str).str.strip()
        frame["population"] = pd.to_numeric(frame["population"], errors="coerce")
        male_columns = [column for column in frame.columns if str(column).startswith("M")]
        female_columns = [column for column in frame.columns if str(column).startswith("F")]
        frame[male_columns] = frame[male_columns].apply(pd.to_numeric, errors="coerce")
        frame[female_columns] = frame[female_columns].apply(pd.to_numeric, errors="coerce")
        frame["male_total"] = frame[male_columns].sum(axis=1)
        frame["female_total"] = frame[female_columns].sum(axis=1)
        subset = frame[frame["code"].isin(valid_codes)].copy()
        found_codes = set(subset["code"])
        missing = sorted(valid_codes - found_codes)
        if missing:
            raise RuntimeError(f"Year {year} is missing {len(missing)} London MSOA codes; sample: {missing[:10]}")
        series[year] = {
            code: {
                "population": int(population),
                "male_total": float(male_total),
                "female_total": float(female_total),
            }
            for code, population, male_total, female_total in zip(
                subset["code"],
                subset["population"],
                subset["male_total"],
                subset["female_total"],
            )
        }
    return series


def main() -> None:
    data = json.loads(GEOJSON_PATH.read_text())
    features = data["features"]
    codes = {feature["properties"]["msoa_code"] for feature in features}

    yearly_population = load_year_population_and_sex(WORKBOOK_2011_2022, list(range(2011, 2023)), codes)
    yearly_population.update(load_year_population_and_sex(WORKBOOK_2022_2024, [2022, 2023, 2024], codes))

    for feature in features:
        props = feature["properties"]
        code = props["msoa_code"]
        area = float(props["area_km2"])
        for year in sorted(yearly_population):
            entry = yearly_population[year][code]
            population = entry["population"]
            male_share = entry["male_total"] / population * 100 if population else None
            female_share = entry["female_total"] / population * 100 if population else None
            props[f"population_{year}"] = population
            props[f"density_{year}"] = population / area
            props[f"male_share_pct_{year}"] = male_share
            props[f"female_share_pct_{year}"] = female_share
            props[f"gender_balance_pp_{year}"] = male_share - 50 if male_share is not None else None

    GEOJSON_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print(f"Updated {GEOJSON_PATH.name} with years {sorted(yearly_population)} for {len(features)} MSOAs")


if __name__ == "__main__":
    main()
