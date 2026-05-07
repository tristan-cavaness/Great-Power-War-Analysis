# 04_regression.py
# logistic regression - which variables predict winning a war?

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from scipy import stats
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'wars_merged.csv'))
decisive = df[df['outcome'].isin(['Won', 'Lost'])].copy()
print(f"{len(decisive)} decisive wars\n")

out = open(os.path.join(OUTPUT_DIR, 'model_summary.txt'), 'w')

def log(text):
    print(text)
    out.write(text + '\n')


def fit_logit(X, y):
    """
    fit logistic regression and compute p-values.
    sklearn doesn't give p-values by default, so we calculate them
    from the standard errors using the Wald test (coef / std error).
    """
    model = LogisticRegression(C=1e9, solver='lbfgs', max_iter=5000)
    model.fit(X, y)
    y_prob = np.clip(model.predict_proba(X)[:, 1], 1e-10, 1-1e-10)

    # get standard errors from the hessian matrix
    W = y_prob * (1 - y_prob)
    X_aug = np.column_stack([np.ones(len(X)), X])
    try:
        cov = np.linalg.inv(X_aug.T @ np.diag(W) @ X_aug)
        se = np.sqrt(np.diag(cov))
    except:
        se = np.full(X_aug.shape[1], np.nan)

    coefs = np.concatenate([model.intercept_, model.coef_[0]])
    pvals = 2 * (1 - stats.norm.cdf(np.abs(coefs / se)))

    # McFadden pseudo r-squared
    ll = np.sum(y * np.log(y_prob) + (1-y) * np.log(1-y_prob))
    p0 = y.mean()
    ll0 = np.sum(y * np.log(p0) + (1-y) * np.log(1-p0))
    r2 = 1 - ll/ll0

    return coefs, pvals, se, r2


def sig_stars(p):
    if p < 0.001: return '***'
    if p < 0.01: return '**'
    if p < 0.1: return '*'
    return ''


# test each variable on its own
log("INDIVIDUAL PREDICTOR SCREENING\n")

test_vars = [
    ('log_gdp_cap_ratio',  'GDP/cap ratio (log)'),
    ('log_total_gdp_ratio', 'Total GDP ratio (log)'),
    ('log_pop_ratio',       'Population ratio (log)'),
    ('is_offensive',        'Offensive posture'),
    ('is_home',             'Home advantage'),
    ('log_distance',        'Distance (log)'),
    ('log_urban_pct_ratio', 'Urban % ratio (log)'),
    ('log_builtup_ratio',   'Built-up area ratio (log)'),
    ('log_grazing_ratio',   'Grazing land ratio (log)'),
    ('log_cropland_ratio',  'Cropland ratio (log)'),
    ('log_urban_pop_ratio', 'Urban pop ratio (log)'),
]

indiv = []
for var, desc in test_vars:
    if var not in decisive.columns:
        continue
    sub = decisive.dropna(subset=['win', var])
    if len(sub) < 20:
        continue

    coefs, pvals, se, r2 = fit_logit(sub[[var]].values, sub['win'].values)
    p = round(pvals[1], 4)
    c = round(coefs[1], 4)

    log(f"  {desc}: coef={c}, p={p} {sig_stars(p)}, R2={round(r2,4)}, n={len(sub)}")
    indiv.append({'variable': var, 'description': desc, 'coef': c,
                  'p_value': p, 'r2': round(r2, 4), 'n': len(sub)})

pd.DataFrame(indiv).to_csv('../outputs/regression_individual.csv', index=False)


# core 3-variable model
log("\nCORE MODEL: Offensive + GDP/cap + Home\n")

core_vars = ['is_offensive', 'log_gdp_cap_ratio', 'is_home']
sub = decisive.dropna(subset=['win'] + core_vars)
X = sub[core_vars].values
y = sub['win'].values

coefs, pvals, se, r2 = fit_logit(X, y)
log(f"N = {len(y)}, R2 = {round(r2, 4)}\n")

for i in range(len(core_vars)):
    v = core_vars[i]
    c = round(coefs[i+1], 4)
    p = round(pvals[i+1], 4)
    s = round(se[i+1], 4)
    log(f"  {v}: coef={c}, se={s}, p={p} {sig_stars(p)}")

# marginal effects - how much does each variable shift win probability
log("\nMarginal effects at mean:")
Xm = X.mean(axis=0)
prob_at_mean = 1 / (1 + np.exp(-(coefs[0] + Xm @ coefs[1:])))
for i in range(len(core_vars)):
    me = coefs[i+1] * prob_at_mean * (1 - prob_at_mean)
    log(f"  {core_vars[i]}: {round(me, 4)} ({round(me*100, 1)}%)")


# does adding population help the model?
log("\nADDING POPULATION RATIO")
ext = core_vars + ['log_pop_ratio']
sub2 = decisive.dropna(subset=['win'] + ext)
_, pvals2, _, r2_ext = fit_logit(sub2[ext].values, sub2['win'].values)
log(f"  Core R2: {round(r2, 4)}")
log(f"  +Pop R2: {round(r2_ext, 4)}")
log(f"  Delta:   {round(r2_ext - r2, 4)}")
log(f"  Pop p:   {round(pvals2[4], 4)}")


# colonial vs european wars
log("\nCOLONIAL vs EUROPEAN")

for etype in ['Colonial / Eastern', 'European']:
    if 'Colonial' in etype:
        label = 'Colonial'
    else:
        label = 'European'

    s = decisive[decisive['enemy_type'] == etype].dropna(subset=['win'] + core_vars)
    if len(s) < 20:
        continue

    c, p, _, r = fit_logit(s[core_vars].values, s['win'].values)
    log(f"\n  {label} (n={len(s)}, R2={round(r, 4)})")
    for i in range(len(core_vars)):
        log(f"    {core_vars[i]}: coef={round(c[i+1],4)}, p={round(p[i+1],4)} {sig_stars(p[i+1])}")

out.close()
