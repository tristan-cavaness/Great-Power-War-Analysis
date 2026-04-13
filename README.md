# Mapping Food Accessibility Gaps in Syracuse's North Side

## Overview

This project examines food accessibility challenges in Syracuse, New York, with a focus on historically underserved neighborhoods. Using census tract-level demographic data, grocery store locations, and street network analysis, the project maps the distance residents must travel to reach full-service grocery stores (on foot and by public transit) and identifies areas where access falls short.

The closure of the Save A Lot at 500 Butternut Street in early 2026 highlights a problem many Northside residents already knew: healthy, affordable food is hard to reach without a car. This analysis aims to quantify that gap and visualize where it is most severe.

## Data Sources

- **American Community Survey (ACS):** Median household income, population density, vehicle access, and demographic characteristics at the census tract level.
- **USDA Food Access Research Atlas:** Food desert designations and low-access tract classifications.
- **OpenStreetMap (via OSMnx):** Street network data for calculating walking distances.
- **Centro (GTFS data):** Public transit routes and stop locations for Syracuse's bus system.
- **Grocery store locations:** Compiled from [source TBD, manual geocoding].

## Scripts

*Scripts should be run in the order listed below.*

| Script | Description |
|--------|-------------|
| `01_get_acs_data.py` | Downloads ACS demographic and economic data by census tract for Syracuse. |
| `02_get_grocery_locations.py` | Assembles and geocodes grocery store locations in the Syracuse area. |
| `03_build_network.py` | Constructs the street network and calculates walking distances from tract centroids to nearest grocery stores. |
| `04_transit_analysis.py` | Analyzes public transit access to grocery stores using GTFS data. |
| `05_merge_and_analyze.py` | Merges all datasets and produces summary statistics and regression analysis. |
| `06_visualize.py` | Generates maps and figures for the analysis. |

## Output

All figures and output files are saved to the `outputs/` folder, including:

- Choropleth maps of food access by census tract
- Walking distance maps to nearest grocery stores
- Demographic overlays (income, vehicle access, population density)
- Summary statistics and regression results

## Preliminary Findings

*Analysis in progress*

## Reproducibility

To reproduce the analysis:

1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run scripts in order (`01` through `06`).
4. Input data that cannot be redistributed includes instructions for download in the relevant script or in the `data/` folder README.

## Author

Tristan Cavaness
Maxwell School of Citizenship and Public Affairs, Syracuse University
PAI 789 — Advanced Policy Analysis, Spring 2026
