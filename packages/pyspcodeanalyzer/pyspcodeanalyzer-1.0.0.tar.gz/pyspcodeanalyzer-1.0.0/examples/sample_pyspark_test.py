from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, trim, upper, initcap, when, to_date, current_timestamp,
    countDistinct, lit, count, uuid
)
from datetime import datetime

# ------------------------------------------------------------
# 1. Spark Session Setup
# ------------------------------------------------------------
spark = SparkSession.builder \
    .appName("MediumLevelPySparkETL") \
    .config("spark.sql.shuffle.partitions", 4) \
    .getOrCreate()

# ------------------------------------------------------------
# 2. Extract: Load source data from CSV
# ------------------------------------------------------------
input_path = "data/sales_staging.csv"
df_raw = spark.read.option("header", True).csv(input_path)

print(f"Extracted {df_raw.count()} rows from source.")

# ------------------------------------------------------------
# 3. Transform: Clean & standardize data
# ------------------------------------------------------------

df_clean = (
    df_raw
    .dropDuplicates(["transaction_id"])  # Deduplicate
    .withColumn("customer_name", initcap(trim(col("customer_name"))))
    .withColumn("product_code", upper(trim(col("product_code"))))
    .withColumn("quantity", when(col("quantity") == 0, 1).otherwise(col("quantity")))
    .withColumn("sale_date", to_date(col("sale_date"), "MM/dd/yyyy"))
    .filter(col("sale_date").isNotNull())  # drop invalid dates
    .withColumn("load_timestamp", current_timestamp())
)

print(f"Transformed {df_clean.count()} valid rows after cleaning.")

# ------------------------------------------------------------
# 4. Load: Write to Parquet fact table (incremental)
# ------------------------------------------------------------
target_path = "warehouse/sales_fact"

# Read existing target data (if exists)
try:
    df_existing = spark.read.parquet(target_path)
except Exception:
    df_existing = spark.createDataFrame([], df_clean.schema)

# Identify new records (incremental logic)
df_new = df_clean.join(df_existing, ["transaction_id"], "left_anti")

df_new.write.mode("append").parquet(target_path)

print(f"Loaded {df_new.count()} new rows into sales_fact.")

# ------------------------------------------------------------
# 5. Log ETL Run
# ------------------------------------------------------------
log_data = [
    (
        str(uuid().toString()),
        datetime.now(),
        df_new.count(),
        "SUCCESS",
        "ETL completed successfully."
    )
]

log_schema = "run_id string, run_timestamp timestamp, rows_inserted int, status string, message string"
df_log = spark.createDataFrame(log_data, schema=log_schema)

df_log.write.mode("append").parquet("warehouse/etl_log")

print("ETL run logged successfully.")

# ------------------------------------------------------------
# 6. Done
# ------------------------------------------------------------
spark.stop()
print("✅ ETL job completed successfully.")
