# ⚡ PowerBlog Toolkit

**PowerBlog Toolkit** is a lightweight Python package designed to fetch and analyze keyword data from [Serper.dev](https://serper.dev) and save structured insights directly to Google Sheets.  
It helps marketers, SEO professionals, and data enthusiasts build high-quality keyword datasets, extract top results, and generate ranking insights — all in one automated workflow.

---

## 🚀 Features

- 🔍 Fetch keyword search results directly from **Serper.dev**
- 📊 Extract **organic results**, **people also ask**, and **related searches**
- 📈 Generate **top domains** and **URL strength** tables automatically
- 🧾 Save everything neatly into **Google Sheets**
- 💡 Built to work seamlessly in **Google Colab** or locally

## Usage Example (Google Colab)

```python
from powerblog_toolkit import fetch_serper, save_to_sheet, generate_keyword_top5, generate_detailed_strength_tables
from google.colab import auth
from google.auth import default
import gspread
from gspread_dataframe import get_as_dataframe

# Authenticate Google account
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

# Load your keyword data from Google Sheets
file_name = "keywords_list"
sheet_name = "data"
keyword_column="Keyword"
API_KEY = "YOUR_API_KEY"
ws = gc.open(file_name).worksheet(sheet_name)
df = get_as_dataframe(ws)

# Fetch results from Serper
organic_df, more_kw_df = fetch_serper(df, keyword_column=keyword_column, api_key=API_KEY, gl="in")

# Save data to Google Sheets
save_to_sheet(gc, file_name, "organic_results", organic_df)
save_to_sheet(gc, file_name, "more_keywords", more_kw_df)

# Generate analysis reports
kw_top5_domain_df, kw_top5_url_df = generate_keyword_top5(organic_df)
domain_strength_df, url_strength_df = generate_detailed_strength_tables(organic_df)

save_to_sheet(gc, file_name, "kw_top5_domain", kw_top5_domain_df)
save_to_sheet(gc, file_name, "kw_top5_url", kw_top5_url_df)
save_to_sheet(gc, file_name, "domain_strength", domain_strength_df)
save_to_sheet(gc, file_name, "url_strength", url_strength_df)
```
