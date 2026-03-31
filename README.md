# London Population Density Map

Self-contained London population density map inspired by the Rome population map project. The pipeline downloads Kontur population hexes for Great Britain, London boundary data, and Thames geometry, then produces GeoJSON layers consumed by a single-file Leaflet/D3 web app.

## Project Files

```text
map-maker/
├── fetch_london_data.py
├── requirements.txt
├── london-pop-map.html
├── london_spike_map.html
├── README.md
├── london_hexes.geojson
├── london_boroughs.geojson
├── london_wards.geojson
└── london_thames.geojson
```

## Quick Start

```bash
python3 -m pip install -r requirements.txt
python3 fetch_london_data.py
python3 -m http.server 8080
```

Open `http://localhost:8080/london-pop-map.html`.

## App Features

- Ward-level choropleth of population density
- Kontur hex spike view using CSS-transformed 3D bars
- Borough-level aggregation with borough labels
- Thames overlay in every mode
- Hover tooltip with population, area and density
- Dark base map using CartoDB Dark Matter tiles

## Data Sources

- Kontur Population, Great Britain H3 / hex population dataset:
  `https://data.kontur.io/`
  Licence: CC BY 4.0
- Kontur public S3 download path used by the script:
  `https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/`
- London statistical GIS boundaries:
  `https://data.london.gov.uk/dataset/statistical-gis-boundary-files-london`
  Licence: Open Government Licence v3.0
- Thames fallback geometry layer:
  `https://gis2.london.gov.uk/server/rest/services/apps/webmap_context_layer/MapServer/1/query?where=1%3D1&outFields=*&f=geojson`
  Licence: Open Government Licence v3.0
- OpenStreetMap / Overpass API for Thames fetch primary attempt:
  `https://overpass-api.de/`
  Licence: ODbL
- CartoDB Dark Matter tiles:
  `https://carto.com/basemaps`

## Notes

- `fetch_london_data.py` first attempts the Thames fetch through Overpass and falls back to the GLA Thames layer if Overpass times out.
- The generated London totals from the current pipeline are approximately 9.32 million people across 2,546 clipped Kontur hexes.
- The HTML app loads GeoJSON files with `fetch()`, so opening the file directly from disk will not work in most browsers.

## Screenshot

Screenshot placeholder: add a browser capture of `london-pop-map.html` here.
