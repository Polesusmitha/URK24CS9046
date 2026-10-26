import argparse
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
ap = argparse.ArgumentParser(description="Crop and fertilizer recommendation")
for name in features:
    ap.add_argument(name, type=float)
args = ap.parse_args()

soil = pd.read_csv("data/soil_labeled.csv")
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(soil[features], soil["label"])

x = pd.DataFrame([[getattr(args, f) for f in features]], columns=features)
proba = model.predict_proba(x)[0]
top = sorted(zip(model.classes_, proba), key=lambda t: -t[1])[:3]

print("Top 3 recommended crops:")
for crop, p in top:
    print(f"  {crop}: {p * 100:.0f}%")

if top[0][0] == "rice":
    rice = pd.read_csv("data/rice_final.csv")
    doses = pd.read_csv("data/rice_ssnm_doses.csv")
    prices = pd.read_csv("data/fertilizer_prices.csv").set_index("fertilizer")

    def level(value, series):
        lo, hi = series.quantile([1 / 3, 2 / 3])
        if value <= lo:
            return "Low"
        return "Medium" if value <= hi else "High"

    p_lvl = level(args.P, rice["P"])
    k_lvl = level(args.K, rice["K"])
    ref = {
        "P": {"Low": doses["P2O5_kg_ha"].max(), "Medium": doses["P2O5_kg_ha"].median(), "High": doses["P2O5_kg_ha"].min()},
        "K": {"Low": doses["K2O_kg_ha"].max(), "Medium": doses["K2O_kg_ha"].median(), "High": doses["K2O_kg_ha"].min()},
    }
    p_dose = ref["P"][p_lvl]
    k_dose = ref["K"][k_lvl]
    cost = (p_dose * prices.loc["DAP", "cost_per_kg_main_nutrient_inr"]
            + k_dose * prices.loc["MOP", "cost_per_kg_main_nutrient_inr"])
    saving = 6745 - cost

    print()
    print("Rice fertilizer plan (rule based on TNAU range):")
    print(f"  Soil P level: {p_lvl}, P2O5 dose: {p_dose:.0f} kg/ha")
    print(f"  Soil K level: {k_lvl}, K2O dose: {k_dose:.0f} kg/ha")
    print(f"  Cost: Rs {cost:.0f} per ha, saving vs full dose: Rs {saving:.0f}")
else:
    print()
    print("Dose and cost are only available for rice (TNAU data covers rice).")