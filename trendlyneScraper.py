# scrapeBankingCompaniesTrendlyne

import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

BASE_URL = "https://trendlyne.com"
SECTOR_URL = f"{BASE_URL}/equity/sector/21/banking-and-finance/"
CSV_FILENAME = "banking_companies.csv"

# Set up headless browser
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(SECTOR_URL)

# Allow page to load and select 'All'
time.sleep(3)
dropdown = Select(driver.find_element("name", "DataTables_Table_1_length"))
dropdown.select_by_visible_text("All")

# Wait for full table to render
time.sleep(5)

# Parse the page
soup = BeautifulSoup(driver.page_source, "html.parser")
rows = soup.select("td.fs09rem.w-table-first a.stockrow")

# Write to CSV
with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Company Name", "URL"])
    for link in rows:
        name = link.text.strip()
        url = BASE_URL + link["href"]
        writer.writerow([name, url])

driver.quit()
print(f"Scraping completed. Data saved to {CSV_FILENAME}")
