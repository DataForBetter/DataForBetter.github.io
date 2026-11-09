# Data dictionary

All files are in `data/` and are comma-separated with a header row. Currency is Naira (₦). Keys link the tables as shown in the relationships below.

## sales.csv (fact table, 5,702 rows)

| Column | Type | Description |
| --- | --- | --- |
| OrderID | Text | Unique sales line identifier, for example `O000001` |
| OrderDate | Date | First day of the month the order was recorded, 1 January 2024 to 1 December 2025 |
| DistributorID | Text | Key to `distributors.csv` |
| ProductID | Text | Key to `products.csv` |
| Quantity | Whole number | Units sold on this line |
| UnitPrice | Number (₦) | Price per unit, copied from the product master |
| SalesAmount | Number (₦) | Quantity multiplied by UnitPrice |

## distributors.csv (36 rows)

| Column | Type | Description |
| --- | --- | --- |
| DistributorID | Text | Primary key, for example `D001` |
| DistributorName | Text | Fictional distributor name with a number suffix, unique within the file |
| LocationID | Text | Key to `locations.csv`, the state where the distributor operates |
| OnboardedDate | Date | Date the distributor joined the network, between 2021 and 2024 |
| Status | Text | `Active` or `Inactive`. D030 is the only Inactive distributor |
| Tier | Text | `Tier 1`, `Tier 2` or `Tier 3`, derived from cumulative sales share. Kept for transparency and deliberately unused on the dashboards, see SCOPE.md |

## locations.csv (14 rows)

| Column | Type | Description |
| --- | --- | --- |
| LocationID | Text | Primary key, for example `L01` |
| State | Text | Nigerian state name |
| Region | Text | Geopolitical zone the state belongs to, for example `South West` |
| Zone | Text | Same values as Region. Kept for compatibility with the report, and can be ignored |

Borno and Ebonyi have no active distributor and are the two uncovered states.

## products.csv (8 rows)

| Column | Type | Description |
| --- | --- | --- |
| ProductID | Text | Primary key, for example `P01` |
| ProductName | Text | Product name including pack size |
| Category | Text | Breakfast, Cooking Base, Seasonings or Snacks |
| UnitPrice | Number (₦) | Fixed price per unit for the whole period |

## dates.csv (731 rows)

| Column | Type | Description |
| --- | --- | --- |
| Date | Date | Every calendar day in 2024 and 2025 |
| Year | Whole number | Calendar year |
| MonthNumber | Whole number | Month from 1 to 12, used to sort month names |
| Month | Text | Short month name, for example `Mar` |
| MonthYear | Text | For example `Mar 2025` |
| Quarter | Text | `Q1` to `Q4` |

## Relationships in the model

| From | To | Cardinality |
| --- | --- | --- |
| Sales[DistributorID] | Distributors[DistributorID] | Many to one |
| Sales[ProductID] | Products[ProductID] | Many to one |
| Sales[OrderDate] | Dates[Date] | Many to one |
| Distributors[LocationID] | Locations[LocationID] | Many to one |

## Measures

Measures live in the `Sales` table of the Power BI model. Their definitions are listed in `docs/SCOPE.md`.

| Group | Measures |
| --- | --- |
| Core sales | Total Sales, Total Units, Total Orders, Avg Order Value, Sales 2024, Sales 2025, Sales Growth %, Sales Change |
| Coverage | Active Distributors, Covered States |
| Concentration | Top Distributor Share, Cumulative Sales %, 80% Line, Distributors to 80% of Sales |
| Movement | Revenue Gained, Revenue Lost, Median Distributor Growth % |
