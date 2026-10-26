import pandas as pd

df = pd.read_csv("data/Crop_recommendation.csv")
print("Rows:", len(df))
print("Columns:", list(df.columns))
print("Missing values:", int(df.isna().sum().sum()))
print("Duplicate rows:", int(df.duplicated().sum()))

df = df.drop_duplicates().reset_index(drop=True)

# Low / Medium / High for N, P, K, split into thirds of this dataset
for col in ["N", "P", "K"]:
    df[col + "_level"] = pd.qcut(
        df[col], q=3, labels=["Low", "Medium", "High"], duplicates="drop"
    )

# pH class using the standard soil reaction ranges
def ph_class(ph):
    if ph < 6.5:
        return "Acidic"
    if ph <= 7.5:
        return "Neutral"
    return "Alkaline"

df["pH_class"] = df["ph"].apply(ph_class)

df.to_csv("data/soil_labeled.csv", index=False)
print(df.head().to_string())
print()
print(df["N_level"].value_counts())
print(df["pH_class"].value_counts())
print("Saved", len(df), "rows to data/soil_labeled.csv")