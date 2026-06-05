# Does Delhi Build Schools Where Children Live? 
**Spatial Mismatch Between Government School Capacity and Child Population Across Delhi’s MCD Wards**

---

## 1. Introduction and Research Problem

Delhi’s government school system is one of the largest in the world, with over 2,600 government and MCD schools providing education to children. On an aggregate, city-wide level, Delhi appears to have sufficient school capacity. The total seating capacity across government schools roughly matches the total enrolment demand. 

However, a city-wide average conceals the geographic reality of urban planning. The fundamental research problem of this study is spatial: **Are government school seats located in the same geographic areas where the children who depend on them actually live?** 

A surplus of empty classroom seats in wealthy, low-density areas of South Delhi provides no educational relief to overcrowded, high-density informal settlements in North or East Delhi. When educational infrastructure is spatially misallocated, the Right to Education (RTE) Act’s guarantee of accessible schooling becomes structurally compromised.

This study conducts a rigorous spatial econometric analysis to:
1. Map and quantify the geographic mismatch between school capacity and enrolment at the micro (ward) level.
2. Statistically test if this mismatch is randomly distributed or spatially clustered (identifying "crisis zones").
3. Estimate the spatial spillover effects of local educational crises using spatial regression models (SAR).
4. Uncover local geographic variations in the drivers of mismatch using Geographically Weighted Regression (GWR).

---

## 2. Data and Methodology

### 2.1 Data Sources and Preprocessing
The study integrates three primary datasets at the ward level:
- **UDISE+ (2023-24):** Provided school-level administrative data. We extracted all government and MCD schools (Management codes 1, 2, and 3), aggregating total classrooms, total teachers, and total enrolment (Classes 1–12) for each ward.
- **MCD Ward Boundaries (2022):** A geospatial vector file mapping Delhi’s 250 municipal wards (plus NDMC and Cantonment areas), providing the spatial polygons required for contiguity analysis.
- **WorldPop (2020):** High-resolution gridded satellite estimates of child population (ages 6–18), used to calculate local demographic pressure (`log_pop_density`). 

**Defining the Mismatch Index (MI):**
To measure overcrowding, we constructed a Supply-Side Mismatch Index (`MI_supply`). We assumed a maximum legal seating capacity of 40 students per classroom (the upper bound under the RTE Act). 
$$\text{Seat Capacity} = \text{Total Classrooms} \times 40$$
$$\text{MI\_supply} = \frac{\text{Total Enrolment}}{\text{Seat Capacity}}$$
- **MI < 1.0**: Ward has surplus capacity (empty seats).
- **MI > 1.0**: Ward is structurally overcrowded (more students than legal seats).

**Spatial Weights Matrix (W):**
We constructed a **300m Fuzzy Queen Contiguity Matrix**. A standard 150m matrix left one ward (Gharoli, East Delhi) as a topological island due to minor digitisation sliver gaps in the shapefile. Expanding the tolerance to 300m reconnected this island without altering the average neighbour count (4.66), ensuring a robust spatial topology.

### 2.2 Analytical Pipeline
The methodology follows a classic spatial econometric progression:
1. **Exploratory Spatial Data Analysis (ESDA):** Global Moran’s I, LISA, and Variogram analysis to prove spatial dependence exists.
2. **Global Regression (OLS):** Baseline standard regression.
3. **Lagrange Multiplier (LM) Diagnostics:** To statistically determine the correct spatial model (SAR vs. SEM) based on OLS residuals.
4. **Spatial Autoregressive Model (SAR):** To quantify the "spillover" effect of the crisis across ward boundaries.
5. **Spatial Multiplier Decomposition:** Calculating Direct, Indirect, and Total impacts of covariates (LeSage & Pace, 2009).
6. **Geographically Weighted Regression (GWR):** To map how the effect of teacher shortage (PTR) changes across different zones of Delhi.

---

## 3. Exploratory Spatial Data Analysis (ESDA)

### 3.1 The Mismatch Map
Before statistical modeling, we mapped the raw `MI_supply` index across Delhi.

![Mismatch Index](c:/Users/Shivam/OneDrive/Desktop/antissse/map4_mismatch_index.png)

The map reveals a stark divide. Central and South Delhi exhibit deep blue shades (MI < 1.0, indicating massive surplus capacity), while the Northern, North-Western, and Eastern peripheries burn bright red (MI > 1.2 to 2.0+, indicating severe structural overcrowding).

### 3.2 Global Moran's I
To test if this visual clustering is statistically significant, we calculated Global Moran's I.

![Moran Scatter](c:/Users/Shivam/OneDrive/Desktop/antissse/moran_scatter.png)

- **Moran's I = 0.3307 (p = 0.001)**
The positive, highly significant Moran’s I confirms that educational mismatch is not a random occurrence. Overcrowded wards strongly cluster next to other overcrowded wards, and surplus wards cluster next to surplus wards. This violates the core assumption of independent observations required for standard OLS regression.

### 3.3 LISA Cluster Map (Local Indicators of Spatial Association)
To pinpoint the exact locations of these statistically significant clusters, we generated a LISA map.

![LISA Map](c:/Users/Shivam/OneDrive/Desktop/antissse/lisa_map.png)

LISA identified two massive geographic phenomena:
1. **The Core Surplus Zone (Low-Low, Blue):** 23 wards clustered in Central/South Delhi and NDMC. These areas have abundant school infrastructure but relatively few enrolled students.
2. **The Peripheral Crisis Zones (High-High, Red):** 14 wards concentrated in the North/North-West (e.g., Mubarak Pur Dabas, Narela) and East (e.g., Trilokpuri). These are contiguous zones of structural failure, where multiple adjacent wards are simultaneously overwhelmed.

### 3.4 Spatial Continuity (Variogram)

![Variogram](c:/Users/Shivam/OneDrive/Desktop/antissse/variogram.png)

A spatial variogram was fitted to measure the physical range of the crisis. The model identified a **Range of 4.15 km**. This is a profound finding: if a government school in Delhi is overcrowded, you must travel at least 4.15 kilometers away before the overcrowding effect dissipates and you can reliably find a school with normal capacity. For poor families relying on walking or cheap public transit, a 4.15 km "crisis radius" is an insurmountable barrier to education.

---

## 4. Spatial Econometric Modeling

To understand *what* drives this mismatch, we moved to multivariate regression, using Pupil-Teacher Ratio (`PTR`), Satellite Child Population Density (`log_pop_density`), and School Count (`n_schools`) as predictors.

### 4.1 The Failure of OLS
We first ran a standard Ordinary Least Squares (OLS) regression.

![OLS Residuals](c:/Users/Shivam/OneDrive/Desktop/antissse/ols_residuals.png)

The OLS model yielded an $R^2$ of 0.2477. However, testing the residuals of the OLS model revealed a **Residual Moran's I of 0.0621 (p=0.015)**. Furthermore, the residuals exhibited clear geographic clustering (red positive residuals in the North, blue negative in the South). Because the errors were spatially autocorrelated, the OLS coefficients were biased and inefficient. A spatial model was mandatory.

### 4.2 Model Selection: Lagrange Multiplier (LM) Diagnostics
To choose between a Spatial Autoregressive (SAR) model and a Spatial Error Model (SEM), we used Anselin's (1988) LM diagnostics on the OLS residuals.

![LM Diagnostics](c:/Users/Shivam/OneDrive/Desktop/antissse/lm_diagnostics.png)

- **Robust LM-Lag = 23.63 (p < 0.001)**
- **Robust LM-Error = 10.69 (p = 0.001)**

Because the Robust LM-Lag statistic was significantly larger than the Robust LM-Error statistic, the correct mathematical specification for this data is the **Spatial Autoregressive (SAR) Model**. This indicates that the mismatch itself spills over across boundaries (a Y-to-Y spillover), rather than just unobserved variables (errors) spilling over.

### 4.3 The SAR Model and Leave-One-Covariate-Out (LOCO) Sensitivity

The SAR model significantly improved the fit ($R^2 = 0.3041$, AIC dropped from -85.5 to -98.9). The spatial lag coefficient was highly significant:
- **Spillover ($\rho$) = 0.2855 (p < 0.001)**

To determine which variable was the primary driver of the crisis, we performed a LOCO sensitivity analysis.

![LOCO Sensitivity](c:/Users/Shivam/OneDrive/Desktop/antissse/loco_sensitivity.png)

Dropping the Pupil-Teacher Ratio (PTR) caused the model's $R^2$ to collapse by 17 percentage points. Dropping population density or school counts barely affected the model. **The crisis, globally, is primarily a teacher shortage mechanism.**

### 4.4 Spatial Multiplier Decomposition (Direct, Indirect, Total Impacts)

In a SAR model, the raw coefficient ($\beta$) does not equal the total effect, because a change in one ward cascades through the spatial network (LeSage & Pace, 2009). We decomposed the PTR effect using the spatial multiplier matrix $S = (I - \rho W)^{-1}$.

![Impacts Decomposition](c:/Users/Shivam/OneDrive/Desktop/antissse/impacts_decomposition.png)

**Decomposition of PTR Effect:**
- **Direct Impact:** +0.0898 (The effect of a teacher shortage on the ward's *own* schools)
- **Indirect Impact (Spillover):** +0.0333 (The effect of that shortage spilling over to *neighbouring* wards)
- **Total Impact:** +0.1231 

**Finding:** The total harm of a teacher shortage is **39.8% larger** than the raw coefficient suggests. Approximately 27.1% of the impact of local educational mismatch spills over to harm neighbouring administrative units.

---

## 5. Geographically Weighted Regression (GWR)

The SAR model gives us one "global" average for all of Delhi. To understand if the causes of the crisis change depending on where you are in the city, we ran a Geographically Weighted Regression (GWR).

![GWR Maps](c:/Users/Shivam/OneDrive/Desktop/antissse/gwr_maps.png)

### The PTR Paradox: Uncovering Two Distinct Crises

A critical observation emerged from the GWR maps: **PTR's effect is highest (bright red) in East Delhi, but negative/insignificant in North Delhi — yet LISA showed North Delhi has the worst actual mismatch crisis.**

To understand why, we compared the GWR PTR coefficient against actual mismatch.

![GWR PTR Focus](c:/Users/Shivam/OneDrive/Desktop/antissse/gwr_ptr_focus.png)

**The East Delhi Crisis (Teacher Shortage):**
In East Delhi (Trilokpuri, Kalyan Puri, Mayur Vihar), the GWR PTR coefficient is strongly positive. Here, school buildings exist, but they are severely understaffed. The mismatch is genuinely driven by a lack of teachers. 

**The North Delhi Crisis (WorldPop Satellite Bias and Demographic Overflow):**
In North Delhi (Mubarak Pur Dabas, Narela, Burari), the crisis is so extreme that adding teachers cannot fix it — there simply aren't enough physical classrooms for the massive population. However, our regression covariate for population (`log_pop_density`) failed to capture this. 

Why? Because **WorldPop satellite data severely underestimates informal settlements in North Delhi** due to "Vertical Density Blindness." 
- *Evidence:* In Mubarak Pur Dabas, WorldPop estimates only 6,304 children exist in the ward. Yet, UDISE+ data proves that **17,943 children are actually sitting in government classrooms** in that exact ward. WorldPop captured only 35% of the real population.
- Because the population covariate was mathematically corrupted by this satellite bias, the GWR model saw "high mismatch, but low satellite population" and was forced to push the PTR coefficient negative as a mathematical artefact. 

**Conclusion:** The GWR perfectly isolated two distinct planning failures. East Delhi needs rapid teacher deployment. North Delhi needs massive new school construction and a complete demographic census audit, as satellite data is entirely blind to its true population density.

---

## 6. Limitations of the Study

This research acknowledges several formal limitations:
1. **WorldPop Measurement Bias:** As proven in our GWR analysis, global gridded population datasets (like WorldPop) systematically fail in vertical, informal, unauthorised colonies (common in North Delhi). The negative correlation between WorldPop density and actual mismatch in the North (r = -0.361) confirms this bias.
2. **Private School Substitution:** Delhi has 2,804 private schools operating alongside 2,645 government schools. In wealthy areas (South Delhi/NDMC), affluent families exit the government system. Our model's "surplus" in South Delhi is partially an artefact of private school substitution, which we could not fully control for without private enrolment micro-data.
3. **Classroom Norm Assumption:** The 40-seat norm is the RTE upper bound. True usable capacity may be lower (laboratories, broken rooms) or higher (double-shift schools). However, spatial statistics (Moran's I, SAR $\rho$) are scale-invariant and remain highly robust regardless of the specific scalar norm chosen.
4. **Temporal Lag:** WorldPop data is from 2020, while UDISE+ data is from 2023-24, failing to capture post-COVID internal migration to peripheral wards.

---

## 7. Conclusion and Policy Implications

This study definitively proves that Delhi’s educational mismatch is a structural spatial failure, not a random occurrence. 

**Key Policy Takeaways:**
1. **The Spatial Multiplier Exists ($\rho$ = 0.2855):** Educational mismatch does not respect administrative boundaries. 28.6% of a crisis in one ward radiates to its neighbours. Deploying teachers to a failing ward provides a 39.8% larger total benefit to the city than naive accounting suggests, due to the relief of spatial spillover pressure.
2. **The 4.15 km Crisis Radius:** Once a family is inside a High-High crisis cluster, they must travel an average of 4.15 km to escape it. This destroys the RTE Act's mandate of neighbourhood schooling.
3. **Two Distinct Policy Prescriptions:** 
   - **East Delhi** requires an emergency deployment of teachers, as PTR is the binding constraint on capacity.
   - **North & North-West Delhi** requires aggressive land acquisition and the construction of new physical school buildings to handle demographic overflow that satellite models currently fail to detect. 
4. **The Danger of Satellite Demographics:** Urban planners in India cannot rely on standard satellite population grids (WorldPop) to allocate educational resources in unauthorised colonies, as they severely underestimate vertical informal settlements. Ground-truthed census data is irreplaceable.

Educational equity in Delhi cannot be achieved by looking at city-wide averages. To fulfil the promise of the Right to Education, the state must build schools and deploy teachers precisely where the children actually live.
