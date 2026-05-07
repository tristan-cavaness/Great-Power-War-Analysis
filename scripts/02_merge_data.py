# 02_merge_data.py
# merges war list with Maddison (GDP, pop) and OWID/HYDE (urban, land use)

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

# power name mappings - Maddison and OWID use slightly different names
POWER_TO_MADDISON = {
    'France': 'France', 'England/UK': 'United Kingdom', 'Spain': 'Spain',
    'Portugal': 'Portugal', 'Denmark': 'Denmark', 'Russia': 'Russian Federation',
    'Ottoman/Turkey': 'Turkey', 'Austria': 'Austria',
}
POWER_TO_OWID = {
    'France': 'France', 'England/UK': 'United Kingdom', 'Spain': 'Spain',
    'Portugal': 'Portugal', 'Denmark': 'Denmark', 'Russia': 'Russia',
    'Ottoman/Turkey': 'Turkey', 'Austria': 'Austria',
}

# fixes for names that don't match between our data and the databases
MADDISON_FIXES = {
    'Russia': 'Russian Federation', 'Vietnam': 'Viet Nam',
    'Iran': 'Iran (Islamic Republic of)', 'Sudan': 'Sudan (Former)',
    'Syria': 'Syrian Arab Republic',
}
OWID_FIXES = {'Czech Republic': 'Czechia', 'State of Palestine': 'Palestine'}

def to_mad(name):
    return MADDISON_FIXES.get(name, name)

def to_owid(name):
    return OWID_FIXES.get(name, name)


def interpolate_dataset(df, value_cols, countries):
    # fill in missing years between benchmark data points
    frames = []
    for country in countries:
        cd = df[df['Entity'] == country].sort_values('Year')
        if len(cd) == 0:
            continue
        min_yr = int(cd['Year'].min())
        max_yr = int(cd['Year'].max())
        full = pd.DataFrame({'Year': range(min_yr, max_yr + 1)})
        merged = full.merge(cd[['Year'] + value_cols], on='Year', how='left')
        for col in value_cols:
            merged[col] = merged[col].interpolate().bfill(limit=250)
        merged['Entity'] = country
        frames.append(merged)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


def merge_side(wars_df, interp_df, value_cols, name_series, prefix):
    # merge interpolated data onto wars using a country name column
    wars_df['_tmp'] = name_series
    renames = {col: f'{prefix}_{col}' for col in value_cols}
    sub = interp_df[['Entity', 'Year'] + value_cols].rename(columns=renames)
    wars_df = wars_df.merge(sub, left_on=['_tmp', 'start_year'],
                            right_on=['Entity', 'Year'], how='left')
    wars_df = wars_df.drop(columns=['Entity', 'Year', '_tmp'], errors='ignore')
    return wars_df


wars = pd.read_csv('../data/war_list.csv')
print(f"{len(wars)} wars loaded")

# MADDISON (gdp per capita + population)
mad_raw = pd.read_excel('../data/mpd2023_web.xlsx', sheet_name='Full data')
enemy_mad_names = set(wars['enemy_modern_equiv'].dropna().apply(to_mad))
needed = set(POWER_TO_MADDISON.values()) | enemy_mad_names
mad = mad_raw[mad_raw['country'].isin(needed)].copy()

interp = []
for country in mad['country'].unique():
    cd = mad[mad['country'] == country].sort_values('year')
    if len(cd) == 0: continue
    full = pd.DataFrame({'year': range(int(cd['year'].min()), int(cd['year'].max()) + 1)})
    m = full.merge(cd[['year', 'country', 'gdppc', 'pop']], on='year', how='left')
    m['country'] = country
    m['gdppc'] = m['gdppc'].interpolate().bfill(limit=250)
    m['pop'] = m['pop'].interpolate().bfill(limit=250)
    interp.append(m)
mad_full = pd.concat(interp, ignore_index=True)

# merge self
wars['_tmp'] = wars['power'].map(POWER_TO_MADDISON)
wars = wars.merge(mad_full[['country','year','gdppc','pop']],
                  left_on=['_tmp','start_year'], right_on=['country','year'], how='left')
wars = wars.rename(columns={'gdppc': 'self_gdp_cap', 'pop': 'self_pop_thousands'})
wars = wars.drop(columns=['country', 'year', '_tmp'])

# merge opponent
wars['_tmp'] = wars['enemy_modern_equiv'].apply(lambda x: to_mad(x) if pd.notna(x) else np.nan)
wars = wars.merge(mad_full[['country','year','gdppc','pop']],
                  left_on=['_tmp','start_year'], right_on=['country','year'], how='left')
wars = wars.rename(columns={'gdppc': 'opp_gdp_cap', 'pop': 'opp_pop_thousands'})
wars = wars.drop(columns=['country', 'year', '_tmp'])
print(f"  Self GDP/cap: {wars['self_gdp_cap'].notna().sum()}/{len(wars)}")
print(f"  Opp GDP/cap:  {wars['opp_gdp_cap'].notna().sum()}/{len(wars)}")


def all_owid_names():
    opp = set(wars['enemy_modern_equiv'].dropna().apply(to_owid))
    return set(POWER_TO_OWID.values()) | opp

def opp_owid_series():
    return wars['enemy_modern_equiv'].apply(lambda x: to_owid(x) if pd.notna(x) else x)


# OWID urban pop %
print("\nOWID urban pop %")
owid = pd.read_csv('../data/urbanization-vs-gdp.csv')
owid = owid.rename(columns={'Population share in urban areas': 'urban_pct'})
owid_interp = interpolate_dataset(owid, ['urban_pct'], all_owid_names())
wars = merge_side(wars, owid_interp, ['urban_pct'], wars['power'].map(POWER_TO_OWID), 'self')
wars = merge_side(wars, owid_interp, ['urban_pct'], opp_owid_series(), 'opp')
print(f"  Self: {wars['self_urban_pct'].notna().sum()}/{len(wars)}, Opp: {wars['opp_urban_pct'].notna().sum()}/{len(wars)}")

# OWID/HYDE land use
print("\nOWID/HYDE land use")
owid = pd.read_csv('../data/land-use-over-the-long-term.csv')
owid = owid.rename(columns={'Built-up Area': 'builtup_ha', 'Grazing': 'grazing_ha', 'Cropland': 'cropland_ha'})
land_cols = ['builtup_ha', 'grazing_ha', 'cropland_ha']
owid_interp = interpolate_dataset(owid, land_cols, all_owid_names())
wars = merge_side(wars, owid_interp, land_cols, wars['power'].map(POWER_TO_OWID), 'self')
wars = merge_side(wars, owid_interp, land_cols, opp_owid_series(), 'opp')
print(f"  Self built-up: {wars['self_builtup_ha'].notna().sum()}/{len(wars)}, Opp: {wars['opp_builtup_ha'].notna().sum()}/{len(wars)}")

# OWID/HYDE urban + rural pop
print("\nOWID urban/rural pop")
owid = pd.read_csv('../data/urban-and-rural-population-stacked.csv')
owid = owid.rename(columns={'Urban': 'urban_pop', 'Rural': 'rural_pop'})
ur_cols = ['urban_pop', 'rural_pop']
owid_interp = interpolate_dataset(owid, ur_cols, all_owid_names())
wars = merge_side(wars, owid_interp, ur_cols, wars['power'].map(POWER_TO_OWID), 'self')
wars = merge_side(wars, owid_interp, ur_cols, opp_owid_series(), 'opp')
print(f"  Self urban pop: {wars['self_urban_pop'].notna().sum()}/{len(wars)}, Opp: {wars['opp_urban_pop'].notna().sum()}/{len(wars)}")


# compute ratios
def ratio(a, b):
    if a in wars.columns and b in wars.columns:
        return wars[a] / wars[b].replace(0, np.nan)
    return np.nan

wars['gdp_cap_ratio'] = ratio('self_gdp_cap', 'opp_gdp_cap')
wars['pop_ratio'] = ratio('self_pop_thousands', 'opp_pop_thousands')
wars['urban_pct_ratio'] = ratio('self_urban_pct', 'opp_urban_pct')
wars['builtup_ratio'] = ratio('self_builtup_ha', 'opp_builtup_ha')
wars['grazing_ratio'] = ratio('self_grazing_ha', 'opp_grazing_ha')
wars['cropland_ratio'] = ratio('self_cropland_ha', 'opp_cropland_ha')
wars['urban_pop_ratio'] = ratio('self_urban_pop', 'opp_urban_pop')
wars['self_total_gdp'] = wars['self_gdp_cap'] * wars['self_pop_thousands']
wars['opp_total_gdp'] = wars['opp_gdp_cap'] * wars['opp_pop_thousands']
wars['total_gdp_ratio'] = ratio('self_total_gdp', 'opp_total_gdp')

# log transform ratios for regression
for col in ['gdp_cap_ratio', 'total_gdp_ratio', 'pop_ratio', 'urban_pct_ratio',
            'builtup_ratio', 'grazing_ratio', 'cropland_ratio', 'urban_pop_ratio']:
    if col in wars.columns and wars[col].notna().any():
        wars[f'log_{col}'] = np.log(wars[col].clip(lower=0.001))

wars['log_distance'] = np.log(wars['distance_km'].clip(lower=1))

wars['win'] = np.nan
wars.loc[wars['outcome'] == 'Won', 'win'] = 1
wars.loc[wars['outcome'] == 'Lost', 'win'] = 0
wars['is_offensive'] = (wars['posture'] == 'Offensive').astype(int)
wars['is_home'] = (wars['home_away'] == 'Home').astype(int)
wars['is_colonial'] = (wars['enemy_type'] == 'Colonial / Eastern').astype(int)
wars['century'] = (wars['start_year'] // 100) + 1

wars.to_csv('../data/wars_merged.csv', index=False)
print(f"\nSaved {len(wars)} wars to wars_merged.csv")
