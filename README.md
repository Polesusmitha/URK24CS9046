\# Sustainable Fertilizer Usage Optimizer (SIH1639)



Register number: URK24CS9046



\## Problem

Recommend a suitable crop from soil and weather data, and for rice give a

fertilizer dose (P2O5, K2O) and cost per hectare that reduces over-application.



\## Data sources

\- Crop Recommendation Dataset (Kaggle, Atharva Ingle): 2200 rows, 22 crops. Downloaded, not scraped. Not specific to Tamil Nadu.

\- TNAU Agritech SSNM rice P2O5 and K2O doses for 12 Tamil Nadu locations (web scraped, updated Jan 2023).

\- Weather data for Tamil Nadu from NASA POWER (web scraped, data\\raw\\weather.csv). Used as supporting evidence of local conditions. The crop model uses the weather columns from the Kaggle dataset.

\- Fertilizer prices: Lok Sabha Unstarred Question No. 878, answered 26 July 2024,

&#x20; Ministry of Chemicals and Fertilizers, state-wise average selling prices 2023-24 (Tamil Nadu). Taken from an official document, not scraped.



\## Method

1\. Cleaned data (no missing values or duplicates) and labelled N, P, K as Low/Medium/High by thirds of the dataset, and pH as Acidic/Neutral/Alkaline.

2\. Built a rule: the TNAU dose range is applied by soil level (Low = highest dose, Medium = median, High = lowest).

3\. Cost per hectare = P2O5 dose x cost per kg P2O5 (from DAP) + K2O dose x cost per kg K2O (from MOP).

4\. Trained Logistic Regression, KNN and Random Forest for crop recommendation (5-fold cross-validation, 80/20 split).



\## Results

\- Random Forest: 99.4% CV accuracy, 99.5% test accuracy, macro F1 0.995.

\- Logistic Regression 96.8% and KNN 96.5% (CV).

\- Most important features: rainfall, humidity, K.

\- Rice (100 samples): mean fertilizer saving Rs 2126 per hectare (31.5%) against a baseline where every field gets the highest TNAU dose.

\- Predicting rice P level from weather, pH and N gave 33% accuracy (chance), so P and K need a soil test.



\## Limitations

\- The Kaggle data is not from Tamil Nadu, and its N, P, K values are not in kg/ha, so levels are relative to the dataset.

\- The dose is a rule based on the TNAU range, not a trained model, and nitrogen is not included.

\- The savings baseline is an assumption.

\- P cost uses DAP, which also supplies nitrogen, so it is slightly overstated.

\- Scores near 99% reflect a very clean dataset and are not field accuracy.



\## How to run

Scraping (needs internet, outputs go to data\\raw):



&#x20;   python scraper\\get\_npk\_doses.py

&#x20;   python scraper\\get\_weather.py

&#x20;   python src\\clean\_ssnm.py



Analysis:



&#x20;   python src\\make\_prices.py

&#x20;   python src\\make\_soil.py

&#x20;   python src\\make\_rice\_doses.py

&#x20;   python src\\make\_savings.py

&#x20;   python src\\eda.py

&#x20;   python src\\train.py

&#x20;   python src\\predict.py 90 42 43 20.9 82 6.5 203







python -m streamlit run src\\dashboard.py



Arguments for predict.py: N P K temperature humidity ph rainfall.

