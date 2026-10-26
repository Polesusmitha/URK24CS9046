import pandas as pd

df = pd.read_csv("data/rice_dose_labeled.csv")

# Baseline: every field gets the highest TNAU dose (40 P2O5, 80 K2O)
baseline = 6745.0

df["baseline_cost_inr_per_ha"] = baseline
df["saving_inr_per_ha"] = baseline - df["cost_inr_per_ha"]
df["saving_pct"] = (df["saving_inr_per_ha"] / baseline * 100).round(1)

print("Mean saving per ha (INR):", round(df["saving_inr_per_ha"].mean()))
print("Mean saving (%):", round(df["saving_pct"].mean(), 1))
print("Fields with no saving:", int((df["saving_inr_per_ha"] == 0).sum()))

df.to_csv("data/rice_final.csv", index=False)
print("Saved", len(df), "rows to data/rice_final.csv")