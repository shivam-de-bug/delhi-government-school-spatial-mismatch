"""
MISMATCH INDEX (MI) PIPELINE
=============================
As per research proposal:
  MI = enrolment / seat_capacity
  seat_capacity = total_classrooms * 40 (RTE norm)
  enrolment = total enrolment Classes 1-12 (boys + girls)

Also computes ward-level covariates:
  - Pupil-Teacher Ratio (PTR)
  - Number of schools per ward
  - Ward area (from GeoJSON)

Output: ward_level_data.csv + ward_level_data.geojson
"""
import pandas as pd
import geopandas as gpd
import numpy as np
import sys
sys.stdout.reconfigure(encoding='utf-8')

SEATS_PER_CLASSROOM = 40  # RTE Act upper bound norm

# ============================================================
# 1. LOAD ALL DATA
# ============================================================
print("Loading data...")
df = pd.read_csv('Delhi_govtsch_with_wards.csv')
enrol = pd.read_csv('Delhi_Enrolment_Data_Part_1.csv')
fac = pd.read_csv('Delhi_Facilities.csv')
tch = pd.read_csv('Delhi_Teachers_Data.csv')
gdf = gpd.read_file('delhi_274_wards_complete.geojson')

our_pcs = set(df['pseudocode'])
print("  Schools: %d" % len(df))

# ============================================================
# 2. COMPUTE SCHOOL-LEVEL ENROLMENT (Classes 1-12)
# ============================================================
print("\nComputing school-level enrolment...")

# item_group=1 has category-wise enrolment (Gen, SC, ST, OBC)
# Sum across categories to get total per school
enrol_cat = enrol[enrol['item_group'] == 1].copy()
class_cols = ['c%d_b' % i for i in range(1, 13)] + ['c%d_g' % i for i in range(1, 13)]

enrol_agg = enrol_cat.groupby('pseudocode')[class_cols].sum().reset_index()
enrol_agg['total_enrolment'] = enrol_agg[class_cols].sum(axis=1)

# Filter to our govt schools
enrol_govt = enrol_agg[enrol_agg['pseudocode'].isin(our_pcs)].copy()
print("  Schools with enrolment: %d" % len(enrol_govt))
print("  Total enrolment (Classes 1-12): %d" % enrol_govt['total_enrolment'].sum())
print("  Mean per school: %.0f, Median: %.0f" % (enrol_govt['total_enrolment'].mean(), enrol_govt['total_enrolment'].median()))

# ============================================================
# 3. COMPUTE SCHOOL-LEVEL SEAT CAPACITY
# ============================================================
print("\nComputing school-level seat capacity...")

fac_govt = fac[fac['pseudocode'].isin(our_pcs)][['pseudocode', 'total_class_rooms']].copy()
fac_govt['seat_capacity'] = fac_govt['total_class_rooms'] * SEATS_PER_CLASSROOM

print("  Schools with facility data: %d" % len(fac_govt))
print("  Total classrooms: %d" % fac_govt['total_class_rooms'].sum())
print("  Total seat capacity (@ %d seats/class): %d" % (SEATS_PER_CLASSROOM, fac_govt['seat_capacity'].sum()))

# ============================================================
# 4. COMPUTE SCHOOL-LEVEL PTR
# ============================================================
print("\nComputing school-level PTR...")

tch_govt = tch[tch['pseudocode'].isin(our_pcs)][['pseudocode', 'total_tch']].copy()
print("  Schools with teacher data: %d" % len(tch_govt))

# ============================================================
# 5. MERGE EVERYTHING AT SCHOOL LEVEL
# ============================================================
print("\nMerging school-level data...")

school = df[['pseudocode', 'district', 'ward_id_final', 'match_type', 
             'school_category', 'school_type']].copy()

school = school.merge(enrol_govt[['pseudocode', 'total_enrolment']], on='pseudocode', how='left')
school = school.merge(fac_govt[['pseudocode', 'total_class_rooms', 'seat_capacity']], on='pseudocode', how='left')
school = school.merge(tch_govt[['pseudocode', 'total_tch']], on='pseudocode', how='left')

# School-level MI
school['MI_school'] = school['total_enrolment'] / school['seat_capacity']
# School-level PTR
school['PTR_school'] = school['total_enrolment'] / school['total_tch'].replace(0, np.nan)

print("  Schools with all data: %d" % school.dropna(subset=['total_enrolment', 'seat_capacity', 'total_tch']).shape[0])

# Save school-level data
school.to_csv('school_level_data.csv', index=False)
print("  Saved: school_level_data.csv")

# ============================================================
# 6. AGGREGATE TO WARD LEVEL
# ============================================================
print("\nAggregating to ward level...")

# Only schools with ward mapping
ward_schools = school[school['ward_id_final'].notna()].copy()

ward_agg = ward_schools.groupby('ward_id_final').agg(
    n_schools=('pseudocode', 'count'),
    total_enrolment=('total_enrolment', 'sum'),
    total_classrooms=('total_class_rooms', 'sum'),
    total_seat_capacity=('seat_capacity', 'sum'),
    total_teachers=('total_tch', 'sum'),
).reset_index()

# Ward-level MI
ward_agg['MI'] = ward_agg['total_enrolment'] / ward_agg['total_seat_capacity']

# Ward-level PTR
ward_agg['PTR'] = ward_agg['total_enrolment'] / ward_agg['total_teachers'].replace(0, np.nan)

print("  Wards with data: %d" % len(ward_agg))
print()

# ============================================================
# 7. MERGE WITH GEOJSON (add ward area)
# ============================================================
print("Merging with GeoJSON...")

# Compute ward area in sq km
gdf_proj = gdf.to_crs('EPSG:32643')
gdf['area_sqkm'] = gdf_proj.geometry.area / 1e6

# Merge ward data to GeoJSON
gdf_merged = gdf.merge(ward_agg, left_on='unique_id', right_on='ward_id_final', how='left')

# Fill NaN for empty wards (9 wards with 0 schools)
gdf_merged['n_schools'] = gdf_merged['n_schools'].fillna(0).astype(int)
gdf_merged['total_enrolment'] = gdf_merged['total_enrolment'].fillna(0)
gdf_merged['total_seat_capacity'] = gdf_merged['total_seat_capacity'].fillna(0)
gdf_merged['total_classrooms'] = gdf_merged['total_classrooms'].fillna(0)
gdf_merged['total_teachers'] = gdf_merged['total_teachers'].fillna(0)
# MI and PTR stay NaN for empty wards (division by zero)

# Save
ward_data = gdf_merged.drop(columns=['geometry', 'ward_id_final'], errors='ignore')
ward_data.to_csv('ward_level_data.csv', index=False)

gdf_out = gdf_merged[['unique_id', 'zone', 'ward_type', 'ward_name', 
                        'n_schools', 'total_enrolment', 'total_classrooms',
                        'total_seat_capacity', 'total_teachers',
                        'MI', 'PTR', 'area_sqkm', 'geometry']]
gdf_out = gdf_out.drop(columns=['ward_id_final'], errors='ignore')
gdf_out.to_file('ward_level_data.geojson', driver='GeoJSON')

print("  Saved: ward_level_data.csv")
print("  Saved: ward_level_data.geojson")

# ============================================================
# 8. SUMMARY STATISTICS
# ============================================================
valid = ward_agg[ward_agg['MI'].notna() & np.isfinite(ward_agg['MI'])]

print()
print("=" * 70)
print("MISMATCH INDEX (MI) SUMMARY")
print("=" * 70)
print("  Formula: MI = Total Enrolment / Seat Capacity")
print("  Seat capacity = Classrooms × %d" % SEATS_PER_CLASSROOM)
print("  MI > 1: Overcrowded (demand > capacity)")
print("  MI < 1: Under-utilized (capacity > demand)")
print()
print("  Wards analyzed: %d" % len(valid))
print("  MI mean: %.3f" % valid['MI'].mean())
print("  MI median: %.3f" % valid['MI'].median())
print("  MI std: %.3f" % valid['MI'].std())
print("  MI min: %.3f (ward %s)" % (valid['MI'].min(), valid.loc[valid['MI'].idxmin(), 'ward_id_final']))
print("  MI max: %.3f (ward %s)" % (valid['MI'].max(), valid.loc[valid['MI'].idxmax(), 'ward_id_final']))
print()
print("  Overcrowded (MI > 1): %d wards (%.1f%%)" % ((valid['MI'] > 1).sum(), 100*(valid['MI'] > 1).mean()))
print("  Under-utilized (MI < 1): %d wards (%.1f%%)" % ((valid['MI'] < 1).sum(), 100*(valid['MI'] < 1).mean()))
print("  Near capacity (0.8 < MI < 1.2): %d wards" % ((valid['MI'] > 0.8) & (valid['MI'] < 1.2)).sum())
print()
print("  PTR mean: %.1f" % valid['PTR'].mean())
print("  PTR median: %.1f" % valid['PTR'].median())
print()
print("  City-level total:")
print("    Total enrolment: %d" % ward_agg['total_enrolment'].sum())
print("    Total capacity: %d" % ward_agg['total_seat_capacity'].sum())
print("    City-wide MI: %.3f" % (ward_agg['total_enrolment'].sum() / ward_agg['total_seat_capacity'].sum()))
