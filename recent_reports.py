# scrapeRecentHDFCResearchReportsWithTier

import csv
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

REPORT_URL = "https://trendlyne.com/research-reports/stock/533/HDFCBANK/hdfc-bank-ltd/"
CSV_FILENAME = "hdfc_recent_reports.csv"

TIER_1_BROKERS = {
    "ICICI Securities",
    "Kotak Institutional Equities",
    "HDFC Securities",
    "Motilal Oswal",
    "Axis Capital",
    "JM Financial",
    "Edelweiss Financial Services",
    "IIFL Securities",
    "SBI Capital Markets",
    "BOB Capital Markets (BOBCAPS)",
}

# Setup headless browser
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(REPORT_URL)

# Allow JS content to load
time.sleep(5)

# Parse content
soup = BeautifulSoup(driver.page_source, "html.parser")
rows = soup.select("tbody#allreportsbody tr")

# Date filter: last 60 days
cutoff_date = datetime.today() - timedelta(days=60)

# Write to CSV
with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Author", "Upside (%)", "Tier"])

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue

        # Parse date
        date_str = cells[1].get("data-sort", "").strip()
        try:
            report_date = datetime.strptime(date_str, "%d %b %Y")
        except:
            continue

        if report_date < cutoff_date:
            continue

        # Parse author
        author_tag = cells[3].find("a")
        author = author_tag.text.strip() if author_tag else ""

        # Parse upside %
        upside = cells[7].text.strip()

        # Determine tier
        normalized_author = author.lower().strip()
        tier = "Tier 1" if any(broker.lower() in normalized_author for broker in TIER_1_BROKERS) else "Tier 2"

        writer.writerow([report_date.strftime("%Y-%m-%d"), author, upside, tier])

driver.quit()
print(f"Scraping completed. Data saved to {CSV_FILENAME}")
