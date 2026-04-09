import pandas as pd
import folium

df = pd.read_csv("helsinki_sensors.csv")

m = folium.Map(location=[60.19, 24.97], zoom_start=6)

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=5,
        color="red",
        fill=True,
        popup=f"#{row['sensor_id']} — {row['name']} ({row['source']})"
    ).add_to(m)

m.save("helsinki_sensors_map.html")