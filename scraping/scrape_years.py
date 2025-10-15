from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # 👈 ensures correct ChromeDriver
import pandas as pd
import time

# --- SETUP SELENIUM ---
options = Options()
options.add_argument("--headless")  # run Chrome invisibly
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())  # auto-manages driver
driver = webdriver.Chrome(service=service, options=options)

# --- SCRAPE ALL YEAR LINKS ---
base_url = "https://www.baseball-almanac.com/yearmenu.shtml"
driver.get(base_url)
time.sleep(3)

year_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='yearly/yr']")
years = []
links = []

for link in year_links:
    year_text = link.text.strip()
    href = link.get_attribute("href")
    if year_text.isdigit():  # keep only links that are numeric years
        years.append(year_text)
        links.append(href)

driver.quit()

# --- QUICK CHECK ---
print("\n Preview of scraped results:")
for i in range(min(5, len(years))):
    print(f"{years[i]} → {links[i]}")

print(f"\nTotal years scraped: {len(years)}")

# --- SAVE TO CSV ---
df_links = pd.DataFrame({"Year": years, "URL": links})
df_links.to_csv("data/years.csv", index=False)
print("\n Saved data/years.csv with all yearly links")
