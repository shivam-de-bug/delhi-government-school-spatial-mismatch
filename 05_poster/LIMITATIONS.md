# Limitations & Caveats of the Study

> This document provides a complete, transparent account of the methodological limitations. Acknowledging these does not invalidate the findings — it contextualises their scope and generalisability.

---

## 1. Satellite Measurement Bias (WorldPop)

| | |
|---|---|
| **Caveat** | WorldPop underestimates population in dense urban areas due to **Vertical Density Blindness** — satellites capture building footprints, not floors or families within. |
| **Example** | In Mubarak Pur Dabas, WorldPop estimates ~6,300 children vs. ~17,900 enrolled students in UDISE+. |
| **Implication** | Distorts model results in high-density wards; likely underestimates true demand. |

---

## 2. Private School Blind Spot

| | |
|---|---|
| **Caveat** | Only government schools are modelled; private schools are excluded. |
| **Example** | Wards with many private schools may appear underutilized in the government system. |
| **Mitigation** | Zone dummy variables are used to absorb regional private-school effects (e.g., South Delhi). |
| **Implication** | Demand may be underestimated in areas with high private school presence. |

---

## 3. 40-Seat Capacity Assumption (RTE Norm)

| | |
|---|---|
| **Caveat** | Seat capacity is computed as **Total Classrooms × 40**, per RTE guidelines — an upper limit that may exceed practical capacity. |
| **Example** | A 10-classroom school is assumed to hold 400 students, even if realistic capacity is lower. |
| **Implication** | Overcrowding may be underestimated; results are conservative. |

> **Robustness Check:** All spatial statistics (Moran's I = 0.3307, SAR ρ = 0.2855, R²) are perfectly invariant across 30, 35, and 40-seat norms. This is because all spatial statistics are scale-invariant — they depend on relative variation across wards, not absolute levels.

---

## 4. Omission of Senior Secondary Schools

| | |
|---|---|
| **Caveat** | **74 schools** were excluded for lacking ward identifiers. Of these, **40.5% (30 schools)** were **Senior Secondary (Classes 9–12)** institutions. This indicates a structural bias where UDISE+ data is less reliable for high-school level mapping compared to primary levels. |
| **Example** | These schools could not be spatially assigned to specific wards. |
| **Implication** | Findings are more reliable for primary and middle levels; capacity may be slightly underestimated for higher grades. |

---

## 5. Map Boundary Errors (Sliver Gap Problem)

| | |
|---|---|
| **Caveat** | Small digitisation errors in the ward boundary GeoJSON create sliver gaps between adjacent wards, breaking spatial connectivity. |
| **Example** | Ward 9 (Gharoli) appeared as an isolated island at a 150m threshold. |
| **Mitigation** | 300m fuzzy contiguity weights matrix applied to bridge gaps. |
| **Implication** | A 300m fuzzy contiguity matrix was the **minimal threshold** needed to restore a fully connected weights matrix without artificially linking non-adjacent wards. |

---

## 6. Infrastructure Adequacy vs. Service Delivery

| | |
|---|---|
| **Caveat** | The Mismatch Index (MI) measures physical capacity (classrooms), not educational quality. |
| **Example** | A ward with MI = 1.0 may still lack toilets, libraries, or science labs. |
| **Implication** | Analysis captures **infrastructure adequacy only** — not learning outcomes or service quality. |

---

## 7. Temporal Data Gap (4-Year Lag)

| | |
|---|---|
| **Caveat** | School data is from **2023–24**; WorldPop population data is from **2020**. |
| **Example** | Fast-growing wards like Rohini or Bawana may have seen significant population change in the interim. |
| **Implication** | The population variable is lagged, reducing accuracy in high-growth areas. |

---

## 8. Exclusion of Zero-School Wards

| | |
|---|---|
| **Caveat** | **9 wards** with no government schools are excluded from regression (MI is undefined for them). |
| **Example** | Ward No. 120 has **~40,931 children** but zero government schools. |
| **Implication** | The most extreme mismatches remain invisible in the model, leading to underestimation of the overall crisis. Collectively, these 9 wards contain **1,24,142 children** with no local government school access. |

---

## 9. Modifiable Areal Unit Problem (MAUP)

| | |
|---|---|
| **Caveat** | Results are sensitive to the choice of spatial unit; switching from wards to districts or grid cells can alter Moran's I and regression coefficients. |
| **Implication** | Findings are specific to the **MCD ward level** and may not generalise to other spatial scales. |

---

## 10. The "Chicken-and-Egg" Problem (Reverse Causality)

| | |
|---|---|
| **Caveat** | We found that teacher shortages and overcrowding happen together, but we don't know which one started first. |
| **Implication** | It's a reinforcing feedback loop: a lack of teachers makes a school overcrowded, and that overcrowding makes teachers stressed and want to leave. Our model shows they are linked, but it cannot prove who is the original "cause." Results should be interpreted as evidence of this feedback mechanism rather than a unidirectional causal claim. |

---

## Summary Table

| # | Limitation | Severity | Mitigation |
|---|---|---|---|
| 1 | WorldPop Satellite Bias | High (North Delhi) | Zone Fixed Effects; WorldPop not used in MI |
| 2 | Private School Exclusion | Medium | Methodological focus on State obligation (RTE) |
| 3 | 40-Seat Norm Assumption | Low | Robustness invariant across 30/35/40 norms |
| 4 | Senior Secondary Omission | Low–Medium | 40.5% of 74 excluded schools; 2.8% of total |
| 5 | Sliver Gap / Digitisation Error | Technical | 300m fuzzy contiguity; same avg. neighbour count |
| 6 | Quantity vs. Quality | Conceptual | Study scope is infrastructure adequacy only |
| 7 | 4-Year Population Lag | Medium | Zone Fixed Effects; WorldPop not in MI |
| 8 | Zero-School Ward Exclusion | High | 1.24 lakh children underestimated in model |
| 9 | MAUP (Scale Dependency) | Structural | Results are ward-level specific |
| 10 | Reverse Causality | Structural | Cross-sectional design; interpret as association |

---

*Source: Limitations_and_Caveats.pdf — submitted as part of ECO 324/524 final project, IIIT-Delhi, 2025–26.*
