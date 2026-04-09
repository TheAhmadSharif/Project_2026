import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

OUTPUT_DIR = "traffic_data"
PLOT_DIR   = "traffic_plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# ─── Load monthly data ────────────────────────────────────────────────────────
print("Loading raw_monthly_357.csv ...")
df = pd.read_csv(f"{OUTPUT_DIR}/raw_monthly_357.csv")
df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
df["year"]      = df["startTime"].dt.year
df["month"]     = df["startTime"].dt.month
df["month_name"]= df["startTime"].dt.month_name()

print(f"Loaded {len(df):,} rows | Years: {sorted(df['year'].unique())}")


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 1 — Summer vs Winter comparison
# Summer : April–October  (months 4–10)
# Winter : November–March (months 11–12 + 1–3)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ANALYSIS 1 — Summer vs Winter")
print("="*60)

def season(month):
    return "Summer (Apr–Oct)" if 4 <= month <= 10 else "Winter (Nov–Mar)"

df["season"] = df["month"].apply(season)

season_summary = (
    df.groupby(["year", "season"])["aggregatedValue"]
    .sum()
    .reset_index()
    .rename(columns={"aggregatedValue": "total_vehicles"})
    .sort_values(["year", "season"])
)

print("\nSummer vs Winter total vehicles per year:")
print(season_summary.to_string(index=False))
season_summary.to_csv(f"{OUTPUT_DIR}/analysis_summer_winter.csv", index=False)

# ── pivot for plotting ─────────────────────────────────────────────────────
pivot_season = season_summary.pivot(
    index="year", columns="season", values="total_vehicles"
).fillna(0)

years       = pivot_season.index.tolist()
summer_vals = pivot_season["Summer (Apr–Oct)"].tolist()
winter_vals = pivot_season["Winter (Nov–Mar)"].tolist()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Helsinki Traffic — Summer vs Winter", fontsize=14, fontweight="bold", y=1.01)

# ── Grouped bar chart ──────────────────────────────────────────────────────
ax1 = axes[0]
x   = range(len(years))
w   = 0.35
bars1 = ax1.bar([i - w/2 for i in x], summer_vals, width=w,
                label="Summer (Apr–Oct)", color="#378ADD", alpha=0.85)
bars2 = ax1.bar([i + w/2 for i in x], winter_vals, width=w,
                label="Winter (Nov–Mar)", color="#7F77DD", alpha=0.85)

for bar in bars1:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(summer_vals)*0.01,
             f"{bar.get_height()/1e6:.1f}M", ha="center", va="bottom", fontsize=9)
for bar in bars2:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(winter_vals)*0.01,
             f"{bar.get_height()/1e6:.1f}M", ha="center", va="bottom", fontsize=9)

ax1.set_xticks(list(x))
ax1.set_xticklabels(years)
ax1.set_ylabel("Total vehicles")
ax1.set_title("Total vehicles by season per year")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M"))
ax1.legend()
ax1.grid(axis="y", alpha=0.3)
ax1.spines[["top", "right"]].set_visible(False)

# ── Season ratio line chart ────────────────────────────────────────────────
ax2 = axes[1]
ratios = [s/w*100 if w > 0 else 0 for s, w in zip(summer_vals, winter_vals)]
ax2.plot(years, ratios, marker="o", color="#D85A30", linewidth=2.5, markersize=8)
ax2.axhline(100, color="#888780", linestyle="--", linewidth=1, alpha=0.6)
for yr, ratio in zip(years, ratios):
    ax2.annotate(f"{ratio:.0f}%", (yr, ratio),
                 textcoords="offset points", xytext=(0, 10),
                 ha="center", fontsize=9)

ax2.set_xticks(years)
ax2.set_ylabel("Summer traffic as % of Winter")
ax2.set_title("Summer-to-Winter ratio (100% = equal)")
ax2.grid(axis="y", alpha=0.3)
ax2.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/summer_vs_winter.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nPlot saved → {PLOT_DIR}/summer_vs_winter.png")


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 2 — Year-by-Year total vehicle count (2023 / 2024 / 2025)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ANALYSIS 2 — Year by Year (2023 / 2024 / 2025)")
print("="*60)

# Filter only full years of interest
df_years = df[df["year"].isin([2023, 2024, 2025])].copy()

# ── Annual totals ──────────────────────────────────────────────────────────
annual = (
    df_years.groupby("year")["aggregatedValue"]
    .sum()
    .reset_index()
    .rename(columns={"aggregatedValue": "total_vehicles"})
)
annual["growth_%"] = annual["total_vehicles"].pct_change().mul(100).round(1)

print("\nAnnual totals:")
print(annual.to_string(index=False))
annual.to_csv(f"{OUTPUT_DIR}/analysis_yearly.csv", index=False)

# ── Monthly profile per year (trend lines) ────────────────────────────────
monthly_year = (
    df_years.groupby(["year", "month"])["aggregatedValue"]
    .sum()
    .reset_index()
    .rename(columns={"aggregatedValue": "total_vehicles"})
)

month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]
colors_year  = {2023: "#378ADD", 2024: "#1D9E75", 2025: "#D85A30"}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Helsinki Traffic — Year by Year (2023–2025)",
             fontsize=14, fontweight="bold", y=1.01)

# ── Annual bar chart ───────────────────────────────────────────────────────
ax1 = axes[0]
bar_colors = [colors_year.get(y, "#888780") for y in annual["year"]]
bars = ax1.bar(annual["year"].astype(str), annual["total_vehicles"],
               color=bar_colors, alpha=0.85, width=0.5)

for bar, (_, row) in zip(bars, annual.iterrows()):
    label = f"{row['total_vehicles']/1e6:.2f}M"
    if pd.notna(row["growth_%"]) and row["growth_%"] != 0:
        sign  = "+" if row["growth_%"] > 0 else ""
        label += f"\n({sign}{row['growth_%']:.1f}%)"
    ax1.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + annual["total_vehicles"].max() * 0.01,
             label, ha="center", va="bottom", fontsize=9)

ax1.set_ylabel("Total vehicles")
ax1.set_title("Annual total vehicle count")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M"))
ax1.grid(axis="y", alpha=0.3)
ax1.spines[["top", "right"]].set_visible(False)

# ── Monthly trend lines per year ───────────────────────────────────────────
ax2 = axes[1]
for yr, grp in monthly_year.groupby("year"):
    grp_sorted = grp.sort_values("month")
    ax2.plot(grp_sorted["month"], grp_sorted["total_vehicles"],
             marker="o", label=str(yr), color=colors_year.get(yr, "#888780"),
             linewidth=2.5, markersize=6)

ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(month_labels, rotation=45, ha="right")
ax2.set_ylabel("Total vehicles")
ax2.set_title("Monthly profile by year")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M"))
ax2.legend(title="Year")
ax2.grid(alpha=0.3)
ax2.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/year_by_year.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Plot saved → {PLOT_DIR}/year_by_year.png")


# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("DONE")
print("="*60)
print(f"\nCSV outputs in {OUTPUT_DIR}/:")
print("  analysis_summer_winter.csv  — summer vs winter totals per year")
print("  analysis_yearly.csv         — annual totals with growth %")
print(f"\nPlots in {PLOT_DIR}/:")
print("  summer_vs_winter.png        — grouped bars + ratio line")
print("  year_by_year.png            — annual bars + monthly trend lines")
