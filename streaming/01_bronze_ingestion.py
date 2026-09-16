# Databricks notebook source
# streaming/01_bronze_ingestion.py

# COMMAND ----------

# MAGIC %md
# MAGIC # Bronze Layer: Raw Event Hubs Ingestion
# MAGIC **Objective:** Stream raw Kafka/Event Hubs bytes into a Delta table on ADLS Gen2.

# COMMAND ----------

import urllib

# 1. Event Hubs Configuration
EVENTHUB_CONNECTION_STRING = dbutils.secrets.get(scope="market-scope", key="eh-conn-string")
EVENTHUB_TOPIC = "market-trades"
EVENTHUB_NAMESPACE = "eh-marketstream-dev-q40qg.servicebus.windows.net"

# Added "kafkashaded." back to THIS LINE:
EH_SASL = f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{EVENTHUB_CONNECTION_STRING}";'

# 2. Storage Account Configuration
STORAGE_ACCOUNT = "stmarketstreamdevq40qg"
BRONZE_PATH = f"abfss://bronze@{STORAGE_ACCOUNT}.dfs.core.windows.net/trades"
CHECKPOINT_PATH = f"abfss://checkpoints@{STORAGE_ACCOUNT}.dfs.core.windows.net/bronze_trades"

# 3. ADLS Authentication Block
STORAGE_KEY = dbutils.secrets.get(scope="market-scope", key="storage-acct-key")
spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    STORAGE_KEY
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. Read the Stream

# COMMAND ----------

# Configure the Kafka source
raw_stream_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", f"{EVENTHUB_NAMESPACE}:9093")
    .option("subscribe", EVENTHUB_TOPIC)
    .option("kafka.sasl.mechanism", "PLAIN")
    .option("kafka.security.protocol", "SASL_SSL")
    .option("kafka.sasl.jaas.config", EH_SASL)
    .option("kafka.request.timeout.ms", "60000")
    .option("kafka.session.timeout.ms", "30000")
    .option("startingOffsets", "earliest") # Start from the beginning
    .load()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Write to Bronze (Append Only)

# COMMAND ----------

# Write the raw bytes, headers, and metadata to a Delta table
bronze_query = (
    raw_stream_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .trigger(processingTime="10 seconds") # Micro-batch every 10s
    .start(BRONZE_PATH)
)