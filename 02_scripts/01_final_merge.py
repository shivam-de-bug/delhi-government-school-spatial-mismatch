"""
FINAL COMPLETE MERGE: All 2645 govt schools -> 272-ward HT Labs GeoJSON

Ward code mappings verified via:
- elections.in (2017 MCD ward lists)
- myneta.info  
- adrindia.org
- Cross-referencing with HT Labs 272 ward GeoJSON
"""
import pandas as pd
import geopandas as gpd
import re
import json

# ============================================================
# MASTER WARD CODE LOOKUP
# ============================================================
# Uncoded ward names -> 272-ward unique_id (zone+number)
# Sources: elections.in, myneta.info, HT Labs GeoJSON spatial verification

UNCODED_WARD_MAP = {
    # --- EDMC (East Delhi Municipal Corporation) ---
    'SHASTRI PARK':         '025E',   # Ward 025-E, EDMC
    'DALLUPURA':            '060E',   # Ward 060-E, EDMC (confirmed empty in coded data)
    'KONDLI':               '059E',   # Ward 059-E, EDMC (near Mayur Vihar)
    'DILSHAD COLONY':       '028E',   # Ward 028-E (same as coded 028-E Dilshad Colony)
    
    # --- NDMC (North Delhi Municipal Corporation) ---
    'TRI NAGAR':            '071N',   # Ward 071-N, NDMC (confirmed empty in coded data)
    'RAM PURA':             '070N',   # Ward 070-N, NDMC (confirmed empty in coded data)
    'NITHARI':              '040N',   # Ward 040-N, NDMC (confirmed empty in coded data)
    'MUNDKA':               '039N',   # Ward 039-N, NDMC (near Mundka, confirmed empty)
    'MUBARAK PUR DABAS':    '044N',   # Ward 044-N, NDMC (confirmed: elections.in + empty in coded)
    'RAMESH NAGAR':         '104N',   # Ward 104-N, NDMC (Naraina area)
    'ROHINI-F':             '057N',   # Ward 057-N (same as coded 057-N Rohini-F)
    
    # --- SDMC (South Delhi Municipal Corporation) ---
    'LADO SARAI':           '067S',   # Ward 067-S, SDMC (confirmed empty in coded data)
    'MEHRAULI':             '068S',   # Ward 068-S, SDMC (confirmed empty in coded data)
    'SAID-UL-AJAIB':        '072S',   # Ward 072-S, SDMC (Bhati/Chhatarpur area)
    'TUGHLAKABAD':          '083S',   # Ward 083-S, SDMC (Sangam Vihar-C area)
    'HARI NAGAR-A':         '010S',   # Ward 010-S, SDMC (confirmed empty in coded data)
    'SARITA VIHAR':         '101S',   # Ward 101-S, SDMC (confirmed empty in coded data)
    'MADANPUR KHADAR WEST': '104S',   # Ward 104-S, SDMC (confirmed empty in coded data)
    'SAINIK ENCLAVE':       '022S',   # Ward 022-S, SDMC (near Dwarka, confirmed empty)
    
    # --- CANTONMENT ---
    # Ward No. X -> These are Delhi Cantonment Board wards (NOT MCD)
    # They don't map to the 272-ward GeoJSON - handled separately
    'Ward No. 1': 'CANT_1',
    'Ward No. 2': 'CANT_2',
    'Ward No. 3': 'CANT_3',
    'Ward No. 4': 'CANT_4',
    'Ward No. 5': 'CANT_5',
    'Ward No. 7': 'CANT_7',
    
    # --- NDMC (New Delhi Municipal Council) ---
    'ward-1': 'NDMC_1',
}

# ============================================================
# LOAD DATA
# ============================================================
print("Loading data...")
df = pd.read_csv('Delhi_govtsch.csv')
gdf_ht = gpd.read_file('ht_labs_delhi_272_wards.geojson')
gdf_ht['unique_id'] = gdf_ht.apply(lambda r: '%03d%s' % (r['id'], r['zone']), axis=1)

print("Total govt schools: %d" % len(df))

# ============================================================
# ASSIGN WARD IDs TO ALL SCHOOLS
# ============================================================
def assign_ward_id(row):
    """Assign a ward unique_id to each school"""
    ward_name = row['lgd_ward_name']
    
    # NaN ward name
    if pd.isna(ward_name):
        return None, 'NO_WARD_NAME'
    
    ward_name = str(ward_name).strip()
    
    # Try coded pattern: NNN-Z Name
    m = re.match(r'(\d{3})-([NESW])\s*(.*)', ward_name)
    if m:
        uid = '%03d%s' % (int(m.group(1)), m.group(2))
        return uid, 'CODED'
    
    # Try uncoded lookup
    if ward_name in UNCODED_WARD_MAP:
        uid = UNCODED_WARD_MAP[ward_name]
        return uid, 'UNCODED_MAPPED'
    
    return None, 'UNKNOWN'

results = df.apply(assign_ward_id, axis=1, result_type='expand')
df['ward_id'] = results[0]
df['match_type'] = results[1]

# ============================================================
# REPORT
# ============================================================
print()
print("=" * 70)
print("ASSIGNMENT RESULTS")
print("=" * 70)
print(df['match_type'].value_counts().to_string())
print()

# Split by MCD vs special
mcd_schools = df[df['ward_id'].str.match(r'^\d{3}[NESW]$', na=False)]
cant_schools = df[df['ward_id'].str.startswith('CANT', na=False)]
ndmc_schools = df[df['ward_id'].str.startswith('NDMC', na=False)]
no_ward = df[df['ward_id'].isna()]

print("MCD schools (mapped to 272-ward GeoJSON): %d (%.1f%%)" 
      % (len(mcd_schools), 100*len(mcd_schools)/len(df)))
print("Cantonment schools: %d" % len(cant_schools))
print("NDMC (New Delhi) schools: %d" % len(ndmc_schools))
print("No ward name: %d" % len(no_ward))
print()

# Q3: How many wards without schools?
mcd_ward_ids_with_schools = set(mcd_schools['ward_id'].dropna().unique())
all_272_ids = set(gdf_ht['unique_id'])
wards_without_schools = all_272_ids - mcd_ward_ids_with_schools
wards_with_schools = all_272_ids & mcd_ward_ids_with_schools

print("272 HT Labs wards WITH govt schools: %d" % len(wards_with_schools))
print("272 HT Labs wards WITHOUT govt schools: %d" % len(wards_without_schools))
if wards_without_schools:
    print("Empty wards:")
    for uid in sorted(wards_without_schools):
        print("  %s" % uid)
print()

# Schools per ward
ward_counts = mcd_schools.groupby('ward_id').size()
print("Schools per ward: min=%d, max=%d, mean=%.1f, median=%.0f" 
      % (ward_counts.min(), ward_counts.max(), ward_counts.mean(), ward_counts.median()))

# Unknown schools?
unknown = df[df['match_type'] == 'UNKNOWN']
if len(unknown) > 0:
    print()
    print("UNKNOWN (not matched): %d schools" % len(unknown))
    print(unknown['lgd_ward_name'].value_counts().to_string())

# ============================================================  
# CREATE ENHANCED GEOJSON WITH SCHOOL COUNTS + LGD NAMES
# ============================================================
with open('ht_labs_delhi_272_wards.geojson') as f:
    ht_data = json.load(f)

# Build lookup: uid -> list of LGD ward names + school count
uid_info = {}
for uid in all_272_ids:
    ward_schools = mcd_schools[mcd_schools['ward_id'] == uid]
    lgd_names = list(ward_schools['lgd_ward_name'].dropna().unique())
    uid_info[uid] = {
        'school_count': len(ward_schools),
        'lgd_ward_names': '; '.join(lgd_names) if lgd_names else ''
    }

for feat in ht_data['features']:
    uid = feat['properties']['unique']
    info = uid_info.get(uid, {'school_count': 0, 'lgd_ward_names': ''})
    feat['properties']['school_count'] = info['school_count']
    feat['properties']['lgd_ward_names'] = info['lgd_ward_names']
    # Use the ward name from LGD (extract from first coded entry)
    names = info['lgd_ward_names']
    if names:
        first = names.split(';')[0].strip()
        m = re.match(r'\d{3}-[NESW]\s+(.*)', first)
        feat['properties']['ward_name'] = m.group(1) if m else first
    else:
        feat['properties']['ward_name'] = ''

with open('delhi_272_wards_final.geojson', 'w') as f:
    json.dump(ht_data, f)
print()
print("Saved: delhi_272_wards_final.geojson")

# ============================================================
# SAVE SCHOOL DATA WITH WARD IDs
# ============================================================
df.to_csv('Delhi_govtsch_with_wards.csv', index=False)
print("Saved: Delhi_govtsch_with_wards.csv")

# ============================================================
# SUMMARY TABLE
# ============================================================
print()
print("=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print("Total govt schools:           %d" % len(df))
print("Mapped to 272-ward GeoJSON:   %d (%.1f%%)" % (len(mcd_schools), 100*len(mcd_schools)/len(df)))
print("Cantonment Board:             %d (%.1f%%)" % (len(cant_schools), 100*len(cant_schools)/len(df)))
print("NDMC (New Delhi):             %d (%.1f%%)" % (len(ndmc_schools), 100*len(ndmc_schools)/len(df)))
print("No ward info:                 %d (%.1f%%)" % (len(no_ward), 100*len(no_ward)/len(df)))
total_mapped = len(mcd_schools) + len(cant_schools) + len(ndmc_schools)
print("TOTAL MAPPED:                 %d (%.1f%%)" % (total_mapped, 100*total_mapped/len(df)))
print()
print("272 wards with schools:       %d / 272" % len(wards_with_schools))
print("272 wards empty:              %d / 272" % len(wards_without_schools))
