# Analysis: Adun Foods distributor network

Every figure below is produced by `scripts/analyse.py` and written to `outputs/key_metrics.json`. The data is synthetic, so the findings describe this dataset and nothing about real Nigerian trade.

## Data quality

Checked before any analysis: no null cells across the five tables, no duplicate order IDs or distributor names, no orphan keys between tables, and `SalesAmount` equals `Quantity` times `UnitPrice` on all 5,702 rows. Both years hold twelve months, so the year-on-year comparison is like for like.

One defect was found and fixed in the generator. 228 sales were dated before their distributor's onboarding date. Onboarding dates are now pulled back to each distributor's first order.

## 1. How did sales move, and when does demand peak?

Sales grew from ₦424,799,800 in 2024 to ₦481,526,400 in 2025, up 13.35%, on 857,198 units across 5,702 orders. Both years share the same shape: a first-quarter peak, a mid-year dip and a December recovery. March 2025 is the strongest month at ₦44.3M and January 2024 the weakest at ₦31.2M. Every quarter of 2025 beat the matching quarter of 2024, so the gain is steady rather than driven by one period.

*Caveat: seasonality is built into the generator, so the shape is by construction, not discovery.*

## 2. Where are we present, and how dependent is each state on one distributor?

Twelve of fourteen states have an Active distributor. Borno and Ebonyi have none.

At national level the network is not over-dependent on anyone. The largest distributor, Ibrahim Sani Ventures, holds 9.91% of sales. Seven distributors reach half of sales and seventeen of thirty-six reach 80%. The Herfindahl index is 513, against 278 if all thirty-six were equal, and well below the 1,500 that usually marks a concentrated market. The Gini coefficient is 0.47.

The exposure sits one level down. Within each state a single distributor usually dominates:

| State | Active distributors | Sales | Top distributor's share |
| --- | --- | --- | --- |
| Lagos | 3 | ₦53,684,730 | 77% |
| Kano | 3 | ₦119,394,990 | 70% |
| Bauchi | 3 | ₦76,483,490 | 67% |
| Delta | 3 | ₦55,920,580 | 64% |
| Kaduna | 3 | ₦48,118,490 | 64% |
| Rivers | 2 | ₦25,354,570 | 63% |
| Ogun | 3 | ₦74,713,490 | 62% |
| Kwara | 3 | ₦148,336,070 | 60% |
| Enugu | 3 | ₦17,931,840 | 56% |
| Anambra | 3 | ₦59,991,580 | 53% |
| Oyo | 3 | ₦157,500,320 | 53% |
| FCT Abuja | 3 | ₦54,387,040 | 45% |

Losing the top distributor in Lagos costs 77% of that market, not 9.91% of national revenue. The reassuring national number and the uncomfortable local one are both true, and only the second is actionable.

*Caveat: shares are measured over Active distributors only. Counting the inactive distributor too would put Rivers at 40% and make it look like the safest state, when it has the fewest distributors of any state.*

## 3. Where did revenue move between 2024 and 2025?

Thirty of thirty-six distributors grew. ₦61,896,050 was gained and ₦5,169,450 lost, a net ₦56,726,600. Median growth per distributor is 12.66%.

Percentage growth and naira growth rank differently, and the naira view is the one that matters. Yakubu Musa Commodities grew fastest at 38.2% and added ₦2.9M. Ifeanyi Okeke Ventures grew a slower 25.0% and added ₦9.3M, the largest single gain in the network.

| Biggest movers | Change | Growth |
| --- | --- | --- |
| Ifeanyi Okeke Ventures | +₦9,299,020 | 25.0% |
| Kawu Aliyu Distribution | +₦6,012,270 | 26.8% |
| Chidinma Foods Nigeria | +₦5,282,550 | 25.6% |
| Emeka Obi Enterprises | −₦3,786,730 | −41.4% |
| Harmony Foods Nigeria | −₦1,037,300 | −8.1% |

Losses are small and concentrated. Emeka Obi Enterprises, the distributor that stopped trading in June 2025, accounts for ₦3.79M of the ₦5.17M lost. Excluding it, the network lost ₦1,382,720 across five distributors, which is 0.3% of revenue.

Eleven of twelve states grew. Bauchi led at 27.4%, and Rivers alone declined, at −10.2%. Rivers is where Emeka Obi Enterprises traded. Its two remaining distributors gained ₦1.6M between them, so the state's decline is the loss of a distributor rather than weakening demand, and the same event explains both the thin coverage on dashboard 2 and the only negative bar on dashboard 3.

*Caveat: starting size does not predict growth here. The correlation between 2024 sales and subsequent growth is 0.03. Any apparent relationship between distributor size and growth is an artefact of how tiers were defined, which is why tiers appear on no dashboard.*

## Summary

| Measure | Value |
| --- | --- |
| Total sales | ₦906,326,200 |
| Year-on-year growth | 13.35% |
| States covered | 12 of 14 |
| Largest distributor's national share | 9.91% |
| Distributors reaching 80% of sales | 17 of 36 |
| Highest single-state dependency | Lagos, 77% |
| Net revenue change | +₦56,726,600 |
| Distributors growing | 30 of 36 |

## What would come next

1. Second distributors in Lagos, Kano and Bauchi, where one partner holds two thirds or more of the state.
2. A replacement in Rivers, which is down to two distributors and is the only state losing revenue.
3. Entry into Borno and Ebonyi, subject to demand data this dataset does not hold.
4. Margin and cost-to-serve data, without which none of the above can be ranked by value.
