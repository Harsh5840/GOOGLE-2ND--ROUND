import csv
from agents.firestore_agent import fetch_travel_time_records, travel_record_to_features
from typing import List

ROUTE = "Home-Airport"  # Example route, adjust as needed
WEEKDAYS = list(range(7))  # 0=Monday, 6=Sunday
HOURS = list(range(24))
LIMIT_PER_SLOT = 10  # Number of records per weekday/hour slot
OUTPUT_CSV = "travel_features.csv"

all_features: List[dict] = []

for weekday in WEEKDAYS:
    for hour in HOURS:
        records = fetch_travel_time_records(ROUTE, weekday, hour, limit=LIMIT_PER_SLOT)
        for record in records:
            features = travel_record_to_features(record)
            all_features.append(features)

if all_features:
    fieldnames = list(all_features[0].keys())
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_features)
    print(f"Exported {len(all_features)} feature rows to {OUTPUT_CSV}")
else:
    print("No features found to export.")
