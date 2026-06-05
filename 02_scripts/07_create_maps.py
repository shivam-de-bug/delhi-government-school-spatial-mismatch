"""
4 Publication-Quality Maps for Delhi Ward Analysis
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

# Set font
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 10

# Load data
gdf = gpd.read_file('delhi_274_wards_master.geojson')
print("Loaded %d wards" % len(gdf))

# ============================================================
# MAP 1: All Delhi Ward Boundaries
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(12, 14))
ax.set_facecolor('#0a1628')
fig.patch.set_facecolor('#0a1628')

# Color by ward type
colors = {'MCD': '#4a90d9', 'NDMC': '#e8c547', 'CANTONMENT': '#e85d75'}
for wtype, color in colors.items():
    subset = gdf[gdf['ward_type'] == wtype]
    subset.plot(ax=ax, color=color, edgecolor='#1a2a44', linewidth=0.3, alpha=0.85)

# Legend
legend_elements = [
    Patch(facecolor='#4a90d9', edgecolor='#1a2a44', label='MCD Wards (272)'),
    Patch(facecolor='#e8c547', edgecolor='#1a2a44', label='NDMC (1 merged)'),
    Patch(facecolor='#e85d75', edgecolor='#1a2a44', label='Cantonment (1 merged)'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=11, 
          facecolor='#0f1f36', edgecolor='#2a4a6e', labelcolor='white',
          framealpha=0.9)

ax.set_title('Map 1: Delhi Ward Boundaries (274 Wards)', 
             fontsize=18, fontweight='bold', color='white', pad=15)
ax.set_axis_off()
plt.tight_layout()
plt.savefig('map1_ward_boundaries.png', dpi=200, bbox_inches='tight', 
            facecolor='#0a1628', edgecolor='none')
plt.close()
print("Saved: map1_ward_boundaries.png")

# ============================================================
# MAP 2: Wards WITH vs WITHOUT Schools
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(12, 14))
ax.set_facecolor('#0a1628')
fig.patch.set_facecolor('#0a1628')

has_schools = gdf[gdf['n_schools'] > 0]
no_schools = gdf[gdf['n_schools'] == 0]

has_schools.plot(ax=ax, color='#48c78e', edgecolor='#1a2a44', linewidth=0.3, alpha=0.8)
no_schools.plot(ax=ax, color='#ff3860', edgecolor='#ffdd57', linewidth=1.5, alpha=0.95)

# Label empty wards
for _, row in no_schools.iterrows():
    centroid = row.geometry.centroid
    ax.annotate(row['unique_id'], xy=(centroid.x, centroid.y),
                fontsize=6, color='white', fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#ff3860', 
                         edgecolor='white', alpha=0.9, linewidth=0.5))

legend_elements = [
    Patch(facecolor='#48c78e', edgecolor='#1a2a44', label='Has Schools (%d wards)' % len(has_schools)),
    Patch(facecolor='#ff3860', edgecolor='#ffdd57', label='No Schools (%d wards)' % len(no_schools)),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=11,
          facecolor='#0f1f36', edgecolor='#2a4a6e', labelcolor='white',
          framealpha=0.9)

ax.set_title('Map 2: Wards Without Any Government School', 
             fontsize=18, fontweight='bold', color='white', pad=15)
ax.set_axis_off()
plt.tight_layout()
plt.savefig('map2_empty_wards.png', dpi=200, bbox_inches='tight',
            facecolor='#0a1628', edgecolor='none')
plt.close()
print("Saved: map2_empty_wards.png")

# ============================================================
# MAP 3: School Frequency (Number of Schools per Ward)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(12, 14))
ax.set_facecolor('#0a1628')
fig.patch.set_facecolor('#0a1628')

# Custom colormap
cmap = plt.cm.YlOrRd
norm = mcolors.Normalize(vmin=0, vmax=gdf['n_schools'].quantile(0.95))

gdf.plot(ax=ax, column='n_schools', cmap=cmap, norm=norm,
         edgecolor='#1a2a44', linewidth=0.2, alpha=0.9,
         missing_kwds={'color': '#333333'})

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, fraction=0.025, pad=0.02, aspect=30)
cbar.set_label('Number of Schools', fontsize=12, color='white')
cbar.ax.yaxis.set_tick_params(color='white')
cbar.ax.tick_params(labelcolor='white')

# Annotate top 5 wards
top5 = gdf.nlargest(5, 'n_schools')
for _, row in top5.iterrows():
    centroid = row.geometry.centroid
    ax.annotate('%s\n(%d)' % (row['unique_id'], row['n_schools']),
                xy=(centroid.x, centroid.y),
                fontsize=6, color='white', fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#333', 
                         edgecolor='white', alpha=0.8, linewidth=0.5))

ax.set_title('Map 3: Number of Government Schools per Ward', 
             fontsize=18, fontweight='bold', color='white', pad=15)
ax.set_axis_off()
plt.tight_layout()
plt.savefig('map3_school_frequency.png', dpi=200, bbox_inches='tight',
            facecolor='#0a1628', edgecolor='none')
plt.close()
print("Saved: map3_school_frequency.png")

# ============================================================
# MAP 4: Mismatch Index (MI) Choropleth (POSTER VERSION)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 16))  # Slightly larger for poster
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# Custom diverging colormap: Blue (under-utilized) -> White (balanced) -> Red (overcrowded)
# MI < 1 = under-utilized (blue), MI = 1 = balanced (white), MI > 1 = overcrowded (red)
cmap_div = plt.cm.RdYlBu_r  # Red=high, Blue=low
norm_mi = mcolors.TwoSlopeNorm(vmin=0.3, vcenter=1.0, vmax=2.1)

# Plot wards with MI data
valid_mi = gdf[gdf['MI'].notna() & np.isfinite(gdf['MI'])].copy()
empty = gdf[gdf['MI'].isna() | ~np.isfinite(gdf['MI'])].copy()

valid_mi.plot(ax=ax, column='MI', cmap=cmap_div, norm=norm_mi,
              edgecolor='black', linewidth=0.5, alpha=0.9)
empty.plot(ax=ax, color='#e0e0e0', edgecolor='#666666', linewidth=0.5, alpha=0.7, hatch='///')

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap_div, norm=norm_mi)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, fraction=0.035, pad=0.03, aspect=25)
cbar.set_label('Mismatch Index (MI)', fontsize=18, fontweight='bold', color='black', labelpad=15)
cbar.ax.yaxis.set_tick_params(color='black', labelsize=14)
cbar.ax.tick_params(labelcolor='black')
# Add reference line at MI=1
cbar.ax.axhline(y=1.0, color='black', linewidth=3, linestyle='-')
cbar.ax.text(-0.5, 1.0, 'Balanced  \n(MI=1.0) $\\rightarrow$', fontsize=12, fontweight='bold', color='black', va='center', ha='right')

# Annotate crisis wards (MI > 1.5)
crisis = valid_mi[valid_mi['MI'] > 1.5]
for _, row in crisis.iterrows():
    centroid = row.geometry.centroid
    ax.annotate('%s\nMI=%.2f' % (row['unique_id'], row['MI']),
                xy=(centroid.x, centroid.y),
                fontsize=8, color='white', fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='darkred', 
                         edgecolor='black', alpha=0.9, linewidth=1))

# Legend for empty wards
legend_elements = [
    Patch(facecolor='darkred', edgecolor='black', label='Overcrowded (MI > 1)'),
    Patch(facecolor='lightyellow', edgecolor='black', label='Balanced (MI ≈ 1)'),
    Patch(facecolor='darkblue', edgecolor='black', label='Under-utilized (MI < 1)'),
    Patch(facecolor='#e0e0e0', edgecolor='#666666', label='No schools (9 wards)', hatch='///'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=16,
          facecolor='white', edgecolor='black', labelcolor='black',
          framealpha=1.0, shadow=True)

# Remove the title inside the image so you can use your poster's text boxes instead!
# Or if we want it, make it huge. Let's omit it so it blends purely as a map visual.
# ax.set_title(...)
ax.set_axis_off()
plt.tight_layout()
plt.savefig('map4_mismatch_index.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Saved: map4_mismatch_index.png")

print("\nAll 4 maps saved!")
