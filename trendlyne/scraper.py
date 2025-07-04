import csv
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

def scrape_sector_companies(sector_url, driver, output_path, max_retries=3):
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} to load sector companies...")
        driver.get(sector_url)
        time.sleep(2)

        # Scroll slightly to trigger lazy loads
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(2)

        # Wait for dropdown (optional)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "DataTables_Table_1_length"))
            )
            dropdown = Select(driver.find_element(By.NAME, "DataTables_Table_1_length"))
            dropdown.select_by_visible_text("All")
            time.sleep(2)
        except TimeoutException:
            print("Dropdown not found — skipping dropdown selection")

        # Wait for company links to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "td.fs09rem.w-table-first a.stockrow"))
            )
        except TimeoutException:
            print("Company table rows did not load.")
            if attempt == max_retries:
                print("Maximum retries reached. Scraping aborted.")
                return
            else:
                continue  # Retry from top of loop

        # Extract and write data
        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select("td.fs09rem.w-table-first a.stockrow")

        if not rows:
            print("No company links found, retrying...")
            continue

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Company Name", "URL"])
            for link in rows:
                name = link.text.strip()
                url = "https://trendlyne.com" + link["href"]
                writer.writerow([name, url])

        print(f"Scraped {len(rows)} companies to {output_path}")
        return  # Success

    print("Failed to scrape after multiple retries.")
