import requests
import matplotlib.pyplot as plt

API_KEY = "TVY2FUEUPG"   # your PropertyData API key
BASE_URL = "https://api.propertydata.co.uk"

#Function to fetch data for a postcode
def fetch_postcode_raw(postcode):
    endpoint = "/prices"  # Prices endpoint
    url = f"{BASE_URL}{endpoint}"
    params = {
        "postcode": postcode,
        "key": API_KEY
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

#Function to calculate average from raw prices
def average_price_from_raw(data):
    raw_list = data.get("data", {}).get("raw_data", [])
    prices = [item["price"] for item in raw_list if item.get("price") is not None]
    if prices:
        return sum(prices) / len(prices)
    else:
        return 0

#Postcodes to analyse 
postcodes = ["CB2", "SW1", "M1"]
avg_prices = []

for pc in postcodes:
    data = fetch_postcode_raw(pc)
    avg_prices.append(average_price_from_raw(data))

# --- Plot ---
plt.figure(figsize=(8,5))
x = range(len(postcodes))
plt.bar(x, avg_prices, color='skyblue')
plt.xticks(x, postcodes)
plt.title("Average Property Price by Postcode")
plt.xlabel("Postcode")
plt.ylabel("Average Price (£)")
plt.tight_layout()
plt.savefig("avg_price_by_postcodeUK.png")
plt.show()