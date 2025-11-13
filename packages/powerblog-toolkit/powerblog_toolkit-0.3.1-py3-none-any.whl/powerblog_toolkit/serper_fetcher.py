import pandas as pd
import json
import time
import http.client
from urllib.parse import urlparse

def fetch_serper(df, keyword_column, api_key, gl=None, hl=None, delay=1.2, retries=3):
    """
    Takes a DataFrame of keywords and fetches data from Serper.dev.
    Returns: (organic_results_df, more_keywords_df)
    """

    organic_rows = []
    more_kw_rows = []

    conn = http.client.HTTPSConnection("google.serper.dev")

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    keywords = df[keyword_column].dropna().astype(str).tolist()
    print(f"🔍 Total keywords to fetch: {len(keywords)}")

    for idx, keyword in enumerate(keywords, start=1):
        print(f"[{idx}/{len(keywords)}] Fetching: {keyword}")

        for attempt in range(retries):
            try:
                payload = {"q": keyword}
                if hl:
                    payload["hl"] = hl
                if gl:
                    payload["gl"] = gl

                payload = json.dumps(payload)
                conn.request("POST", "/search", payload, headers)
                res = conn.getresponse()

                if res.status == 200:
                    data = res.read()
                    data = json.loads(data.decode("utf-8"))

                    # --- Organic Results ---
                    if "organic" in data:
                        for i, item in enumerate(data["organic"], start=1):
                            link = item.get("link", "")
                            domain = urlparse(link).netloc.replace("www.", "") if link else ""
                            organic_rows.append({
                                "keyword": keyword,
                                "position": i,
                                "link": link,
                                "domain": domain,
                                "title": item.get("title", ""),
                                "snippet": item.get("snippet", "")
                            })

                    # --- People Also Ask ---
                    if "peopleAlsoAsk" in data:
                        for q in data["peopleAlsoAsk"]:
                            more_kw_rows.append({
                                "keyword": keyword,
                                "category": "people_also_ask",
                                "query": q.get("question", "")
                            })

                    # --- Related Searches ---
                    if "relatedSearches" in data:
                        for q in data["relatedSearches"]:
                            more_kw_rows.append({
                                "keyword": keyword,
                                "category": "related_search",
                                "query": q.get("query", "")
                            })

                    time.sleep(delay)
                    break  # success → exit retry loop

                else:
                    print(f"⚠️ {keyword}: HTTP {res.status}")
            except Exception as e:
                print(f"❌ Error fetching '{keyword}' (Attempt {attempt+1}/{retries}): {e}")
            finally:
                conn.close()
            time.sleep(delay)
        else:
            print(f"❌ Skipping '{keyword}' after {retries} retries.")

    organic_df = pd.DataFrame(organic_rows)
    more_kw_df = pd.DataFrame(more_kw_rows)

    print(f"\n✅ Done! Organic: {organic_df.shape[0]} rows | More Keywords: {more_kw_df.shape[0]} rows")
    return organic_df, more_kw_df
