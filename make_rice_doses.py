import pandas as pd

doses = pd.read_csv("data/rice_ssnm_doses.csv")
prices = pd.read_csv("data/fertilizer_prices.csv").set_index("fertilizer")

# TNAU range for P2O5 and K2O across the 12 rice locations
ref = {}
for col in ["P2O5_kg_ha", "K2O_kg_ha"]:
    ref[col] = {
        "Low": doses[col].max(),
        "Medium": doses[col].median(),
        "High": doses[col].min(),
    }
print("TNAU reference doses:", ref)

soil = pd.read_csv("data/soil_labeled.csv")
rice = soil[soil["label"] == "rice"].copy()

# Low / Medium / High for P and K within the rice samples only
names = ["Low", "Medium", "High"]
for col in ["P", "K"]:
    rice[col + "_level_rice"] = pd.qcut(
        rice[col].rank(method="first"), q=3, labels=names
    ).astype(str)

rice["P2O5_dose_kg_ha"] = rice["P_level_rice"].map(ref["P2O5_kg_ha"])
rice["K2O_dose_kg_ha"] = rice["K_level_rice"].map(ref["K2O_kg_ha"])

# Cost per kg of nutrient: P from DAP, K from MOP
p_cost = prices.loc["DAP", "cost_per_kg_main_nutrient_inr"]
k_cost = prices.loc["MOP", "cost_per_kg_main_nutrient_inr"]
rice["cost_inr_per_ha"] = (
    rice["P2O5_dose_kg_ha"] * p_cost + rice["K2O_dose_kg_ha"] * k_cost
).round(0)

rice.to_csv("data/rice_dose_labeled.csv", index=False)
print(rice[["N", "P", "K", "P_level_rice", "K_level_rice",
            "P2O5_dose_kg_ha", "K2O_dose_kg_ha", "cost_inr_per_ha"]].head().to_string())
print()
print(rice["P_level_rice"].value_counts())
print(rice["cost_inr_per_ha"].describe().round(0).to_string())
print("Saved", len(rice), "rows to data/rice_dose_labeled.csv")