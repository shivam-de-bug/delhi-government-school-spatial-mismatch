import pandas as pd
import geopandas as gpd
import libpysal, esda
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from libpysal.weights.spatial_lag import lag_spatial
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# STEP 1: LOAD DATA
# ============================================================
df = pd.read_csv('ward_level_data_with_pop.csv')
wards_gdf = gpd.read_file('delhi_274_wards_master.geojson')

# Drop overlapping columns from GeoJSON to do a clean merge
for col in ['child_pop_6_18', 'seat_capacity', 'MI_demand']:
    if col in wards_gdf.columns:
        wards_gdf = wards_gdf.drop(columns=[col])

wards_gdf = wards_gdf.merge(
    df[['unique_id', 'child_pop_6_18', 'seat_capacity', 'MI_demand']],
    on='unique_id', how='left')

wards_gdf['MI_supply'] = wards_gdf['total_enrolment'] / wards_gdf['seat_capacity']
wards_gdf.replace([np.inf, -np.inf], np.nan, inplace=True)
wards_gdf = wards_gdf.to_crs(epsg=32643)

# ============================================================
# STEP 2: FILTER TO VALID WARDS (N=265)
# ============================================================
valid_wards = wards_gdf[wards_gdf['seat_capacity'] > 0].copy()
valid_wards.reset_index(drop=True, inplace=True)
print(f"Valid wards (seat_capacity > 0): {len(valid_wards)}")

# ============================================================
# STEP 3: BUILD SPATIAL WEIGHTS MATRIX
# Use 300m buffer to guarantee zero islands while preserving contiguity logic
# ============================================================
W = libpysal.weights.fuzzy_contiguity(valid_wards, tolerance=300)
W.transform = 'r'
print(f"W built with 300m tolerance. Islands: {W.islands}")
print(f"Avg neighbors: {round(np.mean([len(v) for v in W.neighbors.values()]), 2)}")

# ============================================================
# STEP 4: GLOBAL MORAN's I FOR ALL VARIABLES
# ============================================================
variables = {
    'child_pop_6_18': 'Child Population (Ages 6-18)',
    'seat_capacity': 'Government School Seat Capacity',
    'MI_supply': 'MI_supply: Enrolment / Seat Capacity',
    'MI_demand': 'MI_demand: Child Pop / Seat Capacity (WorldPop)'
}

global_results = {}
print("\n=== GLOBAL MORAN'S I (N=265, 150m Fuzzy Contiguity, Row-Std) ===")
for var, label in variables.items():
    y = valid_wards[var].values.astype(float)
    y = np.nan_to_num(y, nan=np.nanmedian(y))
    moran = esda.Moran(y, W, permutations=999)
    global_results[var] = {'I': moran.I, 'EI': moran.EI, 'p': moran.p_sim, 'z': moran.z_sim}
    print(f"\n{label}:")
    print(f"   Moran's I = {moran.I:.4f}  |  E[I] = {moran.EI:.4f}  |  z = {moran.z_sim:.4f}  |  p = {moran.p_sim:.4f}")

# ============================================================
# STEP 5: LISA FOR ALL VARIABLES
# ============================================================
lisa_results = {}
for var in variables:
    y = valid_wards[var].values.astype(float)
    y = np.nan_to_num(y, nan=np.nanmedian(y))
    lisa = esda.Moran_Local(y, W)
    sig = lisa.p_sim < 0.05
    hotspots = lisa.q * sig
    valid_wards[f'{var}_lisa'] = hotspots
    lisa_results[var] = hotspots

print("\n=== LISA CLUSTER COUNTS (MI_supply, p<0.05) ===")
label_map = {0: 'Not Significant', 1: 'High-High', 2: 'Low-High', 3: 'Low-Low', 4: 'High-Low'}
valid_wards['MI_supply_label'] = valid_wards['MI_supply_lisa'].map(label_map)
print(valid_wards['MI_supply_label'].value_counts().to_string())

print("\n--- HIGH-HIGH WARDS (Crisis) ---")
hh = valid_wards[valid_wards['MI_supply_lisa']==1][['ward_name','unique_id','zone','MI_supply','total_enrolment','seat_capacity']].sort_values('MI_supply', ascending=False)
print(hh.to_string(index=False))

print("\n--- LOW-LOW WARDS (Surplus) ---")
ll = valid_wards[valid_wards['MI_supply_lisa']==3][['ward_name','unique_id','zone','MI_supply','total_enrolment','seat_capacity']].sort_values('MI_supply')
print(ll.to_string(index=False))

print("\n--- HIGH-LOW WARDS (Crisis Outlier in Surplus Area) ---")
hl = valid_wards[valid_wards['MI_supply_lisa']==4][['ward_name','unique_id','zone','MI_supply']]
print(hl.to_string(index=False))

print("\n--- LOW-HIGH WARDS (Surplus Outlier in Crisis Area) ---")
lh = valid_wards[valid_wards['MI_supply_lisa']==2][['ward_name','unique_id','zone','MI_supply']]
print(lh.to_string(index=False))

# ============================================================
# STEP 6: GENERATE HIGH-RES VISUALIZATIONS
# ============================================================
color_map = {0: '#d3d3d3', 1: '#d7191c', 2: '#abd9e9', 3: '#2c7bb6', 4: '#fdae61'}
label_map_plot = {0: 'Not Significant', 1: 'High-High (Crisis)', 2: 'Low-High', 3: 'Low-Low (Surplus)', 4: 'High-Low'}
handles = [mpatches.Patch(color=color_map[k], label=label_map_plot[k]) for k in [1, 2, 3, 4, 0]]

fig_lisa, axs_lisa = plt.subplots(2, 2, figsize=(22, 22), facecolor='white')
axs_lisa = axs_lisa.flatten()

var_titles = {
    'child_pop_6_18': 'Panel A: Child Population (Age 6-18)',
    'seat_capacity': 'Panel B: Seat Capacity (Government Schools)',
    'MI_supply': 'Panel C: MI Supply (Enrolment / Capacity)',
    'MI_demand': 'Panel D: MI Demand (WorldPop / Capacity)'
}

for i, (var, title) in enumerate(var_titles.items()):
    colors = [color_map[c] for c in valid_wards[f'{var}_lisa']]
    valid_wards.plot(color=colors, edgecolor='white', linewidth=0.3, ax=axs_lisa[i])
    gr = global_results[var]
    subtitle = f"Global Moran's I = {gr['I']:.4f}  |  p = {gr['p']:.3f}"
    axs_lisa[i].set_title(f"{title}\n{subtitle}", fontsize=24, fontweight='bold', pad=15)
    axs_lisa[i].axis('off')
    axs_lisa[i].set_facecolor('white')

fig_lisa.legend(handles=handles, loc='lower center', ncol=5, fontsize=22, frameon=True, bbox_to_anchor=(0.5, 0.02), facecolor='white', edgecolor='black')
fig_lisa.suptitle("LISA Cluster Maps — Delhi Educational Mismatch (N=265 Wards)\nSpatial Weights: 300m Fuzzy Contiguity, Row-Standardized | Significance: p < 0.05 (999 permutations)", fontsize=28, fontweight='bold', y=0.98)
fig_lisa.tight_layout(rect=[0, 0.06, 1, 0.97])
fig_lisa.savefig('multivariate_lisa.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\nSaved: multivariate_lisa.png")

# Moran Scatterplots (Poster Sized)
fig_moran, axs_moran = plt.subplots(2, 2, figsize=(22, 22), facecolor='#f5f5f5')
axs_moran = axs_moran.flatten()

for i, (var, title) in enumerate(var_titles.items()):
    y = valid_wards[var].values.astype(float)
    y = np.nan_to_num(y, nan=np.nanmedian(y))
    y_std = (y - y.mean()) / y.std()
    ylag = lag_spatial(W, y_std)
    
    gr = global_results[var]
    # color points by cluster
    cluster_colors = [color_map[c] for c in valid_wards[f'{var}_lisa']]
    axs_moran[i].scatter(y_std, ylag, c=cluster_colors, alpha=0.7, s=30, edgecolors='grey', linewidth=0.3)
    # regression line
    m, b = np.polyfit(y_std, ylag, 1)
    x_line = np.linspace(y_std.min(), y_std.max(), 100)
    axs_moran[i].plot(x_line, m*x_line + b, 'k-', linewidth=2)
    axs_moran[i].axhline(0, color='grey', linestyle='--', linewidth=0.8)
    axs_moran[i].axvline(0, color='grey', linestyle='--', linewidth=0.8)
    
    subtitle = f"I = {gr['I']:.4f}  |  p = {gr['p']:.3f}  |  (slope = Moran's I)"
    axs_moran[i].set_title(f"{title}\n{subtitle}", fontsize=22, fontweight='bold', pad=15)
    axs_moran[i].set_xlabel('Standardized Value (z-score)', fontsize=18, fontweight='bold', labelpad=10)
    axs_moran[i].set_ylabel('Spatial Lag (Neighbors avg.)', fontsize=18, fontweight='bold', labelpad=10)
    axs_moran[i].tick_params(axis='both', which='major', labelsize=14)
    
    # Quadrant labels
    x_max, y_max = axs_moran[i].get_xlim()[1]*0.7, axs_moran[i].get_ylim()[1]*0.8
    x_min, y_min = axs_moran[i].get_xlim()[0]*0.7, axs_moran[i].get_ylim()[0]*0.8
    axs_moran[i].text(x_max, y_max, 'HH', color='#d7191c', fontsize=26, fontweight='bold', ha='center')
    axs_moran[i].text(x_min, y_max, 'LH', color='#abd9e9', fontsize=26, fontweight='bold', ha='center')
    axs_moran[i].text(x_min, y_min, 'LL', color='#2c7bb6', fontsize=26, fontweight='bold', ha='center')
    axs_moran[i].text(x_max, y_min, 'HL', color='#fdae61', fontsize=26, fontweight='bold', ha='center')
    axs_moran[i].set_facecolor('#f9f9f9')

fig_moran.suptitle("Moran's Scatterplots — Delhi Educational Mismatch (N=265 Wards)\nX-axis: Standardized Variable | Y-axis: Spatial Lag | Slope = Moran's I", fontsize=28, fontweight='bold', y=0.98)
fig_moran.tight_layout(rect=[0, 0, 1, 0.97])
fig_moran.savefig('multivariate_moran.png', dpi=300, bbox_inches='tight')
print("Saved: multivariate_moran.png")
print("\nDONE.")
