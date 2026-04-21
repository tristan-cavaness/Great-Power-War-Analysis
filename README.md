# Three Great Powers: A Macro-Level Analysis of Great Power Wars, 1200–1985

## Overview

This project examines roughly 800 years of military force projection by three European great powers — **France**, **England/United Kingdom**, and **Spain** — to identify patterns in when and why great powers go to war, and what material and strategic conditions predict the outcomes of those conflicts.

The analysis operates at the macro-strategic level rather than the tactical. It does not measure battlefield performance or individual engagements. Instead, it asks: given the economic, demographic, territorial, and geographic conditions at the start of a conflict, can we predict whether a great power's use of force will succeed?

The contemporary relevance is direct. Russia's invasion of Ukraine, the United States' strikes on Iran and intervention in Venezuela, operations against Hezbollah and Hamas, and ongoing tensions over Taiwan all represent great powers projecting military force under varying conditions of advantage and constraint. This analysis asks whether 800 years of history offer identifiable patterns for when such actions succeed or fail.

## Data Sources

This analysis draws on several established academic datasets, supplemented by manually compiled war-level data:

| Source | Variables | Coverage |
|--------|-----------|----------|
| [Maddison Project Database](https://www.rug.nl/ggdc/historicaldevelopment/maddison/) | GDP per capita, population | ~1200–present |
| [Cliopatria (Seshat Global History Databank)](https://github.com/Seshat-Global-History-Databank/cliopatria) | Polity land area in km² | 3400 BCE–2024 CE |
| [Correlates of War — National Material Capabilities](https://correlatesofwar.org/data-sets/) | CINC scores (military expenditure, personnel, energy, steel, population) | 1816–present |
| Wikipedia — Lists of wars involving each power | War names, dates, belligerents, outcomes, theaters | Manual compilation |

### A Note on the War Data

The war-level records (names, dates, opponents, theaters, posture, outcomes) were compiled manually from Wikipedia's "List of wars involving France / England / Spain" pages, with AI assistance for cleaning and standardization. Records were cross-referenced with COW war data where available (post-1816). See **Inclusion and Exclusion Criteria** below for the rules governing which conflicts were included.

### Computed Variables

The following variables are derived from the source data rather than collected directly:

- **GDP ratio** — Power's total GDP divided by opponent's total GDP (GDP per capita × population for each side)
- **Population ratio** — Power's population divided by opponent's population
- **CINC ratio** — Power's CINC score divided by opponent's (post-1816 only)
- **Land area ratio** — Power's territorial area divided by opponent's area, from Cliopatria
- **Near-peer binary** — 1 if GDP ratio falls between 0.5 and 2.0, else 0
- **Capital-to-capital distance** — Computed via haversine formula using historical capital coordinates
- **Currency hegemon binary** — 1 if the power controlled the dominant world currency at the time of the war, coded from standard historical periodization: Portugal (1450–1530), Spain (1530–1640), Netherlands (1640–1720), France (1720–1815), Great Britain (1815–1920), United States (1921–present)

## Inclusion and Exclusion Criteria

### Included

A conflict is included if it meets **all** of the following:

1. **External conflict.** The war is directed against a foreign opponent — another state, kingdom, empire, or organized external entity. Internal civil wars and domestic rebellions are excluded.
2. **Primary belligerent or major contributor.** The great power played a leading or principal military role, not a token coalition contribution.
3. **Organized military resistance.** The opponent fielded an organized armed force capable of and willing to resist — whether a standing army, tribal military confederation, guerrilla force, or naval fleet.
4. **Deployment of organized military force.** The great power deployed regular military forces with the intent or willingness to engage in combat, including cases where the opponent capitulated before significant fighting occurred.

### Excluded

- Purely internal conflicts (civil wars, domestic rebellions without a foreign primary enemy)
- Token coalition participation where the power was not a principal decision-maker
- Naval blockades or diplomatic coercion without combat-ready deployment

### Borderline Guidance

- **Brief wars and single decisive engagements:** included. Duration does not determine strategic significance.
- **Gunboat diplomacy with territorial acquisition:** included. Asymmetric outcomes are data, not noise.
- **Opponent capitulated before major combat:** included. The capitulation is the outcome.
- **Colonial conquest against organized non-state opponents:** included if organized resistance was present.
- **Deployment with intent to fight, even if combat was minimal or the opponent withdrew:** included. The deployment and willingness to engage meets the threshold.

## Variables

Each observation (war) includes the following:

| Variable | Description | Source |
|----------|-------------|--------|
| War name | Name of the conflict | Wikipedia / manual |
| Start year, end year | Temporal bounds | Wikipedia / manual |
| Duration | Length in years | Computed |
| War outcome | Won, Lost, or Indecisive (from the power's perspective) | Wikipedia / manual |
| Primary enemy | Main opponent | Wikipedia / manual |
| Enemy type | European or Colonial/Eastern | Manual |
| Geographic theater | Region of conflict (e.g., Iberian Peninsula, South Asia) | Manual |
| Posture | Offensive or Defensive | Manual |
| Home / Away | Whether fought in or near the power's homeland | Manual |
| GDP per capita (both sides) | In 2011 US dollars (PPP) | Maddison Project Database 2023 |
| Population (both sides) | Estimated population | Maddison |
| CINC (both sides) | Composite Index of National Capability (post-1816) | COW |
| GDP ratio | Power total GDP / Opponent total GDP | Computed |
| Population ratio | Power / Opponent | Computed |
| CINC ratio | Power / Opponent (post-1816) | Computed |
| Land area ratio | Power area / Opponent area in km² | Cliopatria |
| Near-peer binary | 1 if GDP ratio 0.5–2.0, else 0 | Computed |
| Capital-to-capital distance | Kilometers between historical capitals | Computed (haversine) |
| Currency hegemon binary | 1 if power held dominant currency | Manual (historical consensus) |

## Scripts

Scripts should be run in the order listed below.

| Script | Description |
|--------|-------------|
| `01_clean_war_data.py` | Loads the raw war dataset from Excel. Filters to the 1200–1985 window. Standardizes column names and categorical variables. |
| `02_add_computed_variables.py` | Computes GDP ratio, population ratio, CINC ratio, land area ratio, near-peer binary, currency hegemon binary, and capital-to-capital distance. Merges Cliopatria and Maddison data. |
| `03_exploratory_analysis.py` | Generates descriptive statistics and summary tables: win rates by power, century, theater, posture, GDP ratio bin, etc. |
| `04_model.py` | Runs logistic regression predicting war outcome (win/loss) from material and strategic variables. Tests for nonlinear effects (e.g., diminishing returns of GDP advantage). Outputs regression tables. |
| `05_visualize.py` | Generates all figures: war timeline by power and outcome, GDP ratio vs. win rate scatter with fitted curve, win rate heatmap by century and power, near-peer vs. asymmetric outcome comparison, and others. |

## Output

All figures and tables are saved to the `outputs/` folder, including:

- Win rate by GDP ratio bin (scatter plot with fitted curve)
- Win rate heatmap by century and power
- Timeline of all wars, color-coded by outcome
- Offensive vs. defensive win rates by power asymmetry
- Near-peer vs. asymmetric outcome comparison
- Logistic regression results table
- Summary statistics (CSV)

## Preliminary Findings

*Analysis in progress — preliminary findings to be presented the week of April 21.*

## Limitations

- GDP and population estimates before ~1500 are rough approximations based on limited historical evidence. Results for the earliest centuries should be interpreted with caution.
- CINC data is only available from 1816, limiting the full model to modern-era wars.
- War outcomes are coded as discrete categories (Won, Lost, Indecisive), which may oversimplify conflicts with ambiguous results.
- The dataset covers three powers only. Findings may not generalize to other great powers (Ottoman Empire, Russia, China, etc.), though the framework is designed to be extensible.
- Theater, posture, and home/away classifications involve judgment calls for wars fought across multiple fronts.
- The war data was compiled from Wikipedia and may contain errors or omissions; where possible, records were cross-referenced with COW data for the post-1816 period.

## Reproducibility

To reproduce the analysis:

1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Download the Maddison Project Database and Cliopatria GeoJSON (instructions in `data/README.md`).
4. Run scripts in order (`01` through `05`).

## Author

Tristan Cavaness
Maxwell School of Citizenship and Public Affairs, Syracuse University
PAI 789 — Advanced Policy Analysis, Spring 2026
