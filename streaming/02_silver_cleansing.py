# streaming/02_silver_cleansing.py
# Databricks notebook source

# COMMAND ----------
# MAGIC %md
# MAGIC # Silver Layer: Cleansing & Deduplication
# MAGIC **Objective:** Parse JSON, enforce schema, drop duplicates, and filter malformed records.

# COMMAND ----------
from pyspark.sql.functions import col, from_json, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType

# Define ADLS Gen2 Paths
STORAGE_ACCOUNT = "stmarketstreamdevxxxxx"
BRONZE_PATH = f"abfss://bronze@{STORAGE_ACCOUNT}.dfs.core.windows.net/trades"
SILVER_PATH = f"abfss://silver@{STORAGE_ACCOUNT}.dfs.core.windows.net/trades_cleaned"
CHECKPOINT_PATH = f"abfss://checkpoints@{STORAGE_ACCOUNT}.dfs.core.windows.net/silver_trades"

# Define the expected JSON schema
trade_schema = StructType([
    StructField("trade_id", StringType(), False),
    StructField("symbol", StringType(), False),
    StructField("price", DoubleType(), True),
    StructField("volume", IntegerType(), True),
    StructField("timestamp", TimestampType(), False),
    StructField("trade_type", StringType(), True)
])

# COMMAND ----------
# MAGIC %md
# MAGIC ### 1. Read Bronze Stream

# COMMAND ----------
bronze_stream_df = spark.readStream.format("delta").load(BRONZE_PATH)

# COMMAND ----------
# MAGIC %md
# MAGIC ### 2. Parse and Clean Data

# COMMAND ----------
# The data in Bronze is a binary column named "value". 
# We cast it to string, then parse it using our schema.
parsed_df = (
    bronze_stream_df
    .selectExpr("CAST(value AS STRING) as json_payload", "timestamp as ingestion_timestamp")
    .select(from_json(col("json_payload"), trade_schema).alias("data"), "ingestion_timestamp")
    .select("data.*", "ingestion_timestamp")
)

# Filter out the malformed records we injected (missing volume or bad price)
# In a real system, we would route these to a Dead Letter Queue (DLQ) table
cleansed_df = parsed_df.filter(col("price").isNotNull() & col("volume").isNotNull())

# Drop duplicates using the unique trade_id
# We must use watermarking to prevent the state store from growing infinitely
deduped_df = (
    cleansed_df
    .withWatermark("timestamp", "10 minutes")
    .dropDuplicates(["trade_id"])
)

# COMMAND ----------
# MAGIC %md
# MAGIC ### 3. Write to Silver

# COMMAND ----------
silver_query = (
    deduped_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .trigger(processingTime="10 seconds")
    .start(SILVER_PATH)
)
