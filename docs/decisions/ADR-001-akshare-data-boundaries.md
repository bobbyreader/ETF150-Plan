# ADR-001: AkShare Data Boundaries And Fallbacks

## Status
Accepted

## Date
2026-05-09

## Context
The project needs more realistic market data without making strategy output look more precise than the upstream data supports. AkShare provides useful A-share valuation endpoints, ETF IOPV data, and broad historical market prices, but coverage differs by market.

## Decision
Use AkShare as the live provider with explicit per-module data boundaries:

- A-share index valuation uses index PE/PB history plus constituent-level TTM PE where available.
- Non-A-share panel rows use real historical price percentile proxies, not PE/PB valuation percentiles.
- Provider calls are cached as DataFrames under `.cache/etf150/akshare/`.
- Live request success refreshes cache; live request failure falls back to stale cache; missing cache raises an explicit error.
- Mock data remains only for tests and offline demos and is never used as a silent live-data fallback.

## Alternatives Considered

### Fail Fast Without Cache
- Pros: Simple and avoids stale data.
- Cons: AkShare endpoints can be temporarily unavailable, making the app brittle for routine use.
- Rejected because short outages should not prevent reading recent market context.

### Silent Fallback To Mock Data
- Pros: The app always returns something.
- Cons: High risk of mistaking demo data for real market output.
- Rejected for correctness and user trust.

### Treat Price Percentile As Valuation For All Markets
- Pros: Simple cross-market comparison.
- Cons: Price percentile is not the same as valuation percentile.
- Rejected as a label. The app may use price percentile as a proxy only when the note says so clearly.

## Consequences
- A-share outputs are closer to the 150-plan requirement for strict equal-weight PE.
- Non-A-share panel rows are useful as a market-temperature proxy but remain less authoritative than A-share valuation rows.
- Cache files are local runtime artifacts and should not be committed.
