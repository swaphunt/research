# Does "Extreme Fear" mark the bottom?: key figures, sources and caveats

All figures come from `data/results/findings.json`, which `scripts/` produces. The key in parentheses is the path in findings.json; `P` stands for `results.label.fear.reset14` and `G` for `results.label.greed.reset14`. Percentages are rounded to one decimal. Decimals are written with a dot so that `shared/check_numbers.py` can trace them.

**Status: reviewed 2026-10-29.**

Review of the article (2026-10-29): (1) advice and FAQ rest only on the robust finding "no better than the same drop without fear"; "worse than an average day" appears only as a fact with "(including 2018)", because it does not hold without 2018 (2f). (2) The article states precisely that the main definitions were locked before returns were seen, and that the ±14-day check and the analysis without 2018 were added during review. (3) The index's weights are cited with a link and date (see `data/SOURCES.md`). (4) Wording about the spread corrected.

**Wording (decided at review):** "In our data, Extreme Fear added nothing beyond the price drop itself. Days with the same 30-day drop but no Extreme Fear did at least as well." Headline: "Extreme Fear has not been a reliable buy signal for Bitcoin". Not "is a bad signal": the intervals cross zero, and absence of evidence is not evidence of absence.

## Do the expectations hold?

| Expectation from the brief | Found | Holds? |
|---|---|---|
| Extreme Fear gives above-average returns in the long run | Median after 180 days −3.9 % (`P.r180.median`) against +13.6 % for all days (`baseline.all_days.r180.median`); after 90 days −9.1 % against +3.5 % | **No.** Rather below, but the interval is wide |
| … but with large swings | 180 days: 10th percentile −44.4 %, 90th percentile +66.1 % (`P.r180.p10`, `P.r180.p90`) | Yes |
| … and few independent episodes | 27 Fear episodes (`results.label.fear.reset14.episodes`), 14 Greed (`results.label.greed.reset14.episodes`) | Yes |
| (Added at review) Extreme Fear says more than the price drop itself | The episodes do no better than days with the same 30-day drop without Extreme Fear; after 90 days only 4.1 % of the matched draws had a lower median than the episodes (`P.r90.matched_pctile`) | **No.** In our data Extreme Fear added nothing beyond the drop itself (holds without days near the episodes, 2e; without 2018 the groups are roughly level, 2f) |

## 1. Data and definitions

### Data
- **Fear & Greed:** alternative.me, daily from 2018-02-01 (`data.fng_first`) to 2026-10-29 (`data.fng_last`), 3189 days (`data.fng_days`). 4 calendar days are missing (`data.fng_missing_days`): 3 after 2018-04-13 and 1 after 2024-10-25 (`fng_gaps.json`).
- **BTC:** BTCUSDT daily candles from Binance (via `data-api.binance.vision`), from 2017-08-17 (`data.btc_first`) to 2026-10-28 (`data.btc_last`), no gaps (`data.btc_missing_days`). Only completed daily candles; the current day is left out (`data.fng_days_without_btc`).
- Raw responses and their sha256 hashes were logged at fetch time; raw responses are not redistributed, see `data/SOURCES.md`.

### Time alignment (no look-ahead)
The index value for day d has timestamp d 00:00 UTC and is known at the start of the day. Entry is the BTC close on the same UTC day d. Forward return over h days: close(d+h) / close(d) − 1, with h = 7, 30, 90 and 180 calendar days. Signals where d+h falls after the last completed BTC day are left out for that horizon (hence 26 Fear episodes at 180 days).

### Signal zones (approved at review 2026-10-29)
Primarily the index's own labels: Extreme Fear ≤ 25, Extreme Greed ≥ 76 (the labels cover 5–25 and 76–95 in the data, `data.label_range`). Robustness: the brief's < 20 and > 80.

| Zone | Days | Episodes (14-day reset) |
|---|---|---|
| Fear ≤ 25 (primary) | 739 (`data.zone_days.fear_le25`) | 27 (`data.episodes_14d.fear_le25`) |
| Fear < 20 (robustness) | 349 (`data.zone_days.fear_lt20`) | 26 (`data.episodes_14d.fear_lt20`) |
| Greed ≥ 76 (primary) | 282 (`data.zone_days.greed_ge76`) | 14 (`data.episodes_14d.greed_ge76`) |
| Greed > 80 (robustness) | 149 (`data.zone_days.greed_gt80`) | 9 (`data.episodes_14d.greed_gt80`) |

### Episodes
First day in the zone after at least 14 index days outside it. Robustness: 7 and 30 days (approved at review).

### Comparison (baseline)
1. **All days:** forward return from every index day.
2. **Random days:** 10000 draws (`method.n_draws`) of as many random index days as there are episodes. `random_pctile` = share of draws with a lower median than the episodes.
3. **Matched (added at review):** for each episode, one random day outside the zone whose 30-day trailing return lies within ±5 percentage points (`method.match_tol`) of the episode's; 10000 repetitions. All Fear episodes had at least 8 matching days (`P.r7.matched_min_pool`), all Greed episodes at least 29 (`G.r7.matched_min_pool`). `matched_pctile` = share of matched draws with a lower median than the episodes.
- **Uncertainty:** 95 % bootstrap interval on the median (10000 resamples of the episodes). No p-values.
- Seed 20261029 (`method.seed`), so all figures can be reproduced.

### Excluded and why
- Only BTC (the brief). Altcoins have shorter history and survivorship bias.
- No fees or slippage: the study measures what the price did after the signal, not a trading strategy.

## 2. Results

### a) Extreme Fear (≤ 25, 27 episodes)

| Horizon | Median | 95 % interval | Share positive | All days, median | Random: share lower | Matched: median | Matched: share lower |
|---|---|---|---|---|---|---|---|
| 7 days | −2.1 % (`P.r7.median`) | −5.0 to +0.9 % | 37.0 % | +0.4 % | 3.1 % | −0.3 % | 6.3 % |
| 30 days | +0.3 % (`P.r30.median`) | −7.3 to +2.9 % | 51.9 % | +1.6 % | 36.4 % | +1.0 % | 43.7 % |
| 90 days | −9.1 % (`P.r90.median`) | −19.8 to +17.1 % | 48.1 % | +3.5 % | 6.4 % | +2.3 % | 4.1 % |
| 180 days | −3.9 % (`P.r180.median`) | −20.5 to +32.6 % | 46.2 % | +13.6 % | 12.7 % | +15.2 % | 16.2 % |

Sources per column: `P.r{h}.ci_lo/ci_hi`, `P.r{h}.share_positive`, `baseline.all_days.r{h}.median`, `P.r{h}.random_pctile`, `P.r{h}.matched_median`, `P.r{h}.matched_pctile`.

- **No edge.** At no horizon is the median after Extreme Fear above all days or above random days. After 7 and 90 days only 3.1 % and 6.4 % of the random draws had a lower median (`P.r7.random_pctile`, `P.r90.random_pctile`).
- **The drop itself gave at least as much.** Days with the same 30-day drop, but without Extreme Fear, gave a higher median at all four horizons (−0.3 %, +1.0 %, +2.3 %, +15.2 %).
- **The spread is large.** After 180 days the worst outcome was −51.5 % (`P.r180.worst`) and the 90th percentile +66.1 % (`P.r180.p90`). The bootstrap intervals cross zero at all horizons.

### b) Which years carry the result?
Episodes per year: 6 in 2018, 5 in 2019, 1 in 2020, 3 in 2021, 5 in 2022, 3 in 2024, 3 in 2025 and 1 in 2026 (`P.episodes_by_year`).

Leave-one-year-out (the median with one year removed at a time):
- 180 days: from −7.7 % (without 2024, `P.r180.loo_min`) to +22.1 % (without 2018, `P.r180.loo_max`). **The negative 180-day median is carried by the 2018 bear market.** Without 2018 it is positive, but still not above all days (+13.6 %) with any certainty.
- 90 days: from −12.4 % (without 2024) to +4.2 % (without 2018).
- 7 days: from −3.4 % to −1.4 %. The short horizon is stable and negative, regardless of which year is removed.
- The COVID crash (episode 2020-03-09) is only one of 27 episodes and does not carry the result.

### c) Robustness

| Variant | Episodes | Median 7 / 30 / 90 / 180 days |
|---|---|---|
| Primary (≤ 25, 14 days) | 27 | −2.1 / +0.3 / −9.1 / −3.9 % |
| The brief's threshold (< 20, 14 days) | 26 (`results.brief.fear.reset14.episodes`) | −1.0 / −1.1 / −4.0 / −9.1 % |
| 7-day reset | 35 (`results.label.fear.reset7.episodes`) | −1.2 / −1.4 / −4.3 / −5.8 % |
| 30-day reset | 14 (`results.label.fear.reset30.episodes`) | −4.8 / −7.2 / −10.8 / −14.0 % |

Source: `results.<threshold>.fear.reset<n>.r<h>.median`. **The conclusion holds across all variants:** no variant gives a median above all days at any horizon. The direction is the same; the size moves with the definition, as expected with so few episodes.

### e) Are the two groups separate? (check added at review)
Matched days just before or after an episode (e.g. the days before the index crosses 25) can share a price path with the episode. 22.7 % of all days outside the zone lie within ±14 days of an episode (`P.share_nonzone_days_near_episode`). Among the matched days the share is higher: 37.2 % (7 days) to 37.8 % (90 days) (`P.r<h>.matched_share_near14`; expected share, since each episode draws one day uniformly from its pool). The article first used 22.7 % for the matched days; corrected before publication. The variant excludes them from the candidate pool:

| Horizon | Episodes | Matched (all) | Matched without ±14 days | Without ±14: share lower |
|---|---|---|---|---|
| 7 days | −2.1 % | −0.3 % | +0.5 % (`P.r7.matched_excl14_median`) | 0.7 % |
| 30 days | +0.3 % | +1.0 % | +2.1 % | 28.2 % |
| 90 days | −9.1 % | +2.3 % | +7.4 % | 0.9 % |
| 180 days | −3.9 % | +15.2 % | +27.6 % | 2.8 % |

Source: `P.r{h}.matched_excl14_median`, `P.r{h}.matched_excl14_pctile`. **The conclusion holds and becomes sharper:** without the nearby days, "similar drops" do even better. Caveat: the episode 2018-02-02 (30-day drop −40.5 %) has only 1 matching day in the variant (`P.r90.matched_excl14_min_pool`) and 8 in the main analysis; all other episodes have many more. One episode out of 27 does not move the median.

### f) Does the matched comparison hold without 2018? (check added during review)
Without the 6 episodes from 2018, 21 remain (`P.episodes_no2018`).

| Horizon | Episodes without 2018 | Same drop without 2018 | Share lower |
|---|---|---|---|
| 7 days | −1.6 % (`P.r7.no2018_median`) | −0.4 % (`P.r7.no2018_matched_median`) | 17.9 % |
| 30 days | −1.4 % | +1.0 % | 29.2 % |
| 90 days | +4.2 % | +2.4 % | 54.9 % |
| 180 days | +22.1 % | +17.6 % | 61.6 % |

**Without 2018 the two groups are roughly level.** The Fear episodes are slightly behind at 7 and 30 days and slightly ahead at 90 and 180 days, all within the noise (`P.r{h}.no2018_matched_pctile`). The wording "Days with the same 30-day drop but no Extreme Fear did at least as well" applies to the full dataset; without 2018 it is "roughly level". The article says so openly. The conclusion "Extreme Fear added nothing you could rely on" holds in both cases.

### d) Extreme Greed (≥ 76, 14 episodes)
- Median +2.6 / +2.5 / +19.7 / +18.1 % after 7 / 30 / 90 / 180 days (`G.r{h}.median`), i.e. above all days at the three shortest horizons.
- Above the matched days (same 30-day rise without Extreme Greed) in 84.2 / 69.7 / 83.9 / 75.7 % of the draws (`G.r{h}.matched_pctile`).
- **But not robust:** the bootstrap intervals cross zero at all horizons, and with a 7-day reset (23 episodes) the median turns negative after 30 and 90 days (−1.8 % and −4.9 %, `results.label.greed.reset7.r{h}.median`). Only 13-14 episodes. We cannot say that Extreme Greed signals either a fall or a rise. In the article: a short section without a chart, "too few episodes, and the sign flips with the episode definition" (decided at review).

## Caveats and uncertainties
1. **Few independent episodes** (27 Fear, 14 Greed). The bootstrap intervals are wide and cross zero everywhere.
2. **Long horizons overlap.** Episodes closer together than 90 or 180 days share part of the same price path (e.g. five episodes in 2022). The intervals therefore understate the uncertainty at 90 and 180 days.
3. **Many comparisons.** 2 zones × 4 horizons × 4 variants = 32 comparisons. That one of them (Fear, 7 days) has a median that only 3.1 % of the random draws fall below is exactly the kind of result one expects to see by chance among so many. It should not be phrased as a finding.
4. **The matched baseline is not perfect.** The matched days often lie in the same market phases as the episodes and are mutually dependent. It shows that the drop alone gives at least as good returns, not that the fear does harm.
5. **The index's methodology has changed over time** (the brief). alternative.me does not document a changelog.
6. **BTCUSDT on one exchange** is not the same as a global USD price. The difference is small for daily closes.
7. **None of the results is a trading rule.** They describe the history 2018–2026.
