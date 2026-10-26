import os
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Fertilizer Optimizer", layout="wide")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def path(*p):
    return os.path.join(BASE, *p)

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

@st.cache_data
def load():
    soil = pd.read_csv(path("data", "soil_labeled.csv"))
    rice = pd.read_csv(path("data", "rice_final.csv"))
    doses = pd.read_csv(path("data", "rice_ssnm_doses.csv"))
    prices = pd.read_csv(path("data", "fertilizer_prices.csv"))
    return soil, rice, doses, prices

@st.cache_resource
def train(_soil):
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(_soil[FEATURES], _soil["label"])
    return model

soil, rice, doses, prices = load()
model = train(soil)
price_idx = prices.set_index("fertilizer")
p_cost = price_idx.loc["DAP", "cost_per_kg_main_nutrient_inr"]
k_cost = price_idx.loc["MOP", "cost_per_kg_main_nutrient_inr"]
baseline = doses["P2O5_kg_ha"].max() * p_cost + doses["K2O_kg_ha"].max() * k_cost

def level(value, series):
    lo, hi = series.quantile([1 / 3, 2 / 3])
    if value <= lo:
        return "Low"
    return "Medium" if value <= hi else "High"

st.title("Sustainable Fertilizer Usage Optimizer")
st.caption("SIH1639 | URK24CS9046 | Crop recommendation and TNAU-range fertilizer plan for rice")

# Sidebar inputs
st.sidebar.header("Soil and weather input")
defaults = {"N": 90, "P": 42, "K": 43, "temperature": 20.9,
            "humidity": 82.0, "ph": 6.5, "rainfall": 203.0}
values = {}
for f in FEATURES:
    lo, hi = float(soil[f].min()), float(soil[f].max())
    values[f] = st.sidebar.slider(f, lo, hi, float(defaults[f]))

tab1, tab2, tab3, tab4 = st.tabs(
    ["Recommend", "Rice savings", "Model results", "Data"])

with tab1:
    x = pd.DataFrame([[values[f] for f in FEATURES]], columns=FEATURES)
    proba = model.predict_proba(x)[0]
    top = sorted(zip(model.classes_, proba), key=lambda t: -t[1])[:3]

    st.subheader("Top 3 recommended crops")
    cols = st.columns(3)
    for c, (crop, p) in zip(cols, top):
        c.metric(crop, f"{p * 100:.0f}%")

    if top[0][0] == "rice":
        p_lvl = level(values["P"], rice["P"])
        k_lvl = level(values["K"], rice["K"])
        p_ref = {"Low": doses["P2O5_kg_ha"].max(),
                 "Medium": doses["P2O5_kg_ha"].median(),
                 "High": doses["P2O5_kg_ha"].min()}
        k_ref = {"Low": doses["K2O_kg_ha"].max(),
                 "Medium": doses["K2O_kg_ha"].median(),
                 "High": doses["K2O_kg_ha"].min()}
        p_dose, k_dose = p_ref[p_lvl], k_ref[k_lvl]
        cost = p_dose * p_cost + k_dose * k_cost

        st.subheader("Rice fertilizer plan (rule based on TNAU range)")
        a, b, c, d = st.columns(4)
        a.metric("P2O5 dose", f"{p_dose:.0f} kg/ha", f"soil P: {p_lvl}", delta_color="off")
        b.metric("K2O dose", f"{k_dose:.0f} kg/ha", f"soil K: {k_lvl}", delta_color="off")
        c.metric("Cost", f"Rs {cost:.0f} per ha")
        d.metric("Saving vs full dose", f"Rs {baseline - cost:.0f} per ha")
    else:
        st.info("Dose and cost are only available for rice, because the TNAU data covers rice.")

with tab2:
    st.subheader("Rice: fertilizer cost and saving")
    a, b, c = st.columns(3)
    a.metric("Mean cost", f"Rs {rice['cost_inr_per_ha'].mean():.0f} per ha")
    b.metric("Mean saving", f"Rs {rice['saving_inr_per_ha'].mean():.0f} per ha")
    c.metric("Mean saving", f"{rice['saving_pct'].mean():.1f} %")
    st.caption(f"Baseline assumption: every field gets the highest TNAU dose (Rs {baseline:.0f} per ha).")

    counts, edges = np.histogram(rice["cost_inr_per_ha"], bins=10)
    hist = pd.DataFrame({"fields": counts},
                        index=[f"{int(edges[i])}-{int(edges[i + 1])}" for i in range(len(counts))])
    st.write("Fields by cost per hectare (Rs)")
    st.bar_chart(hist)

    by_p = rice.groupby("P_level_rice")["saving_inr_per_ha"].mean().reindex(["Low", "Medium", "High"])
    st.write("Mean saving by soil phosphorus level (Rs per ha)")
    st.bar_chart(by_p)

with tab3:
    st.subheader("Model results")
    metrics_path = path("results", "metrics.txt")
    if os.path.exists(metrics_path):
        st.code(open(metrics_path).read())
    st.caption("Accuracy near 99% reflects a very clean dataset, not field accuracy. "
               "The rice P-level check scored at chance (0.33): P and K need a soil test.")
    c1, c2 = st.columns(2)
    for col, name, cap in [(c1, "5_confusion_matrix.png", "Confusion matrix"),
                           (c2, "6_feature_importance.png", "Feature importance")]:
        p = path("results", name)
        if os.path.exists(p):
            col.image(p, caption=cap)

with tab4:
    st.subheader("Fertilizer prices (Lok Sabha Unstarred Q. 878, 26 July 2024, Tamil Nadu 2023-24)")
    st.dataframe(prices)
    st.subheader("TNAU SSNM rice doses (scraped)")
    st.dataframe(doses)
    st.subheader("Crops in the soil dataset")
    st.bar_chart(soil["label"].value_counts())