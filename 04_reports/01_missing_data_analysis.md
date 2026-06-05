# 1. Missing Data Analysis: NaN Schools & Empty Wards

## 1. Scope of Data Loss

| Category | Count | % of Total |
|----------|------:|----------:|
| Total Govt Schools | 2,645 | 100% |
| Mapped to wards | 2,571 | 97.2% |
| **Unmapped (NaN ward)** | **74** | **2.8%** |

- **Enrolment lost**: 40,332 students (1.73% of 23.3 lakh total)  
- **Classrooms lost**: 1,728 (2.76%)  
- **Teachers lost**: 1,285 (0.80%)

---

## 2. Are NaN Schools Systematically Different? (Welch's t-test)

| Variable | NaN Mean | Mapped Mean | t-stat | p-value | Significant? |
|----------|:--------:|:-----------:|:------:|:-------:|:----------:|
| **Enrolment** | 545 | 767 | -2.68 | 0.009 | **Yes ✱✱** |
| Classrooms | 23.4 | 23.3 | 0.05 | 0.963 | No |
| **MI (Enrol/Seats)** | 0.60 | 0.73 | -2.46 | 0.016 | **Yes ✱** |
| **PTR** | 38.9 | 26.8 | 3.70 | 0.0004 | **Yes ✱✱✱** |

> [!WARNING]
> **NaN schools are NOT "missing at random" (MAR)**. They are statistically significantly:
> - **Smaller** (lower enrolment)
> - **More under-utilized** (lower MI)  
> - **Worse staffed** (PTR of 38.9 vs 26.8 — exceeding the RTE norm of 30:1)
>
> This suggests these are resource-deprived schools that lack proper UDISE+ data entry, which is itself a marker of institutional neglect.

---

## 3. School Category Over-Representation

| Category | NaN % | Mapped % | Over-represented? |
|----------|:-----:|:--------:|:-----------------:|
| Sec-HSec (9-12) | **40.5%** | 0.9% | **YES ✱✱✱** |
| Sec only (9-10) | **8.1%** | 0.0% | **YES ✱✱✱** |
| Prim-UP (1-8) | **6.8%** | 0.1% | **YES ✱✱✱** |
| UP only (6-8) | **1.4%** | 0.4% | **YES ✱✱** |
| Primary (1-5) | 18.9% | 59.8% | No (under-rep) |

> [!IMPORTANT]
> **30 of the 74 NaN schools (40.5%) are "Sec-HSec (9-12)" schools** — these are exclusively senior secondary institutions. In the mapped data, this category is only 0.9%. This is a **massive structural bias**: the UDISE+ system systematically fails to record ward names for senior secondary schools, likely because they are managed at the state/directorate level rather than the local MCD body.

---

## 4. Empty Wards — Children Without Government Schools

9 wards have **zero government schools** but **significant child populations**:

| Ward | Child Pop (6-18) | Status |
|------|:----------------:|--------|
| **071S** | **40,930** | Largest gap — South Delhi, likely Deoli rural area |
| **093S** | **25,295** | South-East Delhi, peri-urban |
| **005E** | **18,081** | East Delhi, Yamuna floodplain |
| **101N** | **11,417** | North Delhi |
| **007E** | **7,662** | East Delhi, near 005E (cluster) |
| **023S** | **6,665** | South-West Delhi |
| **052N** | **6,061** | North-West Delhi |
| **041N** | **4,600** | North Delhi |
| **098S** | **3,427** | South-East Delhi |
| **TOTAL** | **1,24,142** | **1.24 lakh children with zero local govt school seats** |

> [!CAUTION]
> **1.24 lakh children live in wards with absolutely no government school.**  
> These children must either:
> 1. Travel to neighboring wards (spatial spillover / commuting cost)
> 2. Attend private schools (economic burden)
> 3. Drop out entirely
>
> This is a critical finding — it directly supports the need for spatial regression models that account for cross-ward "demand leakage."

---

## 5. Implications for Research Methodology

The 74 NaN schools and 9 empty wards are not just "missing data" — they carry **information value**:

1. **Selection Bias Risk**: By excluding 74 schools, we are systematically dropping poorly-administered, under-resourced senior secondary schools. This makes the mapped data look **better** than reality (lower PTR, higher MI).

2. **Sensitivity Analysis Required**: We should report results with and without these schools. Since they represent only 1.73% of enrolment, the MI change is minimal, but the **PTR bias** (38.9 vs 26.8) is substantial.

3. **Empty Wards as Policy Variables**: The 9 wards with zero schools should be **included** in the spatial analysis with MI = ∞ (or a capped value). They represent the most extreme form of mismatch. Excluding them would understate the spatial inequality.


*"Ward ID,Probable Ward Name,Status Check
071S,Deoli,"Partially True. Deoli is a massive urban village. While there are schools nearby (like in Sangam Vihar or Ambedkar Nagar), the core ward has a severe shortage of government senior secondary schools relative to its population."
093S,Tughlakabad,"Verified. This area is a mix of heritage land and dense unauthorized colonies. Most government schools are located on the periphery (Tughlakabad Ext. or Kalkaji), leaving the inner ward under-served."
005E,Bhajanpura / Yamuna Vihar,True (for floodplains). Areas near the Yamuna floodplain (like Sonia Vihar parts) often lack permanent government school infrastructure due to land zoning restrictions.
101N,Narela / Lampur,"Likely. These are peripheral North Delhi wards where industrial or agricultural land dominates, and residential clusters are often far from existing school buildings."*
