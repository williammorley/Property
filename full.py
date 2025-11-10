# # UK PropertyData API Dashboard  

# This notebook uses your PropertyData API key to fetch market metrics for a set of UK postcodes, then visualises them using Plotly.

import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any

# Set your API key (can override with env var PROPERTYDATA_API_KEY)
API_KEY = os.getenv("PROPERTYDATA_API_KEY", "B0OWZ6EJZM")
BASE_URL = "https://api.propertydata.co.uk"

def fetch_endpoint(postcode: str, endpoint: str) -> Any:
    url = f"{BASE_URL}/{endpoint}"
    params = {"key": API_KEY, "postcode": postcode}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

def _is_number(val):
    try:
        if isinstance(val, (int, float)):
            return True
        float(str(val).replace(",", "").replace("£", "").replace("%", ""))
        return True
    except Exception:
        return False

def _to_number(val):
    try:
        return float(str(val).replace(",", "").replace("£", "").replace("%", ""))
    except Exception:
        return None

def find_value_by_keys(obj, keywords):
    """
    Recursively search obj (dict/list) for a value whose key contains any keyword.
    Returns first numeric-like value found, or None.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower()
            if any(kw in kl for kw in keywords) and _is_number(v):
                return _to_number(v)
            # sometimes value is nested dict with 'value' / 'amount'
            if isinstance(v, dict):
                # common nested names
                for subk in ("value", "amount", "avg", "average", "percentage", "percent"):
                    if subk in v and _is_number(v[subk]):
                        return _to_number(v[subk])
            # recurse
            res = find_value_by_keys(v, keywords)
            if res is not None:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_value_by_keys(item, keywords)
            if res is not None:
                return res
    else:
        # primitive
        return None
    return None

def extract_avg_price(resp):
    # try common keys related to average price
    return find_value_by_keys(resp, ["average_price", "avg_price", "average", "price", "median", "mean", "avg"])

def extract_rental_yield(resp):
    return find_value_by_keys(resp, ["average_yield", "average_yield_pct", "yield", "rental_yield", "yield_pct", "yield_percent", "yield%"])

#List of postcodes to analyse 
postcodes = ["CB1", "CB2"]

def fetch_metrics(postcodes, need_price=True, need_yield=True):
    rows = []
    for pc in postcodes:
        row = {"Postcode": pc}
        try:
            if need_price:
                resp_prices = fetch_endpoint(pc, "prices")
                val = extract_avg_price(resp_prices)
                row["Avg_asking_price"] = val
            if need_yield:
                resp_yields = fetch_endpoint(pc, "yields")
                val = extract_rental_yield(resp_yields)
                row["Rental_yield_pct"] = val
        except Exception as e:
            print(f"Warning: fetch failed for {pc}: {e}")
        rows.append(row)
    return pd.DataFrame(rows)

df_price = fetch_metrics(postcodes, need_price=True, need_yield=False)
df_yield = fetch_metrics(postcodes, need_price=False, need_yield=True)

# Clean numeric columns
for df, col in ((df_price, "Avg_asking_price"), (df_yield, "Rental_yield_pct")):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Plot average asking price for postcodes
if not df_price.empty and df_price["Avg_asking_price"].notna().any():
    df_plot = df_price.dropna(subset=["Avg_asking_price"])
    x = range(len(df_plot))
    plt.figure(figsize=(8,5))
    plt.bar(x, df_plot["Avg_asking_price"], color="skyblue")
    plt.xticks(x, df_plot["Postcode"])
    plt.title("Average Asking Price by Postcode ")
    plt.xlabel("Postcode")
    plt.ylabel("Average Asking Price (£)")
    plt.tight_layout()
    plt.savefig("avg_price_postcodes.png")
    plt.show()
else:
    print("No average price data available to plot for price_postcodes. Debug info:")
    print(df_price.to_dict(orient="records"))

# Plot rental yield for 3 postcodes
if not df_yield.empty and df_yield["Rental_yield_pct"].notna().any():
    df_plot = df_yield.dropna(subset=["Rental_yield_pct"])
    x = range(len(df_plot))
    plt.figure(figsize=(8,5))
    plt.bar(x, df_plot["Rental_yield_pct"], color="orange")
    plt.xticks(x, df_plot["Postcode"])
    plt.title("Average Rental Yield (%) by Postcode ")
    plt.xlabel("Postcode")
    plt.ylabel("Rental Yield (%)")
    plt.tight_layout()
    plt.savefig("rental_yield_postcodes.png")
    plt.show()
else:
    print("No rental yield data available to plot for yield_postcodes. Debug info:")
    print(df_yield.to_dict(orient="records"))