# A1 Poster Design Guide: Ultra-Concise 4-Column Layout

To fit large 4-panel images (`multivariate_moran.png` and `multivariate_lisa.png`), we must be extremely wise with our text space. Every bullet point is now compressed to 1-2 punchy sentences. 

Divide your canvas into 4 vertical columns. Here is space-optimized layout:

---

## ⬅️ COLUMN 1: Context & Reality

**[Heading 1] The Spatial Problem**
* **Reality:** Delhi’s total school capacity seems sufficient, but empty seats in South Delhi provide no relief to overcrowded children in North Delhi. 
* **Objective:** Quantify the spatial mismatch, prove it is clustered, and measure the spillover effect.

**[Heading 2] The Baseline Mismatch**
* **Mismatch Index (MI):** `Total Enrolment / (Classrooms × 40)`
* *Rule:* MI > 1.0 = Overcrowded. MI < 1.0 = Surplus.
* 🖼️ **PASTE IMAGE:** `map4_mismatch_index.png` 

**[Heading 3] Methodology Flow**
* **ESDA:** Moran's I, LISA, and Variograms prove clustering. *(See Col 2 & 3)*
* **Global Model:** OLS fails $\rightarrow$ SAR quantifies spillover. *(See Col 3)*
* **Local Model:** GWR maps local crisis drivers. *(See Col 4)*

---

## 🟦 COLUMN 2: Global Spatial Diagnosis

**[Heading 4] Proving the Crisis**
* Are overcrowded schools just random bad luck? No.
* 🖼️ **PASTE IMAGE:** `multivariate_moran.png` (4-Panel Scatterplot)
* *Caption:* Moran's I confirms severe clustering across 4 metrics. Note: **MI Supply** measures actual school enrolment, while **MI Demand** uses WorldPop satellite estimates.

**[Heading 5] The 4.15km Barrier**
* 🖼️ **PASTE IMAGE:** `variogram.png`
* **Finding:** The variogram proves the spatial crisis stretches for **4.15 km**.
* **Impact:** A child must travel over 4km to escape the overcrowding, actively destroying the RTE Act’s 1km walkable "neighbourhood schooling" mandate.

---

## 🟧 COLUMN 3: Local Clusters & Regression

**[Heading 6] Pinpointing the Clusters**
* 🖼️ **PASTE IMAGE:** `multivariate_lisa.png`
* *Caption:* **Red:** 14 Overcrowded Wards (North/East). **Blue:** 23 Surplus Wards (South).

**[Heading 7] The Spatial Multiplier (SAR Model)**
* *OLS fails due to clustering. SAR quantifies this network spillover (**ρ = 0.2855**, p<0.01).*
* 🖼️ **PASTE IMAGE:** `impacts_decomposition.png`
* **The 39.8% Rule:** A local teacher shortage forces students across borders, causing 39.8% *more* overcrowding across the network than expected.

---

## ➡️ COLUMN 4: Local Depth & Policy

**[Heading 8] Geographic Non-Stationarity (GWR)**
* 🖼️ **PASTE IMAGE:** `gwr_maps.png`
* **The PTR Paradox:** GWR proves East Delhi mismatch is driven by severe teacher shortages. However, in North Delhi, PTR is insignificant.
* **The Invisible Population:** North Delhi is overcrowded due to massive, unmapped populations. WorldPop satellite data missed these people because of Vertical Density Blindness, Census Averaging / Spatial Smoothing, and Unrecognised Settlement Exclusion.

**[Heading 9] Policy Implications**
* **Targeted Relief:** East Delhi needs rapid teacher deployment. North Delhi needs physical land/school construction.
* **Spillover Benefit:** Adding teachers to one ward provides a 39.8% larger benefit by relieving cross-border overcrowding pressure.
* **Data Warning:** Urban planners cannot blindly trust global satellite demographics for Indian informal settlements.
