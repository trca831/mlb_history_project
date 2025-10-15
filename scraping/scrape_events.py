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

events_data = []

# --- LOOP THROUGH ALL YEARS ---
for index, row in years_df.iterrows():
    year = row["Year"]
    url = row["URL"]

    print(f"Scraping events for {year}...")
    try:
        driver.get(url)
        time.sleep(2)

        # Try different header tags (<b>, <h2>, <h3>, <strong>)
        event_sections = driver.find_elements(By.XPATH, "//b | //h2 | //h3 | //strong")

        for section in event_sections:
            event_name = section.text.strip()

            # Try to find the next paragraph or blockquote as the description
            event_desc = "N/A"
            for tag in ["p", "blockquote", "div"]:
                try:
                    next_elem = section.find_element(By.XPATH, f"following-sibling::{tag}[1]")
                    event_desc = next_elem.text.strip()
                    if event_desc:
                        break
                except:
                    continue

            # Save event if valid
            if event_name and event_desc and event_desc != "N/A":
                events_data.append({
                    "Year": year,
                    "Event": event_name,
                    "Description": event_desc
                })

    except Exception as e:
        print(f"⚠️ Skipping {year} due to error: {e}")
        continue

driver.quit()

# --- SAVE TO CSV ---
df_events = pd.DataFrame(events_data)
df_events.to_csv("data/events.csv", index=False)

print("\n✅ Saved data/events.csv with yearly events and summaries")
print(f"Total records collected: {len(df_events)}")
print("👀 Preview:")
print(df_events.head(10))

