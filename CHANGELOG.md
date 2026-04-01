# Changelog

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
