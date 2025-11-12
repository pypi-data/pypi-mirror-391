-- Use a transaction for consistency (BigQuery supports multi-statement transactions)
BEGIN TRANSACTION;

-- Step 1: Deduplicate staging data
CREATE OR REPLACE TEMP TABLE deduped_staging AS
SELECT
  transaction_id,
  ANY_VALUE(customer_name) AS customer_name,
  ANY_VALUE(product_code) AS product_code,
  ANY_VALUE(quantity) AS quantity,
  ANY_VALUE(sale_amount) AS sale_amount,
  ANY_VALUE(sale_date) AS sale_date
FROM raw.sales_staging
GROUP BY transaction_id;

-- Step 2: Transform and clean data
CREATE OR REPLACE TEMP TABLE transformed_staging AS
SELECT
  transaction_id,
  INITCAP(TRIM(customer_name)) AS customer_name,    -- standardize name
  UPPER(TRIM(product_code)) AS product_code,        -- uppercase product codes
  IFNULL(NULLIF(quantity, 0), 1) AS quantity,       -- replace 0 with 1
  sale_amount,
  SAFE.PARSE_DATE('%m/%d/%Y', sale_date) AS sale_date -- safely convert date
FROM deduped_staging
WHERE SAFE.PARSE_DATE('%m/%d/%Y', sale_date) IS NOT NULL;

-- Step 3: Load clean data incrementally into target table
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.sales_fact (
  transaction_id INT64,
  customer_name STRING,
  product_code STRING,
  quantity INT64,
  sale_amount NUMERIC,
  sale_date DATE,
  load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

MERGE INTO analytics.sales_fact AS tgt
USING transformed_staging AS src
ON tgt.transaction_id = src.transaction_id
WHEN NOT MATCHED THEN
  INSERT (transaction_id, customer_name, product_code, quantity, sale_amount, sale_date)
  VALUES (src.transaction_id, src.customer_name, src.product_code, src.quantity, src.sale_amount, src.sale_date);

-- Step 4: Log ETL summary
CREATE TABLE IF NOT EXISTS analytics.etl_log (
  run_id STRING,
  run_timestamp TIMESTAMP,
  rows_inserted INT64,
  status STRING,
  message STRING
);

INSERT INTO analytics.etl_log (run_id, run_timestamp, rows_inserted, status, message)
SELECT
  GENERATE_UUID(),
  CURRENT_TIMESTAMP(),
  (SELECT COUNT(*) FROM transformed_staging) AS rows_inserted,
  'SUCCESS',
  'ETL completed successfully.';

-- Step 5: Clean up raw table (optional)
TRUNCATE TABLE raw.sales_staging;

COMMIT TRANSACTION;
