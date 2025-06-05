# scrapeRecentHDFCResearchReports

import csv
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

REPORT_URL = "https://trendlyne.com/research-reports/stock/533/HDFCBANK/hdfc-bank-ltd/"
CSV_FILENAME = "hdfc_recent_reports.csv"

# Setup headless browser
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(REPORT_URL)

# Let JavaScript render
time.sleep(5)

# Parse the full table
soup = BeautifulSoup(driver.page_source, "html.parser")
rows = soup.select("tbody#allreportsbody tr")

# Filter date cutoff
cutoff_date = datetime.today() - timedelta(days=60)

# Prepare CSV
with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Author", "Upside (%)"])

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        # Extract date from `data-sort`
        date_cell = cells[1]
        date_str = date_cell.get("data-sort", "").strip()
        try:
            report_date = datetime.strptime(date_str, "%d %b %Y")
        except:
            continue

        # Check if date is within last 60 days
        if report_date < cutoff_date:
            continue

        # Extract author
        author_tag = cells[3].find("a")
        author = author_tag.text.strip() if author_tag else ""

        # Extract upside %
        upside_cell = cells[7].text.strip()

        writer.writerow([report_date.strftime("%Y-%m-%d"), author, upside_cell])

driver.quit()
print(f"Scraping completed. Data saved to {CSV_FILENAME}")
