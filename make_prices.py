import pandas as pd

data = [
    ("Urea", 45, 242.00, 46, 0, 0),
    ("DAP", 50, 1331.26, 18, 46, 0),
    ("MOP", 50, 1661.24, 0, 0, 60),
    ("SSP", 50, 531.66, 0, 16, 0),
]

df = pd.DataFrame(data, columns=[
    "fertilizer", "bag_kg", "price_per_bag_inr", "N_pct", "P2O5_pct", "K2O_pct"
])

df["price_per_kg_inr"] = (df["price_per_bag_inr"] / df["bag_kg"]).round(2)

def cost_per_kg_nutrient(row):
    if row["fertilizer"] == "Urea":
        return round(row["price_per_kg_inr"] / (row["N_pct"] / 100), 2)
    if row["fertilizer"] == "MOP":
        return round(row["price_per_kg_inr"] / (row["K2O_pct"] / 100), 2)
    return round(row["price_per_kg_inr"] / (row["P2O5_pct"] / 100), 2)

df["cost_per_kg_main_nutrient_inr"] = df.apply(cost_per_kg_nutrient, axis=1)
df["source"] = "Lok Sabha reply AU878 (eparlib.nic.in)"

df.to_csv("data/fertilizer_prices.csv", index=False)
print(df.to_string())
print("Saved", len(df), "rows to data/fertilizer_prices.csv")