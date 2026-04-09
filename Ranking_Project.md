https://avoindata.suomi.fi/data/fi/search?q=toimeentulotuki

https://avoindata.suomi.fi/data/fi/showcase/perustoimeentulotukiuomessa

https://avoindata.suomi.fi/data/en_GB/dataset/?vocab_keywords_en=social+security  ****










| Rank | Project                                                     | Rating   | Core Value                                                                 |
|------|-------------------------------------------------------------|----------|----------------------------------------------------------------------------|
| 1    | Finnish Social Welfare Stress Index (Kela)                 | 9.5/10   | Most unique, most Finland-specific, directly policy-relevant              |
| 2    | Helsinki Building Energy Intelligence                      | 9/10     | Live API + geospatial + forecasting + climate relevance                   |
| 3    | Helsinki Demographic Shift Atlas                           | 8.5/10   | 20 years of district-level data, pairs with Kela project                  |
| 4    | Air Quality + Traffic Fusion                               | 8.5/10   | Two live APIs combined, strong ML signal                                  |
| 5    | District Heat Demand Forecasting                           | 8/10     | Hourly timeseries since 2015, clean forecasting showcase                  |
| 6    | Solar Investment Prioritization Map                        | 7.5/10   | Visually impressive, optimization angle, actionable output                |
| 7    | Helsinki Multimodal Mobility (extend existing)             | 7/10     | You already have the foundation, needs extension                          |
| 8    | GHG Emissions Decomposition (waste + energy + transport)   | 7/10     | Strong if all three sectors combined into one model                       |
| 9    | Helsinki Circular Economy Dashboard                        | 6/10     | Clean and visual but lighter on ML depth                                  |
| 10   | Cross-City SDG Benchmarking (Helsinki/Espoo/Vantaa)        | 5.5/10   | Interesting but XLSX-heavy, limited modeling opportunity                  |








# Finland Open Data — Portfolio Project Ranking

| Rank | Score | Project Title | Original Dataset Title | Project Scope | Key Datasets | Tech Stack | Target Employer |
|------|-------|--------------|----------------------|---------------|--------------|------------|-----------------|
| 1 | 9.5 | Finnish Social Welfare Stress Index | Summary of data on benefit decisions / Number of recipients of unemployment benefits / Basic social assistance: Recipient households / Sickness allowance: Recipients and benefit expenditures by diagnosis | Build a composite welfare dependency index per municipality over time. Cluster municipalities by welfare profile. Forecast 2025–2030 benefit expenditure. Detect post-COVID anomalies in sickness/unemployment patterns. | Kela benefit decisions, unemployment benefits by municipality, sickness allowance by diagnosis (1993–), disability pension, basic social assistance, housing allowance | Python, pandas, scikit-learn, Prophet/ARIMA, LSTM, Plotly/Dash, GeoPandas | Public sector, Kela, THL, Finnish municipalities, policy consultancies |
| 2 | 9.0 | Helsinki Building Energy Intelligence | Energy consumption data of city of Helsinki's utility and service properties / Heat loss from buildings in Helsinki / Photovoltaic potential in the Helsinki metropolitan area / District heat production in Helsinki | Identify heat-inefficient buildings using thermographic data. Score buildings on solar potential vs. current energy consumption. Rank districts by retrofit priority. Forecast district heating demand using hourly timeseries. Output interactive priority investment map. | Nuuka open API (live), heat loss thermographic data, PV potential per building, solar radiant energy on roofs, district heat production hourly (2015–) | Python, REST API, GeoPandas, XGBoost, Prophet, Folium/Kepler.gl, FastAPI | Energy companies, city planning depts, Fortum, Helen, climate tech startups |
| 3 | 8.5 | Helsinki Demographic Shift Atlas | Population in Helsinki by district and age 2004–2023 / Population and foreign people in Helsinki by citizenship / Population and housing production projections of Helsinki / Households in Helsinki by size and district | Cluster Helsinki districts by demographic profile (age, language, origin). Track cluster changes over 20 years. Detect gentrification and aging patterns. Validate against official population projections with your own forecast model. | Population by district/age/language/citizenship (2004–2023), household structure, population projection XLSX, population grid SHP | Python, pandas, scikit-learn (clustering), GeoPandas, Folium, ARIMA/Prophet, Plotly | Finnish municipalities, HSY, urban planning consultancies, research institutes |
| 4 | 8.5 | Helsinki Air Quality & Traffic Fusion | Real time air quality at HSY monitoring sites / Concentrations of air pollutants in Uusimaa / Statistical API for traffic measurement data / Traffic noise zones in Helsinki / Air quality monitoring sites and annual NO2 averages | Predict NO2/PM levels by district from traffic volume + time of day. Use HSY live API as real-time input. Train on historical Uusimaa pollution data. Overlay noise zones as spatial features. Flag high-risk districts. | HSY real-time air quality API (hourly), traffic sensor API (3,569 sensors), Uusimaa historical NO2, noise zones WFS, NO2 exceedance areas | Python, REST API, scikit-learn/XGBoost, LSTM, GeoPandas, Folium, FastAPI, Docker | HSY, environmental consultancies, smart city startups, city of Helsinki |
| 5 | 8.0 | District Heat Demand Forecasting | District heat production in Helsinki / Energy consumption in the Helsinki metropolitan area / Greenhouse emissions in the Helsinki metropolitan area | Forecast hourly district heat demand using 80,000+ data points since 2015. Engineer weather/season features. Compare ARIMA vs Prophet vs LSTM. Detect anomaly winters. Quantify emission savings from demand reduction scenarios. | District heat production hourly CSV (2015–), energy consumption by sector XLSX, GHG emissions by sector XLSX | Python, pandas, Prophet, ARIMA, LSTM, TensorFlow/PyTorch, Matplotlib, Plotly | Helen, Fortum, Vattenfall, energy sector, climate tech |
| 6 | 7.5 | Helsinki Solar Investment Prioritization | Suitable areas for solar panels in Helsinki metropolitan area / Photovoltaic potential in the Helsinki metropolitan area / Amount of solar radiant energy on the roofs / Heat loss from buildings in Helsinki | Build per-building solar ROI score combining PV potential, roof suitability, and current heat loss. Cluster buildings by investment priority tier. Output ranked district map showing where solar investment yields highest return. | Solar suitability SHP, PV potential per building WFS, solar radiant energy WMS, heat loss WMS | Python, GeoPandas, scikit-learn, Folium/Kepler.gl, optimization (PuLP or scipy) | City of Helsinki, solar installers, real estate developers, green investment funds |
| 7 | 7.0 | Helsinki Multimodal Mobility (Extended) | Statistical API for traffic measurement data of the city of Helsinki | Extend existing traffic analysis with ML. Add anomaly detection for unusual traffic events. Fuse with air quality API to predict pollution from traffic volume. Add cyclist/pedestrian trend forecasting. Deploy as live dashboard. | Traffic sensor API (vehicles + pedestrians + cyclists), HSY air quality API, noise zones | Python, REST API, Isolation Forest, XGBoost, Prophet, Streamlit/Dash, Docker | Smart city teams, HSL, city of Helsinki, transport consultancies |
| 8 | 7.0 | Helsinki GHG Emissions Decomposition | Greenhouse emissions in the Helsinki metropolitan area / District heating in the Helsinki metropolitan area / Waste generated in the Helsinki metropolitan area by sector / Energy consumption in the Helsinki metropolitan area | Decompose GHG emissions by sector (transport, heating, waste, industry) over time. Identify which sectors drive increases/reductions. Build scenario models — what emission reduction is achievable per sector by 2030? Compare Helsinki vs EU targets. | GHG emissions XLSX, district heating emissions XLSX, waste by sector XLSX, energy consumption XLSX | Python, pandas, statsmodels, Prophet, Plotly, scenario modeling | HSY, city sustainability offices, EU-funded research, climate consultancies |
| 9 | 6.0 | Helsinki Circular Economy Dashboard | Amount of waste collected from properties / Waste sorting activity levels / Mixed waste composition in Helsinki Metropolitan Area / Total amount of household waste by type and recycling rate | Track recycling rates by waste fraction monthly. Correlate sorting behaviour survey with actual recycling outcomes. Forecast when Helsinki hits EU recycling targets. Visualize district waste generation vs collection efficiency. | Monthly waste collection XLSX, sorting behaviour survey XLSX, waste composition study XLSX, household waste totals XLSX | Python, pandas, Plotly/Dash, Prophet, Streamlit | HSY, waste management companies, circular economy startups |
| 10 | 5.5 | Cross-City SDG Benchmarking | Helsinki sustainable development indicators / Espoo's Sustainable Development Indicator / Vantaa sustainable development indicators | Compare Helsinki, Espoo, Vantaa across UN SDG indicators. Rank cities by SDG progress. Identify which goals are lagging. Build a simple scoring dashboard. Limited ML depth but good for visualization portfolio. | Helsinki SDG PX/JSON, Espoo SDG XLSX, Vantaa SDG XLSX | Python, pandas, Plotly, Streamlit | Municipal strategy teams, UN-affiliated orgs, sustainability consultancies |

---

## Quick Decision Guide

| If you want to target... | Build this first |
|--------------------------|-----------------|
| Public sector / Kela / THL | Project 1 |
| Energy / Climate tech | Projects 2 + 5 |
| Urban planning / Smart city | Projects 3 + 4 |
| Quick win to extend existing work | Project 7 |
| Broadest employer appeal | Projects 1 + 4 + 2 |

---

## Recommended Build Order
1. **Project 7** — Extend your existing traffic work first (fastest to complete, builds momentum)
2. **Project 4** — Fuse traffic with air quality (natural next step, reuses traffic code)
3. **Project 1** — Kela welfare index (most unique, most Finland-specific)
4. **Project 2** — Building energy intelligence (most technically impressive)