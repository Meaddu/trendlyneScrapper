# trendlyneScraper.py

import csv
import time
import sys
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

def extract_sector_id(url):
    """Extract sector name or ID from the URL for naming output file"""
    path_parts = urlparse(url).path.strip("/").split("/")
    return path_parts[-1] if path_parts else "sector"

def scrape_sector_companies(sector_url):
    sector_name = extract_sector_id(sector_url)
    output_file = f"{sector_name}_companies.csv"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(sector_url)

    # Wait for dropdown and switch to "All"
    time.sleep(3)
    dropdown = Select(driver.find_element("name", "DataTables_Table_1_length"))
    dropdown.select_by_visible_text("All")

    time.sleep(5)  # Wait for all companies to render

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("td.fs09rem.w-table-first a.stockrow")

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "URL"])
        for link in rows:
            name = link.text.strip()
            url = "https://trendlyne.com" + link["href"]
            writer.writerow([name, url])

    driver.quit()
    print(f"Scraped {len(rows)} companies. Data saved to {output_file}")

# Accept input
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trendlyneScraper.py <sector_url>")
        sys.exit(1)
    
    sector_url = sys.argv[1]
    scrape_sector_companies(sector_url)
