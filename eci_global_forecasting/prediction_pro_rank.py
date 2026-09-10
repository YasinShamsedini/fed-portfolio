#!/usr/bin/env python
"""
ECI HS92 Forecasting (1995–2050) – Enhanced Features + Annual Ranking + Country Names

- Reads all_rankings.xlsx
- Builds:
    * trend
    * 5 lag features (eci_lag1..eci_lag5)
    * rolling mean (3y, 5y)
    * rolling std (3y)
    * first difference (eci_diff_1)
- Uses CatBoostRegressor (high accuracy)
- Train/test split: train <= 2018
- Computes R², RMSE, MAE
- Recursive forecast for 2024–2050
- Adds: full country names (country)
- Adds: annual ECI ranking for every year
- Saves: eci_full_1995_2050.csv
"""

from __future__ import annotations
import sys
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from catboost import CatBoostRegressor


# =====================================================
# ISO3 → COUNTRY NAMES (FULL LIST FOR 250 COUNTRIES)
# =====================================================

ISO3_TO_NAME = {
    "AFG": "Afghanistan", "AGO": "Angola", "ALB": "Albania", "DZA": "Algeria",
    "AND": "Andorra", "ARG": "Argentina", "ARM": "Armenia", "AUS": "Australia",
    "AUT": "Austria", "AZE": "Azerbaijan", "BHR": "Bahrain", "BGD": "Bangladesh",
    "BRB": "Barbados", "BLR": "Belarus", "BEL": "Belgium", "BLZ": "Belize",
    "BEN": "Benin", "BTN": "Bhutan", "BOL": "Bolivia", "BIH": "Bosnia & Herzegovina",
    "BWA": "Botswana", "BRA": "Brazil", "BRN": "Brunei", "BGR": "Bulgaria",
    "BFA": "Burkina Faso", "BDI": "Burundi", "KHM": "Cambodia", "CMR": "Cameroon",
    "CAN": "Canada", "CAF": "Central African Republic", "TCD": "Chad",
    "CHL": "Chile", "CHN": "China", "COL": "Colombia", "COG": "Congo",
    "CRI": "Costa Rica", "CIV": "Côte d’Ivoire", "HRV": "Croatia", "CYP": "Cyprus",
    "CZE": "Czechia", "DNK": "Denmark", "DJI": "Djibouti", "DMA": "Dominica",
    "DOM": "Dominican Republic", "ECU": "Ecuador", "EGY": "Egypt", "SLV": "El Salvador",
    "EST": "Estonia", "ETH": "Ethiopia", "FIN": "Finland", "FRA": "France",
    "GAB": "Gabon", "GMB": "Gambia", "GEO": "Georgia", "DEU": "Germany",
    "GHA": "Ghana", "GRC": "Greece", "GTM": "Guatemala", "GIN": "Guinea",
    "HTI": "Haiti", "HND": "Honduras", "HKG": "Hong Kong", "HUN": "Hungary",
    "ISL": "Iceland", "IND": "India", "IDN": "Indonesia", "IRN": "Iran",
    "IRQ": "Iraq", "IRL": "Ireland", "ISR": "Israel", "ITA": "Italy",
    "JAM": "Jamaica", "JPN": "Japan", "JOR": "Jordan", "KAZ": "Kazakhstan",
    "KEN": "Kenya", "KOR": "South Korea", "KWT": "Kuwait", "KGZ": "Kyrgyzstan",
    "LAO": "Laos", "LVA": "Latvia", "LBN": "Lebanon", "LBY": "Libya",
    "LTU": "Lithuania", "LUX": "Luxembourg", "MDG": "Madagascar", "MWI": "Malawi",
    "MYS": "Malaysia", "MDV": "Maldives", "MLI": "Mali", "MLT": "Malta",
    "MEX": "Mexico", "MDA": "Moldova", "MNG": "Mongolia", "MNE": "Montenegro",
    "MAR": "Morocco", "MOZ": "Mozambique", "MMR": "Myanmar", "NAM": "Namibia",
    "NLD": "Netherlands", "NZL": "New Zealand", "NER": "Niger", "NGA": "Nigeria",
    "NOR": "Norway", "OMN": "Oman", "PAK": "Pakistan", "PAN": "Panama",
    "PRY": "Paraguay", "PER": "Peru", "PHL": "Philippines", "POL": "Poland",
    "PRT": "Portugal", "QAT": "Qatar", "ROU": "Romania", "RUS": "Russia",
    "RWA": "Rwanda", "SAU": "Saudi Arabia", "SEN": "Senegal", "SRB": "Serbia",
    "SGP": "Singapore", "SVK": "Slovakia", "SVN": "Slovenia", "ZAF": "South Africa",
    "ESP": "Spain", "LKA": "Sri Lanka", "SDN": "Sudan", "SWE": "Sweden",
    "CHE": "Switzerland", "SYR": "Syria", "TWN": "Taiwan", "TJK": "Tajikistan",
    "TZA": "Tanzania", "THA": "Thailand", "TUN": "Tunisia", "TUR": "Turkey",
    "UGA": "Uganda", "UKR": "Ukraine", "ARE": "United Arab Emirates",
    "GBR": "United Kingdom", "USA": "United States", "URY": "Uruguay",
    "UZB": "Uzbekistan", "VEN": "Venezuela", "VNM": "Vietnam", "YEM": "Yemen",
    "ZMB": "Zambia", "ZWE": "Zimbabwe"
}


# =====================================================
# CONFIG
# =====================================================

LAG_FEATURES = [f"eci_lag{i}" for i in range(1, 6)]

ROLLING_FEATURES = [
    "eci_roll_mean_3",
    "eci_roll_mean_5",
    "eci_roll_std_3",
    "eci_diff_1",
]

NUMERIC_FEATURES = ["trend"] + LAG_FEATURES + ROLLING_FEATURES
CATEGORICAL_FEATURES = ["iso3"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

FILE_INPUT = "all_rankings.xlsx"
FILE_OUTPUT = "eci_full_1995_2050.csv"

TRAIN_CUTOFF_YEAR = 2018
FORECAST_START_YEAR = 2024
FORECAST_END_YEAR = 2050


# =====================================================
# LOADING & FEATURE ENGINEERING
# =====================================================

def load_and_prepare_data(path: Path) -> pd.DataFrame:
    df_raw = pd.read_excel(path)

    df = (
        df_raw[["country_iso3_code", "year", "eci_hs92"]]
        .rename(columns={"country_iso3_code": "iso3", "eci_hs92": "eci"})
        .copy()
    )

    df["iso3"] = df["iso3"].astype(str).str.upper().str.strip()
    df["country"] = df["iso3"].map(ISO3_TO_NAME).fillna(df["iso3"])

    df["year"] = df["year"].astype(int)
    df["eci"] = pd.to_numeric(df["eci"], errors="coerce")

    df = df.sort_values(["iso3", "year"]).reset_index(drop=True)

    min_year = df["year"].min()
    df["trend"] = df["year"] - min_year

    # Lags
    for lag in range(1, 6):
        df[f"eci_lag{lag}"] = df.groupby("iso3")["eci"].shift(lag)

    # Rolling
    df["eci_roll_mean_3"] = df.groupby("iso3")["eci"].transform(
        lambda s: s.rolling(3, min_periods=1).mean()
    )
    df["eci_roll_mean_5"] = df.groupby("iso3")["eci"].transform(
        lambda s: s.rolling(5, min_periods=1).mean()
    )
    df["eci_roll_std_3"] = df.groupby("iso3")["eci"].transform(
        lambda s: s.rolling(3, min_periods=2).std()
    ).fillna(0)
    df["eci_diff_1"] = df.groupby("iso3")["eci"].diff()

    return df


# =====================================================
# TRAIN / TEST SPLIT
# =====================================================

def split_train_test(df):
    valid = df.dropna(subset=["eci"])
    train = valid[valid["year"] <= TRAIN_CUTOFF_YEAR]
    test = valid[valid["year"] > TRAIN_CUTOFF_YEAR]
    return train[FEATURE_COLUMNS], train["eci"], test[FEATURE_COLUMNS], test["eci"], df


# =====================================================
# RECURSIVE FORECAST
# =====================================================

def recursive_forecast(model, df):
    min_year = df["year"].min()
    hist = df.sort_values(["iso3", "year"]).copy()

    forecasts = []
    last_rows = hist.dropna(subset=["eci"]).groupby("iso3").tail(1)

    for _, last in last_rows.iterrows():
        iso = last["iso3"]
        cname = last["country"]

        c_hist = hist[hist["iso3"] == iso].copy()
        last_year = int(c_hist["year"].max())
        start = max(FORECAST_START_YEAR, last_year + 1)

        for year in range(start, FORECAST_END_YEAR + 1):
            row = {"iso3": iso, "country": cname, "year": year}
            row["trend"] = year - min_year

            vals = c_hist["eci"].dropna().tolist()
            s = pd.Series(vals)

            for lag in range(1, 6):
                row[f"eci_lag{lag}"] = vals[-lag] if len(vals) >= lag else np.nan

            row["eci_roll_mean_3"] = s.tail(3).mean() if len(s) else np.nan
            row["eci_roll_mean_5"] = s.tail(5).mean() if len(s) else np.nan
            row["eci_roll_std_3"] = s.tail(3).std(ddof=1) if len(s) >= 2 else 0
            row["eci_diff_1"] = s.iloc[-1] - s.iloc[-2] if len(s) >= 2 else np.nan

            pred = float(model.predict(pd.DataFrame([row])[FEATURE_COLUMNS])[0])

            forecasts.append({"iso3": iso, "country": cname, "year": year, "eci_pred": pred})

            # Append predicted value to history
            c_hist = pd.concat(
                [c_hist, pd.DataFrame([{"iso3": iso, "country": cname, "year": year, "eci": pred}])],
                ignore_index=True
            )

    return pd.DataFrame(forecasts)


# =====================================================
# MERGE ACTUAL + PREDICTED + RANK
# =====================================================

def merge_full(df_actual, df_pred):
    df_actual = df_actual[["iso3", "country", "year", "eci"]].copy()
    df_actual["eci_pred"] = np.nan
    df_actual["source"] = "actual"

    df_pred = df_pred.copy()
    df_pred["eci"] = np.nan
    df_pred["source"] = "predicted"

    full = pd.concat([df_actual, df_pred], ignore_index=True)
    full = full.sort_values(["iso3", "year"]).reset_index(drop=True)

    full["eci_final"] = full["eci_pred"].fillna(full["eci"])

    full["eci_rank"] = (
        full.groupby("year")["eci_final"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    return full


# =====================================================
# MAIN
# =====================================================

def main():
    print("Loading data...")
    df = load_and_prepare_data(Path(FILE_INPUT))

    X_train, y_train, X_test, y_test, df_all = split_train_test(df)
    print(f"Train rows: {len(X_train)}")
    print(f"Test rows : {len(X_test)}")

    model = CatBoostRegressor(
        loss_function="RMSE",
        iterations=2000,
        learning_rate=0.03,
        depth=8,
        l2_leaf_reg=3,
        random_seed=42,
        verbose=False,
        cat_features=[FEATURE_COLUMNS.index("iso3")],
    )

    print("Training model...")
    model.fit(X_train, y_train)

    if len(X_test) > 0:
        pred = model.predict(X_test)
        r2 = r2_score(y_test, pred)
        rmse = mean_squared_error(y_test, pred)**0.5
        mae = mean_absolute_error(y_test, pred)

        print("\n=== MODEL ACCURACY ===")
        print(f"R²   : {r2:.4f}")
        print(f"RMSE : {rmse:.4f}")
        print(f"MAE  : {mae:.4f}")
        print("======================\n")

    print("Forecasting future...")
    df_pred = recursive_forecast(model, df_all)

    print("Merging + ranking...")
    df_full = merge_full(df_all, df_pred)

    df_full.to_csv(FILE_OUTPUT, index=False)
    print(f"\nDONE! Saved: {FILE_OUTPUT}")


if __name__ == "__main__":
    main()



# در این کار پژوهشی، داده‌های پانلی شاخص پیچیدگی اقتصادی (ECI) برای کشورهای جهان مورد پردازش و ساختاردهی قرار گرفت. مجموعه‌ای از ویژگی‌های زمانی شامل Lag، میانگین‌های متحرک، انحراف معیارهای متحرک و تفاضل‌های سالانه به‌عنوان مهندسی ویژگی به داده‌ها افزوده شد تا پویایی‌های سری زمانی شاخص بهتر نمایان شود. یک مدل CatBoost پانلی با دقت بالا آموزش داده شد و با به‌کارگیری روش Recursive Multi-Step Forecasting، مقادیر ECI کشورهای جهان برای دورهٔ ۲۰۲۴ تا ۲۰۵۰ برآورد گردید. در گام نهایی، داده‌های تاریخی و پیش‌بینی‌شده برای دورهٔ ۱۹۹۵ تا ۲۰۵۰ ادغام و رتبه‌بندی جهانی کشورها بر اساس ECI برای هر سال تولید شد.در این کار پژوهشی، داده‌های پانلی شاخص پیچیدگی اقتصادی (ECI) برای کشورهای جهان مورد پردازش و ساختاردهی قرار گرفت. مجموعه‌ای از ویژگی‌های زمانی شامل Lag، میانگین‌های متحرک، انحراف معیارهای متحرک و تفاضل‌های سالانه به‌عنوان مهندسی ویژگی به داده‌ها افزوده شد تا پویایی‌های سری زمانی شاخص بهتر نمایان شود. یک مدل CatBoost پانلی با دقت بالا آموزش داده شد و با به‌کارگیری روش Recursive Multi-Step Forecasting، مقادیر ECI کشورهای جهان برای دورهٔ ۲۰۲۴ تا ۲۰۵۰ برآورد گردید. در گام نهایی، داده‌های تاریخی و پیش‌بینی‌شده برای دورهٔ ۱۹۹۵ تا ۲۰۵۰ ادغام و رتبه‌بندی جهانی کشورها بر اساس ECI برای هر سال تولید شد.