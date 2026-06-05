# Does Delhi Build Schools Where Children Live?
### Spatial Mismatch Between Government School Capacity and Child Population Across Delhi's MCD Wards


📄 **[ Research Poster](05_poster/poster_A1.pdf)** | 📋 **[Project Initiation Report](05_poster/Project_Initiation_Report.docx)** | ⚠️ **[Limitations & Caveats](05_poster/LIMITATIONS.md)**

---

## 🗺️ Overview

Delhi's government school system contains approximately **2,645 schools** with a combined seat capacity of **~1.47 million**, yet only **~681,000 students** are enrolled — an average Mismatch Index (MI) of 0.46. On the surface, this suggests a city-wide surplus. However, this aggregate average conceals extreme ward-level variation.

This study demonstrates that the problem is not the *total* number of government school seats in Delhi — it is *where* those seats are located. Using ward-level spatial econometric methods applied to UDISE+ 2023–24 data, we provide the first empirical evidence of **geographic clustering of government school capacity mismatch** in an Indian megacity, and the first quantification of its **cross-ward spillover effect**.

### The Three Core Findings

| # | Finding | Statistic |
|---|---|---|
| 1 | **Spatial Clustering is Statistically Confirmed** | Global Moran's I = 0.3307, p = 0.001 |
| 2 | **Teacher Shortage (PTR) is the Dominant Driver** | PTR Total Impact = +0.1231 (37.2% amplified by spatial multiplier) |
| 3 | **North Delhi's Crisis is Invisible to Satellite Data** | WorldPop undercounts children by 35–65% in informal settlements |

---

## 📐 Research Objectives

**O1:** Test whether government school capacity mismatch (MI) is spatially clustered across Delhi's 274 wards using Global Moran's I.

**O2:** Identify and map specific crisis-cluster wards using Local Moran's I (LISA) at p < 0.05.

**O3:** Estimate spatial dependence and ward-level predictors using a Spatial Autoregressive (SAR) model selected by Lagrange Multiplier diagnostic tests, and characterise geographic heterogeneity using Geographically Weighted Regression (GWR).

---

## 📁 Repository Structure

```
delhi-school-spatial-mismatch/
│
├── README.md                          ← You are here
│
├── 01_data/
│   ├── raw/                           ← Original UDISE+ 2023-24 CSVs (do not edit)
│   ├── spatial/                       ← Ward boundary GeoJSON + WorldPop population
│   └── processed/                     ← Analysis-ready merged datasets
│
├── 02_scripts/                        ← Run these IN ORDER (01 → 07)
│   ├── 01_final_merge.py              ← Merge UDISE school records to ward boundaries
│   ├── 02_compute_MI.py               ← Calculate Mismatch Index (MI = Enrolment / Capacity)
│   ├── 03_run_esda_final.py           ← Global Moran's I + LISA cluster maps
│   ├── 04_generate_variogram.py       ← Empirical variogram (spatial range = 4.15 km)
│   ├── 05_spatial_regression.py       ← OLS → LM Tests → SAR → GWR pipeline
│   ├── 06_depth_analysis.py           ← SAR Impacts Decomposition + SDM robustness
│   └── 07_create_maps.py              ← Final cartographic maps for the poster
│
├── 03_outputs/
│   ├── maps/                          ← Ward boundary, school density, MI choropleth maps
│   ├── esda/                          ← Moran scatter plots, LISA cluster maps, variogram
│   └── regression/                    ← LM diagnostics, OLS residuals, GWR maps, impacts
│
├── 04_reports/
│   ├── 01_missing_data_analysis.md       ← 1. Data quality audit: unmapped schools & empty wards
│   ├── 02_multivariate_esda_report.md    ← 2. Multivariate ESDA findings
│   ├── 03_spatial_regression_report.md   ← 3. SAR & GWR analysis
│   └── 04_depth_report.md                ← 4. Impact decomposition, SDM, robustness
│
└── 05_poster/
    ├──  Poster_Design_Layout.md
    ├──  Does_Delhi_Build_Schools_Where_Children_Live.md
    ├──  LIMITATIONS.md
    ├──  poster_A1.pdf
    ├──  References.pdf
    ├──  Limitations_and_Caveats.pdf
    └──  Project_Initiation_Report.docx
```

---

## 🔢 How to Replicate (Step-by-Step)

### 1. Prerequisites

```bash
pip install geopandas libpysal esda spreg mgwr matplotlib seaborn numpy pandas
```

> **Python version:** 3.10 or above recommended.

### 2. Run the Pipeline in Order

```bash
# Step 1 — Merge school records to ward IDs
python 02_scripts/01_final_merge.py

# Step 2 — Compute the Mismatch Index at the ward level
python 02_scripts/02_compute_MI.py

# Step 3 — Run exploratory spatial data analysis (Moran's I + LISA)
python 02_scripts/03_run_esda_final.py

# Step 4 — Generate the empirical variogram
python 02_scripts/04_generate_variogram.py

# Step 5 — Full spatial regression pipeline (OLS → LM → SAR → GWR)
python 02_scripts/05_spatial_regression.py

# Step 6 — Depth analysis (Impacts decomposition, SDM, robustness checks)
python 02_scripts/06_depth_analysis.py

# Step 7 — Generate final cartographic maps
python 02_scripts/07_create_maps.py
```

All outputs are saved automatically to `03_outputs/`.

### 3. Key Output Files

| File | What It Shows |
|---|---|
| `03_outputs/esda/multivariate_lisa.png` | LISA cluster maps for all four variables |
| `03_outputs/esda/multivariate_moran.png` | Moran scatter plots (standardised) |
| `03_outputs/regression/lm_diagnostics.png` | LM tests confirming SAR model selection |
| `03_outputs/regression/impacts_decomposition.png` | Direct / Indirect / Total PTR impact |
| `03_outputs/regression/gwr_maps.png` | GWR local coefficient maps |
| `03_outputs/regression/robustness_norm.png` | Invariance across 30/35/40 seat norms |

---

## 📊 Data Sources

| Dataset | Source | Usage |
|---|---|---|
| **UDISE+ 2023–24** | Ministry of Education, Government of India | School enrolment, classrooms, teachers |
| **Delhi MCD Ward Boundaries** | OpenCity (GeoJSON, 274 wards) | Spatial unit for all analysis |
| **WorldPop 2020** | University of Southampton (Google Earth Engine) | Child population covariate (6–18 years) |
| **Right to Education Act (2009)** | Ministry of Law and Justice, GoI | Basis for 40-seat classroom norm |

> **Note:** Raw UDISE+ data is included in `01_data/raw/` for full replicability.

---

## 🔑 Key Methodology

### The Mismatch Index (MI)
$$MI_i = \frac{\text{Total Enrolment}_i}{\text{Seat Capacity}_i} = \frac{\text{Total Enrolment}_i}{\text{Total Classrooms}_i \times 40}$$

- **MI > 1.0** → Ward is overcrowded beyond physical capacity.
- **MI < 1.0** → Ward has surplus government school seats.
- Constructed entirely from UDISE+ 2023–24. No population estimate is used in the MI itself.

### Spatial Weights Matrix
- **Method:** 300m Fuzzy Contiguity (`libpysal.weights.fuzzy_contiguity`)
- **Transformation:** Row-standardised
- **Why 300m:** Ward 9 (Gharoli) was a topological island at 150m due to digitisation sliver gaps in the boundary file. 300m bridges these gaps without adding any spurious long-distance connections (average neighbour count = 4.66 at both thresholds).

### Model Selection (Anselin 1988 Decision Rule)
| LM Test | Statistic | p-value |
|---|---|---|
| Robust LM-Lag | **23.63** | < 0.0001 |
| Robust LM-Error | 10.69 | 0.0011 |

Since **Robust LM-Lag > Robust LM-Error**, the **Spatial Autoregressive (SAR)** model is selected.

### The SAR Spatial Lag Coefficient
$$\rho = 0.2855 \quad (z = 4.18,\ p < 0.001)$$

A crisis in one ward radiates **28.6%** of its intensity into neighbouring wards, after controlling for all covariates.

### The PTR Spatial Multiplier (LeSage & Pace 2009)
| Effect | Value | Interpretation |
|---|---|---|
| Direct Impact | +0.0898 | Effect on the local ward only |
| Indirect Impact (Spillover) | +0.0333 | Effect cascading to all other wards |
| **Total Impact** | **+0.1231** | **37.2% larger than the raw SAR coefficient** |

---

## 🌍 Key Findings in Detail

### Finding 1: Spatial Clustering (LISA Maps)
- **14 High-High (HH) Crisis Wards** identified, concentrated in **North Delhi** (Nihal Vihar MI=1.56, Mukund Pur MI=1.55, Burari MI=1.50) and **East Delhi**.
- **23 Low-Low (LL) Surplus Wards** concentrated in **South Delhi** (Rohtash Nagar MI=0.38, Hauz Khas MI=0.42) and NDMC.
- 999 Monte Carlo permutations used for significance testing.

### Finding 2: The PTR Paradox (Dominant Driver)
Dropping PTR from the OLS model collapses R² from **24.8% to 7.7%** (LOCO Sensitivity Analysis). The crisis is primarily a **teacher shortage and classroom overcrowding** mechanism, not simply the absence of school buildings.

### Finding 3: The WorldPop Satellite Bias in North Delhi

WorldPop's Random Forest model suffers from **Vertical Density Blindness** in North Delhi's unauthorised colonies:

| Ward | WorldPop Estimate | UDISE+ Enrolled | WorldPop Accuracy |
|---|---|---|---|
| Nihal Vihar | 6,593 children | 4,255 enrolled (govt. only) | Severely underestimated |
| Mukund Pur | 5,627 children | 9,904 enrolled | Only 57% of actual |
| Mubarak Pur Dabas | 6,304 children | **17,943 enrolled** | **Only 35% of actual** |

The correlation between WorldPop density and actual mismatch in North Delhi is **r = −0.361** — a *negative* relationship where the satellite predicts *lower* overcrowding in the most overcrowded wards.

---

## ⚠️ Limitations

See [`Missing_Data_Analysis`](04_reports/01_missing_data_analysis.md) for the full quantitative data quality audit, and [`LIMITATIONS`](05_poster/LIMITATIONS.md) for the complete limitations and caveats document.

Key limitations:
1. **WorldPop Satellite Bias** — 35–65% undercount in informal North Delhi settlements.
2. **Private School Exclusion** — Study focuses exclusively on the government school system (State's constitutional obligation under the RTE Act).
3. **40-Seat Norm Assumption** — Upper bound from RTE Act; robustness checks confirm findings are invariant across 30, 35, and 40-seat norms.
4. **74 Schools Unmapped** — 2.8% of schools lacked ward identifiers in UDISE+; 40.5% of these were Senior Secondary (Classes 9–12).
5. **9 Wards with Zero Schools** — 1.24 lakh children live in wards with no government school; these wards are excluded from MI calculation.
6. **Modifiable Areal Unit Problem (MAUP)** — Results are specific to the ward spatial scale.

---

## 🖼️ Research Poster

The A1 academic poster [`Poster`](05_poster/poster_A1.pdf) presents the full research narrative across four columns:

| Column | Section | Key Content |
|---|---|---|
| 1 | The Spatial Illusion vs. Reality | MI formula, baseline statistics, 4.15km variogram |
| 2 | Proving Spatial Clustering | Global Moran's I across 4 variables, LISA maps |
| 3 | Pinpointing the Clusters | 14 HH crisis wards, 23 LL surplus wards, SAR spillover ρ=0.2855 |
| 4 | Geographic Non-Stationarity | GWR maps, PTR paradox, WorldPop satellite bias, Policy implications |

---

## 📚 References

> Full reference list is available in [`References`](05_poster/References.pdf)

### Primary Data & Policy Sources
1. **Ministry of Education (2024).** *UDISE+ 2023–24: Unified District Information System for Education Plus.* Government of India.
2. **Ministry of Law and Justice (2009).** *The Right of Children to Free and Compulsory Education Act, 2009.* Government of India.
3. **WorldPop (2020).** *Global High-Resolution Population Denominators Project — India 2020.* University of Southampton. doi:10.5258/SOTON/WP00674.

### Education & Delhi-Specific Literature
4. **Ghosh, P., & Bose, S. (2022).** Estimating the Excess Demand for Government Schools in Delhi. *Working Paper No. 387*, National Institute of Public Finance and Policy.
5. **Venkatesan, R. G., & Mappillairaju, B. (2023).** Detection of Hotspots of School Dropouts in India: A Spatial Clustering Approach. *PLOS ONE, 18*(1).
6. **Sharma, G., & Patil, G. R. (2022).** Spatial and Social Inequities for Educational Services Accessibility: A Case Study for Greater Mumbai. *Cities, 122*.
7. **Talen, E. (2001).** School, Community, and Spatial Equity: An Empirical Investigation of Access to Elementary Schools in West Virginia. *Annals of the Association of American Geographers, 91*(3).

### Satellite Bias & Spatial Methodology
8. **Wardrop, N. A., et al. (2018).** Spatially Disaggregated Population Estimates in the Absence of National Census Data. *Proceedings of the National Academy of Sciences (PNAS)*.
9. **Leyk, S., et al. (2019).** The Architectural and Spatial Characteristics of the World's Informal Settlements. *Nature Scientific Reports*.
10. **Boo, G., et al. (2022).** Vertical Density Blindness in Gridded Population Products: Evidence from Sub-Saharan Africa and South Asia. Working Paper.

### Spatial Econometrics
11. **Anselin, L. (1995).** Local Indicators of Spatial Association — LISA. *Geographical Analysis, 27*(2).
12. **Anselin, L. (1988).** *Spatial Econometrics: Methods and Models.* Kluwer Academic Publishers.
13. **LeSage, J., & Pace, R. K. (2009).** *Introduction to Spatial Econometrics.* CRC Press.

### International Comparisons
14. **Xu, C., & Shi, B. (2026).** Spatial Inequality in School Physical Education Resources in Shaanxi, China (2021–2024): Patterns, Determinants, and Policy Implications. *Scientific Reports, 16*.

---

## 🛠️ Technologies

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PySAL](https://img.shields.io/badge/PySAL-libpysal%20%7C%20esda%20%7C%20spreg-green)
![GeoPandas](https://img.shields.io/badge/GeoPandas-spatial-orange)
![MGWR](https://img.shields.io/badge/MGWR-GWR-red)

| Library | Purpose |
|---|---|
| `geopandas` | Spatial data loading, merging, and plotting |
| `libpysal` | Spatial weights matrix construction |
| `esda` | Moran's I and LISA computation |
| `spreg` | OLS, SAR (ML), and LM Diagnostic tests |
| `mgwr` | Geographically Weighted Regression |
| `matplotlib` / `seaborn` | All visualisations |

---

## 👤 Author

**Shivam** | B.Tech. | IIIT-Delhi

---

*"The problem is not whether Delhi has enough government school seats in total — in aggregate it does. The problem is whether those seats are located in the same wards where children who depend on government schools actually live."*
