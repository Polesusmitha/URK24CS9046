import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)
soil = pd.read_csv("data/soil_labeled.csv")
rice = pd.read_csv("data/rice_final.csv")

# Plot 1: N, P, K for every crop (boxplots)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, col in zip(axes, ["N", "P", "K"]):
    order = soil.groupby("label")[col].median().sort_values().index
    data = [soil[soil["label"] == c][col] for c in order]
    ax.boxplot(data, tick_labels=order, vert=False)
    ax.set_title(col + " by crop")
plt.tight_layout()
plt.savefig("results/1_npk_by_crop.png", dpi=150)
plt.close()

# Plot 2: correlation heatmap for rice samples
cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
corr = rice[cols].corr()
fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(cols)))
ax.set_xticklabels(cols, rotation=45, ha="right")
ax.set_yticks(range(len(cols)))
ax.set_yticklabels(cols)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax.text(j, i, round(corr.iloc[i, j], 2), ha="center", va="center", fontsize=8)
plt.colorbar(im)
ax.set_title("Correlation (rice samples)")
plt.tight_layout()
plt.savefig("results/2_rice_correlation.png", dpi=150)
plt.close()

# Plot 3: fertilizer cost per hectare for rice
plt.figure(figsize=(7, 5))
plt.hist(rice["cost_inr_per_ha"], bins=10, edgecolor="black")
plt.axvline(6745, color="red", linestyle="--", label="Baseline (full dose)")
plt.xlabel("Cost (INR per ha)")
plt.ylabel("Number of fields")
plt.title("Fertilizer cost per hectare, rice")
plt.legend()
plt.tight_layout()
plt.savefig("results/3_cost_histogram.png", dpi=150)
plt.close()

# Plot 4: mean saving by P level
order = ["Low", "Medium", "High"]
means = rice.groupby("P_level_rice")["saving_inr_per_ha"].mean().reindex(order)
plt.figure(figsize=(6, 5))
plt.bar(order, means.values, edgecolor="black")
plt.xlabel("Soil P level")
plt.ylabel("Mean saving (INR per ha)")
plt.title("Saving by soil phosphorus level")
plt.tight_layout()
plt.savefig("results/4_saving_by_p_level.png", dpi=150)
plt.close()

print("Saved 4 plots in the results folder")
print(corr.round(2).to_string())