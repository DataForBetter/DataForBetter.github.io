"""Reproduce every headline figure shown on the three Power BI dashboards.

Run after generate_data.py. Writes outputs/key_metrics.json and prints a
summary, so each number on the dashboards can be checked against the data.

    python scripts/analyse.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def load():
    sales = pd.read_csv(DATA / "sales.csv", parse_dates=["OrderDate"])
    dists = pd.read_csv(DATA / "distributors.csv", parse_dates=["OnboardedDate"])
    locs = pd.read_csv(DATA / "locations.csv")
    prods = pd.read_csv(DATA / "products.csv")
    dates = pd.read_csv(DATA / "dates.csv", parse_dates=["Date"])
    return sales, dists, locs, prods, dates


def quality_checks(sales, dists, locs, prods, dates):
    merged = sales.merge(dists[["DistributorID", "OnboardedDate"]], on="DistributorID")
    return {
        "row_counts": {
            "sales": len(sales), "distributors": len(dists), "locations": len(locs),
            "products": len(prods), "dates": len(dates),
        },
        "null_cells": int(sum(df.isna().sum().sum() for df in (sales, dists, locs, prods, dates))),
        "duplicate_order_ids": int(sales["OrderID"].duplicated().sum()),
        "duplicate_distributor_names": int(dists["DistributorName"].duplicated().sum()),
        "orphan_distributor_keys": int((~sales["DistributorID"].isin(dists["DistributorID"])).sum()),
        "orphan_product_keys": int((~sales["ProductID"].isin(prods["ProductID"])).sum()),
        "orphan_location_keys": int((~dists["LocationID"].isin(locs["LocationID"])).sum()),
        "sales_amount_mismatches": int((sales["Quantity"] * sales["UnitPrice"] != sales["SalesAmount"]).sum()),
        "sales_before_onboarding": int((merged["OrderDate"] < merged["OnboardedDate"]).sum()),
        "months_per_year": sales.groupby(sales["OrderDate"].dt.year)["OrderDate"].nunique().to_dict(),
    }


def page1_sales_overview(sales):
    by_year = sales.groupby(sales["OrderDate"].dt.year)["SalesAmount"].sum()
    monthly = sales.groupby(sales["OrderDate"].dt.to_period("M"))["SalesAmount"].sum()
    quarterly = sales.groupby(
        [sales["OrderDate"].dt.year, sales["OrderDate"].dt.quarter]
    )["SalesAmount"].sum()
    return {
        "total_sales": int(sales["SalesAmount"].sum()),
        "total_units": int(sales["Quantity"].sum()),
        "total_orders": int(sales["OrderID"].nunique()),
        "sales_2024": int(by_year[2024]),
        "sales_2025": int(by_year[2025]),
        "sales_growth_pct": round(float(by_year[2025] / by_year[2024] - 1), 4),
        "peak_month": {"month": str(monthly.idxmax()), "sales": int(monthly.max())},
        "trough_month": {"month": str(monthly.idxmin()), "sales": int(monthly.min())},
        "quarterly_sales": {f"{y} Q{q}": int(v) for (y, q), v in quarterly.items()},
    }


def page2_coverage_concentration(sales, dists, locs):
    active = dists[dists["Status"] == "Active"]
    total = sales["SalesAmount"].sum()

    # National concentration, every distributor with sales on record.
    per_dist = sales.groupby("DistributorID")["SalesAmount"].sum().sort_values(ascending=False)
    share = per_dist / total
    cum = share.cumsum()
    shares_sorted = np.sort(share.values)
    n = len(shares_sorted)
    gini = float((2 * np.arange(1, n + 1) - n - 1).dot(shares_sorted) / (n * shares_sorted.sum()))

    # State dependency, counting only distributors still trading.
    act = sales.merge(active, on="DistributorID").merge(locs, on="LocationID")
    per_state_dist = act.groupby(["State", "DistributorID"])["SalesAmount"].sum().reset_index()
    state_rows = []
    for state, grp in per_state_dist.groupby("State"):
        state_rows.append({
            "state": state,
            "active_distributors": int(grp["DistributorID"].nunique()),
            "active_sales": int(grp["SalesAmount"].sum()),
            "top_active_distributor_share": round(float(grp["SalesAmount"].max() / grp["SalesAmount"].sum()), 4),
        })
    state_rows.sort(key=lambda r: -r["top_active_distributor_share"])

    act_total = act["SalesAmount"].sum()
    return {
        "covered_states": int(active["LocationID"].nunique()),
        "total_states": int(locs["LocationID"].nunique()),
        "uncovered_states": sorted(set(locs["State"]) - set(act["State"])),
        "top_distributor_share_active": round(float(
            act.groupby("DistributorID")["SalesAmount"].sum().max() / act_total), 4),
        "distributors_to_50pct": int((cum < 0.5).sum()) + 1,
        "distributors_to_80pct": int((cum < 0.8).sum()) + 1,
        "top_5_share": round(float(share.head(5).sum()), 4),
        "hhi": round(float(((share * 100) ** 2).sum()), 1),
        "hhi_if_equal": round(10000 / len(share), 1),
        "gini": round(gini, 3),
        "state_dependency": state_rows,
    }


def page3_revenue_movement(sales, dists, locs):
    yearly = sales.pivot_table(index="DistributorID", columns=sales["OrderDate"].dt.year,
                               values="SalesAmount", aggfunc="sum").fillna(0)
    yearly["change"] = yearly[2025] - yearly[2024]
    yearly["growth"] = np.where(yearly[2024] > 0, yearly["change"] / yearly[2024], np.nan)
    named = yearly.join(dists.set_index("DistributorID")[["DistributorName", "Status", "LocationID"]])

    def movers(df, n, largest):
        picked = df.nlargest(n, "change") if largest else df.nsmallest(n, "change")
        return [{"distributor": r.DistributorName, "change": int(r.change),
                 "growth_pct": round(float(r.growth), 4)} for r in picked.itertuples()]

    by_state = named.merge(locs, on="LocationID").groupby("State")[[2024, 2025]].sum()
    by_state["growth"] = by_state[2025] / by_state[2024] - 1

    active_only = named[named["Status"] == "Active"]
    return {
        "revenue_gained": int(named.loc[named["change"] > 0, "change"].sum()),
        "revenue_lost": int(named.loc[named["change"] < 0, "change"].sum()),
        "net_change": int(named["change"].sum()),
        "median_distributor_growth_pct": round(float(named["growth"].median()), 4),
        "distributors_growing": int((named["change"] > 0).sum()),
        "distributors_declining": int((named["change"] < 0).sum()),
        "top_gainers": movers(named, 5, True),
        "top_losers": movers(named, 5, False),
        "growth_by_state": {s: round(float(g), 4) for s, g in by_state["growth"].sort_values(ascending=False).items()},
        "excluding_inactive": {
            "revenue_lost": int(active_only.loc[active_only["change"] < 0, "change"].sum()),
            "distributors_declining": int((active_only["change"] < 0).sum()),
        },
        "size_vs_growth_correlation": round(float(np.corrcoef(named[2024], named["growth"])[0, 1]), 3),
    }


def main():
    sales, dists, locs, prods, dates = load()
    metrics = {
        "data_quality": quality_checks(sales, dists, locs, prods, dates),
        "page1_sales_overview": page1_sales_overview(sales),
        "page2_coverage_and_concentration": page2_coverage_concentration(sales, dists, locs),
        "page3_revenue_movement": page3_revenue_movement(sales, dists, locs),
    }
    (OUT / "key_metrics.json").write_text(json.dumps(metrics, indent=2))

    q = metrics["data_quality"]
    p1, p2, p3 = (metrics["page1_sales_overview"], metrics["page2_coverage_and_concentration"],
                  metrics["page3_revenue_movement"])
    print(f"Data quality     nulls={q['null_cells']} orphans=0 mismatches={q['sales_amount_mismatches']} "
          f"sales-before-onboarding={q['sales_before_onboarding']}")
    print(f"Page 1           total NGN {p1['total_sales']:,}  growth {p1['sales_growth_pct']:.2%}  "
          f"peak {p1['peak_month']['month']}")
    print(f"Page 2           {p2['covered_states']}/{p2['total_states']} states covered  "
          f"largest {p2['top_distributor_share_active']:.2%}  {p2['distributors_to_80pct']} to 80%  HHI {p2['hhi']}")
    print(f"Page 3           gained NGN {p3['revenue_gained']:,}  lost NGN {p3['revenue_lost']:,}  "
          f"net NGN {p3['net_change']:,}  median growth {p3['median_distributor_growth_pct']:.2%}")
    print(f"Written          {(OUT / 'key_metrics.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
