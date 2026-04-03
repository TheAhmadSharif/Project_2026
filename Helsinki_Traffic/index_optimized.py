import requests
import csv
import time
import logging
import os
from tqdm import tqdm
from typing import Dict, List, Generator, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://lidotiku.api.hel.fi"

class HelsinkiTrafficCollector:
    def __init__(self, output_file="helsinki_traffic_all_data.csv", batch_flush=100000):
        self.output_file = output_file
        self.batch_flush = batch_flush  # Flush every N rows
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HelsinkiTrafficCollector/1.0'
        })
        
        # Configure connection pool for better performance
        from requests.adapters import HTTPAdapter
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
        self.session.mount('https://', adapter)

    def fetch_all_counters(self) -> List[Dict]:
        """Fetch all counters with metadata."""
        counters = []
        url = f"{BASE_URL}/api/counters/?format=json&page_size=200"
        
        with tqdm(desc="Fetching counter list", unit="page", leave=False) as pbar:
            while url:
                try:
                    resp = self.session.get(url, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    for feature in data.get("results", {}).get("features", []):
                        props = feature.get("properties", {})
                        counters.append({
                            "id": props.get("id"),
                            "name": props.get("name"),
                            "source": props.get("source"),
                            "first_observation": props.get("firstStoredObservation"),
                            "municipalityCode": props.get("municipalityCode"),
                            "data_received": props.get("dataReceived")  # Added for filtering
                        })
                    
                    url = data.get("next")
                    pbar.update(1)
                    
                    if url:
                        time.sleep(0.1)  # Slightly reduced delay
                        
                except Exception as e:
                    logger.error(f"Error fetching counters: {e}")
                    break
        
        logger.info(f"Found {len(counters)} counters total")
        return counters

    def stream_observations(self, counter: Dict) -> Generator[Dict, None, None]:
        """Generator: yields one row at a time with improved retry logic."""
        counter_id = counter["id"]
        
        # Skip sensors with no data (early filter)
        if not counter.get("first_observation") or counter.get("data_received") == False:
            return

        url = f"{BASE_URL}/api/observations/aggregate/"
        params = {
            "counter": counter_id,
            "period": "hour",
            "measurement_type": "count",
            "format": "json",
            "page_size": 1000  # Increased for fewer API calls
        }
        
        retry_count = 0
        max_retries = 3

        while url:
            try:
                resp = self.session.get(url, params=params, timeout=60)
                
                # Handle rate limiting with exponential backoff
                if resp.status_code == 429:
                    retry_count += 1
                    if retry_count <= max_retries:
                        wait_time = 5 * retry_count
                        logger.warning(f"Rate limited on counter {counter_id} - waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Counter {counter_id} failed after {max_retries} retries")
                        break
                    
                resp.raise_for_status()
                data = resp.json()
                
                # Reset retry count on success
                retry_count = 0

                # Process records (potentially batch yield for better performance)
                for record in data.get("results", []):
                    yield {
                        "sensor_id": counter_id,
                        "counter_name": counter.get("name", ""),
                        "startTime": record.get("startTime"),
                        "direction": record.get("direction"),
                        "period": record.get("period"),
                        "unit": record.get("unit"),
                        "aggregatedValue": record.get("aggregatedValue"),
                        "municipalityCode": counter.get("municipalityCode", "")
                    }

                url = data.get("next")
                params = {}
                
                if url:
                    time.sleep(0.1)  # Reduced between pages
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on counter {counter_id}, retrying...")
                retry_count += 1
                if retry_count > max_retries:
                    break
                time.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error on counter {counter_id}: {e}")
                retry_count += 1
                if retry_count > max_retries:
                    break
                time.sleep(3)

    def collect_all(self) -> int:
        """Main method with batched writes for better performance."""
        counters = self.fetch_all_counters()
        
        # More aggressive filtering
        counters_with_data = [
            c for c in counters 
            if c.get("first_observation") and c.get("data_received") != False
        ]
        
        logger.info(f"Starting collection for {len(counters_with_data)} counters with data...")
        logger.info(f"Output file: {self.output_file}")
        
        header_written = False
        total_rows = 0
        batch_buffer = []  # Buffer for batched writes
        batch_size = 5000  # Write 5000 rows at once

        start_time = time.time()
        
        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            writer = None
            
            # Use manual tqdm for more control
            with tqdm(total=len(counters_with_data), desc="Downloading sensors", unit="sensor") as pbar:
                for counter in counters_with_data:
                    for row in self.stream_observations(counter):
                        if not header_written:
                            writer = csv.DictWriter(f, fieldnames=row.keys())
                            writer.writeheader()
                            header_written = True
                        
                        batch_buffer.append(row)
                        total_rows += 1
                        
                        # Write in batches for better performance
                        if len(batch_buffer) >= batch_size:
                            writer.writerows(batch_buffer)
                            batch_buffer = []
                            
                            # Periodic flush
                            if total_rows % self.batch_flush == 0:
                                f.flush()
                                elapsed = time.time() - start_time
                                rate = total_rows / elapsed if elapsed > 0 else 0
                                logger.info(f"Progress: {total_rows:,} rows ({rate:.0f} rows/sec)")
                    
                    pbar.update(1)
                    time.sleep(0.15)  # Small delay between sensors
            
            # Write remaining rows
            if batch_buffer:
                writer.writerows(batch_buffer)
                f.flush()
        
        # Final statistics
        elapsed = time.time() - start_time
        rate = total_rows / elapsed if elapsed > 0 else 0
        file_size = os.path.getsize(self.output_file) / (1024 * 1024)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Collection complete!")
        logger.info(f"📊 Total rows: {total_rows:,}")
        logger.info(f"⏱️  Time: {elapsed:.2f} seconds ({elapsed/3600:.2f} hours)")
        logger.info(f"⚡ Rate: {rate:.0f} rows/second")
        logger.info(f"💾 File: {self.output_file} ({file_size:.1f} MB)")
        logger.info(f"{'='*60}")
        
        return total_rows


def main():
    """Main entry point with optional command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch Helsinki traffic data')
    parser.add_argument('--output', '-o', default='helsinki_traffic_all_data.csv',
                       help='Output CSV file name')
    parser.add_argument('--batch-flush', type=int, default=100000,
                       help='Flush to disk every N rows')
    parser.add_argument('--test', type=int, default=None,
                       help='Test with first N sensors only')
    
    args = parser.parse_args()
    
    collector = HelsinkiTrafficCollector(
        output_file=args.output,
        batch_flush=args.batch_flush
    )
    
    if args.test:
        # Test mode: only fetch first N sensors
        logger.info(f"TEST MODE: Only first {args.test} sensors")
        counters = collector.fetch_all_counters()
        counters_with_data = [c for c in counters if c.get("first_observation")]
        collector.counters_with_data = counters_with_data[:args.test]
        collector.collect_all()
    else:
        collector.collect_all()


if __name__ == "__main__":
    main()