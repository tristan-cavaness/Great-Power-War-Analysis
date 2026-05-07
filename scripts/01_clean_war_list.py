# 01_clean_war_list.py
# combines all Excel sheets into one CSV file

import pandas as pd
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

sheets = pd.read_excel(os.path.join(BASE_DIR, 'data', 'Great-Power-Wars-Dataset.xlsx'), sheet_name=None)

SHEET_NAMES = {
    'France': 'France', 'England-UK': 'England/UK', 'Spain': 'Spain',
    'Denmark': 'Denmark', 'Portugal': 'Portugal', 'Russia': 'Russia',
    'Ottoman-Turkey': 'Ottoman/Turkey', 'Austria': 'Austria',
}

cols = ['War / Campaign', 'Start', 'End', 'Duration', 'War Outcome',
        'Primary Enemy', 'Enemy Modern Equivalent', 'Enemy Type',
        'Posture', 'Home/Away', 'Self Capital', 'Enemy Capital', 'Distance (km)']

all_wars = []
for sheet, power in SHEET_NAMES.items():
    df = sheets[sheet][cols].copy()
    df.insert(0, 'power', power)
    df.columns = ['power', 'war_name', 'start_year', 'end_year', 'duration',
                   'outcome', 'primary_enemy', 'enemy_modern_equiv', 'enemy_type',
                   'posture', 'home_away', 'self_capital', 'enemy_capital', 'distance_km']
    all_wars.append(df)
    print(f"{power}: {len(df)} wars")

war_list = pd.concat(all_wars, ignore_index=True)
war_list.to_csv('../data/war_list.csv', index=False)
print(f"\nTotal: {len(war_list)} wars")
