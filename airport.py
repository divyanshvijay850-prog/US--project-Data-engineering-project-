import requests
import csv
import json

url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

columns = [
    "airport_id", "name", "city", "country",
    "iata", "icao", "latitude", "longitude",
    "altitude", "timezone", "dst", "tz_database",
    "type", "source"
]

print("Downloading...")

# Step 1: Download with requests (SSL verify off - fixes network issues)
response = requests.get(url, verify=False, timeout=30)
response.raise_for_status()
print("Downloaded ")

# Step 2: Read and convert to list of dicts
airports = []
lines = response.text.splitlines()

reader = csv.reader(lines)
for row in reader:
    if len(row) == len(columns):
        airport = dict(zip(columns, row))
        airports.append(airport)

# Step 3: Save as JSON
with open("airports.json", "w", encoding="utf-8") as f:
    json.dump(airports, f, indent=4, ensure_ascii=False)

print(f"airports.json saved! Total records: {len(airports)} ")