import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, ConfusionMatrixDisplay

os.makedirs("results", exist_ok=True)
soil = pd.read_csv("data/soil_labeled.csv")
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
X, y = soil[features], soil["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

models = {
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier()),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
lines = ["Crop recommendation, 22 classes (chance = 4.5%)"]
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=cv)
    lines.append(f"{name}: CV accuracy {scores.mean():.3f} (+/- {scores.std():.3f})")

best = models["Random Forest"].fit(X_train, y_train)
pred = best.predict(X_test)
lines.append(f"Random Forest TEST accuracy: {accuracy_score(y_test, pred):.3f}")
lines.append(f"Random Forest TEST macro F1: {f1_score(y_test, pred, average='macro'):.3f}")

fig, ax = plt.subplots(figsize=(12, 12))
ConfusionMatrixDisplay.from_predictions(
    y_test, pred, ax=ax, xticks_rotation=90, colorbar=False
)
plt.tight_layout()
plt.savefig("results/5_confusion_matrix.png", dpi=120)
plt.close()

imp = pd.Series(best.feature_importances_, index=features).sort_values()
plt.figure(figsize=(7, 5))
imp.plot.barh(edgecolor="black")
plt.title("Random Forest feature importance")
plt.tight_layout()
plt.savefig("results/6_feature_importance.png", dpi=150)
plt.close()
lines.append("Feature importance: " + imp.sort_values(ascending=False).round(3).to_dict().__str__())

# Honest check: predict rice P level without using P
rice = pd.read_csv("data/rice_final.csv")
Xr = rice[["N", "K", "temperature", "humidity", "ph", "rainfall"]]
yr = rice["P_level_rice"]
cv_r = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
sr = cross_val_score(RandomForestClassifier(n_estimators=200, random_state=42), Xr, yr, cv=cv_r)
lines.append(f"Rice P-level from other features: CV accuracy {sr.mean():.3f} (chance = 0.33)")

print("\n".join(lines))
with open("results/metrics.txt", "w") as f:
    f.write("\n".join(lines))