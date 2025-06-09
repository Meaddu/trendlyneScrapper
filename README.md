````markdown
# Trendlyne Sector Report Scraper

Fetch recent analyst reports (last 60 days) for all companies in a given Trendlyne sector.

## Installation

```bash
pip install -r requirements.txt
````

##  Usage

```bash
python sector_report_pipeline.py https://trendlyne.com/equity/sector/21/banking-and-finance/
```

## Output

* `data/<sector>_companies.csv`
* `data/<sector>_sector_reports.csv`

Includes: Company, Date, Author, Upside (%), Tier, and Recommendation Type.

```
```
