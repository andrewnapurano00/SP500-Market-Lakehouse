# Setup and operations

## 1. Install and configure

Install the project with `python -m pip install -e ".[postgres,databricks,test]"`. Copy `.env.example` to `.env` and configure credentials locally. Use an authenticated Databricks CLI profile; never place access tokens in committed JSON or notebook parameters.

`config/operator.example.json` documents the operator-local values. Copy it to ignored `config/operator.json`. Replace every placeholder with reviewed infrastructure paths and SHA256 values. Required-feature lists describe data coverage and deliberately exclude forward outcomes.

## 2. Create the lakehouse

Run `notebooks/00_setup.py` with a writable catalog and prefix. It creates the schemas and Volumes. The `free` bundle target uses serverless compute; the `classic` target requires an explicitly supplied Unity Catalog-capable cluster.

Build a wheel with `python -m build --wheel`. Use a content-addressed wheel path for operational jobs so a changed build cannot reuse a stale dependency URI. Import the source notebooks into the configured Workspace directory. The portable deployment helper creates job IDs when absent and records them in ignored operator configuration; it does not contain the author's live job IDs.

```bash
databricks bundle validate -t free --var catalog=your_catalog --profile SP500
```

## 3. Bootstrap historical data

The optional `sql/postgres` DDL creates structure only. For an existing reviewed PostgreSQL source, configure environment credentials and use:

```bash
python scripts/export_full_history.py --output outputs/baseline_export
```

The export is a single read-only repeatable-read snapshot. Tables must match the reviewed contract. Its manifest records schemas, counts, NULL rates, date ranges, key multiplicity and content hashes. An interrupted transaction cannot be resumed as the same snapshot; retain the failed run and use a new directory.

Upload the verified export and manifest to the configured exports Volume. Run `05_import_history.py`, `10_publish_canonical_baseline.py`, `11_complete_silver_baseline.py`, `08_build_gold_history.py` and the relevant validation notebooks using their explicit widgets. Supply original profile/identity evidence, the ordered feature contract and required source mappings. Do not point a new installation at example paths and claim the historical dataset exists.

Some earlier notebooks implement bounded migration proofs; they are not replacements for the complete baseline path. `16_repair_target_basis.py` is an explicit recovery operation for an affected historical release, not a step to run during ordinary setup.

## 4. Collect and normalize

Register reviewed security routes and evidence before collection. The collector preflights membership and identity in Databricks. Unknown identities stop for review rather than inventing security IDs.

The collector supports an explicit date range, request budget and unique run ID. Only `--execute` fetches vendor payloads. Source responses and normalized envelopes are written separately, uploaded with hash verification and committed through a collector manifest. Databricks notebook `09_ingest_landed_fmp.py` handles the landed capture.

## 5. Build and activate a data release

`07_refresh_features.py` builds feature families and publishes a candidate Gold binding. The local coordinator checks the declared predictor schema and the operator's required-feature coverage. This source-only edition does not load the private trained-model adapter; model validation is a downstream responsibility.

```bash
python scripts/deploy_operational_jobs.py --config config/operator.json
python scripts/run_local_pipeline.py --config config/operator.json --run-id YOUR_UNIQUE_RUN
# Deliberate data-source publication:
python scripts/run_local_pipeline.py --config config/operator.json --run-id YOUR_UNIQUE_RUN --activate
```

A same-ID restart verifies immutable files and recorded stages. New independent source observations require a new ID. A changed parent or failed validation prevents activation. The active registry is the authoritative pointer; local `config/data_source.json` is ignored operator state.

## 6. Scheduling and recovery

The optional Windows scripts assume the repository `.venv`, an authenticated user, and the Eastern Windows time zone. They register a weekday 19:30 local task with overlapping runs disabled. The machine must be on and signed in. Inspect the scripts and your operator configuration before installing the task.

Logs and per-run receipts remain local and ignored. No scheduled task or cloud job is installed by cloning or running unit tests. Restore only a previously validated release that is not quarantined, using the current expected-parent hash. Never delete raw evidence to undo a release.

## Data limitations

Historical vendor revisions are not original filing vintages. Retrospective sector/profile data is not certified historical GICS. Unknown terminal valuations remain NULL. Legacy auxiliary tables remain archives unless an explicit live source contract is implemented.
