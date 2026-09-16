# Databricks notebook source
# streaming/03_gold_vwap_aggregation.py

# COMMAND ----------

# MAGIC %md
# MAGIC # Gold Layer: Real-Time VWAP Calculation
# MAGIC **Objective:** Calculate the Volume-Weighted Average Price (VWAP) over 1-minute tumbling windows.

# COMMAND ----------

from pyspark.sql.functions import col, window, sum as _sum

STORAGE_ACCOUNT = "stmarketstreamdevq40qg"
SILVER_PATH = f"abfss://silver@{STORAGE_ACCOUNT}.dfs.core.windows.net/trades_cleaned"
GOLD_PATH = f"abfss://silver@{STORAGE_ACCOUNT}.dfs.core.windows.net/gold_vwap"
CHECKPOINT_PATH = f"abfss://checkpoints@{STORAGE_ACCOUNT}.dfs.core.windows.net/gold_vwap_v2"


# ADLS Authentication Block
STORAGE_KEY = dbutils.secrets.get(scope="market-scope", key="storage-acct-key")
spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    STORAGE_KEY
)

# COMMAND ----------

silver_stream_df = spark.readStream.format("delta").load(SILVER_PATH)

# Calculate VWAP: Sum(Price * Volume) / Sum(Volume)
# We aggregate over a tumbling window of 1 minute based on the event timestamp
vwap_df = (
    silver_stream_df
    .withWatermark("timestamp", "5 minutes") # Allow late data up to 5 minutes
    .groupBy(
        window(col("timestamp"), "1 minute"),
        col("symbol")
    )
    .agg(
        (_sum(col("price") * col("volume")) / _sum(col("volume"))).alias("vwap"),
        _sum(col("volume")).alias("total_volume")
    )
    .select("window.start", "window.end", "symbol", "vwap", "total_volume")
)

# Because we are doing aggregations, outputMode must be "update" or "complete"
gold_query = (
    vwap_df.writeStream
    .format("delta")
    .outputMode("complete")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .trigger(processingTime="1 minute")
    .start(GOLD_PATH)
)

# COMMAND ----------

from pyspark.sql.functions import col

# Read a static snapshot of the Gold table as it currently exists
display(
    spark.read.format("delta").load(GOLD_PATH)
    .orderBy(col("end").desc(), col("symbol"))
)