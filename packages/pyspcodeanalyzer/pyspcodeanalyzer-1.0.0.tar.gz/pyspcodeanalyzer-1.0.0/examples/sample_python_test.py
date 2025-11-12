import pandas as pd
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
import sys
import os

# ------------------------------------------------------------
# 1. Configuration and Setup
# ------------------------------------------------------------
LOG_FILE = "etl_log.txt"
DATA_FILE = "sales_data.csv"

# Example: PostgreSQL connection URL
DB_URL = "postgresql+psycopg2://username:password@localhost:5432/etl_demo"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create database connection
try:
    engine = create_engine(DB_URL)
    conn = engine.connect()
    logging.info("Database connection established.")
except Exception as e:
    logging.error(f"Database connection failed: {e}")
    sys.exit(1)

# ------------------------------------------------------------
# 2. Extract: Read source data
# ------------------------------------------------------------
try:
    df = pd.read_csv(DATA_FILE)
    logging.info(f"Data extracted from {DATA_FILE} — {len(df)} rows.")
except Exception as e:
    logging.error(f"Data extraction failed: {e}")
    sys.exit(1)

# ------------------------------------------------------------
# 3. Transform: Clean & validate data
# ------------------------------------------------------------
try:
    df.columns = [c.strip().lower() for c in df.columns]

    # Drop duplicates
    df = df.drop_duplicates(subset=["transaction_id"])

    # Trim and normalize text
    df["customer_name"] = df["customer_name"].str.strip().str.title()
    df["product_code"] = df["product_code"].str.strip().str.upper()

    # Replace 0 quantity with 1
    df["quantity"] = df["quantity"].replace(0, 1)

    # Convert sale_date safely
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")

    # Drop rows with invalid dates
    before = len(df)
    df = df.dropna(subset=["sale_date"])
    after = len(df)
    logging.info(f"Removed {before - after} rows with invalid dates.")

except Exception as e:
    logging.error(f"Data transformation failed: {e}")
    sys.exit(1)

# ------------------------------------------------------------
# 4. Load: Insert into target database
# ------------------------------------------------------------
try:
    table_name = "sales_fact"

    # Option 1: Use pandas to_sql (simple + fast for medium data)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)

    logging.info(f"{len(df)} rows successfully loaded into {table_name}.")

except Exception as e:
    logging.error(f"Data load failed: {e}")
    sys.exit(1)

# ------------------------------------------------------------
# 5. ETL Run Logging
# ------------------------------------------------------------
try:
    run_summary = {
        "run_time": datetime.now(),
        "rows_inserted": len(df),
        "status": "SUCCESS"
    }

    with engine.begin() as conn:
        conn.execute(
            text("""
            CREATE TABLE IF NOT EXISTS etl_run_log (
                id SERIAL PRIMARY KEY,
                run_time TIMESTAMP,
                rows_inserted INT,
                status TEXT
            );
            """)
        )
        conn.execute(
            text("""
            INSERT INTO etl_run_log (run_time, rows_inserted, status)
            VALUES (:run_time, :rows_inserted, :status)
            """), run_summary
        )
    logging.info("ETL run logged successfully.")

except Exception as e:
    logging.error(f"ETL logging failed: {e}")

finally:
    conn.close()
    logging.info("Database connection closed.")
