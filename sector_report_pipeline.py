# sector_report_pipeline.py

import csv
import time
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

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

def extract_sector_name(url):
    path_parts = urlparse(url).path.strip("/").split("/")
    return path_parts[-1] if path_parts else "sector"

def convert_to_reports_url(company_url):
    return company_url.replace("/equity/", "/research-reports/stock/")

def extract_ticker_from_url(url):
    parts = urlparse(url).path.split("/")
    return parts[4] if len(parts) > 4 else "UNKNOWN"

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def scrape_sector_companies(sector_url, driver, output_file):
    driver.get(sector_url)
    time.sleep(3)

    dropdown = Select(driver.find_element("name", "DataTables_Table_1_length"))
    dropdown.select_by_visible_text("All")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("td.fs09rem.w-table-first a.stockrow")

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "URL"])
        for link in rows:
            name = link.text.strip()
            url = "https://trendlyne.com" + link["href"]
            writer.writerow([name, url])

    print(f"Scraped {len(rows)} companies from sector page.")

def scrape_company_reports(driver, report_url, writer):
    ticker = extract_ticker_from_url(report_url)
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
        if upside.lower() == "target met":
            continue  # Skip "Target met" rows

        # Extract type (Buy/Sell/Hold/etc.)
        type_span = cells[8].select_one("span.fs085rem")
        rating_type = type_span.text.strip() if type_span else ""

        normalized_author = author.lower().strip()
        tier = "Tier 1" if any(b.lower() in normalized_author for b in TIER_1_BROKERS) else "Tier 2"

        writer.writerow([ticker, report_date.strftime("%Y-%m-%d"), author, upside, tier, rating_type])

def run_pipeline(sector_url):
    sector_name = extract_sector_name(sector_url)
    companies_csv = f"{sector_name}_companies.csv"
    reports_csv = f"{sector_name}_sector_reports.csv"

    driver = setup_driver()

    # Step 1: Scrape companies in sector
    scrape_sector_companies(sector_url, driver, companies_csv)

    # Step 2: Load companies and fetch reports
    with open(companies_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        company_list = list(reader)

    with open(reports_csv, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Company", "Date", "Author", "Upside (%)", "Tier", "Type"])

        for company in company_list:
            base_url = company["URL"]
            report_url = convert_to_reports_url(base_url)
            print(f"Fetching reports for: {report_url}")
            try:
                scrape_company_reports(driver, report_url, writer)
            except Exception as e:
                print(f"Error fetching {report_url}: {e}")

    driver.quit()
    print(f"Reports saved to {reports_csv}")

# Command-line usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sector_report_pipeline.py <sector_url>")
        sys.exit(1)

    sector_url_input = sys.argv[1]
    run_pipeline(sector_url_input)
