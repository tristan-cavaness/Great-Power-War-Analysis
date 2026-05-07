# 03_exploratory_analysis.py
# win rate tables, matchups, streaks, summary stats

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'wars_merged.csv'))
decisive = df[df['outcome'].isin(['Won', 'Lost'])].copy()

powers = ['France', 'England/UK', 'Spain', 'Portugal', 'Denmark',
          'Russia', 'Ottoman/Turkey', 'Austria']

# win rates by power
rows = []
for p in powers:
    pw = decisive[decisive['power'] == p]
    w = len(pw[pw['outcome'] == 'Won'])
    t = len(pw)
    wr = w/t if t > 0 else 0
    rows.append({'power': p, 'won': w, 'lost': t-w, 'total': t, 'win_rate': round(wr, 3)})
    print(f"{p:18s} {w:3d}W / {t-w:3d}L = {wr:.1%}")
pd.DataFrame(rows).to_csv('../outputs/win_rates_by_power.csv', index=False)

# by posture and enemy type
print("")
rows = []
for posture in ['Offensive', 'Defensive']:
    for etype in decisive['enemy_type'].unique():
        sub = decisive[(decisive['posture'] == posture) & (decisive['enemy_type'] == etype)]
        w = len(sub[sub['outcome'] == 'Won'])
        t = len(sub)
        wr = w/t if t > 0 else 0
        rows.append({'posture': posture, 'enemy_type': etype, 'won': w, 'total': t, 'win_rate': round(wr, 3)})
        print(f"{posture:10s} vs {etype:20s} = {wr:.1%} (n={t})")
pd.DataFrame(rows).to_csv('../outputs/win_rates_by_posture_type.csv', index=False)

# by gdp/cap ratio bins
print("")
bins = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, float('inf')]
labels = ['<0.5x', '0.5-1x', '1-1.5x', '1.5-2x', '2-3x', '3-5x', '>5x']
has = decisive['gdp_cap_ratio'].notna()
decisive.loc[has, 'gdp_cap_bin'] = pd.cut(decisive.loc[has, 'gdp_cap_ratio'], bins=bins, labels=labels)
rows = []
for lab in labels:
    sub = decisive[decisive['gdp_cap_bin'] == lab]
    w = len(sub[sub['outcome'] == 'Won'])
    t = len(sub)
    wr = w/t if t > 0 else 0
    rows.append({'bin': lab, 'won': w, 'total': t, 'win_rate': round(wr, 3)})
    print(f"{lab:10s} = {wr:.1%} (n={t})")
pd.DataFrame(rows).to_csv('../outputs/win_rates_by_gdp_cap_bin.csv', index=False)

# longest win streaks with timeframes
print("\nLONGEST WIN STREAKS")
streak_rows = []
for power in powers:
    pw = decisive[decisive['power'] == power].sort_values('start_year')

    streak = 0
    best = 0
    streak_start = None
    best_start = None
    best_end = None

    for _, row in pw.iterrows():
        if row['outcome'] == 'Won':
            if streak == 0:
                streak_start = int(row['start_year'])
            streak += 1
            if streak > best:
                best = streak
                best_start = streak_start
                best_end = int(row['end_year'])
        else:
            streak = 0

    streak_rows.append({
        'power': power, 'streak': best,
        'from': best_start, 'to': best_end
    })
    print(f"  {power:18s} {best} wins ({best_start}-{best_end})")

pd.DataFrame(streak_rows).to_csv('../outputs/win_streaks.csv', index=False)

# summary statistics
stats_cols = [c for c in ['duration', 'distance_km', 'self_gdp_cap', 'opp_gdp_cap',
              'gdp_cap_ratio', 'pop_ratio'] if c in df.columns]
df[stats_cols].describe().round(2).to_csv('../outputs/summary_statistics.csv')
