import requests
import pandas as pd
import random
import time
import os

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_URL       = "https://lidotiku.api.hel.fi/api"
SENSORS_FILE   = "helsinki_sensors.csv"
OUTPUT_DIR     = "traffic_data"

# Statistical sample: 10% of 3569 = 357 sensors
# → 95% confidence level, ±5% margin of error (with FPC correction)
SAMPLE_SIZE    = 357
PAGE_SIZE      = 1000
RETRY_ATTEMPTS = 3
RETRY_DELAY    = 60          # seconds between retries
REQUEST_DELAY  = 1         # polite pause between API calls

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Step 1: Load sensors & draw stratified random sample ─────────────────────
print("=" * 60)
print("STEP 1 — Drawing 357 sensor sample (10% of 3,569)")
print("         95% confidence | ±5% margin of error")
print("=" * 60)

df_sensors = pd.read_csv(SENSORS_FILE)

# Only sample sensors that actually have stored data
df_valid = df_sensors.dropna(subset=["first_stored_observation"]).copy()

print(f"Total sensors        : {len(df_sensors)}")
print(f"Sensors with data    : {len(df_valid)}")
print(f"Sensors to skip      : {len(df_sensors) - len(df_valid)} (no observations)")

# ── Stratified sampling by source ──────────────────────────────────────────
# Instead of pure random, sample proportionally from each source
# so all sensor types are fairly represented in the 357
source_counts = df_valid["source"].value_counts()
print(f"\nSource distribution in valid sensors:")
for src, cnt in source_counts.items():
    proportion = cnt / len(df_valid)
    allocated  = max(1, round(proportion * SAMPLE_SIZE))
    print(f"  {src:<20} {cnt:>4} sensors → sample {allocated}")

random.seed(42)   # reproducibility — same 357 sensors every run

sampled_frames = []
total_allocated = 0

for src, cnt in source_counts.items():
    src_df     = df_valid[df_valid["source"] == src]
    proportion = cnt / len(df_valid)
    allocated  = max(1, round(proportion * SAMPLE_SIZE))

    # Don't sample more than available
    allocated = min(allocated, len(src_df))
    sampled   = src_df.sample(n=allocated, random_state=42)
    sampled_frames.append(sampled)
    total_allocated += allocated

df_sample = pd.concat(sampled_frames).reset_index(drop=True)

# Trim or top-up to exactly SAMPLE_SIZE if rounding caused drift
if len(df_sample) > SAMPLE_SIZE:
    df_sample = df_sample.sample(n=SAMPLE_SIZE, random_state=42)
elif len(df_sample) < SAMPLE_SIZE:
    remaining = df_valid[~df_valid["sensor_id"].isin(df_sample["sensor_id"])]
    extra     = remaining.sample(n=SAMPLE_SIZE - len(df_sample), random_state=42)
    df_sample = pd.concat([df_sample, extra]).reset_index(drop=True)

df_sample.to_csv(f"{OUTPUT_DIR}/sampled_sensors_357.csv", index=False)
sample_ids = df_sample["sensor_id"].astype(int).tolist()

print(f"\nFinal sample size    : {len(df_sample)} sensors")
print(f"Saved to             : {OUTPUT_DIR}/sampled_sensors_357.csv")

# ─── Step 2: Fetch aggregate observations with retry ──────────────────────────
def fetch_aggregate(counter_id, period):
    """Fetch all paginated aggregate data for one counter + period."""
    all_results = []
    url = (
        f"{BASE_URL}/observations/aggregate/"
        f"?counter={counter_id}&period={period}"
        f"&measurement_type=count&format=json&page_size={PAGE_SIZE}"
    )

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 504:
                print(f"      [504 Timeout] attempt {attempt}/{RETRY_ATTEMPTS}, retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                continue

            if response.status_code != 200:
                print(f"      [HTTP {response.status_code}] skipping")
                return None

            data = response.json()
            all_results.extend(data.get("results", []))

            # Paginate through all remaining pages
            next_url = data.get("next")
            while next_url:
                r = requests.get(next_url, timeout=30)
                if r.status_code != 200:
                    break
                page_data = r.json()
                all_results.extend(page_data.get("results", []))
                next_url = page_data.get("next")

            return all_results

        except requests.exceptions.Timeout:
            print(f"      [Timeout] attempt {attempt}/{RETRY_ATTEMPTS}")
            time.sleep(RETRY_DELAY)
        except requests.exceptions.ConnectionError:
            print(f"      [Connection Error] attempt {attempt}/{RETRY_ATTEMPTS}")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"      [Error] {e}")
            return None

    return None  # all retries exhausted


# ─── Step 3: Download hourly, daily, monthly for all 357 sensors ──────────────
print("\n" + "=" * 60)
print("STEP 2 — Downloading data for 357 sensors × 3 periods")
print(f"         Estimated API calls: {357 * 3} requests")
print("=" * 60)

periods     = ["hour", "day", "month"]
missing_log = []
all_data    = {p: [] for p in periods}

for i, sensor_id in enumerate(sample_ids, 1):
    sensor_name = df_sample[df_sample["sensor_id"] == sensor_id]["name"].values[0]
    print(f"\n[{i:>3}/{SAMPLE_SIZE}] Sensor {sensor_id} — {sensor_name}")

    for period in periods:
        print(f"  {period:<6} ... ", end="", flush=True)
        results = fetch_aggregate(sensor_id, period)

        if results is None:
            print("FAILED")
            missing_log.append({
                "sensor_id": sensor_id,
                "period":    period,
                "reason":    f"Failed after {RETRY_ATTEMPTS} retries"
            })
        elif len(results) == 0:
            print("0 records")
        else:
            for r in results:
                r["sensor_id"] = sensor_id
            all_data[period].extend(results)
            print(f"{len(results):,} records")

    time.sleep(REQUEST_DELAY)

# ─── Step 4: Save raw CSVs ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3 — Saving raw data")
print("=" * 60)

for period in periods:
    if all_data[period]:
        df = pd.DataFrame(all_data[period])
        path = f"{OUTPUT_DIR}/raw_{period}ly_357.csv"
        df.to_csv(path, index=False)
        print(f"  raw_{period}ly_357.csv   → {len(df):,} rows")

if missing_log:
    pd.DataFrame(missing_log).to_csv(f"{OUTPUT_DIR}/missing_log.csv", index=False)
    print(f"\n  missing_log.csv       → {len(missing_log)} failed requests")
else:
    print("\n  No missing data — all sensors fetched successfully.")


# ─── Step 5: Analysis — busiest hour / day / month ────────────────────────────
print("\n" + "=" * 60)
print("STEP 4 — Analysis: Busiest Hour / Day / Month")
print("=" * 60)

# ── Busiest hour of the day (0–23) ─────────────────────────────
if all_data["hour"]:
    df_hour = pd.DataFrame(all_data["hour"])
    df_hour["startTime"]   = pd.to_datetime(df_hour["startTime"], utc=True)
    df_hour["hour_of_day"] = df_hour["startTime"].dt.hour

    busiest_hour = (
        df_hour.groupby("hour_of_day")["aggregatedValue"]
        .mean()
        .round(1)
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"hour_of_day": "hour", "aggregatedValue": "avg_vehicles"})
    )

    print("\n Top 5 Busiest Hours of the Day:")
    print(busiest_hour.head(5).to_string(index=False))
    busiest_hour.to_csv(f"{OUTPUT_DIR}/analysis_busiest_hour.csv", index=False)

# ── Busiest day of the week ─────────────────────────────────────
if all_data["day"]:
    df_day = pd.DataFrame(all_data["day"])
    df_day["startTime"]   = pd.to_datetime(df_day["startTime"], utc=True)
    df_day["day_of_week"] = df_day["startTime"].dt.day_name()
    df_day["day_num"]     = df_day["startTime"].dt.dayofweek   # 0=Mon

    busiest_day = (
        df_day.groupby(["day_num", "day_of_week"])["aggregatedValue"]
        .mean()
        .round(1)
        .reset_index()
        .sort_values("day_num")
        .rename(columns={"day_of_week": "day", "aggregatedValue": "avg_vehicles"})
        [["day", "avg_vehicles"]]
        .sort_values("avg_vehicles", ascending=False)
    )

    print("\n Busiest Days of the Week:")
    print(busiest_day.to_string(index=False))
    busiest_day.to_csv(f"{OUTPUT_DIR}/analysis_busiest_day.csv", index=False)

# ── Busiest month of the year ───────────────────────────────────
if all_data["month"]:
    df_month = pd.DataFrame(all_data["month"])
    df_month["startTime"]   = pd.to_datetime(df_month["startTime"], utc=True)
    df_month["month_name"]  = df_month["startTime"].dt.month_name()
    df_month["month_num"]   = df_month["startTime"].dt.month

    busiest_month = (
        df_month.groupby(["month_num", "month_name"])["aggregatedValue"]
        .mean()
        .round(1)
        .reset_index()
        .sort_values("month_num")
        .rename(columns={"month_name": "month", "aggregatedValue": "avg_vehicles"})
        [["month", "avg_vehicles"]]
        .sort_values("avg_vehicles", ascending=False)
    )

    print("\n Busiest Months:")
    print(busiest_month.to_string(index=False))
    busiest_month.to_csv(f"{OUTPUT_DIR}/analysis_busiest_month.csv", index=False)


# ─── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
print(f"\nOutput files in: {OUTPUT_DIR}/")
print(f"  sampled_sensors_357.csv      — 357 stratified random sensors")
print(f"  raw_hourly_357.csv           — raw hourly observations")
print(f"  raw_daily_357.csv            — raw daily observations")
print(f"  raw_monthly_357.csv          — raw monthly observations")
print(f"  analysis_busiest_hour.csv    — avg traffic by hour (0–23)")
print(f"  analysis_busiest_day.csv     — avg traffic by day of week")
print(f"  analysis_busiest_month.csv   — avg traffic by month")
print(f"  missing_log.csv              — failed requests (if any)")
print(f"\nStatistical validity:")
print(f"  Sample size  : 357 sensors")
print(f"  Population   : 3,569 sensors")
print(f"  Coverage     : 10%")
print(f"  Confidence   : 95%")
print(f"  Margin error : ±5%")