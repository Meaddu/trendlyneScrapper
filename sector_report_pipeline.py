# sector_report_pipeline.py

import csv, os, sys, glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from trendlyne.scraper import scrape_sector_companies
from trendlyne.reports import (
    scrape_company_reports,
    convert_to_reports_url,
    slug_to_title,
)

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def get_sector_slug(sector_url):
    return sector_url.rstrip("/").split("/")[-1]

def combine_all_sector_reports(data_dir="data", output_file="data/all_sectors_combined.csv"):
    fieldnames = ["Company", "Date", "Author", "Upside (%)", "Tier", "Type", "Sector"]
    combined_rows = []

    for file in glob.glob(f"{data_dir}/*_sector_reports.csv"):
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                combined_rows.append([
                    row["Company"],
                    row["Date"],
                    row["Author"],
                    row["Upside (%)"],
                    row["Tier"],
                    row["Type"],
                    row["Sector"]
                ])

    # Write combined file
    with open(output_file, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(fieldnames)
        writer.writerows(combined_rows)

    print(f"Combined file updated: {output_file} ({len(combined_rows)} rows)")

def run_pipeline(sector_url):
    slug = get_sector_slug(sector_url)
    sector_name_readable = slug_to_title(slug)

    os.makedirs("data", exist_ok=True)
    companies_csv = f"data/{slug}_companies.csv"
    reports_csv = f"data/{slug}_sector_reports.csv"

    driver = setup_driver()
    scrape_sector_companies(sector_url, driver, companies_csv)

    with open(companies_csv, "r", encoding="utf-8") as f:
        companies = list(csv.DictReader(f))

    with open(reports_csv, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["Company", "Date", "Author", "Upside (%)", "Tier", "Type", "Sector"])

        for company in companies:
            report_url = convert_to_reports_url(company["URL"])
            print(f"Fetching reports for {report_url}")
            try:
                scrape_company_reports(driver, report_url, writer, sector_name_readable)
            except Exception as e:
                print(f"Error: {e}")

    driver.quit()

    # Combine all sector reports
    combine_all_sector_reports()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sector_report_pipeline.py <sector_url>")
        sys.exit(1)
    run_pipeline(sys.argv[1])
