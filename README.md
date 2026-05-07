# Great Power War Analysis, 1200-1989

## Overview

This project analyzes 411 wars fought by eight great powers France, England/UK, Spain, Portugal, Denmark, Russia, Ottoman Empire/Turkey, and Austria over roughly 800 years to identify what socio-economic conditions best predict war outcomes.

## At a Glance

Some highlights from 800 years of data:

**Russia wins the most.** With a 76% win rate across 45 decisive wars, Russia has the best track record of any European great power. But France has fought nearly twice as many wars (86 decisive)  making it everyone else's most common enemy. France is the #1 opponent for England, Spain, and Austria. Russia and the Ottoman Empire have their own mutual rivalry spanning 8-9 wars over five centuries.

**Spain holds the longest win streak** at 16 consecutive victories  almost certainly driven by its colonial conquests in the Americas. France comes in second at 13, England at 12. Austria's best streak is just 5 wins, which partly explains its 46% win rate  the lowest among the eight powers along with Denmark at 44%.

**The 20th century broke everything.** Win rates dropped to 49%  essentially a coin flip. The era of reliable colonial conquest was over, and peer-level conflicts between industrialized powers are much less predictable.

**War duration barely affects the outcome.** Whether a war lasts 1 year or 25, the aggressor's win rate stays between 56% and 67%. Only wars lasting over 50 years show a dramatic drop (33%), but there are only 3 of those in the dataset.

**Offense dominates  but only against weaker opponents.** Offensive wars against colonial/eastern opponents win 84% of the time. Defensive wars against those same opponents? Just 44%. Against European peers, the offensive advantage narrows to 63% vs 50% and is not statistically significant.

**The France-Spain rivalry** is the most fought matchup in the dataset: 16 wars from the English side against France, 16 from Spain against France, and 15 from the French side against Spain. Europe's western triangle was locked in near-permanent conflict for centuries.

## Data Sources

| Source | File | Variables |
| --- | --- | --- |
| [Maddison Project Database 2023](https://www.rug.nl/ggdc/historicaldevelopment/maddison/) | `data/mpd2023_web.xlsx` | GDP per capita (2011$), population |
| [OWID / HYDE 3.3](https://ourworldindata.org/urbanization) | `data/urbanization-vs-gdp.csv` | Urban population share (%) |
| [OWID / HYDE 3.3](https://ourworldindata.org/grapher/land-use-over-the-long-term) | `data/land-use-over-the-long-term.csv` | Built-up area, cropland, grazing land (hectares) |
| [OWID / HYDE 3.3](https://ourworldindata.org/grapher/urban-and-rural-population-stacked) | `data/urban-and-rural-population-stacked.csv` | Urban and rural population counts |
| Manually compiled from Wikipedia | `data/Great-Power-Wars-Dataset.xlsx` | War records, outcomes, opponents, posture |

- Source Lists
Wars involving France
Wars involving England / United Kingdom
Wars involving Spain
Wars involving Denmark
Wars involving Portugal
Wars involving Russia
Wars involving the Ottoman Empire / Turkey
Wars involving Austria


- Maddison Project Database 2023

Used for:

GDP per capita (Constant 2011 international dollars)
Total GDP (Constant 2011 international dollars)
Population estimates

Citation:

Bolt, Jutta and Jan Luiten van Zanden (2024), “Maddison style estimates of the evolution of the world economy: A new 2023 update”, Journal of Economic Surveys.


- HYDE 3.3 / Our World in Data

Used for:

Urban population
Rural population
Urbanization rate
Built-up area
Cropland
Grazing land

Citation:

Klein Goldewijk, K., Beusen, A., Doelman, J., and Stehfest, E. (2017), “Anthropogenic land use estimates for the Holocene – HYDE 3.2”, Earth System Science Data, 9, 927–953.

Utrecht University / PBL Netherlands Environmental Assessment Agency — History Database of the Global Environment (HYDE v3.3, 2023).

Processed and distributed through Our World in Data.


The war dataset includes an "Enemy Modern Equivalent" column mapping each historical opponent to its modern country name for lookup against Maddison and OWID. Of 411 wars, 399 map to a modern state. The 12 unmatchable entries are Mongol/Tatar successor states, the Caucasian Imamate, Tahiti, the Iroquois Confederacy, Palestinian Arab rebels, and Knights Hospitalier.

## Why Log Transforms?

All ratio variables (GDP per capita ratio, population ratio, built-up area ratio, etc.) are log-transformed before regression. This matters for three reasons:

1. **Symmetry.** A raw ratio of 2.0 (twice as rich) and 0.5 (half as rich) represent the same magnitude of difference in opposite directions, but on a linear scale they are not symmetric around 1. Log transformation fixes this: log(2.0) = +0.69 and log(0.5) = -0.69 are perfectly symmetric around zero.

2. **Skew compression.** Ratio variables are heavily right-skewed. A colonial power might have a GDP/cap ratio of 15x against a pre-industrial opponent, while European peer wars cluster around 0.5-2.0x. Without log transformation, the regression would be dominated by a few extreme colonial ratios. Log transformation compresses the extremes to get similar weight going from 1x to 2x and 3x and 6x.

3. **Proportional interpretation.** With log-transformed ratios, the regression coefficient measures the effect of a proportional change in advantage (e.g. doubling your GDP/cap ratio) rather than an absolute change (e.g. adding $500 to your GDP/cap advantage). This makes more sense for comparing wars across 800 years where absolute values change dramatically but proportional advantages does not. 

## Inclusion Criteria

A conflict is included if it involves an external opponent, the great power contributed a significant share of the fighting force, the opponent fielded organized resistance, and regular military forces were deployed.

## Scripts

Run in order from the repo root directory.

| Script | Description |
| --- | --- |
| `01_clean_war_list.py` | Loads the Excel war dataset and combines all 8 sheets into a single CSV |
| `02_merge_data.py` | Merges war list with Maddison GDP/population and OWID urbanization/land use data for both self and opponent, interpolating between benchmark years. Computes all ratios and derived variables |
| `03_exploratory_analysis.py` | Win rate tables by power, posture, enemy type, and GDP ratio bins |
| `04_regression.py` | Logistic regression predicting war outcomes using sklearn and scipy |
| `05_visualize.py` | Generates all figures |

### Setup

```
pip install -r requirements.txt
python scripts/01_clean_war_list.py
python scripts/02_merge_data.py
python scripts/03_exploratory_analysis.py
python scripts/04_regression.py
python scripts/05_visualize.py
```

## Data Coverage

| Variable | Self | Opponent |
| --- | --- | --- |
| GDP per capita | 375/411 (91%) | 379/411 (92%) |
| Urban pop % | 411/411 (100%) | 397/411 (97%) |
| Built-up area | 411/411 (100%) | 397/411 (97%) |
| Grazing/Cropland | 411/411 (100%) | 397/411 (97%) |
| Urban/Rural pop | 411/411 (100%) | 397/411 (97%) |

Missing Maddison data is interpolated between benchmark years and backfilled up to 250 years from the earliest available estimate. GDP/cap gaps are primarily for Austria and Denmark before ~1820 and for the 12 unmatchable opponent entities.

## Results

### Individual Predictor Screening

| Variable | Coefficient | p-value | R^² |
| --- | --- | --- | --- |
| Offensive posture | +1.05 | < 0.001 | 0.045 |
| Total GDP ratio (log) | +0.19 | 0.002 | 0.024 |
| Population ratio (log) | +0.20 | 0.002 | 0.021 |
| Urban population ratio (log) | +0.14 | 0.003 | 0.020 |
| Built-up area ratio (log) | +0.12 | 0.011 | 0.014 |
| Grazing land ratio (log) | +0.13 | 0.024 | 0.012 |
| Urban % ratio (log) | +0.17 | 0.026 | 0.011 |
| Home advantage | -0.59 | 0.022 | 0.011 |
| GDP per capita ratio (log) | +0.24 | 0.087 | 0.007 |
| Cropland ratio (log) | +0.09 | 0.090 | 0.006 |

Distance was not statistically ignificant.

### Core Model

The three-variable model (offensive posture + GDP/cap ratio + home advantage) explains 4.4% of variance (pseudo R-squared). Offensive posture is the dominant predictor (+25 percentage points, p < 0.001). Adding population ratio improves the model significantly (R^² = 0.015, p = 0.013).

### Colonial vs European Wars

Colonial wars: R^² = 12.6%, with offensive posture highly significant (p < 0.001), signaling the innate advantage in attacking a distant weaker power in a war of choice. European wars: R^² = 1.7%, with no variable reaching significance. In peer conflicts, macro socio-economic advantages explain almost nothing  strategy, diplomacy, alliances, and battlefield tactics carry the most weight.

### Home Advantage Confound

Home advantage is negative when tested alone (p = 0.022) but positive in the combined model. Colonial wars  which have high win rates  are almost always fought away from home, creating a confound that reverses once you control for offensive posture.

## Limitations

- GDP and population estimates before ~1820 rely on backfill from the earliest Maddison data point for Austria and Denmark
- 12 opponent entities have no modern country equivalent and are excluded from the analysis, most others were assigned a logical modern day equivalent entity for data analysis purposes
- Coalition wars are attributed to the primary belligerent, which may understate aggregate opposition
- War outcomes are coded as discrete categories which may oversimplify often ambiguous results
- The model explains 4.4% of variance  most of what determines war outcomes is not easily estimated by macro-level physical advantages
- War data was compiled from Wikipedia and may contain computing and data entry errors

## Requirements

```
pandas
numpy
matplotlib
seaborn
scikit-learn
scipy
openpyxl
```

## Author

Tristan Cavaness
Maxwell School of Citizenship and Public Affairs, Syracuse University
May 2026
