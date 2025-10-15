from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# --- SETUP SELENIUM ---
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# --- LOAD YEAR LINKS ---
years_df = pd.read_csv("data/years.csv")

stats_data = []

# --- LOOP THROUGH ALL YEARS (skip failures safely) ---
for index, row in years_df.iterrows():
    year = row["Year"]
    url = row["URL"]

    try:
        print(f"Scraping stats for {year}...")
        driver.get(url)
        time.sleep(2)

        # --- Locate stat tables ---
        tables = driver.find_elements(By.TAG_NAME, "table")

        for table in tables:
            # --- Try multiple tag types to detect category name ---
            category = "General Statistics"
            try:
                category = table.find_element(By.XPATH, "preceding-sibling::b[1]").text.strip()
            except:
                try:
                    category = table.find_element(By.XPATH, "preceding-sibling::font[1]").text.strip()
                except:
                    try:
                        category = table.find_element(By.XPATH, "preceding-sibling::center[1]").text.strip()
                    except:
                        pass

            # --- Extract all rows from the table ---
            rows = table.find_elements(By.TAG_NAME, "tr")

            for r in rows[1:]:  # skip header row
                cols = r.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 2:
                    player = cols[0].text.strip()
                    value = cols[1].text.strip()
                    if player and value:
                        stats_data.append({
                            "Year": year,
                            "Category": category,
                            "Player": player,
                            "Value": value
                        })

        # ---  Save a backup every 25 years scraped ---
        if index % 25 == 0 and index > 0:
            pd.DataFrame(stats_data).to_csv("data/statistics_partial.csv", index=False)
            print(f" Backup saved after {index} years scraped...")

    except Exception as e:
        print(f"⚠️ Skipping {year} due to error: {e}")
        continue

driver.quit()

# --- SAVE FINAL DATA TO CSV ---
df_stats = pd.DataFrame(stats_data)
df_stats.to_csv("data/statistics.csv", index=False)

print("\n Saved data/statistics.csv with player statistics")
print(f"Total records collected: {len(df_stats)}")
print(" Preview:")
print(df_stats.head(10))
