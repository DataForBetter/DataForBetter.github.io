# Project scope: Adun Foods distributor network

## Purpose

Adun Foods is a fictional Nigerian consumer goods manufacturer selling packaged foods through independent distributors. This project asks where the network is exposed and where its revenue is moving. It is a portfolio project, built end to end from raw data to dashboards, and written so every figure can be checked against the source.

## Business questions

Three questions, one dashboard each. No dashboard repeats another's measure and dimension pair.

| # | Question | Dashboard |
| --- | --- | --- |
| 1 | How did sales move across 2024 and 2025, and when does demand peak? | 01 Sales Overview |
| 2 | Where are we present, and how dependent is each state on one distributor? | 02 Coverage and Concentration |
| 3 | Where did revenue move between 2024 and 2025? | 03 Revenue Movement |

## In scope

- Order-level sales from January 2024 to December 2025, recorded monthly.
- 36 distributors across 14 states in six geopolitical zones, with 12 states covered.
- 8 products in 4 categories: Breakfast, Cooking Base, Seasonings and Snacks.
- Sales value, units and orders, plus the relationships between distributors, locations, products and dates.
- Descriptive analysis: totals, trends, shares, rankings, growth and concentration measures.
- A Power BI model, three report pages and a colour theme.

## Out of scope

- Margins, costs, discounts, returns and payment terms. The data holds revenue only.
- Stock levels, delivery routes and cost to serve.
- End-consumer data. The unit of analysis is the distributor.
- Market size, competitor sales and population. Coverage is judged against the distributors on file, not against demand.
- Forecasting. The analysis describes what happened.
- Real company data. Every figure is synthetic.

## Data sources

All data sits in `data/` and is produced by `scripts/generate_data.py` with a fixed seed, so it reproduces byte for byte. Column definitions are in `docs/DATA_DICTIONARY.md`.

| File | Rows | Content |
| --- | --- | --- |
| `sales.csv` | 5,702 | Order-level sales lines |
| `distributors.csv` | 36 | Distributor master data and status |
| `locations.csv` | 14 | State, region and zone reference |
| `products.csv` | 8 | Product master data and unit prices |
| `dates.csv` | 731 | Calendar for 2024 and 2025 |

## Assumptions

1. Each sales line is one distributor buying one product in one month.
2. Each product holds one unit price for the whole period, so price effects are not analysed.
3. Status is a recorded attribute. The one Inactive distributor still traded until June 2025.
4. A state counts as covered when it has at least one Active distributor.
5. Growth compares full-year 2025 against full-year 2024. Both years are complete, twelve months each.
6. Dependency is measured over Active distributors only, since a distributor that has stopped trading cannot be depended on.

## A field deliberately left unused

`distributors.csv` carries a `Tier` column, assigned by cumulative share of sales across the whole period. It is not used on any dashboard, and that is deliberate. Tier is derived from the same sales it would be used to explain, so any chart of sales or growth by tier is partly restating its own definition. Growth by tier reads 25.0% for Tier 1 against 13.8% for Tier 3, which suggests large distributors grow faster. Band the same distributors by their 2024 sales instead, which is an independent starting point, and the pattern disappears: 14.4%, 9.4% and 14.7%. The correlation between 2024 size and subsequent growth is 0.03. The column is kept in the data for transparency and left off the dashboards.

## Measure definitions

All measures live in the `Sales` table of the Power BI model.

| Measure | Definition |
| --- | --- |
| Total Sales | `SUM(Sales[SalesAmount])` |
| Total Units | `SUM(Sales[Quantity])` |
| Total Orders | `DISTINCTCOUNT(Sales[OrderID])` |
| Avg Order Value | `DIVIDE([Total Sales], [Total Orders])` |
| Sales 2024 | `CALCULATE([Total Sales], Dates[Year] = 2024)` |
| Sales 2025 | `CALCULATE([Total Sales], Dates[Year] = 2025)` |
| Sales Growth % | `DIVIDE([Sales 2025] - [Sales 2024], [Sales 2024])` |
| Sales Change | `[Sales 2025] - [Sales 2024]` |
| Active Distributors | `CALCULATE(DISTINCTCOUNT(Distributors[DistributorID]), Distributors[Status] = "Active")` |
| Covered States | `CALCULATE(DISTINCTCOUNT(Distributors[LocationID]), Distributors[Status] = "Active")` |
| Top Distributor Share | Largest Active distributor's share of the sales in the current filter context |
| Cumulative Sales % | Running share of total sales, distributors ordered high to low |
| 80% Line | Constant `0.8`, drawn as the Pareto reference line |
| Distributors to 80% of Sales | Count of distributors needed to reach 80% of sales |
| Median Distributor Growth % | `MEDIANX` of each distributor's 2024 to 2025 growth |
| Revenue Gained | Sum of positive `Sales Change` across distributors |
| Revenue Lost | Sum of negative `Sales Change` across distributors |

## Limitations

- The data is synthetic. Patterns come from the generator, so state-level differences are artefacts and carry no claim about Nigerian trade.
- Revenue only. Nothing here speaks to profitability.
- Two years of monthly data is too short to separate trend from seasonality with any confidence.
- Coverage is measured against the distributor list, not against market demand, so an uncovered state is not necessarily an opportunity.

## Deliverables

- `data/` five CSVs, and `AdunFoods_data.xlsx`, the same tables in one workbook.
- `scripts/generate_data.py` and `scripts/analyse.py`, which reproduce the data and every figure on the dashboards.
- `docs/` scope, analysis and data dictionary.
- `dashboards/` three PNG captures from Power BI Desktop.
- `theme/AdunFoods_Theme.json` the report theme.
