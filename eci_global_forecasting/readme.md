# Global Economic Complexity Index Forecasting: 1995–2050

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Model](https://img.shields.io/badge/Model-CatBoost-yellow.svg)](https://catboost.ai/)
[![Data](https://img.shields.io/badge/Data-Harvard%20Growth%20Lab-red.svg)](https://growthlab.cid.harvard.edu/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Project Overview

This repository presents an end-to-end machine learning framework for analyzing and forecasting the Economic Complexity Index (ECI) across countries over the period 1995–2050. The project uses historical ECI observations from the Harvard Growth Lab's Atlas of Economic Complexity for 1995–2023 and develops a panel-data machine learning model to generate country-level forecasts for 2024–2050. Rather than treating each country as an independent univariate time series, the framework models the international economy as a panel in which country identity, historical ECI values, temporal dynamics, and cross-country structure are jointly incorporated into the prediction process. The repository also provides interactive visualizations for examining the historical evolution and geographic distribution of economic complexity.

### RQs

The project is designed around three main questions:

1. How effectively can historical ECI dynamics be used to predict future country-level ECI values?
2. How do countries' projected economic complexity trajectories evolve over the 2024–2050 forecasting horizon?
3. How does the relative position of countries in the global ECI distribution change under the model's projections?


<br>

## Data

### Source

Historical ECI data are obtained from the **Harvard Growth Lab's Atlas of Economic Complexity**, using the HS92-based ECI series.

- Historical observations: **1995–2023**
- Forecasting period: **2024–2050**

The final processed dataset combines historical observations with model-generated forecasts and annual country rankings.

### Panel Structure

The dataset is organized as a country-year panel, with countries identified using their **ISO3 country codes**.

The main outcome variable is:

- `eci` — Economic Complexity Index

Additional variables are constructed from the historical ECI series to represent temporal dependence, momentum, and recent variability.

 <br>

## Machine Learning Model

### CatBoost Regressor

The primary forecasting model is a **CatBoost Regressor**, a gradient-boosted decision-tree algorithm capable of incorporating categorical variables.

The country identifier (`iso3`) is treated as a categorical feature rather than being expanded into a large one-hot encoded matrix. This allows the model to incorporate country-specific information while maintaining the panel structure of the dataset.

The main implementation is available in [`prediction_pro_rank.py`](./prediction_pro_rank.py).

During the development of the project, modern LLM-based tools, including **ChatGPT and Gemini**, were used as development aids for debugging, code refinement, and implementation support.

### Model Configuration

The current implementation uses the following main hyperparameters:

| Parameter | Value |
| <br>| <br>:|
| Loss function | RMSE |
| Iterations | 2,000 |
| Learning rate | 0.03 |
| Tree depth | 8 |
| L2 regularization | 3 |

These parameters define the model specification implemented in the repository.

 <br>

## Forecasting Framework

The model produces forecasts from **2024 through 2050** using recursive multi-step forecasting.

For each country, the procedure can be summarized as follows:

1. Historical observations through 2023 are used to construct the initial feature set.
2. The model predicts ECI for 2024.
3. The predicted 2024 value is added to the country's historical sequence.
4. Lagged variables and rolling statistics are recalculated using the expanded sequence.
5. The model predicts 2025.
6. The process continues recursively until 2050.

This procedure allows forecasts at later horizons to depend on previously generated predictions.

Conceptually:

```text
Historical ECI
1995 ─────────────── 2023
                       │
                       ▼
                    Model
                       │
                       ▼
                     2024
                       │
                       ▼
               Feature Update
                       │
                       ▼
                     2025
                       │
                      ...
                       │
                       ▼
                     2050
````

The recursive structure is particularly relevant for this project because the forecasting horizon extends substantially beyond the final observed year.

The final country-level predictions, historical observations, and associated rankings are provided in the Excel output:

**[Download: eci_full_1995_2050.xlsx](./eci_full_1995_2050.xlsx)**

The complete-period visualization generated from the forecasting results is available here:

**[Full-period interactive plot](./full_period_plot.html)**

 <br>

## Model Evaluation

The implemented pipeline uses **strict temporal out-of-sample validation** to reduce the risk of data leakage.

The model is trained using historical observations from **1995 to 2018** and evaluated on unseen future observations from **2019 to 2023**.

This temporal structure ensures that observations from future periods are not used to train the model before those periods are evaluated.

The current execution produced the following results:

| Metric                |     Result |
|  <br> <br> <br> <br> <br> <br> <br> |  <br> <br> <br>: |
| Training observations |      3,454 |
| Test observations     |        725 |
| Total observations    |      4,179 |
| Test $R^2$            | **0.9995** |

The reported $R^2$ indicates that the model explains approximately **99.95% of the variance** in the held-out test observations under the current evaluation procedure.

> **Note:** $R^2 = 0.9995$ should not be interpreted as 99.95% forecasting accuracy. It represents the proportion of variance in the test target explained by the model under the specified evaluation procedure.

Because the validation is performed on later years than the training period, the evaluation is designed to better reflect the forecasting setting than a random country-year split.

 <br>

## Historical Analysis and Visualization

The repository includes interactive visualizations designed to examine both the geographic and temporal dimensions of economic complexity.

### Global ECI Maps

Interactive choropleth dashboards are provided for each year from 2020 to 2023:

* **[2020 — All Countries](./all_2020.html)**
* **[2021 — All Countries](./all_2021.html)**
* **[2022 — All Countries](./all_2022.html)**
* **[2023 — All Countries](./all_2023.html)**

These dashboards display country-level ECI values and provide a geographic view of the global distribution of economic complexity.

The dashboards also include comparisons of the **Top 20** and **Bottom 20** countries according to their HS92-based ECI rankings.

### Historical ECI Trajectories

The repository also includes an interactive visualization comparing the trajectories of selected high- and low-complexity economies over **1995–2023**.

The timeline slider allows users to examine how the relative positions of the selected countries change over time.

**[Full-period interactive visualization](./full_period_plot.html)**

The script used to generate individual-year visualizations is available in:

**[`single_year_plot_maker.py`](./single_year_plot_maker.py)**

 <br>

## Interpretation of Forecasts

The 2024–2050 values generated by this repository should be interpreted as **model-based projections rather than official forecasts of future economic complexity**.

Long-term ECI trajectories can be affected by factors that are difficult to infer from historical ECI dynamics alone, including:

* structural changes in international trade;
* technological development;
* industrial policy;
* geopolitical shocks;
* changes in global production networks;
* resource discoveries and depletion;
* institutional changes;
* major economic crises.

The recursive forecasting design also means that prediction uncertainty can accumulate over longer horizons because forecasts become inputs for subsequent predictions. Consequently, the 2050 projections should be interpreted as **model-based projections conditional on historical patterns**, rather than deterministic predictions of future economic outcomes.

 <br>

## Limitations and Future Research

Several extensions could further strengthen the empirical framework.

### Additional Economic Predictors

The current framework is primarily based on historical ECI dynamics. Future versions could incorporate additional country-level variables such as:

* GDP per capita;
* trade openness;
* export diversification, and etc.

### Alternative Forecasting Models

Model performance could also be compared with alternative approaches, including:

* XGBoost;
* Random Forest;
* LightGBM, and etc.

Such comparisons would help determine whether the observed predictive performance is specific to the CatBoost architecture or remains robust across alternative modeling approaches.

### Uncertainty Quantification

Future versions could additionally report prediction intervals or alternative forecast scenarios rather than presenting point forecasts alone. This would be particularly valuable for the long-term 2024–2050 forecasting horizon.

 <br>

## Repo Structure

```text
eci-global-forecasting/
│
├── all_2020.html
├── all_2021.html
├── all_2022.html
├── all_2023.html
│
├── eci_full_1995_2050.xlsx
├── full_period_plot.html
│
├── prediction_pro_rank.py
├── single_year_plot_maker.py
└── readme.md
```

### Main Files

* **[`prediction_pro_rank.py`](./prediction_pro_rank.py)** — Main forecasting pipeline using CatBoost, including country identification and annual ranking.
* **[`single_year_plot_maker.py`](./single_year_plot_maker.py)** — Script used to generate individual-year ECI visualizations.
* **[`eci_full_1995_2050.xlsx`](./eci_full_1995_2050.xlsx)** — Final dataset containing historical observations, model-generated forecasts, and rankings.
* **[`full_period_plot.html`](./full_period_plot.html)** — Interactive visualization covering the full historical period.
* **[`all_2020.html`](./all_2020.html)** — Interactive ECI visualization for 2020.
* **[`all_2021.html`](./all_2021.html)** — Interactive ECI visualization for 2021.
* **[`all_2022.html`](./all_2022.html)** — Interactive ECI visualization for 2022.
* **[`all_2023.html`](./all_2023.html)** — Interactive ECI visualization for 2023.
* **[`readme.md`](./readme.md)** — Project documentation.

 <br>


## Data Source

Historical ECI data are obtained from the **Harvard Growth Lab's Atlas of Economic Complexity**.

Users of this repository should cite the underlying Atlas of Economic Complexity and the relevant methodological publications associated with the ECI measure when using the dataset or derived results in academic work.

**Data source:**
[Harvard Growth Lab — Atlas of Economic Complexity](https://atlas.hks.harvard.edu/)

 <br>

##  License

This project is released under the **MIT License**.

See the `LICENSE` file for the complete license text.

