import requests
import pandas as pd
import time

BASE_URL = "https://lidotiku.api.hel.fi/api"
PAGE_SIZE = 1000
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

def fetch_page(url):
    """Fetch a single page with retry logic."""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 504:
                print(f"  [504 Gateway Timeout] Attempt {attempt}/{RETRY_ATTEMPTS}")
                time.sleep(RETRY_DELAY)
                continue

            if response.status_code != 200:
                print(f"  [HTTP {response.status_code}] Attempt {attempt}/{RETRY_ATTEMPTS}")
                time.sleep(RETRY_DELAY)
                continue

            return response.json()

        except requests.exceptions.Timeout:
            print(f"  [Timeout] Attempt {attempt}/{RETRY_ATTEMPTS}")
            time.sleep(RETRY_DELAY)

        except requests.exceptions.ConnectionError:
            print(f"  [Connection Error] Attempt {attempt}/{RETRY_ATTEMPTS}")
            time.sleep(RETRY_DELAY)

        except Exception as e:
            print(f"  [Unknown Error] {e} — Attempt {attempt}/{RETRY_ATTEMPTS}")
            time.sleep(RETRY_DELAY)

    return None  # all retries failed


def fetch_all_counters():
    all_features = []
    missing_pages = []

    url = f"{BASE_URL}/counters/?format=json&page_size={PAGE_SIZE}"
    page = 1

    while url:
        print(f"Fetching page {page} — {url}")

        data = fetch_page(url)

        if data is None:
            # all retries failed — skip and log
            print(f"  SKIPPED page {page} after {RETRY_ATTEMPTS} failed attempts\n")
            missing_pages.append({
                "page":   page,
                "url":    url,
                "reason": f"Failed after {RETRY_ATTEMPTS} retries"
            })
            # manually advance to next page to not get stuck
            page += 1
            url = f"{BASE_URL}/counters/?format=json&page_size={PAGE_SIZE}&page={page}"
            continue

        features = data["results"]["features"]
        all_features.extend(features)
        print(f"  Got {len(features)} sensors (total so far: {len(all_features)})")

        url = data.get("next")
        page += 1

    return all_features, missing_pages


def parse_to_dataframe(features):
    rows = []
    for feature in features:
        coords = feature["geometry"]["coordinates"]
        props  = feature["properties"]
        rows.append({
            "sensor_id":                props.get("id"),
            "source_id":                props.get("sourceId"),
            "name":                     props.get("name"),
            "source":                   props.get("source"),
            "longitude":                coords[0],
            "latitude":                 coords[1],
            "first_stored_observation": props.get("firstStoredObservation"),
            "last_stored_observation":  props.get("lastStoredObservation"),
        })
    return pd.DataFrame(rows)


def save_missing_log(missing_pages):
    if not missing_pages:
        print("\nNo missing pages — all data fetched successfully.")
        return

    df_missing = pd.DataFrame(missing_pages)
    df_missing.to_csv("missing_pages.csv", index=False)

    print(f"\n{'='*50}")
    print(f"  MISSING PAGES: {len(missing_pages)}")
    print(f"  Saved to: missing_pages.csv")
    print(f"{'='*50}")
    for m in missing_pages:
        print(f"  Page {m['page']} — {m['reason']}")
        print(f"  URL: {m['url']}")


def main():
    print("Starting Helsinki sensor fetch...\n")

    features, missing_pages = fetch_all_counters()

    # save sensors CSV
    if features:
        df = parse_to_dataframe(features)
        df.to_csv("helsinki_sensors.csv", index=False)
        print(f"\nSaved {len(df)} sensors to helsinki_sensors.csv")
        print(df.head())
    else:
        print("\nNo data fetched.")

    # save missing pages log
    save_missing_log(missing_pages)


main()