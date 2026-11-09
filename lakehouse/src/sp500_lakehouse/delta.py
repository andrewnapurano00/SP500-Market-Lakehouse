"""Insert-only Delta runtime. Imports Spark only when executed on compute."""
import hashlib
import json
from .config import identifier


def spark_dtype(value):
    """Accept the explicit SQL type names emitted by live table contracts."""
    import re
    value=str(value).strip().lower()
    aliases={'bigint':'long','integer':'int','smallint':'short','float':'double','varchar':'string','text':'string'}
    value=aliases.get(value,value)
    if value in {'string','date','timestamp','double','long','int','short','boolean'}:
        return value
    decimal=re.fullmatch(r'decimal\((\d+),(\d+)\)',value)
    if decimal and 1<=int(decimal[1])<=38 and 0<=int(decimal[2])<=int(decimal[1]):
        return value
    raise ValueError('Unsupported explicit Spark type')


def event_identity(source, entity, source_record_key, payload_hash):
    """Stable across retries, different for any observed payload revision."""
    return hashlib.sha256(json.dumps([source, entity, source_record_key, payload_hash], separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def setup_unity_catalog(spark, config):
    for layer in ("files", "bronze", "silver", "gold", "ops"):
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {config.schema(layer)}")
    for volume in ("landing", "checkpoints", "exports"):
        spark.sql(f"CREATE VOLUME IF NOT EXISTS {config.schema('files')}.{volume}")


def _insert_only(spark, frame, table, keys, conflict_columns):
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    if frame.where(F.expr(" OR ".join(f"`{identifier(k)}` IS NULL" for k in keys))).limit(1).count():
        raise ValueError("Null revision/business key")
    if frame.groupBy(*keys).count().where("count > 1").limit(1).count():
        raise ValueError("Ambiguous duplicate source keys")
    if not spark.catalog.tableExists(table):
        frame.write.format("delta").mode("error").saveAsTable(table)
        return
    existing = spark.table(table)
    joined = frame.alias("s").join(existing.alias("t"), keys, "inner")
    difference = None
    for column in conflict_columns:
        unequal = ~F.col(f"s.`{identifier(column)}`").eqNullSafe(F.col(f"t.`{column}`"))
        difference = unequal if difference is None else difference | unequal
    if difference is not None and joined.where(difference).limit(1).count():
        raise ValueError("Existing immutable key conflicts with incoming content")
    # Exact duplicate retries are harmless; revisions are separate keys. No updates/deletes.
    condition = " AND ".join(f"t.`{identifier(k)}` = s.`{k}`" for k in keys)
    DeltaTable.forName(spark, table).alias("t").merge(frame.alias("s"), condition).whenNotMatchedInsertAll().execute()


def ingest_bronze(spark, config, landing_path, entity):
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    paths = landing_path if isinstance(landing_path, list) else [landing_path]
    if not paths: raise ValueError('Explicit nonempty landing paths required')
    for path in paths: config.require_landing_path(path)
    identifier(entity)
    raw = spark.read.text(paths).withColumn("source_file", F.col('_metadata.file_path'))
    fields = ("source", "entity", "dt", "run_id", "ingested_at", "retrieved_at", "request_parameters", "source_record_key", "payload_hash", "source_kind")
    frame = raw.select("source_file", F.col("value").alias("raw_envelope"), *[F.get_json_object("value", f"$.meta.{k}").alias(k) for k in fields], F.get_json_object("value", "$.data").alias("data"))
    required = ("source", "entity", "source_record_key", "payload_hash", "ingested_at", "retrieved_at", "run_id", "dt", "data")
    invalid = " OR ".join(f"`{k}` IS NULL" for k in required)
    if frame.where(F.expr(invalid) | (F.col("entity") != entity)).limit(1).count():
        raise ValueError("Malformed or mixed-entity landing batch")
    identity = F.to_json(F.array(*[F.col(k) for k in ("source", "entity", "source_record_key", "payload_hash")]))
    frame = frame.withColumn("event_id", F.sha2(identity, 256))
    # Canonical hash check detects corrupted payloads before retaining evidence.
    @F.udf("string")
    def payload_digest(value):
        return hashlib.sha256(json.dumps(json.loads(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()).hexdigest()
    if frame.where(payload_digest("data") != F.col("payload_hash")).limit(1).count():
        raise ValueError("Landing payload hash mismatch")
    frame = frame.withColumn("_rank", F.row_number().over(Window.partitionBy("event_id").orderBy("retrieved_at", "ingested_at", "source_file"))).where("_rank = 1").drop("_rank")
    _insert_only(spark, frame, config.table("bronze", entity), ["event_id"], ["data"])
    spark.sql(f"ALTER TABLE {config.table('bronze', entity)} SET TBLPROPERTIES ('delta.appendOnly' = 'true')")


def normalize_silver(spark, config, entity, fields, business_keys):
    """fields = {payload field: Spark SQL type}; retain all payload-hash revisions.

    Missing/failed non-null casts fail the batch rather than silently producing null.
    Does not assert reconstructed vendor data was known historically.
    """
    from pyspark.sql import functions as F
    if not fields or not business_keys or not set(business_keys) <= set(fields):
        raise ValueError("Explicit fields and business keys required")
    for key, dtype in fields.items():
        identifier(key)
        if key.startswith("_landing_"):
            raise ValueError("Payload field collides with reserved lineage metadata")
        spark_dtype(dtype)
    source = spark.table(config.table("bronze", entity))
    expressions=[]
    invalid=None
    for key, dtype in fields.items():
        raw = F.get_json_object("data", f"$.{key}")
        typed=raw.cast(spark_dtype(dtype))
        expressions.append(typed.alias(key))
        failed=raw.isNotNull() & typed.isNull()
        invalid=failed if invalid is None else invalid | failed
    # One validation action even for the wide financial feature table. Metadata
    # is projected directly, so payload fields cannot overwrite capture clocks.
    if source.where(invalid).limit(1).count():
        raise ValueError('Type conversion failed in explicit Silver projection')
    frame=source.select(*expressions,F.col('payload_hash').alias('_landing_payload_revision'),
        F.col('event_id').alias('_landing_event_id'),
        *[F.col(k).alias('_landing_'+k) for k in ('source','source_kind','retrieved_at','ingested_at','run_id')])
    frame = frame.withColumn("_landing_availability_quality", F.lit("revision_uncertain"))
    keys = [*business_keys, "_landing_payload_revision", "_landing_source"]
    # Do not silently choose one conflicting row: key ambiguity fails _insert_only.
    frame = frame.dropDuplicates()
    _insert_only(spark, frame, config.table("silver", entity), keys, list(fields))


def validate_snapshot_contract(columns, manifest):
    import re
    from .transforms import is_outcome_column
    if not {"security_id", "signal_month"} <= set(columns):
        raise ValueError("Gold cohort requires security_id/signal_month")
    if any(is_outcome_column(c) for c in columns):
        raise ValueError("Outcomes are prohibited in feature snapshots")
    if not all(manifest.get(k) for k in ("feature_version", "as_of", "run_id", "source_hashes")):
        raise ValueError("Manifest requires feature_version/as_of/run_id/source_hashes")
    if not isinstance(manifest["source_hashes"], dict) or not all(re.fullmatch(r"[0-9a-f]{64}", str(v)) for v in manifest["source_hashes"].values()):
        raise ValueError("Source hashes must be SHA256")
    from datetime import datetime
    as_of = datetime.fromisoformat(str(manifest["as_of"]).replace("Z", "+00:00"))
    if as_of.tzinfo is None:
        raise ValueError("Manifest as_of requires explicit timezone")
    return hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def validate_signal_months(months, as_of):
    """Publication itself enforces completed NYSE months after projections."""
    import re
    import pandas as pd
    import pandas_market_calendars as mcal
    cutoff=pd.Timestamp(as_of)
    if pd.isna(cutoff) or cutoff.tzinfo is None or not months:
        raise ValueError('Nonempty monthly signals and aware as_of required')
    calendar=mcal.get_calendar('NYSE')
    for month in months:
        if not isinstance(month,str) or not re.fullmatch(r'\d{4}-\d{2}',month):
            raise ValueError('Canonical YYYY-MM signal month required')
        period=pd.Period(month,freq='M')
        closes=calendar.schedule(start_date=period.start_time,end_date=period.end_time)
        if closes.empty or closes.market_close.iloc[-1]>cutoff:
            raise ValueError('Gold signal month has not closed by as_of')


def publish_gold_snapshot(spark, config, frame, snapshot_id, manifest):
    """Unique table per snapshot; retry never overwrites a frozen publication."""
    identifier(snapshot_id)
    digest = validate_snapshot_contract(frame.columns, manifest)
    table = config.table("gold", "snapshot_" + snapshot_id)
    from pyspark.sql import functions as F
    months=frame.select('signal_month').distinct().limit(2401).collect()
    if len(months)>2400:
        raise ValueError('Monthly publication exceeds 200-year safety bound')
    validate_signal_months([row.signal_month for row in months],manifest['as_of'])
    if 'signal_at' in frame.columns and frame.where(F.col('signal_at') > F.to_timestamp(F.lit(manifest['as_of']))).limit(1).count():
        raise ValueError('Signal close exceeds manifest as_of')
    if frame.where("security_id IS NULL OR signal_month IS NULL").limit(1).count() or frame.groupBy("security_id", "signal_month").count().where("count > 1").limit(1).count():
        raise ValueError("Null/duplicate Gold cohort keys")
    frame = frame.withColumn("data_snapshot_id", F.lit(snapshot_id)).withColumn("feature_version", F.lit(manifest["feature_version"])).withColumn("run_id", F.lit(manifest["run_id"]))
    if spark.catalog.tableExists(table):
        props = {row.key: row.value for row in spark.sql(f"SHOW TBLPROPERTIES {table}").collect()}
        existing = spark.table(table)
        if props.get("sp500.manifest_sha256") != digest or set(existing.columns) != set(frame.columns):
            raise FileExistsError("Snapshot identity/manifest conflict")
        if existing.select(*frame.columns).exceptAll(frame).limit(1).count() or frame.exceptAll(existing.select(*frame.columns)).limit(1).count():
            raise FileExistsError("Snapshot content conflicts with existing publication")
        return table
    manifest_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    # V2 create atomically commits data and immutable provenance properties.
    frame.writeTo(table).using('delta').tableProperty('delta.appendOnly','true').tableProperty(
        'sp500.snapshot_manifest',manifest_json).tableProperty('sp500.manifest_sha256',digest).create()
    # Publication is a dataset candidate, never an automatic consumer switch.
    return table
