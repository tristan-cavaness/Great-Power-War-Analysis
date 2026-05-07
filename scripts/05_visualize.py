# 05_visualize.py
# generates all figures

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
os.makedirs('outputs', exist_ok=True)

df = pd.read_csv('../data/wars_merged.csv')
decisive = df[df['outcome'].isin(['Won', 'Lost'])].copy()

outcome_colors = {'Won': 'green', 'Lost': 'firebrick', 'Indecisive': 'goldenrod'}
power_colors = {
    'France': 'royalblue', 'England/UK': 'crimson', 'Spain': 'goldenrod',
    'Denmark': 'purple', 'Portugal': 'forestgreen',
    'Russia': 'orangered', 'Ottoman/Turkey': 'teal', 'Austria': 'dimgray',
}
powers = ['France', 'England/UK', 'Spain', 'Portugal', 'Denmark',
          'Russia', 'Ottoman/Turkey', 'Austria']


# timeline
fig, ax = plt.subplots(figsize=(16, 10))
for i, power in enumerate(powers):
    power_wars = df[df['power'] == power]
    for _, war in power_wars.iterrows():
        color = outcome_colors.get(war['outcome'], 'gray')
        ax.barh(i, war['duration'], left=war['start_year'], height=0.6, color=color, alpha=0.7)

ax.set_yticks(range(len(powers)))
ax.set_yticklabels(powers)
ax.set_xlim(1190, 2000)
ax.set_title('800 Years of Great Power Warfare')
patches = []
for outcome in ['Won', 'Lost', 'Indecisive']:
    patches.append(mpatches.Patch(color=outcome_colors[outcome], label=outcome, alpha=0.7))
ax.legend(handles=patches, loc='upper left')
plt.tight_layout()
plt.savefig('../outputs/fig_timeline.png')
plt.close()
print("fig_timeline.png")


# win rate by power
fig, ax = plt.subplots(figsize=(12, 5))
win_rates = []
counts = []
for power in powers:
    pw = decisive[decisive['power'] == power]
    win_rates.append(pw['win'].mean())
    counts.append(len(pw))

bars = ax.bar(powers, win_rates, color=[power_colors[p] for p in powers])
for i in range(len(bars)):
    ax.text(bars[i].get_x() + bars[i].get_width()/2,
            bars[i].get_height() + 0.01,
            f'{win_rates[i]:.0%}\n(n={counts[i]})', ha='center')

ax.set_ylim(0, 1.0)
ax.set_title('Win Rate by Power')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('../outputs/fig_win_rate_by_power.png')
plt.close()
print("fig_win_rate_by_power.png")


# heatmap
pivot = decisive.groupby(['power', 'century'])['win'].mean().reset_index()
matrix = pivot.pivot(index='power', columns='century', values='win')
matrix = matrix.reindex(powers)

fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(matrix, annot=True, fmt='.0%', cmap='RdYlGn',
            vmin=0, vmax=1, linewidths=0.5, ax=ax)
ax.set_title('Win Rate by Power and Century')
ax.set_xticklabels([f'{int(c)}th' for c in matrix.columns], rotation=0)
ax.set_ylabel('')
plt.tight_layout()
plt.savefig('../outputs/fig_win_rate_heatmap.png')
plt.close()
print("fig_win_rate_heatmap.png")


# offensive vs defensive
etypes = ['Colonial / Eastern', 'European']
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(etypes))
width = 0.35

for i, posture in enumerate(['Offensive', 'Defensive']):
    rates = []
    ns = []
    for etype in etypes:
        sub = decisive[(decisive['posture'] == posture) & (decisive['enemy_type'] == etype)]
        if len(sub) > 0:
            rates.append(sub['win'].mean())
        else:
            rates.append(0)
        ns.append(len(sub))

    if posture == 'Offensive':
        color = 'darkorange'
    else:
        color = 'steelblue'

    bars = ax.bar(x + i*width, rates, width, label=posture, color=color)
    for j in range(len(bars)):
        ax.text(bars[j].get_x() + bars[j].get_width()/2,
                bars[j].get_height() + 0.01,
                f'{rates[j]:.0%}\n(n={ns[j]})', ha='center')

ax.set_xticks(x + width/2)
ax.set_xticklabels(etypes)
ax.set_ylim(0, 1.0)
ax.set_title('Offensive vs Defensive Win Rate by Enemy Type')
ax.legend()
plt.tight_layout()
plt.savefig('../outputs/fig_offensive_vs_defensive.png')
plt.close()
print("fig_offensive_vs_defensive.png")


# duration
dur_bins = [0, 1, 2, 5, 10, 25, 50, 999]
dur_labels = ['1yr', '2yr', '3-5yr', '6-10yr', '11-25yr', '26-50yr', '>50yr']
decisive['dur_bin'] = pd.cut(decisive['duration'], bins=dur_bins, labels=dur_labels)

fig, ax = plt.subplots(figsize=(10, 5))
rates = []
ns = []
for label in dur_labels:
    sub = decisive[decisive['dur_bin'] == label]
    if len(sub) > 0:
        rates.append(sub['win'].mean())
    else:
        rates.append(0)
    ns.append(len(sub))

bars = ax.bar(dur_labels, rates, color='slategray')
for i in range(len(bars)):
    ax.text(bars[i].get_x() + bars[i].get_width()/2,
            bars[i].get_height() + 0.01,
            f'{rates[i]:.0%}\n(n={ns[i]})', ha='center')

ax.set_ylim(0, 1.0)
ax.set_title('Aggressor Win Rate by War Duration')
plt.tight_layout()
plt.savefig('../outputs/fig_duration_vs_winrate.png')
plt.close()
print("fig_duration_vs_winrate.png")


# colonial vs european r-squared
from sklearn.linear_model import LogisticRegression

def compute_r2(X, y):
    model = LogisticRegression(C=1e9, solver='lbfgs', max_iter=5000)
    model.fit(X, y)
    y_prob = np.clip(model.predict_proba(X)[:, 1], 1e-10, 1-1e-10)
    ll = np.sum(y * np.log(y_prob) + (1-y) * np.log(1-y_prob))
    p0 = y.mean()
    ll0 = np.sum(y * np.log(p0) + (1-y) * np.log(1-p0))
    return 1 - ll/ll0

core_vars = ['is_offensive', 'log_gdp_cap_ratio', 'is_home']
r2_values = {}
for etype, label in [('Colonial / Eastern', 'Colonial'), ('European', 'European')]:
    sub = decisive[decisive['enemy_type'] == etype].dropna(subset=['win'] + core_vars)
    if len(sub) > 20:
        r2_values[label] = compute_r2(sub[core_vars].values, sub['win'].values)

sub = decisive.dropna(subset=['win'] + core_vars)
if len(sub) > 20:
    r2_values['All Wars'] = compute_r2(sub[core_vars].values, sub['win'].values)

fig, ax = plt.subplots(figsize=(8, 5))
categories = [k for k in ['Colonial', 'European', 'All Wars'] if k in r2_values]
values = [r2_values[k] for k in categories]
bar_colors = {'Colonial': 'darkorange', 'European': 'steelblue', 'All Wars': 'slategray'}
bars = ax.bar(categories, values, color=[bar_colors[c] for c in categories])
for i in range(len(bars)):
    ax.text(bars[i].get_x() + bars[i].get_width()/2,
            bars[i].get_height() + 0.005,
            f'{values[i]:.1%}', ha='center')

ax.set_ylabel('Pseudo R-Squared')
ax.set_title('Model R-Squared: Colonial vs European')
ax.set_ylim(0, max(values) * 1.3)
plt.tight_layout()
plt.savefig('../outputs/fig_colonial_vs_european.png')
plt.close()
print("fig_colonial_vs_european.png")


# home vs away
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(etypes))
width = 0.35

for i, ha in enumerate(['Home', 'Away']):
    rates = []
    ns = []
    for etype in etypes:
        sub = decisive[(decisive['home_away'] == ha) & (decisive['enemy_type'] == etype)]
        if len(sub) > 0:
            rates.append(sub['win'].mean())
        else:
            rates.append(0)
        ns.append(len(sub))

    if ha == 'Home':
        color = 'forestgreen'
    else:
        color = 'firebrick'

    bars = ax.bar(x + i*width, rates, width, label=ha, color=color)
    for j in range(len(bars)):
        ax.text(bars[j].get_x() + bars[j].get_width()/2,
                bars[j].get_height() + 0.01,
                f'{rates[j]:.0%}\n(n={ns[j]})', ha='center')

ax.set_xticks(x + width/2)
ax.set_xticklabels(etypes)
ax.set_ylim(0, 1.0)
ax.set_title('Home vs Away Win Rate by Enemy Type')
ax.legend()
plt.tight_layout()
plt.savefig('../outputs/fig_home_away.png')
plt.close()
print("fig_home_away.png")


# wars per century
fig, ax = plt.subplots(figsize=(14, 5))
counts = df.groupby(['century', 'power']).size().unstack(fill_value=0)
counts = counts.reindex(columns=powers)
counts.plot(kind='bar', stacked=True, ax=ax,
            color=[power_colors[p] for p in powers])
ax.set_title('Wars per Century')
ax.set_xticklabels([f'{int(c)}th' for c in counts.index], rotation=0)
ax.legend(title='Power', fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig('../outputs/fig_wars_per_century.png')
plt.close()
print("fig_wars_per_century.png")
