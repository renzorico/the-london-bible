# The London Bible

The London Bible is a self-contained London atlas: a static web app that layers borough and MSOA density, Tube lines, bikes, POIs, schools, hospitals, and other civic overlays into a single editorial map experience.

Repo:
- `renzorico/the-london-bible`

Public URL:
- `https://renzorico.github.io/the-london-bible/`

## Project Structure

```text
the-london-bible/
├── index.html
├── london-pop-map.html
├── london_spike_map.html
├── data/
│   ├── london_cycle_network.geojson
│   ├── london_hospitals.geojson
│   ├── london_pois.geojson
│   └── london_schools_ofsted.geojson
├── fetch_london_data.py
├── prepare_london_cycle_network.py
├── prepare_london_hospitals.py
├── prepare_london_pois.py
├── prepare_london_schools_ofsted.py
├── update_msoa_density_years.py
└── README.md
```

## Run Locally

```bash
python3 -m pip install -r requirements.txt
python3 -m http.server 8080
```

Open:
- `http://localhost:8080/`

Notes:
- The app now publishes from `index.html`.
- The HTML app loads GeoJSON and JSON data with `fetch()`, so opening the file directly from disk will not work in most browsers.

## GitHub Pages Deployment

Use GitHub Pages from the repository settings:

1. Open `renzorico/the-london-bible` on GitHub.
2. Go to `Settings` -> `Pages`.
3. Under `Build and deployment`, choose:
   - `Source`: `Deploy from a branch`
   - `Branch`: your publishing branch, usually `main`
   - `Folder`: `/ (root)`
4. Save and wait for Pages to publish.

Expected public URL:
- `https://renzorico.github.io/the-london-bible/`

## Data Notes

The atlas is static-hosted and fetches local files from the repo, including:
- London borough / ward / Thames / Tube geometry
- MSOA density and pubs data
- preprocessed bike network, POIs, schools, and hospitals overlays

Several refresh scripts are included for rebuilding those datasets locally when needed.
