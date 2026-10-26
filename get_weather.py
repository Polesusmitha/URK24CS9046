import requests
import pandas as pd
import time

districts = {
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Thanjavur": (10.7870, 79.1378),
    "Salem": (11.6643, 78.1460),
    "Tiruchirappalli": (10.7905, 78.7047),
    "Erode": (11.3410, 77.7172),
}

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
frames = []

for name, (lat, lon) in districts.items():
    params = {
        "parameters": "T2M,PRECTOTCORR,RH2M",
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "start": "20220101",
        "end": "20241231",
        "format": "JSON",
    }
    print("Downloading", name)
    r = requests.get(URL, params=params, timeout=120)
    r.raise_for_status()
    data = r.json()["properties"]["parameter"]

    df = pd.DataFrame(data)
    df.index.name = "date"
    df = df.reset_index()
    df["district"] = name
    frames.append(df)
    time.sleep(2)

weather = pd.concat(frames, ignore_index=True)
weather = weather.rename(columns={
    "T2M": "temperature_c",
    "PRECTOTCORR": "rainfall_mm",
    "RH2M": "humidity_pct",
})
weather = weather.replace(-999, pd.NA)
weather.to_csv("data/raw/weather.csv", index=False)
print("Saved", len(weather), "rows to data/raw/weather.csv")