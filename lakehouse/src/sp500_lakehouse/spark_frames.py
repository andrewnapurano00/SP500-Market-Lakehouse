"""Bounded pandas -> Spark transport through governed Parquet staging.

Avoids Spark Connect's pandas-3 Arrow ChunkedArray conversion limitation and
keeps wide historical frames outside the serialized Connect query plan.
"""
import hashlib,uuid
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

def parquet_bytes(frame):
    table=pa.Table.from_pandas(frame,preserve_index=False).combine_chunks()
    for index,field in enumerate(table.schema):
        if pa.types.is_null(field.type):table=table.set_column(index,field.name,pa.nulls(len(table),type=pa.string()))
    buffer=pa.BufferOutputStream();pq.write_table(table,buffer,compression='zstd',coerce_timestamps='us',allow_truncated_timestamps=False)
    return buffer.getvalue().to_pybytes()

def pandas_to_spark(spark,cfg,frame):
    data=parquet_bytes(frame);digest=hashlib.sha256(data).hexdigest()
    folder=Path(cfg.volume('exports'))/'_materializations'/uuid.uuid4().hex
    folder.mkdir(parents=True,exist_ok=False)
    path=folder/(digest+'.parquet')
    with path.open('xb') as stream:stream.write(data)
    frame=spark.read.parquet(str(path))
    from pyspark.sql import functions as F
    for field in frame.schema.fields:
        if field.dataType.simpleString()=='void':frame=frame.withColumn(field.name,F.col(field.name).cast('string'))
    return frame
