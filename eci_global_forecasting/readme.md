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

Historical ECI data are obtained from the Harvard Growth Lab's Atlas of Economic Complexity using the HS92-based ECI series.

Historical observations cover: 1995–2023

The forecasting period is: 2024–2050

The final processed dataset combines the historical observations with model-generated forecasts and annual country rankings.

### Panel Structure

The dataset is organized as a country-year panel, with countries identified using their **ISO3 country codes**.

The main outcome variable is:

* `eci` — Economic Complexity Index

Additional variables are constructed from the historical ECI series to represent temporal dependence, momentum, and recent variability.

<br>



## Machine Learning Model

### CatBoost Regressor

The primary forecasting model is a **CatBoost Regressor**, a gradient-boosted decision-tree algorithm capable of incorporating categorical variables. The country identifier (`iso3`) is treated as a categorical feature rather than being expanded into a large one-hot encoded matrix. This is particularly useful for panel data containing a large number of country entities while preserving country-specific information within the model. In this section, modern LLM tools (ChatGPT & Gemini) widely used for debugging and developing the model. 

### Model Configuration

The current implementation uses the following main hyperparameters:

| Parameter         | Value |
| ----------------- | ----: |
| Loss function     |  RMSE |
| Iterations        | 2,000 |
| Learning rate     |  0.03 |
| Tree depth        |     8 |
| L2 regularization |     3 |

These parameters define the current model specification implemented in the repository.

---

## 5. Forecasting Framework

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
```

The recursive structure is important because the forecasting horizon extends substantially beyond the final observed year.

---

## Model Evaluation

The implemented pipeline evaluates the CatBoost model using a separate test set.

The current execution produced the following results:

Metric	Result
Training observations	3,454
Test observations	725
Total observations	4,179
Test \(R^2\)	0.9995

The reported \(R^2\) indicates that the model explains approximately 99.95% of the variance in the held-out test observations under the current evaluation procedure.

Important: The reported \(R^2\) should not be interpreted as 99.95% forecasting accuracy. Model performance is dependent on the train/test splitting strategy and the temporal structure of the panel data.

For a forecasting application, temporal out-of-sample validation is particularly important because randomly splitting country-year observations can allow information from later periods to enter the training set while earlier periods are evaluated in the test set. Future versions of the project should therefore include strict time-based validation to provide a more rigorous assessment of long-horizon forecasting performance.

---

## Historical Analysis and Visualization

The repository includes interactive visualizations designed to examine both the geographic and temporal dimensions of economic complexity.

### Global ECI Maps

Interactive choropleth dashboards are provided for:

* 2020
* 2021
* 2022
* 2023

These maps display country-level ECI values and provide a geographic view of the global distribution of economic complexity.

The dashboards also include comparisons of the highest- and lowest-ranked economies.

![Global Dashboard 2023](image_33db6b.png)

### Historical ECI Trajectories

The repository also includes an interactive visualization comparing the trajectories of selected high- and low-complexity economies over 1995–2023.

The timeline allows users to examine how the relative positions of countries changed over time.

![Interactive Top/Bottom 7](image_33dc28.png)


---


## Interpretation of Forecasts

The 2024–2050 values generated by this repository should be interpreted as **model-based projections rather than official forecasts of future economic complexity**.

Long-term ECI trajectories can be affected by factors that are difficult to infer from historical ECI alone, including:

* structural changes in international trade;
* technological development;
* industrial policy;
* geopolitical shocks;
* changes in global production networks;
* resource discoveries and depletion;
* institutional changes;
* major economic crises.

The recursive forecasting design also means that prediction uncertainty can accumulate over longer horizons because forecasts become inputs for subsequent predictions.

Consequently, the 2050 projections should be interpreted primarily as **scenario-like model outputs conditional on historical patterns**, rather than deterministic predictions of future economic outcomes.

---

## 11. Limitations and Future Research

Several extensions could improve the empirical framework.

### Additional Economic Predictors

The current framework is primarily based on historical ECI dynamics. Future versions could incorporate additional country-level variables such as:

* GDP per capita;
* trade openness;
* export diversification;
* R&D expenditure;
* human capital and etc.

### Alternative Forecasting Models

Model performance could also be compared with alternative approaches, including:

* XGBoost;
* Random Forest;
* panel regression models, and etc.


### Out-of-Sample Evaluation

A particularly important extension is systematic temporal validation, in which earlier years are used for training and later observed years are reserved for testing.



```text
Training:   1995–2018
Test:       2019–2023
```

Such evaluation would provide a more rigorous assessment of the model's ability to generalize to unseen future periods.

### Uncertainty Quantification

Future versions could additionally report prediction intervals or alternative forecast scenarios rather than presenting point forecasts alone.



---

## 13. Citation and Data Source

Historical ECI data are obtained from the **Harvard Growth Lab's Atlas of Economic Complexity**.

Users of this repository should cite the underlying Atlas of Economic Complexity and the relevant methodological publications associated with the ECI measure when using the dataset or derived results in academic work.

Data source:

[Harvard Growth Lab — Atlas of Economic Complexity](https://atlas.hks.harvard.edu/)

---

## 14. License

This project is released under the **MIT License**.

See the `LICENSE` file for the complete license text.
