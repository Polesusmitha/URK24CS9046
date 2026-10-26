import requests
import pandas as pd
from io import StringIO

URL = "https://agritech.tnau.ac.in/agriculture/agri_Nutrient_%20P_K_fSSNM%20based.html"

headers = {"User-Agent": "Mozilla/5.0 (student project)"}
r = requests.get(URL, headers=headers, timeout=60)
r.raise_for_status()

# Keep the raw page as proof of scraping
with open("data/raw/tnau_ssnm_rice.html", "w", encoding="utf-8") as f:
    f.write(r.text)

# Try to read HTML tables
try:
    tables = pd.read_html(StringIO(r.text))
except ValueError:
    tables = []

print("Tables found:", len(tables))
for i, t in enumerate(tables):
    print("--- table", i, "shape", t.shape)
    print(t.head(15))
    t.to_csv(f"data/raw/tnau_ssnm_table{i}.csv", index=False)