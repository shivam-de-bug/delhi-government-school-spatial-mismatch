"""
spatial_regression.py
=====================
Phase 4: Spatial Regression Modeling — Delhi Educational Mismatch
Pipeline: Data Prep → OLS → LM Tests → SAR/SEM → LOCO → GWR
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize, TwoSlopeNorm
import matplotlib.cm as cm
from scipy import stats
import libpysal
import esda
import spreg
from libpysal.weights.spatial_lag import lag_spatial
import warnings
warnings.filterwarnings('ignore')

import sys
sys.stdout.reconfigure(encoding='utf-8')

CWD = r'c:\Users\Shivam\OneDrive\Desktop\antissse'

print("=" * 65)
print("PHASE 4: SPATIAL REGRESSION MODELING")
print("Delhi Educational Infrastructure Mismatch")
print("=" * 65)

# ============================================================
# STEP 1: DATA PREPARATION
# ============================================================
print("\n[STEP 1] Loading and Preparing Data...")

df = pd.read_csv(CWD + r'\ward_level_data_with_pop.csv')
wards_gdf = gpd.read_file(CWD + r'\delhi_274_wards_master.geojson')

# Drop overlapping cols from geojson before merge
for col in ['seat_capacity', 'total_enrolment', 'MI', 'PTR', 'area_sqkm', 'n_schools', 'zone', 'ward_name']:
    if col in wards_gdf.columns:
        wards_gdf = wards_gdf.drop(columns=[col])

wards_gdf = wards_gdf.merge(
    df[['unique_id', 'child_pop_6_18', 'seat_capacity', 'total_enrolment',
        'MI_demand', 'PTR', 'n_schools', 'area_sqkm', 'zone']],
    on='unique_id', how='left')

wards_gdf['MI_supply'] = wards_gdf['total_enrolment'] / wards_gdf['seat_capacity']
wards_gdf.replace([np.inf, -np.inf], np.nan, inplace=True)
wards_gdf = wards_gdf.to_crs(epsg=32643)

# Filter valid wards
valid = wards_gdf[wards_gdf['seat_capacity'] > 0].copy()
valid.reset_index(drop=True, inplace=True)
print(f"  Valid wards: {len(valid)}")

# Create log population density (controls for demand pressure)
valid['log_pop_density'] = np.log(valid['child_pop_6_18'] / valid['area_sqkm'])

# Zone Fixed Effects — Dummies to absorb WorldPop satellite bias
zone_dummies = pd.get_dummies(valid['zone'], prefix='zone', drop_first=True)
zone_dummies = zone_dummies.astype(float)
valid = pd.concat([valid.reset_index(drop=True), zone_dummies.reset_index(drop=True)], axis=1)

# All variables we need
VARLIST = ['MI_supply', 'log_pop_density', 'PTR', 'n_schools']
zone_cols = [c for c in valid.columns if c.startswith('zone_')]

# Drop rows with any NaN in key variables
valid.dropna(subset=VARLIST, inplace=True)
valid.reset_index(drop=True, inplace=True)
print(f"  After dropping NaNs: {len(valid)} wards")
print(f"  Zone dummies: {zone_cols}")

# Standardize continuous X variables (for comparable coefficients)
for col in ['log_pop_density', 'PTR', 'n_schools']:
    valid[col + '_z'] = stats.zscore(valid[col])
print("  Variables standardized (z-scores).")

# ============================================================
# BUILD SPATIAL WEIGHTS MATRIX (same as ESDA)
# ============================================================
print("\n[STEP 1b] Building Spatial Weights Matrix (300m fuzzy contiguity)...")
W = libpysal.weights.fuzzy_contiguity(valid, tolerance=300)
W.transform = 'r'
print(f"  Islands: {W.islands} | Avg neighbors: {np.mean([len(v) for v in W.neighbors.values()]):.2f}")

# ============================================================
# STEP 2: OLS BASELINE
# ============================================================
print("\n[STEP 2] Running OLS Baseline Model...")

Y = valid['MI_supply'].values
X_cols = ['log_pop_density_z', 'PTR_z', 'n_schools_z'] + zone_cols
X = valid[X_cols].values

# spreg OLS (gives us Moran's I on residuals automatically)
ols = spreg.OLS(
    Y.reshape(-1, 1),
    X,
    w=W,
    name_y='MI_supply',
    name_x=X_cols,
    spat_diag=True,
    name_ds='Delhi Wards'
)

print(f"\n  OLS R² = {ols.r2:.4f}")
print(f"  OLS Adj-R² = {ols.ar2:.4f}")
print(f"  OLS AIC = {ols.aic:.2f}")
print(f"  OLS Log-Likelihood = {ols.logll:.2f}")
print("\n  === OLS Coefficient Table ===")
print(f"  {'Variable':<25} {'Coeff':>10} {'Std Err':>10} {'t-stat':>10} {'p-value':>10}")
print("  " + "-" * 65)
for i, name in enumerate(['const'] + X_cols):
    coeff = ols.betas[i][0]
    se = ols.std_err[i]
    t = ols.t_stat[i][0]
    p = ols.t_stat[i][1]
    sig = '*' if p < 0.05 else ''
    print(f"  {name:<25} {coeff:>10.4f} {se:>10.4f} {t:>10.4f} {p:>10.4f} {sig}")

# Plot OLS Residuals Map + compute Moran's I manually on residuals
residuals_ols = ols.u.flatten()
valid['ols_residual'] = residuals_ols

# Manual Moran's I on residuals
moran_resid = esda.Moran(residuals_ols, W)
print(f"  Moran's I (residuals) = {moran_resid.I:.4f}, p = {moran_resid.p_sim:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(20, 9), facecolor='#f9f9f9')

# Map of residuals
divnorm = TwoSlopeNorm(vmin=residuals_ols.min(), vcenter=0, vmax=residuals_ols.max())
valid.plot(column='ols_residual', cmap='RdBu_r', norm=divnorm, edgecolor='white',
           linewidth=0.3, legend=True,
           legend_kwds={'label': 'OLS Residual', 'orientation': 'vertical'},
           ax=axes[0])
axes[0].set_title(f"OLS Residuals Map\nMoran's I={moran_resid.I:.3f}, p={moran_resid.p_sim:.3f}",
                  fontsize=13, fontweight='bold')
axes[0].axis('off')

# Moran scatter of OLS residuals
resid_std = (residuals_ols - residuals_ols.mean()) / residuals_ols.std()
resid_lag = lag_spatial(W, resid_std)
axes[1].scatter(resid_std, resid_lag, alpha=0.5, s=25, color='steelblue', edgecolors='grey', linewidth=0.3)
m, b = np.polyfit(resid_std, resid_lag, 1)
xline = np.linspace(resid_std.min(), resid_std.max(), 100)
axes[1].plot(xline, m * xline + b, 'r-', linewidth=2)
axes[1].axhline(0, color='grey', linestyle='--', lw=0.8)
axes[1].axvline(0, color='grey', linestyle='--', lw=0.8)
axes[1].set_title(f"Moran Scatterplot of OLS Residuals\nSlope = Moran's I = {moran_resid.I:.4f}",
                  fontsize=13, fontweight='bold')
axes[1].set_xlabel("Standardized OLS Residual", fontsize=11)
axes[1].set_ylabel("Spatial Lag of Residual", fontsize=11)

fig.suptitle("Figure 3: OLS Residual Diagnostics — Proving Spatial Autocorrelation",
             fontsize=15, fontweight='bold')
fig.tight_layout()
fig.savefig(CWD + r'\ols_residuals.png', dpi=300, bbox_inches='tight')
print("  Saved: ols_residuals.png")

# ============================================================
# STEP 3: LM DIAGNOSTICS
# ============================================================
print("\n[STEP 3] Lagrange Multiplier (LM) Diagnostics...")
print("\n  === LM Diagnostic Table ===")
print(f"  {'Test':<30} {'LM Stat':>10} {'p-value':>10} {'Decision':>10}")
print("  " + "-" * 62)

lm_tests = {
    'LM-Lag': (ols.lm_lag[0], ols.lm_lag[1]),
    'Robust LM-Lag': (ols.rlm_lag[0], ols.rlm_lag[1]),
    'LM-Error': (ols.lm_error[0], ols.lm_error[1]),
    'Robust LM-Error': (ols.rlm_error[0], ols.rlm_error[1]),
    'LM-SARMA': (ols.lm_sarma[0], ols.lm_sarma[1]),
}

for name, (stat, pval) in lm_tests.items():
    sig = '*** SIGNIFICANT' if pval < 0.05 else 'not significant'
    print(f"  {name:<30} {stat:>10.4f} {pval:>10.4f}  {sig}")

# Model selection logic
lag_sig = lm_tests['Robust LM-Lag'][1] < 0.05
err_sig = lm_tests['Robust LM-Error'][1] < 0.05
lag_stronger = lm_tests['Robust LM-Lag'][0] > lm_tests['Robust LM-Error'][0]

if lag_sig and err_sig:
    if lag_stronger:
        model_choice = 'SAR'
    else:
        model_choice = 'SEM'
elif lag_sig:
    model_choice = 'SAR'
elif err_sig:
    model_choice = 'SEM'
else:
    model_choice = 'OLS'  # No spatial model needed

print(f"\n  >>> MODEL SELECTED: {model_choice} <<<")

# LM bar chart
fig_lm, ax_lm = plt.subplots(figsize=(10, 6), facecolor='#f9f9f9')
test_names = list(lm_tests.keys())
stats_vals = [v[0] for v in lm_tests.values()]
p_vals = [v[1] for v in lm_tests.values()]
colors_lm = ['#d7191c' if p < 0.05 else '#bababa' for p in p_vals]
bars = ax_lm.barh(test_names, stats_vals, color=colors_lm, edgecolor='white', height=0.5)
ax_lm.axvline(3.84, color='navy', linestyle='--', linewidth=2, label='$\\chi^2_{0.05}$ = 3.84')
ax_lm.set_xlabel("LM Statistic", fontsize=12, fontweight='bold')
ax_lm.set_title("Figure 4: Lagrange Multiplier Diagnostics\n(Red = Significant at p<0.05)", fontsize=13, fontweight='bold')
for i, (bar, v) in enumerate(zip(bars, stats_vals)):
    ax_lm.text(v + 0.1, bar.get_y() + bar.get_height()/2,
               f"p={p_vals[i]:.3f}", va='center', fontsize=10)
ax_lm.legend(fontsize=11)
ax_lm.set_facecolor('#f5f5f5')
fig_lm.tight_layout()
fig_lm.savefig(CWD + r'\lm_diagnostics.png', dpi=300, bbox_inches='tight')
print("  Saved: lm_diagnostics.png")

# ============================================================
# STEP 4: SPATIAL REGRESSION (SAR or SEM)
# ============================================================
print(f"\n[STEP 4] Estimating {model_choice} Model via Maximum Likelihood...")

if model_choice == 'SAR':
    sp_model = spreg.ML_Lag(
        Y.reshape(-1, 1), X, w=W,
        name_y='MI_supply', name_x=X_cols, name_ds='Delhi Wards'
    )
    rho_val = sp_model.rho
    lambda_val = None
    print(f"  Spatial Lag Coefficient (ρ) = {rho_val:.4f}")
else:
    sp_model = spreg.ML_Error(
        Y.reshape(-1, 1), X, w=W,
        name_y='MI_supply', name_x=X_cols, name_ds='Delhi Wards'
    )
    rho_val = None
    lambda_val = sp_model.lam
    print(f"  Spatial Error Coefficient (λ) = {lambda_val:.4f}")

print(f"\n  {model_choice} R² = {sp_model.pr2:.4f}")
print(f"  {model_choice} AIC = {sp_model.aic:.2f}")
print(f"  {model_choice} Log-Likelihood = {sp_model.logll:.2f}")

print(f"\n  === {model_choice} Coefficient Table ===")
print(f"  {'Variable':<25} {'Coeff':>10} {'Std Err':>10} {'z-stat':>10} {'p-value':>10}")
print("  " + "-" * 65)
for i, name in enumerate(sp_model.name_x):
    coeff = sp_model.betas[i][0]
    se = sp_model.std_err[i]
    z = sp_model.z_stat[i][0]
    p = sp_model.z_stat[i][1]
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
    print(f"  {name:<25} {coeff:>10.4f} {se:>10.4f} {z:>10.4f} {p:>10.4f} {sig}")

# Model comparison table
print("\n  === MODEL COMPARISON: OLS vs " + model_choice + " ===")
print(f"  {'Metric':<20} {'OLS':>12} {model_choice:>12}")
print("  " + "-" * 44)
print(f"  {'R²':<20} {ols.r2:>12.4f} {sp_model.pr2:>12.4f}")
print(f"  {'AIC':<20} {ols.aic:>12.2f} {sp_model.aic:>12.2f}")
print(f"  {'Log-Likelihood':<20} {ols.logll:>12.2f} {sp_model.logll:>12.2f}")

# ============================================================
# STEP 5: LOCO DETRENDING (Leave-One-Covariate-Out)
# ============================================================
print("\n[STEP 5] LOCO Sensitivity Analysis (Leave-One-Covariate-Out)...")

continuous_vars = ['log_pop_density_z', 'PTR_z', 'n_schools_z']
loco_results = []

# Full model baseline (OLS for LOCO comparison speed)
full_ols = spreg.OLS(Y.reshape(-1, 1), X, w=W, name_y='MI_supply', name_x=X_cols)
full_r2 = full_ols.r2

for drop_var in continuous_vars:
    remaining = [c for c in X_cols if c != drop_var]
    X_loco = valid[remaining].values
    loco_ols = spreg.OLS(Y.reshape(-1, 1), X_loco, w=W, name_y='MI_supply', name_x=remaining)
    delta_r2 = full_r2 - loco_ols.r2
    loco_results.append({
        'dropped_var': drop_var.replace('_z', ''),
        'full_r2': round(full_r2, 4),
        'loco_r2': round(loco_ols.r2, 4),
        'delta_r2': round(delta_r2, 4),
        'aic_full': round(full_ols.aic, 2),
        'aic_loco': round(loco_ols.aic, 2),
    })

loco_df = pd.DataFrame(loco_results)
print("\n  === LOCO Detrending Table ===")
print(f"  Full Model R² = {full_r2:.4f}")
print()
print(f"  {'Variable Dropped':<25} {'LOCO R²':>10} {'ΔR² Lost':>12} {'AIC Full':>10} {'AIC LOCO':>10} {'Importance':>12}")
print("  " + "-" * 79)
for _, row in loco_df.iterrows():
    importance = 'HIGH' if row['delta_r2'] > 0.05 else ('MEDIUM' if row['delta_r2'] > 0.01 else 'LOW')
    print(f"  {row['dropped_var']:<25} {row['loco_r2']:>10.4f} {row['delta_r2']:>12.4f} {row['aic_full']:>10.2f} {row['aic_loco']:>10.2f} {importance:>12}")

# LOCO plot
fig_loco, ax_loco = plt.subplots(figsize=(10, 6), facecolor='#f9f9f9')
var_labels = loco_df['dropped_var'].tolist()
delta_vals = loco_df['delta_r2'].tolist()
colors_loco = ['#d7191c' if d > 0.05 else ('#fdae61' if d > 0.01 else '#bababa') for d in delta_vals]
bars_loco = ax_loco.bar(var_labels, delta_vals, color=colors_loco, edgecolor='white', width=0.5)
ax_loco.axhline(0.05, color='navy', linestyle='--', linewidth=1.5, label='High Importance Threshold (ΔR²=0.05)')
ax_loco.axhline(0.01, color='green', linestyle=':', linewidth=1.5, label='Medium Importance Threshold (ΔR²=0.01)')
ax_loco.set_ylabel("R² Lost When Dropped (ΔR²)", fontsize=12, fontweight='bold')
ax_loco.set_title("Figure 5: LOCO Sensitivity Analysis\nContribution of Each Variable to Explaining Mismatch",
                   fontsize=13, fontweight='bold')
for bar, val in zip(bars_loco, delta_vals):
    ax_loco.text(bar.get_x() + bar.get_width()/2, val + 0.001,
                 f"ΔR²={val:.4f}", ha='center', fontsize=11, fontweight='bold')
ax_loco.legend(fontsize=10)
ax_loco.set_facecolor('#f5f5f5')
fig_loco.tight_layout()
fig_loco.savefig(CWD + r'\loco_sensitivity.png', dpi=300, bbox_inches='tight')
print("\n  Saved: loco_sensitivity.png")

# ============================================================
# STEP 6: GWR (Geographically Weighted Regression)
# ============================================================
print("\n[STEP 6] Fitting Geographically Weighted Regression (GWR)...")

try:
    from mgwr.gwr import GWR
    from mgwr.sel_bw import Sel_BW

    # Prepare coords and data
    coords = np.array([[g.centroid.x, g.centroid.y] for g in valid.geometry])
    Y_gwr = valid['MI_supply'].values.reshape(-1, 1)
    X_gwr = valid[['log_pop_density_z', 'PTR_z', 'n_schools_z']].values

    # Select optimal bandwidth using AICc
    print("  Selecting optimal bandwidth (this may take 2-3 minutes)...")
    bw_selector = Sel_BW(coords, Y_gwr, X_gwr, kernel='bisquare', fixed=False)
    bw = bw_selector.search(criterion='AICc')
    print(f"  Optimal adaptive bandwidth (k neighbors): {int(bw)}")

    # Fit GWR
    gwr_model = GWR(coords, Y_gwr, X_gwr, bw=bw, kernel='bisquare', fixed=False)
    gwr_results = gwr_model.fit()

    print(f"\n  GWR AIC = {gwr_results.aic:.2f}")
    print(f"  GWR Mean Local R² = {gwr_results.localR2.mean():.4f}")
    print(f"  GWR Min Local R² = {gwr_results.localR2.min():.4f}")
    print(f"  GWR Max Local R² = {gwr_results.localR2.max():.4f}")

    # Store GWR results in geodataframe
    valid['gwr_local_r2'] = gwr_results.localR2.flatten()
    valid['gwr_b_log_pop'] = gwr_results.params[:, 0]
    valid['gwr_b_ptr'] = gwr_results.params[:, 1]
    valid['gwr_b_nschools'] = gwr_results.params[:, 2]
    valid['gwr_t_ptr'] = gwr_results.tvalues[:, 1]

    # Generate GWR multi-panel maps
    gwr_vars = [
        ('gwr_local_r2', 'Local R² (Model Fit)', 'YlOrRd', False),
        ('gwr_b_log_pop', 'Local β: Population Density\n(+ve = Demand drives crisis)', 'RdBu_r', True),
        ('gwr_b_ptr', 'Local β: PTR\n(+ve = Crowding drives crisis)', 'RdBu_r', True),
        ('gwr_b_nschools', 'Local β: N Schools\n(+ve = More schools = more mismatch?)', 'RdBu_r', True),
    ]

    fig_gwr, axes_gwr = plt.subplots(2, 2, figsize=(22, 22), facecolor='white')
    axes_gwr = axes_gwr.flatten()

    for i, (col, title, cmap, diverge) in enumerate(gwr_vars):
        vals = valid[col].values
        vmin, vmax = vals.min(), vals.max()
        if diverge and vmin < 0 < vmax:
            norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        else:
            norm = Normalize(vmin=vmin, vmax=vmax)
        valid.plot(column=col, cmap=cmap, norm=norm, edgecolor='white',
                   linewidth=0.3, legend=True, ax=axes_gwr[i])
        
        # Increase colorbar tick label sizes if possible (geopandas automatically creates it as the second axis in the figure if not specified, but it's attached to the main axis. A simple workaround is to find the most recently created axes which is the colorbar)
        cb_ax = fig_gwr.axes[-1]
        cb_ax.tick_params(labelsize=16)

        axes_gwr[i].set_title(f"Panel {chr(65+i)}: {title}", fontsize=24, fontweight='bold', pad=15)
        axes_gwr[i].axis('off')
        axes_gwr[i].set_facecolor('white')

    fig_gwr.suptitle(
        f"GWR Coefficient Maps — Delhi Educational Mismatch\n"
        f"Optimal Bandwidth: {int(bw)} neighbors | Kernel: Adaptive Bisquare | Mean Local R²: {gwr_results.localR2.mean():.3f}",
        fontsize=28, fontweight='bold', y=0.99
    )
    fig_gwr.tight_layout(rect=[0, 0, 1, 0.98])
    fig_gwr.savefig(CWD + r'\gwr_maps.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("  Saved: gwr_maps.png")

    # GWR Summary comparison
    print(f"\n  === FINAL MODEL COMPARISON ===")
    print(f"  {'Model':<15} {'R²/Mean R²':>15} {'AIC':>12}")
    print("  " + "-" * 44)
    print(f"  {'OLS':<15} {ols.r2:>15.4f} {ols.aic:>12.2f}")
    print(f"  {model_choice:<15} {sp_model.pr2:>15.4f} {sp_model.aic:>12.2f}")
    print(f"  {'GWR':<15} {gwr_results.localR2.mean():>15.4f} {gwr_results.aic:>12.2f}")

    GWR_RAN = True

except Exception as e:
    print(f"  GWR Error: {e}")
    print("  GWR skipped — will report results from SAR/SEM only.")
    GWR_RAN = False

# ============================================================
# SAVE RESULTS SUMMARY
# ============================================================
print("\n" + "=" * 65)
print("ALL PLOTS GENERATED:")
print("  - ols_residuals.png     : OLS Residual Map + Moran Scatter")
print("  - lm_diagnostics.png    : LM Test Bar Chart (SAR vs SEM choice)")
print("  - loco_sensitivity.png  : LOCO Detrending Bar Chart")
if GWR_RAN:
    print("  - gwr_maps.png          : GWR Coefficient Maps (4 panels)")
print("=" * 65)
print("\nDONE. Phase 4 Execution Complete.")
