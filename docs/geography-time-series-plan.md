# London atlas: next geography and time-series plan

## Recommended next geography: MSOA

Use **MSOA** as the default next step after boroughs.

Why MSOA is the best compromise:

- **Data richness**: MSOA is the smallest geography in this stack that has a realistic path for all core metrics, including an official small-area **income proxy** from ONS.
- **Time coverage**: annual or rolling-annual time series are available for population and house prices, while census-based variables can be compared at **2011 vs 2021**.
- **Rendering performance**: London has about **983 MSOAs** in the cached boundary files, versus about **4,835 LSOAs** and **25,053 output areas**. MSOA is detailed enough to feel neighborhood-like without pushing the browser too hard.
- **Conceptual clarity**: MSOAs are stable statistical areas used consistently across ONS, Nomis, and housing datasets; wards and postcodes are less suitable as the main analytical layer.

## Geometry comparison

Local cached London boundary counts in this repo:

| Geography | London polygons | Suitability |
|---|---:|---|
| Borough | 33 | Existing overview layer |
| Ward | 625 | Familiar politically, but less stable and less consistent for time series |
| **MSOA** | **983** | Best next default |
| LSOA | 4,835 | Strong future detailed layer for selected metrics |
| OA | 25,053 | Too detailed for the next step |
| Postcode sector/district | varies | Poor fit for official demographic series |

## Why not the other options

### LSOA

Strong for:

- annual population and density
- house prices
- Census 2011 / 2021 demographic variables

Weakness:

- no comparable official small-area income series at LSOA in the current source set
- much heavier polygon count for the browser

Recommendation:

- use LSOA later for **density / housing / selected census layers**
- do **not** make it the first small-area default

### Wards

Weaknesses:

- ward boundaries change more often
- datasets are less consistently maintained over time than MSOA / LSOA
- weaker long-run comparability for a time slider

### Postcode districts / sectors

Weaknesses:

- not the main geography used by ONS / Nomis demographic releases
- weak compatibility across the target metrics
- less analytically clean than standard statistical areas

## Metric -> dataset plan

### Population / density

- **Dataset**: ONS, *Population estimates by output areas, electoral, health and other geographies, England and Wales: mid-2023 and mid-2024, revised mid-2022*
- **Geography**: MSOA and LSOA
- **Years**: mid-2011 to mid-2024 across the current small-area release set
- **Use**: compute population density from annual population and polygon area
- **Caveats**:
  - mid-2022 has been revised
  - publication lag exists for the newest years
- **URLs**:
  - https://www.ons.gov.uk/releases/populationestimatesbyoutputareaselectoralhealthandothergeographiesenglandandwalesmid2023andmid2024revisedmid2022
  - https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/methodologies/smallareapopulationestimatesqmi

### House prices

- **Dataset**: ONS, *Median house prices by Middle layer Super Output Area* (formerly HPSSA dataset 2)
- **Geography**: MSOA
- **Years**: long-running annual / rolling-annual series; current editions run through **year ending March 2025**
- **Use**: first time-slider housing layer at MSOA
- **Caveats**:
  - property transactions, not stock valuation
  - rolling-annual updates in the newer publication format
- **URL**:
  - https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/medianhousepricesbymiddlelayersuperoutputarea

LSOA housing fallback:

- **Dataset**: ONS, *Median house prices by lower layer super output area: HPSSA dataset 46*
- **Geography**: LSOA
- **Use**: later finer-grained housing mode
- **URL**:
  - https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/medianpricepaidbylowerlayersuperoutputareahpssadataset46

### Income / earnings proxy

- **Dataset**: ONS, *Income estimates for small areas, England and Wales*
- **Geography**: MSOA
- **Years**: realistic first slice is **FYE 2018, FYE 2020, FYE 2023**
- **Use**: replace borough-only earnings with a small-area **income proxy**
- **Caveats**:
  - model-based
  - **mean household income**, not median earnings
  - published around every two years rather than annually
- **URLs**:
  - https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/smallareamodelbasedincomeestimates/financialyearending2023
  - https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/methodologies/incomeestimatesforsmallareasqmi

### Gender balance

- **Dataset**: ONS small-area population estimates plus sex splits
- **Geography**: MSOA and LSOA
- **Years**: annual, aligned with the small-area population estimate releases
- **Use**: derive male share / female share / parity gap each year
- **Caveat**:
  - should be framed as population sex balance, not a separate survey-based gender dataset

### Children / family

- **Dataset**:
  - Census 2021, *Households containing dependent children*
  - 2011 Census comparable household composition / dependent-children tables via Nomis
- **Geography**: MSOA is the clean default
- **Years**: **2011 and 2021**
- **Use**: two-point “time travel” only
- **Caveats**:
  - effectively decennial
  - not an annual series without additional modelling
- **URLs**:
  - https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/householdscontainingdependentchildrencensus2021
  - https://www.ons.gov.uk/census/census2021dictionary/variablesbytopic/demographyvariablescensus2021/dependentchildreninhouseholdandtheirage
  - https://www.nomisweb.co.uk/census/2011/dc1109ew

### Country of birth / origin

- **Dataset**:
  - Census 2021, *TS004 Country of birth*
  - 2011 Census via Nomis *KS204EW Country of birth*
- **Geography**: MSOA preferred, with LSOA possible for some slices
- **Years**: **2011 and 2021**
- **Use**:
  - UK-born vs not-UK-born overview
  - selected-country shares where available
- **Caveats**:
  - decennial only
  - detailed country breakdowns become harder at very small geographies
- **URLs**:
  - https://www.ons.gov.uk/datasets/TS004
  - https://www.nomisweb.co.uk/census/2011/ks204ew

## Recommended first time-slider target

Build the first slider around **MSOA** and add metrics in this order:

1. **Population density**: mid-2011 to mid-2024
2. **House prices**: annual / rolling-annual MSOA series through the latest release
3. **Income proxy**: FYE 2018, 2020, 2023
4. **Country of birth** and **children**: 2011 vs 2021 two-point mode

## Metrics likely to remain borough-only for now

- current **median earnings** layer, because the borough implementation is based on a different source concept than the small-area income estimates
- any metric that depends on borough-only curated GLA summaries without a matching MSOA release

## Risks

- **Boundary vintages**: small-area datasets are moving from 2011 to 2021 statistical geographies, so joins need explicit version handling
- **Performance**: LSOA is feasible later, but MSOA is safer for the first browser implementation
- **Income comparability**: small-area income is an official proxy, but not a direct replacement for ASHE-style earnings
- **Decennial metrics**: country of birth and family composition will support a two-point census comparison before they support a true annual slider
