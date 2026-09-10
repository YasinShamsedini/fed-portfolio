# ============================================================
# 🌍 Economic Complexity Dashboard
#  - Rank by eci_rank_hs92
#  - Color by ECI (Green → White → Violet)
#  - Full country names on hover
#  - Interactive zoomable map
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ---------------------------
# STEP 1. Load Excel Data
# ---------------------------
file_path = "FILE_NAME.xlsx"  # 🔹 Change to your Excel file path
df = pd.read_excel(file_path)

# Auto-detect columns
iso_col_candidates  = [c for c in df.columns if "iso" in c.lower()] or ["ISO3"]
eci_col_candidates  = [c for c in df.columns if ("eci_hs" in c.lower()) and ("rank" not in c.lower())]
rank_col_candidates = [c for c in df.columns if "eci_rank_hs92" in c.lower()]

iso_col  = iso_col_candidates[0]
eci_col  = eci_col_candidates[0]
rank_col = rank_col_candidates[0]

df = df[[iso_col, eci_col, rank_col]].copy()
df.columns = ["ISO3", "ECI", "Rank"]

df["ECI"]  = pd.to_numeric(df["ECI"], errors="coerce")
df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
df = df.dropna(subset=["ISO3", "ECI", "Rank"])

# ---------------------------
# STEP 2. ISO3 → Country Names (Gapminder + manual fixes)
# ---------------------------
gm = px.data.gapminder()[["country", "iso_alpha"]].drop_duplicates()
iso_to_name = dict(zip(gm["iso_alpha"], gm["country"]))

manual_names = {
    "TWN": "Taiwan",
    "CIV": "Côte d’Ivoire",
    "COD": "Congo (Democratic Republic)",
    "COG": "Congo (Republic)",
    "SWZ": "Eswatini",
    "LAO": "Lao PDR",
    "RUS": "Russia",
    "VEN": "Venezuela",
    "IRN": "Iran",
    "SYR": "Syria",
    "PRK": "North Korea",
    "KOR": "South Korea",
    "TZA": "Tanzania",
    "AGO": "Angola",
    "BFA": "Burkina Faso",
    "GNQ": "Equatorial Guinea",
    "ARE": "United Arab Emirates",
    "GBR": "United Kingdom",
    "USA": "United States",
}
iso_to_name.update(manual_names)
df["Country"] = df["ISO3"].map(iso_to_name).fillna(df["ISO3"])

print(f"✅ Loaded {len(df)} countries (names mapped)")

# ---------------------------
# STEP 3. Color Scale (Green → White → Violet)
# ---------------------------
ECI_MIN = df["ECI"].min()
ECI_MAX = df["ECI"].max()

ECI_COLORSCALE = [
    [0.0, "#1a9850"],  # green (low/negative)
    [0.5, "#f7f7f7"],  # white (neutral)
    [1.0, "#762a83"]   # violet (high/positive)
]

# ---------------------------
# STEP 4. Prepare subsets (by HS92 rank)
# ---------------------------
top20    = df.sort_values("Rank", ascending=True).head(20)
bottom20 = df.sort_values("Rank", ascending=False).head(20)

# ---------------------------
# STEP 5. Build Dashboard (map + bars)
# ---------------------------
dashboard = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "choropleth", "colspan": 2}, None],
           [{"type": "xy"}, {"type": "xy"}]],
    subplot_titles=("Economic Complexity (Color = ECI)",
                    "Top 20 by HS92 Rank",
                    "Bottom 20 by HS92 Rank")
)

# (A) Choropleth — interactive & hover full names
map_custom = np.stack([df["Country"], df["Rank"], df["ECI"]], axis=-1)
map_trace = go.Choropleth(
    locations=df["ISO3"],
    z=df["ECI"],
    locationmode="ISO-3",
    customdata=map_custom,
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "ECI: %{customdata[2]:.3f}<br>"
        "Rank (HS92): %{customdata[1]}<extra></extra>"
    ),
    coloraxis="coloraxis",
    marker_line_color="white",
    marker_line_width=0.25,
    name=""
)
dashboard.add_trace(map_trace, row=1, col=1)

# (B) Top 20 bar
bar_top = go.Bar(
    x=top20["Country"],
    y=top20["ECI"],
    marker=dict(
        color=top20["ECI"],
        coloraxis="coloraxis2",
        line=dict(color="white", width=0.8)
    ),
    hovertemplate="<b>%{x}</b><br>ECI: %{y:.3f}<extra></extra>",
    name="Top 20",
)
dashboard.add_trace(bar_top, row=2, col=1)

# (C) Bottom 20 bar
bar_bottom = go.Bar(
    x=bottom20["Country"],
    y=bottom20["ECI"],
    marker=dict(
        color=bottom20["ECI"],
        coloraxis="coloraxis3",
        line=dict(color="white", width=0.8)
    ),
    hovertemplate="<b>%{x}</b><br>ECI: %{y:.3f}<extra></extra>",
    name="Bottom 20",
)
dashboard.add_trace(bar_bottom, row=2, col=2)

# ---------------------------
# STEP 6. Layout & Coloraxes
# ---------------------------
dashboard.update_layout(
    template="plotly_white",
    title=dict(
        text="🌐 Economic Complexity Index — Ranked based on HS92 — YEAR: XXXX",
        font=dict(size=22, color="#111", family="Arial Black"),
        x=0.5,  # ✅ Center the title
        xanchor="center"
    ),
    font=dict(family="Segoe UI", size=13, color="#222"),
    height=960,
    paper_bgcolor="#ffffff",
    plot_bgcolor="#fafafa",
    showlegend=False,

    # unified color axes (ECI-based)
    coloraxis=dict(
        colorscale=ECI_COLORSCALE,
        cmin=ECI_MIN, cmax=ECI_MAX,
        colorbar=dict(title="ECI", ticks="")
    ),
    coloraxis2=dict(
        colorscale=ECI_COLORSCALE,
        cmin=ECI_MIN, cmax=ECI_MAX,
        showscale=False
    ),
    coloraxis3=dict(
        colorscale=ECI_COLORSCALE,
        cmin=ECI_MIN, cmax=ECI_MAX,
        showscale=False
    ),

    # 🌍 Enable zoomable, pannable map
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#999",
        showland=True,
        landcolor="rgb(240, 240, 240)",
        projection_type="natural earth",
        fitbounds="locations",   # auto-fit to visible countries
        lonaxis=dict(showgrid=True, gridcolor="rgba(180,180,180,0.3)"),
        lataxis=dict(showgrid=True, gridcolor="rgba(180,180,180,0.3)")
    ),
    dragmode="zoom",  # enable zoom box
    hovermode="closest",
    margin=dict(l=30, r=30, t=80, b=40),
)

# Axis styling
dashboard.update_xaxes(showgrid=False, row=2, col=1)
dashboard.update_yaxes(gridcolor="#e9e9e9", row=2, col=1, title_text="ECI")
dashboard.update_xaxes(showgrid=False, row=2, col=2)
dashboard.update_yaxes(gridcolor="#e9e9e9", row=2, col=2, title_text="ECI")

dashboard.show()

# ---------------------------
# (Optional) Scatter Plot — color by ECI, full names on hover
# ---------------------------
scatter = go.Figure(
    data=[go.Scatter(
        x=df["ECI"],
        y=df["Rank"],
        mode="markers",
        marker=dict(
            size=9,
            color=df["ECI"],
            line=dict(color="white", width=0.8),
            coloraxis="coloraxis"
        ),
        text=df["Country"],
        hovertemplate="<b>%{text}</b><br>ECI: %{x:.3f}<br>Rank (HS92): %{y}<extra></extra>",
        name=""
    )]
)
scatter.update_layout(
    template="plotly_white",
    title=dict(
        text="🌀 ECI vs HS92 Rank — Full Country Names",
        font=dict(size=20, color="#111", family="Arial Black"),
        x=0.5,
        xanchor="center"
    ),
    font=dict(family="Segoe UI", size=13, color="#222"),
    yaxis=dict(autorange="reversed", title="Rank (HS92)", gridcolor="#e9e9e9"),
    xaxis=dict(title="ECI", gridcolor="#e9e9e9"),
    paper_bgcolor="#ffffff",
    plot_bgcolor="#fafafa",
    coloraxis=dict(colorscale=ECI_COLORSCALE, cmin=ECI_MIN, cmax=ECI_MAX)
)
# scatter.show()

# ---------------------------
# (Optional) Export to HTML
# ---------------------------
# dashboard.write_html("eci_dashboard_final.html")
# scatter.write_html("eci_scatter_final.html")
