# Data and temporal contracts

## Identity and membership

Use reviewed `security_id` values. Tickers, API routes and CIKs are not interchangeable
security IDs. The live `sp500_long_latest_profiles` table has no `security_id` column;
the monthly population and daily population audit supply stable identities. Membership
is historical and date-specific. A holding's next-month valuation does not depend on
remaining in the index, but a different security reusing its route must block continuity.
Prices stay separated by adjustment basis; stock technicals use `adj_close` and original
volume conventions. Never substitute an acquirer's prices for a predecessor.

## Landing and Bronze

Each JSONL line is `{meta,data}`. `data` retains the source payload; metadata includes
source/entity, source kind, run, retrieval/ingestion clocks, safe request parameters,
canonical string source key, canonical payload SHA256 and stable event SHA256. Requests
with missing business keys are explicitly marked unresolved, not silently certified.
Observation identity also includes capture, normalization version and source-row ordinal.
Same-capture retries deduplicate; independent captures and A-to-B-to-A revisions survive. Files publish without replacement. Checkpoints
verify file hashes before resuming. API errors cannot advance checkpoints.

Raw wrapped API responses remain wrapped. Generic Silver projections expect flat rows;
source-specific wrapper normalization must be reviewed before those APIs feed generic jobs.
PostgreSQL bootstraps are `postgres_reconstruction`, never original vendor vintages.

## Silver and knowledge time

Typed fields and business keys are explicit. Failed casts, NULL keys, duplicate revision
keys or conflicting immutable rows fail. Payload knowledge clocks retain their meaning;
capture provenance lives in `_landing_*` fields. Capture time is not historical first-seen
time. Revision history remains available rather than being reduced to today's latest row.

Strict as-of selection requires known `source_release_at`, `first_seen_at`, `ingested_at`
and `eligible_at`, all no later than the signal cutoff, with `observed_vintage` evidence.
Uncertain reconstructed financial history is replay-only and cannot pass strict vintage
certification. Fiscal period end alone does not make a filing available.

## Gold and monthly semantics

Legacy `quarterly`/`week_end` SQL names represent monthly signals. The signal session and
following month's endpoint must match the NYSE calendar, including early closes. A partial
following month produces unknown outcomes, not a short-period monthly return. Known
signal cutoffs must be timezone-aware. No join may shift across an absent month.

Features use an explicit projection and exclude outcomes. Forward returns, beat-benchmark
and target labels belong to separate datasets. Missing factor or valuation rows stay NULL;
no outcome test determines predictor eligibility or silently shrinks the population.
Top-quintile labels rank known returns in the full retained monthly population; unknown
returns retain NULL labels. The binding records the population used for ranking.

Stock technical calculations reuse reviewed pure definitions from the original notebook;
they retain its observed-row rolling policy for comparison. The optional exploratory
session-aligned technical function is separately labeled and is not production parity.
The feature factory recomputes the original fundamental, stock, sector and macro
formulas from canonical observations. The model-input assembler then applies the
three documented stock-relative-sector formulas and the ordered predictor contract.
Historical fundamental parity covers 64 fields across all 53,423 baseline rows.

## Snapshots and acceptance

Local snapshots bind feature version, snapshot ID, run ID, source SHA256 values, schema
and deterministic payload bytes. A retry with different content or lineage fails.
Cloud snapshots also require an aware as-of time and manifest hash. Outcomes remain
separate. Same-ID retries compare both manifest and actual rows. Application-level
immutability requires coordinated writers and Unity Catalog permissions; consumers must
not have overwrite/drop rights over frozen evidence.

Exact cohort/key, column and NULL-pattern checks precede numeric tolerance checks.
No intersection-only comparison can pass by dropping mismatches. A local test or ZIP hash
cannot substitute for source coverage, actual Delta execution, factor/label/backtest
reconciliation or repeated parallel refresh validation.
