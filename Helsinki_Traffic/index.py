import requests
import pandas as pd

# Base URL for aggregated observations
base_url = "https://lidotiku.api.hel.fi/api/observations/aggregate/"

# Sensor IDs we want
sensor_ids = [1, 2, 3, 4, 5]

# Store all data
all_data = []

for sensor in sensor_ids:
    params = {
        "counter": sensor,
        "period": "hour",          # aggregate hourly
        "measurement_type": "count",
        "format": "json",
        "page_size": 5             # fetch first 5 records only
    }

    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        json_data = response.json()
        results = json_data.get("results", [])
        
        for record in results:
            record["sensor_id"] = sensor
            all_data.append(record)
    else:
        print(f"Failed to fetch data for sensor {sensor}, status: {response.status_code}")

# Convert to pandas DataFrame
df = pd.DataFrame(all_data)

# Reorder columns for readability
cols = ["sensor_id", "counterId", "startTime", "direction", "unit", "aggregatedValue", "period"]
df = df[cols]

# Save all data to CSV
csv_filename = "sensors_1_to_5.csv"
df.to_csv(csv_filename, index=False)

print(f"Saved {len(df)} records to {csv_filename}")