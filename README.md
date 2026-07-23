
# yshop_ranking_tracker
Automated ranking tracker for Yahoo Shopping's Korean cosmetics（韓コスメ）promotion page.

## Overview
Collects popular brand and product from the category ranking sections on Yahoo Shopping's 韓コスメ page.

## Tech Stack
- python (BeautifulSoup4)
- Yahoo Shopping's internal mc-module API response parsing

## How It Works
Calling the mc-module API directly from Python gets blocked by bot detection. 
So instead:
 
 1. The request is captured from the browser console using the real, authenticated session ("Copy as fetch" + a download snippet), and saved locally as ranking_data.json
 2. This script reads that file and parses the htmlTag fields inside it.
 3. Since the response's module order isn't reliably tied to category, 
    the script identifies category by counting the order in which product-containing modules appear, then maps them to the page's tab order

## Data Collected
- Product name
- Product URL
- Price (discounted)
- Category
- Original price
- Store name
- Rank within category

## Usage
```
python ranking_collector.py
```
Requires ranking_data.json in the same folder (see "How It Works" above for how to generate it). Outputs ranking_result.csv

## Progress
- [x] Investigated rendering method (server-side rendering vs API-based)
- [x] Identified the data source API (mc-module response structure)
- [x] Implemented parsing logic
- [x] Solved bot-detection blocking via browser-session-based fetching
- [x] Fixed category-to-product mapping
- [ ] Google Sheets integration / scheduled automation