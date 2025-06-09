# trendlyne/scraper.py

import csv, time
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

def scrape_sector_companies(sector_url, driver, output_path):
    driver.get(sector_url)
    time.sleep(3)

    dropdown = Select(driver.find_element("name", "DataTables_Table_1_length"))
    dropdown.select_by_visible_text("All")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("td.fs09rem.w-table-first a.stockrow")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Company Name", "URL"])
        for link in rows:
            name = link.text.strip()
            url = "https://trendlyne.com" + link["href"]
            writer.writerow([name, url])

    print(f"Scraped {len(rows)} companies to {output_path}")
