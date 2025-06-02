# scrapeTrendlyneBankingFinanceCompaniesToCSV

import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

BASE_URL = "https://trendlyne.com"
SECTOR_URL = f"{BASE_URL}/equity/sector/21/banking-and-finance/"

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Visit the URL
driver.get(SECTOR_URL)
time.sleep(5)  # wait for full render

# Parse page
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Extract company data
companies = []
rows = soup.select("td.fs09rem.w-table-first a.stockrow")
for link in rows:
    name = link.text.strip()
    full_url = BASE_URL + link["href"]
    companies.append([name, full_url])

# Save to CSV
with open("banking_companies.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Company Name", "URL"])
    writer.writerows(companies)

print("✅ Data saved to banking_companies.csv")
