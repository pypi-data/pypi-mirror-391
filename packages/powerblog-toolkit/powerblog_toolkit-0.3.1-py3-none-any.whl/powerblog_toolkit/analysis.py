import pandas as pd

def generate_keyword_top5(organic_df):
    """
    Returns two DataFrames:
      - kw_top5_domain_df: Top 5 domains per keyword
      - kw_top5_url_df: Top 5 URLs per keyword
    """
    if organic_df.empty:
        print("⚠️ No organic data available.")
        return pd.DataFrame(), pd.DataFrame()

    top5_df = organic_df.groupby("keyword").head(5)
    kw_top5_domain_df = (
        top5_df.groupby(["keyword", "domain"])
        .size()
        .reset_index(name="count")
        .sort_values(["keyword", "count"], ascending=[True, False])
    )

    kw_top5_url_df = (
        top5_df.groupby(["keyword", "link"])
        .size()
        .reset_index(name="count")
        .sort_values(["keyword", "count"], ascending=[True, False])
    )

    return kw_top5_domain_df, kw_top5_url_df


def generate_detailed_strength_tables(organic_df):
    """
    Returns:
      - domain_detailed_strength_df: position-based average rank for domains
      - url_detailed_strength_df: same but per URL
    """
    if organic_df.empty:
        print("⚠️ No organic data available.")
        return pd.DataFrame(), pd.DataFrame()

    domain_strength = (
        organic_df.groupby("domain")["position"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"count": "total_keywords", "mean": "avg_position"})
        .sort_values("avg_position")
    )

    url_strength = (
        organic_df.groupby("link")["position"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"count": "total_keywords", "mean": "avg_position"})
        .sort_values("avg_position")
    )

    return domain_strength, url_strength
