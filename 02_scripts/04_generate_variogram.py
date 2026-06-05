import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load Data
print("Loading data...")
cwd = r'c:\Users\Shivam\OneDrive\Desktop\antissse'
wards_gdf = gpd.read_file(cwd + r'\delhi_274_wards_master.geojson')
df = pd.read_csv(cwd + r'\ward_level_data_with_pop.csv')

# Merge MI_supply
for col in ['seat_capacity', 'total_enrolment']:
    if col in wards_gdf.columns:
        wards_gdf = wards_gdf.drop(columns=[col])

wards_gdf = wards_gdf.merge(df[['unique_id', 'seat_capacity', 'total_enrolment']], on='unique_id', how='left')
wards_gdf['MI_supply'] = wards_gdf['total_enrolment'] / wards_gdf['seat_capacity']
wards_gdf.replace([np.inf, -np.inf], np.nan, inplace=True)

# 2. Filter Valid Wards and Project to Metric (UTM Zone 43N)
valid_wards = wards_gdf[wards_gdf['seat_capacity'] > 0].copy()
valid_wards.reset_index(drop=True, inplace=True)
valid_wards = valid_wards.to_crs(epsg=32643)

print(f"Valid wards: {len(valid_wards)}")

# 3. Extract Centroids & Values
coords = np.array([[g.centroid.x, g.centroid.y] for g in valid_wards.geometry])
z = valid_wards['MI_supply'].values
z = np.nan_to_num(z, nan=np.nanmedian(z))

# 4. Calculate Pairwise Distances and Variances
# Convert meters to kilometers
dist_matrix = squareform(pdist(coords)) / 1000.0  
var_matrix = 0.5 * squareform(pdist(z.reshape(-1, 1), metric='sqeuclidean'))

# Flatten upper triangle to avoid duplicates
indices = np.triu_indices_from(dist_matrix, k=1)
h_flat = dist_matrix[indices]
gamma_flat = var_matrix[indices]

# 5. Bin the distances (Empirical Variogram)
max_dist = np.max(h_flat)
# Typical rule of thumb: only trust variogram up to half the maximum distance
cutoff_dist = max_dist / 2.0 
num_bins = 20
bins = np.linspace(0, cutoff_dist, num_bins + 1)
bin_centers = (bins[:-1] + bins[1:]) / 2.0

empirical_gamma = np.zeros(num_bins)
for i in range(num_bins):
    mask = (h_flat >= bins[i]) & (h_flat < bins[i+1])
    if np.sum(mask) > 0:
        empirical_gamma[i] = np.mean(gamma_flat[mask])
    else:
        empirical_gamma[i] = np.nan

# Interpolate any NaNs if empty bins exist
valid_idx = ~np.isnan(empirical_gamma)
bin_centers = bin_centers[valid_idx]
empirical_gamma = empirical_gamma[valid_idx]

# 6. Find the Sill and Range (The "first dip" or plateau)
# We look for the first local maximum or where the curve flattens.
# A simple heuristic: find the first peak.
peaks = []
for i in range(1, len(empirical_gamma) - 1):
    if empirical_gamma[i] > empirical_gamma[i-1] and empirical_gamma[i] > empirical_gamma[i+1]:
        peaks.append(i)

if peaks:
    # First prominent peak
    sill_idx = peaks[0]
else:
    # If no peak, just take the max value in the first half
    sill_idx = np.argmax(empirical_gamma)

range_val = bin_centers[sill_idx]
sill_val = empirical_gamma[sill_idx]

print(f"Calculated Range: {range_val:.2f} km")
print(f"Calculated Sill: {sill_val:.4f}")

# 7. Generate Poster-Quality Variogram Cloud Plot
plt.figure(figsize=(12, 8), facecolor='#f9f9f9')

# Plot the Variogram Cloud (Raw Pairs)
plt.scatter(h_flat, gamma_flat, color='grey', alpha=0.15, s=10, label='Variogram Cloud (Raw Pairs)')

# Plot the Empirical Variogram (Binned Means)
plt.plot(bin_centers, empirical_gamma, 'ko-', linewidth=3, markersize=8, label='Empirical Semi-Variogram (Binned)')

# Mark the Sill and Range (Professor's Request)
plt.plot(range_val, sill_val, 'ro', markersize=12, label=f'Range & Sill Point', zorder=5)

# Drop lines to axes
plt.vlines(x=range_val, ymin=0, ymax=sill_val, colors='red', linestyles='dashed', linewidth=2)
plt.hlines(y=sill_val, xmin=0, xmax=range_val, colors='red', linestyles='dashed', linewidth=2)

# Annotations
plt.text(range_val + 0.5, 0.01, f'Range = {range_val:.1f} km', color='red', fontsize=14, fontweight='bold', va='bottom', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
plt.text(0.5, sill_val + 0.01, f'Sill = {sill_val:.3f}', color='red', fontsize=14, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.title("Variogram Cloud & Empirical Variogram of Educational Mismatch (MI_supply)\nIdentifying the Spatial Range of the Crisis", fontsize=16, fontweight='bold', pad=20)
plt.xlabel("Lag Distance (h) in Kilometers", fontsize=14, fontweight='bold')
plt.ylabel("Semi-Variance $\gamma(h)$", fontsize=14, fontweight='bold')

plt.grid(True, linestyle='--', alpha=0.6)
# Use a custom legend to ensure it's visible over the cloud
legend = plt.legend(fontsize=12, loc='upper right', framealpha=0.9)
legend.set_zorder(10)
plt.xlim(left=0, right=cutoff_dist) # Only show up to the cutoff distance to keep the plot focused
# Dynamically scale Y-axis to show the Sill clearly but not get distorted by massive outliers in the cloud
plt.ylim(bottom=0, top=np.percentile(gamma_flat[h_flat <= cutoff_dist], 95)) 

plt.tight_layout()
plt.savefig(cwd + r'\variogram_cloud.png', dpi=300, bbox_inches='tight')
print("Saved variogram_cloud.png")
