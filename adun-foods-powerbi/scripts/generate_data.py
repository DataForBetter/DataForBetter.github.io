"""
Generate the synthetic Adun Foods distributor dataset used by the Power BI project.

Everything here is fictional. The seed is fixed so the output is reproducible.
Run from the project root:  python scripts/generate_data.py
Outputs CSV files into data/ and a metrics.json summary used by the portfolio website.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2024
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# ---------------------------------------------------------------- locations
# Fictional region grouping of Nigerian states (six geopolitical zones).
LOCATIONS = [
    # LocationID, State, Region, Zone
    ("L01", "Lagos", "South West", "South West"),
    ("L02", "Oyo", "South West", "South West"),
    ("L03", "Ogun", "South West", "South West"),
    ("L04", "Anambra", "South East", "South East"),
    ("L05", "Enugu", "South East", "South East"),
    ("L06", "Rivers", "South South", "South South"),
    ("L07", "Delta", "South South", "South South"),
    ("L08", "FCT Abuja", "North Central", "North Central"),
    ("L09", "Kwara", "North Central", "North Central"),
    ("L10", "Kano", "North West", "North West"),
    ("L11", "Kaduna", "North West", "North West"),
    ("L12", "Borno", "North East", "North East"),
    ("L13", "Bauchi", "North East", "North East"),
    ("L14", "Ebonyi", "South East", "South East"),
]
locations = pd.DataFrame(
    LOCATIONS, columns=["LocationID", "State", "Region", "Zone"]
)

# Two states deliberately have no active distributor, to show coverage gaps.
UNCOVERED = {"Borno", "Ebonyi"}

# ---------------------------------------------------------------- distributors
# A fixed roster of 36 distinct trading names, so no distributor needs a
# numeric suffix to stay unique.
DISTRIBUTOR_NAMES = [
    "Adewale & Sons Trading", "Bright Horizon Ventures", "Chidinma Foods Nigeria",
    "Danjuma Commodities", "Eagle Crest Distribution", "Folasade Enterprises",
    "Garba Yusuf Trading", "Harmony Foods Nigeria", "Ibrahim Sani Ventures",
    "Jubilee Wholesale Nigeria", "Kelechi Brothers Trading", "Lanre Adebayo Ventures",
    "Mainland Provisions", "Nwachukwu Trading Company", "Oluwaseun Global Concept",
    "Pacesetter Distribution", "Queensway Foods", "Rahman Bello Enterprises",
    "Sabon Gari Provisions", "Tunde Ogunleye Ventures", "Unity Mart Distribution",
    "Victory Gate Trading", "Wazobia Foods Nigeria", "Yakubu Musa Commodities",
    "Zenith Pantry Supplies", "Abiola Grace Ventures", "Bendel Foods Company",
    "Chukwuemeka Trading", "Dangogo Provisions", "Emeka Obi Enterprises",
    "Fountain Head Foods", "Golden Gate Provisions", "Hauwa Bala Trading",
    "Ifeanyi Okeke Ventures", "Jide Martins Company", "Kawu Aliyu Distribution",
]

covered_locs = locations[~locations["State"].isin(UNCOVERED)].reset_index(drop=True)
n_distributors = len(DISTRIBUTOR_NAMES)

dist_rows = []
size_factor = rng.lognormal(mean=0.0, sigma=1.0, size=n_distributors)
for i in range(n_distributors):
    loc = covered_locs.iloc[i % len(covered_locs)]
    onboarded = pd.Timestamp("2021-01-01") + pd.Timedelta(days=int(rng.integers(0, 1400)))
    status = "Active"
    dist_rows.append({
        "DistributorID": f"D{i + 1:03d}",
        "DistributorName": DISTRIBUTOR_NAMES[i],
        "LocationID": loc["LocationID"],
        "OnboardedDate": onboarded.date().isoformat(),
        "Status": status,
        "SizeFactor": round(float(size_factor[i]), 4),
    })
distributors = pd.DataFrame(dist_rows)

# Add one lapsed distributor to show status filtering.
distributors.loc[distributors["DistributorID"] == "D030", "Status"] = "Inactive"

# ---------------------------------------------------------------- products
products = pd.DataFrame([
    ("P01", "Jollof Seasoning 100g", "Seasonings", 850),
    ("P02", "Pepper Soup Spice 50g", "Seasonings", 620),
    ("P03", "Instant Oats 500g", "Breakfast", 1450),
    ("P04", "Cocoa Drink 400g", "Breakfast", 1900),
    ("P05", "Groundnut Snack 80g", "Snacks", 420),
    ("P06", "Plantain Chips 75g", "Snacks", 380),
    ("P07", "Tomato Paste 210g", "Cooking Base", 560),
    ("P08", "Palm Oil 1L", "Cooking Base", 2300),
], columns=["ProductID", "ProductName", "Category", "UnitPrice"])

# ---------------------------------------------------------------- dates
months = pd.date_range("2024-01-01", "2025-12-01", freq="MS")

# ---------------------------------------------------------------- sales
sales_rows = []
product_ids = products["ProductID"].tolist()
prices = dict(zip(products["ProductID"], products["UnitPrice"]))
for _, d in distributors.iterrows():
    base = d["SizeFactor"] * 220
    for m_idx, month in enumerate(months):
        growth = 1 + 0.015 * m_idx
        seasonal = 1 + 0.12 * np.sin(2 * np.pi * month.month / 12)
        for pid in product_ids:
            if rng.random() < 0.18:  # not every distributor stocks every line
                continue
            qty = int(max(0, rng.poisson(base * growth * seasonal * rng.uniform(0.2, 0.5))))
            if qty == 0:
                continue
            sales_rows.append({
                "OrderDate": month.date().isoformat(),
                "DistributorID": d["DistributorID"],
                "ProductID": pid,
                "Quantity": qty,
                "UnitPrice": prices[pid],
                "SalesAmount": qty * prices[pid],
            })
sales = pd.DataFrame(sales_rows)
sales.insert(0, "OrderID", [f"O{i + 1:06d}" for i in range(len(sales))])

# Inactive distributor stops selling after mid 2025.
inactive_ids = distributors.loc[distributors["Status"] == "Inactive", "DistributorID"]
sales = sales[~(sales["DistributorID"].isin(inactive_ids) & (sales["OrderDate"] > "2025-06-01"))]
sales = sales.reset_index(drop=True)
sales["OrderID"] = [f"O{i + 1:06d}" for i in range(len(sales))]

# ---------------------------------------------------------------- calendar
dates = pd.DataFrame({"Date": pd.date_range("2024-01-01", "2025-12-31", freq="D")})
dates["Year"] = dates["Date"].dt.year
dates["MonthNumber"] = dates["Date"].dt.month
dates["Month"] = dates["Date"].dt.strftime("%b")
dates["MonthYear"] = dates["Date"].dt.strftime("%b %Y")
dates["Quarter"] = "Q" + dates["Date"].dt.quarter.astype(str)
dates["Date"] = dates["Date"].dt.date.astype(str)

# ------------------------------------------------- onboarding date integrity
# A distributor cannot be onboarded after its first order, so pull any later
# onboarding date back to the first sale on record.
_first_sale = sales.groupby("DistributorID")["OrderDate"].min()
distributors["OnboardedDate"] = [
    min(pd.Timestamp(o), pd.Timestamp(_first_sale[d])).date().isoformat()
    for d, o in zip(distributors["DistributorID"], distributors["OnboardedDate"])
]

# ---------------------------------------------------------------- distributor tiers
# Tier 1: distributors that make up the first 50% of total sales (ranked by sales).
# Tier 2: the next 30% of sales (up to 80% cumulative). Tier 3: the remaining 20%.
ranked_sales = sales.groupby("DistributorID")["SalesAmount"].sum().sort_values(ascending=False)
cum_before = ranked_sales.cumsum().shift(fill_value=0) / ranked_sales.sum()


def tier_for(distributor_id):
    share_before = cum_before.get(distributor_id, 1.0)
    if share_before < 0.5:
        return "Tier 1"
    if share_before < 0.8:
        return "Tier 2"
    return "Tier 3"


distributors["Tier"] = distributors["DistributorID"].map(tier_for)

# ---------------------------------------------------------------- write CSVs
locations.to_csv(DATA / "locations.csv", index=False)
distributors.drop(columns=["SizeFactor"]).to_csv(DATA / "distributors.csv", index=False)
products.to_csv(DATA / "products.csv", index=False)
sales.to_csv(DATA / "sales.csv", index=False)
dates.to_csv(DATA / "dates.csv", index=False)

# ---------------------------------------------------------------- metrics
dist_sales = sales.groupby("DistributorID")["SalesAmount"].sum().sort_values(ascending=False)
total = dist_sales.sum()
top_n = max(1, round(len(dist_sales) * 0.2))
top20_share = dist_sales.head(top_n).sum() / total

# Gini coefficient over distributor sales (including zero-sales distributors).
all_sales = distributors[["DistributorID"]].merge(
    dist_sales.rename("Sales").reset_index(), on="DistributorID", how="left"
)["Sales"].fillna(0).sort_values().to_numpy(dtype=float)
n = len(all_sales)
cum = np.cumsum(all_sales)
gini = (n + 1 - 2 * np.sum(cum) / cum[-1]) / n

covered_state_count = distributors.merge(locations, on="LocationID")["State"].nunique()
uncovered_count = len(UNCOVERED)

region_sales = (
    sales.merge(distributors, on="DistributorID")
    .merge(locations, on="LocationID")
    .groupby("Region")["SalesAmount"].sum()
    .sort_values(ascending=False)
)
top_region = region_sales.index[0]
top_region_share = region_sales.iloc[0] / total

active_distributors = int((distributors["Status"] == "Active").sum())

metrics = {
    "total_sales_ngn": int(total),
    "distributor_count": int(len(distributors)),
    "active_distributor_count": active_distributors,
    "top20_share_pct": round(float(top20_share) * 100, 1),
    "top20_distributor_count": int(top_n),
    "gini": round(float(gini), 2),
    "uncovered_locations": int(uncovered_count),
    "covered_states": int(covered_state_count),
    "top_region": top_region,
    "top_region_share_pct": round(float(top_region_share) * 100, 1),
}

(ROOT / "outputs").mkdir(exist_ok=True)
(ROOT / "outputs" / "generation_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(json.dumps(metrics, indent=2))
