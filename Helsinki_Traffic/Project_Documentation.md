# Helsinki Traffic Analysis — Project Brief

Statistical analysis of traffic measurement data from the City of Helsinki using the [Lidotiku REST API](https://lidotiku.api.hel.fi). The project fetches sensor observations, samples statistically representative data, and analyses traffic patterns by hour, day, and month.

---

## Project overview

The City of Helsinki operates 3,569 traffic sensors across the metropolitan area, collecting vehicle counts, average speeds, and pedestrian/cyclist volumes. This project queries the public REST API, draws a statistically valid random sample, downloads aggregate observations, and extracts key traffic patterns.

**Key findings:**
- Busiest hour: **13:00** (622 avg vehicles) — lunch hour dominates over morning rush
- Busiest day: **Wednesday** (9,683 avg) — Friday dips significantly, likely hybrid work
- Busiest month: **May** (352,650 avg) — anomaly under investigation; all other months cluster between 142k–241k

---

## Folder structure

```
.
├── helsinki_sensors.csv          # Full registry of all 3,569 sensors
├── helsinki_sensors_map.html     # Interactive Leaflet map of sensor locations
├── index.py                      # Entry point / scratchpad
├── map_plot.py                   # Map generation script
├── Query.txt                     # API query reference notes
├── Traffic_Analysis.py           # Main analysis script (357 sensors, 3 periods)
└── traffic_data/
    ├── sampled_sensors_357.csv   # 357 randomly sampled sensors (stratified)
    ├── raw_hourly_357.csv        # Raw hourly observations (5,455,294 rows)
    ├── raw_dayly_357.csv         # Raw daily observations (250,616 rows)
    ├── raw_monthly_357.csv       # Raw monthly observations (11,170 rows)
    ├── analysis_busiest_hour.csv # Avg traffic by hour of day (0–23)
    ├── analysis_busiest_day.csv  # Avg traffic by day of week
    ├── analysis_busiest_month.csv# Avg traffic by month
    └── missing_log.csv           # 29 failed API requests logged for retry
```

---

## Data source

| Property | Value |
|---|---|
| API | [Lidotiku REST API](https://lidotiku.api.hel.fi/api/) |
| Format | JSON / CSV |
| License | CC-BY-4.0 |
| Total sensors | 3,569 |
| Data sources | LIVA, HEL LAM, Fintraffic, EcoCounter, InfoTripla, Marksman, SmartJunction |

### Key endpoints used

| Endpoint | Purpose |
|---|---|
| `GET /api/metadata/sources/` | List all data sources |
| `GET /api/counters/` | List all sensors with coordinates |
| `GET /api/observations/` | Raw observations per sensor |
| `GET /api/observations/aggregate/` | Aggregated data by period |

---

## Statistical sampling

From 3,569 total sensors, **357 were sampled** using stratified random sampling (proportional by source).

| Metric | Value |
|---|---|
| Population (N) | 3,569 sensors |
| Sample size (n) | 357 sensors |
| Coverage | 10% |
| Confidence level | 95% |
| Margin of error | ±5% |
| Method | Cochran formula + Finite Population Correction (FPC) |
| Seed | `random.seed(42)` — reproducible |

**Why 10% and not more?** The Cochran formula shows that for N=3,569, a sample of 357 already achieves ±5% margin of error at 95% confidence. Going to 30% (1,071 sensors) would only improve this to ±2.5% — a modest gain for 3× more API calls and processing time.

**Formula used:**

```
n₀ = Z² × p(1−p) / e²        (Cochran initial estimate)
n  = n₀ / (1 + (n₀−1)/N)     (Finite Population Correction)

Where: Z = 1.96 (95% confidence), p = 0.5 (max variance), e = 0.05 (±5%)
Result: n₀ = 384 → n = 349 → rounded up to 357 (10% of 3,569)
```

---

## File excerpts

### `helsinki_sensors.csv`
Full registry of all 3,569 sensors fetched from `/api/counters/`.

```
sensor_id,source_id,name,source,longitude,latitude,first_stored_observation,last_stored_observation
1,1.0,Harbor 3 light,InfoTripla,24.920879,60.155215,,
2,2.0,Harbor 3 light,InfoTripla,24.920879,60.155215,,
3,,3_343_6-005,LIVA,24.94837,60.19771,2023-11-15T14:00:00+02:00,2026-03-05T12:30:00+02:00
4,,3_442_6-001,LIVA,24.96881,60.20368,2023-11-15T14:00:00+02:00,2026-03-05T12:30:00+02:00
5,,3_816_2-060A,LIVA,24.84937,60.24571,2023-11-15T14:00:00+02:00,2026-03-05T12:30:00+02:00
```

---

### `traffic_data/sampled_sensors_357.csv`
357 sensors drawn via stratified random sampling, proportional by source.

```
sensor_id,source_id,name,source,longitude,latitude,first_stored_observation,last_stored_observation
42,,3_201_4-010,LIVA,24.95312,60.17842,2023-11-15T14:00:00+02:00,2026-03-05T12:30:00+02:00
87,,3_414_2-020A,LIVA,24.96102,60.18823,2023-11-15T14:00:00+02:00,2026-03-05T12:30:00+02:00
103,103.0,HEL214,HEL LAM,24.93841,60.20112,2022-01-01T00:00:00+02:00,2026-03-05T11:00:00+02:00
215,,EC_Baana_1,EcoCounter,24.92674,60.16931,2021-06-01T00:00:00+03:00,2026-03-04T23:00:00+02:00
```

---

### `traffic_data/raw_hourly_357.csv`
5,455,294 rows of hourly vehicle counts across all 357 sampled sensors.

```
period,counterId,startTime,direction,unit,aggregatedValue,sensor_id
hour,5,2026-03-05T12:00:00+02:00,,n,144,5
hour,5,2026-03-05T11:00:00+02:00,,n,132,5
hour,5,2026-03-05T10:00:00+02:00,,n,233,5
hour,42,2026-03-05T12:00:00+02:00,,n,87,42
hour,42,2026-03-05T11:00:00+02:00,,n,74,42
```

---

### `traffic_data/raw_dayly_357.csv`
250,616 rows of daily vehicle counts.

```
period,counterId,startTime,direction,unit,aggregatedValue,sensor_id
day,5,2026-03-05T00:00:00+02:00,,n,1306,5
day,5,2026-03-04T00:00:00+02:00,,n,1289,5
day,5,2026-03-03T00:00:00+02:00,,n,952,5
day,42,2026-03-05T00:00:00+02:00,,n,743,42
day,42,2026-03-04T00:00:00+02:00,,n,811,42
```

---

### `traffic_data/raw_monthly_357.csv`
11,170 rows of monthly aggregated vehicle counts.

```
period,counterId,startTime,direction,unit,aggregatedValue,sensor_id
month,5,2026-03-01T00:00:00+02:00,,n,28431,5
month,5,2026-02-01T00:00:00+02:00,,n,26817,5
month,5,2026-01-01T00:00:00+02:00,,n,29204,5
month,42,2026-03-01T00:00:00+02:00,,n,17342,42
month,42,2026-02-01T00:00:00+02:00,,n,15901,42
```

---

### `traffic_data/analysis_busiest_hour.csv`
Average vehicle count per hour of day across all 357 sensors.

```
hour,avg_vehicles
13,622.3
12,588.2
14,582.6
11,538.9
15,507.4
8,412.3
7,298.4
0,38.2
```

---

### `traffic_data/analysis_busiest_day.csv`
Average vehicle count per day of week.

```
day,avg_vehicles
Wednesday,9682.8
Tuesday,9668.3
Monday,9452.4
Thursday,9044.5
Sunday,8779.8
Friday,7191.3
Saturday,6817.0
```

---

### `traffic_data/analysis_busiest_month.csv`
Average vehicle count per month of year.

```
month,avg_vehicles
May,352650.3
October,241370.8
November,237401.2
July,216610.8
December,184648.0
January,184302.9
June,172932.1
March,164451.0
September,157941.8
August,153596.3
February,149566.2
April,142138.8
```

---

### `traffic_data/missing_log.csv`
29 API requests that failed after 3 retry attempts.

```
sensor_id,period,reason
312,hour,Failed after 3 retries
312,day,Failed after 3 retries
489,month,Failed after 3 retries
1024,hour,Failed after 3 retries
1024,day,Failed after 3 retries
```

---

## Analysis results

### Busiest hour of day
Peak traffic occurs at **13:00 (lunch hour)** with an average of 622 vehicles, not during the traditional morning commute. The full peak window spans 11:00–15:00. Night hours (00:00–05:00) average fewer than 40 vehicles.

### Busiest day of week
**Wednesday** is the busiest day (9,683 avg). **Friday** drops to 7,191 — a ~26% decline compared to Wednesday — consistent with hybrid/remote work patterns. Weekend traffic runs ~28% lower than peak weekday levels.

### Busiest month
**May** records 352,650 average vehicles — more than double the next highest month (October: 241,370). This outlier warrants further investigation: it may reflect a genuine seasonal surge, spring construction activity, or a data anomaly from a small number of high-volume sensors skewing the sample mean. Excluding May, October and November are consistently the busiest months.

---

## Data quality

| Metric | Value |
|---|---|
| Total API calls made | ~1,071 (357 sensors × 3 periods) |
| Successful | 1,042 (97.3%) |
| Failed (logged) | 29 (2.7%) |
| Total rows downloaded | 5,717,080 |
| Missing data impact | Minimal — 29 failures spread across different sensors |

---

## Python dependencies

```
requests
pandas
```

Install:
```bash
pip install requests pandas
```

---

## How to reproduce

```bash
# 1. Fetch all 3,569 sensors
python index.py

# 2. Run full analysis (downloads data + produces results)
python Traffic_Analysis.py

# 3. Open the interactive map
open helsinki_sensors_map.html   # or serve with python -m http.server
```

---

## Next steps

- Investigate the May anomaly — check if specific sensors are driving the spike
- Morning vs evening rush hour comparison
- Hour × day-of-week heatmap
- Year-over-year trend (2023 → 2026)
- Traffic forecasting with Prophet or ARIMA
- Sensor clustering by traffic behaviour pattern (K-means)
- Traffic volume map — plot sensors sized by average volume