# trendlyne/reports.py

import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from trendlyne.config import TIER_1_BROKERS

def extract_ticker(url):
    parts = urlparse(url).path.split("/")
    return parts[4] if len(parts) > 4 else "UNKNOWN"

def convert_to_reports_url(company_url):
    return company_url.replace("/equity/", "/research-reports/stock/")

def scrape_company_reports(driver, report_url, writer):
    ticker = extract_ticker(report_url)
    driver.get(report_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("tbody#allreportsbody tr")
    cutoff = datetime.today() - timedelta(days=60)

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 9:
            continue

        date_str = cells[1].get("data-sort", "").strip()
        try:
            report_date = datetime.strptime(date_str, "%d %b %Y")
        except:
            continue
        if report_date < cutoff:
            continue

        author_tag = cells[3].find("a")
        author = author_tag.text.strip() if author_tag else ""
        upside = cells[7].text.strip()

        try:
            float(upside)
        except ValueError:
            continue

        type_span = cells[8].select_one("span.fs085rem")
        rating_type = type_span.text.strip() if type_span else ""

        tier = "Tier 1" if any(b.lower() in author.lower() for b in TIER_1_BROKERS) else "Tier 2"

        writer.writerow([ticker, report_date.strftime("%Y-%m-%d"), author, upside, tier, rating_type])
