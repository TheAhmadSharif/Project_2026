import requests
import pandas as pd

# Sensors we want to fetch
sensor_ids = [1, 2]

# List to store all data
all_sensors_data = []

# Loop over each sensor
for sensor_id in sensor_ids:
    print(f"Fetching data for sensor {sensor_id}...")
    
    # Start URL and parameters
    url = "https://lidotiku.api.hel.fi/api/observations/aggregate/"
    params = {
        "counter": sensor_id,
        "period": "hour",          # hourly aggregation
        "measurement_type": "count",
        "format": "json",
        "page_size": 100           # fetch 100 rows per page
    }
    
    while url:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch data for sensor {sensor_id}, status: {response.status_code}")
            break

        data = response.json()
        results = data.get("results", [])
        
        # Add sensor_id for clarity
        for record in results:
            record["sensor_id"] = sensor_id
            all_sensors_data.append(record)
        
        # Prepare for next page
        url = data.get("next")  # next page URL
        params = {}             # next URL already contains all query params

# Convert to DataFrame
df = pd.DataFrame(all_sensors_data)

# Reorder columns for readability
cols = ["sensor_id", "counterId", "startTime", "direction", "unit", "aggregatedValue", "period"]
df = df[cols]

# Save to CSV
csv_filename = "sensors_1_to_5_full_data.csv"
df.to_csv(csv_filename, index=False)

print(f"Saved {len(df)} rows for sensors 1–5 to {csv_filename}")