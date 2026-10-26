import pandas as pd

raw = pd.read_csv("data/raw/tnau_ssnm_table1.csv", header=None)

rows = []
parent = None

for _, r in raw.iterrows():
    loc = str(r[1]).strip()
    c2 = str(r[2]).strip()
    c3 = str(r[3]).strip()

    # skip the saved column-number line (loc is just "1")
    if loc.isdigit():
        continue

    # a parent row repeats its name in all columns (e.g. "Cauvery delta")
    if loc == c2 == c3:
        parent = loc
        continue

    # skip header rows: the dose columns must be numbers
    if not (c2.isdigit() and c3.isdigit()):
        continue

    # sub-rows such as "(i) Old delta" get the parent name in front
    if loc.startswith("(") and parent:
        name = f"{parent} {loc}"
    else:
        name = loc
        parent = None

    rows.append({
        "crop": "Rice",
        "location": name,
        "P2O5_kg_ha": int(c2),
        "K2O_kg_ha": int(c3),
        "source": "TNAU Agritech SSNM (updated Jan 2023)",
    })

clean = pd.DataFrame(rows)
clean.to_csv("data/rice_ssnm_doses.csv", index=False)
print(clean.to_string())
print("Saved", len(clean), "rows to data/rice_ssnm_doses.csv")