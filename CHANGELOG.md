# Changelog

## 2026-04-01 — POI priority and bikes intensity

- Fixed POI interaction so hover and click now prefer places over borough or tube geometry in Boroughs and ONLY-TUBE view, and clicking a POI keeps the card POI-specific instead of falling through to the normal metric pin state.
- Increased the bike overlay’s visual intensity with brighter jade-to-mint linework, stronger halos, and heavier city-scale widths so the cycling network reads more clearly in both day and night themes.

## 2026-04-01 — POI interaction cleanup

- Fixed POI hover and click behavior so place names remain easy to inspect in Boroughs and ONLY-TUBE view, and clicking a POI now opens POI-specific info instead of the normal metric pin card.

## 2026-04-01 — Restored POI place-name hover

- Restored compact hover labels for POIs so place names remain discoverable while keeping the calmer POI-first background behavior and reduced borough hover noise.

## 2026-04-01 — POI overlay reliability and focus

- Fixed the POIs overlay so categories reliably reappear when toggled, prevented the filter UI from ending in an all-off empty state, and added clearer zoom feedback when smaller place categories are not yet visible.
- Refined the map into a POI-first hover mode by calming borough hover behavior while POIs are active, keeping the background readable and the points themselves visually dominant.

## 2026-04-01 — Curated POI overlay

- Added a new POIs overlay that reveals London through a curated set of city-life categories, combining an OSM cafe extract with London Datastore cultural infrastructure points for nightlife, culture, landmarks, and urban sport.
- Styled the layer as compact art-directed dots with category filters, zoom-based visibility, and lightweight hover/click cards so the city lights up without turning into directory clutter.

## 2026-04-01 — London bikes overlay

- Added a new Bikes overlay built from TfL’s published London cycle routes, preprocessed into a local GeoJSON with a clean major / primary / connector hierarchy and a dedicated toggle alongside Contours.
- Styled the cycle network as layered jade-to-mint linework with zoom-based halos and route weighting so London’s cycling structure reads clearly across borough, MSOA, and tube views without clashing with Tube lines or contours.

## 2026-04-01 — Wider homepage framing

- Zoomed the default homepage map view out to a noticeably wider London framing and updated the loading intro handoff so it still lands cleanly on the same final home camera.

## 2026-04-01 — Loading intro alignment refinement

- Tuned the logo spin-down to finish in the correct upright orientation and refined the intro map choreography so the logo more convincingly transforms into the homepage map view before settling into the default framing.

## 2026-04-01 — Loading intro motion pass

- Refined the loading screen proportions, shortened the intro to roughly three seconds, and added a decelerating logo-spin reveal that blends into the default London map view for a more cinematic first load.

## 2026-04-01 — Tube lines overlay restored

- Fixed a regression that hid Tube lines by restoring the full local Tube network source and keeping the line overlay path intact, so Tube lines and stations render together again without affecting the new contours layer.

## 2026-04-01 — Contours layer and MSOA gender rollback

- Reverted the experimental MSOA gender-balance path so gender balance is borough-only again, leaving MSOA density as the only annual small-area timeline and MSOA pubs density as a fixed-year snapshot.
- Added a new London contours overlay generated from open Terrarium elevation tiles, with a dedicated Contours toggle and day/night line styling that etches the city’s terrain onto borough, MSOA, and tube views without turning contours into a metric.

## 2026-04-01 — MSOA controls cleanup and metric audit

- Simplified the expanded MSOA density time control by labeling only milestone years plus the active year, and tightened transient hover cards so they stay compact instead of stretching across the map.
- Added defensible MSOA gender-balance support from the same ONS MSOA 2021 annual population-by-sex series used for density, while keeping unsupported metrics borough-only or fixed-year where no honest small-area dataset exists.

## 2026-04-01 — Expanded MSOA density timeline

- Expanded the MSOA population-density timeline to the full ONS-backed annual series currently available on MSOA 2021 geographies, using mid-2011 to mid-2022 data plus the revised mid-2022 to mid-2024 edition.
- Kept MSOA pubs density fixed-year, tightened the MSOA year control for the longer timeline, and only exposed annual switching for the density metric that actually has year-by-year support.

## 2026-04-01 — Branded loading screen

- Added a branded first-load overlay using the project `logo.png` asset, a restrained breathing animation, and a centered `THE LONDON BIBLE` lockup so the atlas opens with a calmer editorial entry state.
- Switched loader dismissal from a fixed timeout to app readiness, fading the overlay out smoothly once the map style and core UI have initialized, while respecting reduced-motion preferences.

## 2026-04-01 — View icon and flag refinement

- Replaced the Views text buttons with compact icon controls plus hover labels, swapped the pub metric icon for a clearer pint-glass mark, and tightened the Origin focus picker into one horizontal flag row.
- Replaced the Origin overview swatch with a UK flag treatment while keeping hover/focus labels and active-state clarity intact across the icon-based controls.

## 2026-04-01 — Compact metric icons and origin flags

- Shortened the METRICS panel by replacing the text metric buttons with a compact icon grid, keeping full metric names available through hover/focus labels and aria-labels while preserving the existing metric-switching behavior.
- Replaced the Origin country labels with compact flag buttons plus hover/focus labels, using lightweight CSS-rendered flag swatches instead of emoji so the picker stays cleaner and visually consistent.

## 2026-04-01 — Metrics rail repair and MSOA audit

- Repaired the METRICS panel with a cleaner single-column metric list, restored clearer nested metric controls, moved the pinned borough summary into a fixed top card so it no longer blocks the center of the map, and removed the redundant selected-year chip from the Density time control.
- Fixed Similar Areas so selecting a borough now rebuilds the map highlight layers immediately, keeping the three returned matches visibly highlighted on the map and in sync with the panel, and confirmed that current small-area support is limited to MSOA density and MSOA pub density with density years available only for 2021 and 2024.

## 2026-04-01 — Control rail cleanup and metric switching fix

- Reduced the visual weight of the Views and Metrics buttons to match the Analysis controls more closely, and reorganized those groups into cleaner two-column grids for a more ordered left rail.
- Fixed the intermittent Density switching issue by separating the metric button grid from the nested Density options surface in the stacking order, so the open scope panel no longer blocks clicks on other metric buttons.

## 2026-04-01 — Hexes and spikes refinement

- Restored HEXES spikes to proper extruded hex geometry, improved the density palette toward a cleaner stone-to-plum range, and tightened the HEXES style controls so Flat map, Spikes, and Reset distribute evenly.
- Refined the Residents per km² legend with calmer typography, better alignment and width, capitalized Sparse / Dense labels, and corrected spike rendering by excluding clipped edge cells below `0.18 km²` from spike extrusion while switching to a quantile-anchored piecewise height scale with a q99.7 render cap so mid- and high-density variation reads more clearly again.

## 2026-04-01 — Tube interaction and branding polish

- Fixed the actual only-tube interaction path so station hover restores station names, line selection from the legend or the map visibly updates rendered Tube lines, and empty-space click clears tube selection cleanly without falling back to borough metrics.
- Tightened the title/subtitle lockup, softened the footer credit styling, and nudged Tube label spacing closer to their lines without changing the wider atlas structure.

## 2026-04-01 — Atlas UI refinement pass

- Refined the atlas typography with a sharper one-line `THE LONDON BIBLE` wordmark, the subtitle `One city, every layer`, a stronger footer credit, and more readable analysis-panel text.
- Fixed only-tube hover to stay station-specific, enlarged and linked the Tube legend to line selection, cleaned up spikes rendering and outlier handling, improved compare / story / similarity / correlation readability, and aligned legend gradients more closely with the visible map palette.

## 2026-04-01 — Atlas UI cleanup & control rail redesign

- Rebuilt the atlas controls into a single left-hand rail with clearer brand, views, metrics, analysis, and nested-option hierarchy so the interface feels calmer and more editorial.
- Renamed key metric families to Pubs density, Buildings density, Greenspace, and Origin, nested MSOA pub scope under the pub family, refreshed the loading/branding/footer treatment, and removed the station-access metric from the top-level visible chip row for a cleaner first read.

## 2026-04-01 — Unified analysis mode shell

- Refactored Compare, Why here?, Similar areas, Correlation, and Stories into one mutually exclusive borough analysis-mode system with a shared right-side panel shell.
- Replaced the separate ad-hoc analysis cards with one consistent header, close affordance, scrollable body, and borough-only visibility rules without removing any existing analysis capability.

## 2026-04-01 — MSOA pub density metric

- Added an MSOA-only pubs-per-km² metric using the same OpenStreetMap amenity=pub snapshot, spatially joined to London MSOA 2021 polygons.
- Kept borough pubs / km² as the headline pub density metric and labeled the MSOA version as exploratory, with explicit snapshot and community-maintained coverage caveats.

## 2026-04-01 — Borough building density metric

- Added a borough-level mapped-buildings-per-km² metric using an OpenStreetMap building footprint snapshot aggregated to London borough polygons.
- Wired the built-form metric into borough choropleths, tooltips, comparison, spotlight, and correlation, while explicitly leaving average building height out because the available London-wide height data was not borough-complete enough for a truthful average-height measure.

## 2026-04-01 — Borough pub density metric

- Added a borough-level pubs-per-km² metric using an OpenStreetMap amenity=pub snapshot aggregated to London borough polygons.
- Wired pub density into borough choropleths, legend copy, tooltips, comparison, spotlight, similarity, and correlation while intentionally leaving pint price out on source-quality grounds.

## 2026-04-01 — Borough correlation view

- Added a borough-only Correlation tool with a compact linked scatterplot for comparing two existing borough metrics at once.
- Linked map hover and pin state to the scatter so borough highlights and X/Y summaries stay in sync without adding new data.

## 2026-04-01 — Story chapters v1

- Added compact borough-only story chapters that preset key analytical views such as inner vs outer London, family suburbs, and the high-rent core.
- Added a lightweight chapter card with a short reading prompt while keeping normal map interaction, compare, spotlight, and similarity workflows available after the preset is applied.

## 2026-04-01 — Borough similarity search

- Added a borough-only Similar areas analysis tool that finds the top three profile matches using the existing normalized borough metrics.
- Added compact similarity explanations based on the closest matching dimensions without introducing new datasets or a black-box model.

## 2026-04-01 — Borough station-access transport metric

- Added a borough-level transport proxy based on mapped TfL / rail stations per 10,000 residents, aggregated from the official TfL stations feed.
- Wired the transport metric into borough choropleths, legend copy, tooltips, comparison, and spotlight insight rules without extending small-area transport support yet.

## 2026-04-01 — MSOA density time-travel control

- Replaced the temporary MSOA year buttons with a compact time-travel scrubber that appears only for Boroughs → Density → MSOA.
- Wired the time control to the existing year-aware MSOA density data so map colours, tooltips, and legend metadata all stay in sync as the year changes.

## 2026-04-01 — Borough median age metric

- Added borough-level median age as a first-class metric using ONS Census 2021 single-year age counts, derived into a borough median-age measure.
- Wired median age into borough choropleths, legend copy, tooltips, comparison, and spotlight insight rules without changing the small-area flow.

## 2026-04-01 — Greenspace trust-cues pass

- Tightened the borough greenspace wording so the metric reads consistently as a GLUD 2005 land-use baseline rather than a current live environmental measure.
- Clarified greenspace labels, legend metadata, tooltips, comparison copy, and spotlight narratives without changing the underlying data.

## 2026-04-01 — Borough greenspace metric

- Added borough-level greenspace share as a first-class metric using the London Datastore GLUD 2005 Greenspace land-use class.
- Wired greenspace into borough choropleths, legend copy, tooltips, comparison, and spotlight insight rules without changing the small-area flow.

## 2026-04-01 — Spotlight cross-metric insight pass

- Deepened the borough `Why here?` spotlight to rank and surface the strongest cross-metric patterns instead of listing one blurb per metric.
- Expanded the comparison card to a wider desktop layout with clearer A, B, and difference zones.

## 2026-04-01 — Spotlight panel placement & comparison spacing

- Moved the borough `Why here?` spotlight out of the left control stack into its own centre-right analysis card and fixed first-click spotlight refresh on borough selection.
- Loosened the borough comparison card layout so A/B values, names, and `B − A` are easier to scan without crowding the bottom-right corner.

## 2026-04-01 — Borough spotlight narratives

- Upgraded the borough `Why here?` panel from fixed metric rows to 3–5 short, data-driven spotlight sentences using the existing borough metrics only.
- Added simple ranking and above/below-average buckets so different boroughs now read as distinct profiles without adding new datasets.

## 2026-04-01 — Why here? spotlight & project changelog

- Added a root changelog to track major user-facing atlas changes and borough analysis milestones.
- Added a borough-only `Why here?` spotlight scaffold that compares a selected borough with London averages across the existing in-app metrics.

## 2026-04-01 — Comparison polish & layout hardening

- Refined the borough comparison panel with clearer A/B hierarchy, stronger onboarding states, and a more readable `B − A` summary.
- Moved comparison into borough-only tools and refactored the left control stack so borough panels flow naturally without fragile vertical offsets.

## 2026-04-01 — Borough comparison & MSOA density

- Added side-by-side borough comparison for the active borough metric, including A/B highlights and a compact comparison card.
- Added year-aware MSOA density rendering with 2021 and 2024 support while keeping borough metrics intact.

## 2026-04-01 — Borough controls & state stability

- Polished the borough density geography/year controls into a compact secondary options panel under `Metric`.
- Stabilized pinned tooltip and search-highlight behavior so metric, geography, year, and view changes stay in sync.
