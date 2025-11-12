-- Use SparkSQL transaction-like flow (atomic within the job)

-- Step 1: Deduplicate staging data
CREATE OR REPLACE TEMP VIEW deduped_staging AS
SELECT
  transaction_id,
  FIRST(customer_name) AS customer_name,
  FIRST(product_code) AS product_code,
  FIRST(quantity) AS quantity,
  FIRST(sale_amount) AS sale_amount,
  FIRST(sale_date) AS sale_date
FROM sales_staging
GROUP BY transaction_id;

-- Step 2: Transform and clean data
CREATE OR REPLACE TEMP VIEW transformed_sales AS
SELECT
  transaction_id,
  INITCAP(TRIM(customer_name)) AS customer_name,
  UPPER(TRIM(product_code)) AS product_code,
  CASE WHEN quantity = 0 THEN 1 ELSE quantity END AS quantity,
  sale_amount,
  TO_DATE(sale_date, 'MM/dd/yyyy') AS sale_date,
  CURRENT_TIMESTAMP() AS load_timestamp
FROM deduped_staging
WHERE TO_DATE(sale_date, 'MM/dd/yyyy') IS NOT NULL;

-- Step 3: Incremental load (merge pattern)
MERGE INTO sales_fact AS target
USING transformed_sales AS source
ON target.transaction_id = source.transaction_id
WHEN NOT MATCHED THEN
  INSERT (transaction_id, customer_name, product_code, quantity, sale_amount, sale_date, load_timestamp)
  VALUES (source.transaction_id, source.customer_name, source.product_code, source.quantity, source.sale_amount, source.sale_date, source.load_timestamp);

-- Step 4: Create ETL log table if not exists
CREATE TABLE IF NOT EXISTS etl_log (
  run_id STRING,
  run_timestamp TIMESTAMP,
  rows_inserted INT,
  status STRING,
  message STRING
)
USING PARQUET;

-- Step 5: Insert ETL summary
INSERT INTO etl_log
SELECT
  UUID() AS run_id,
  CURRENT_TIMESTAMP() AS run_timestamp,
  (SELECT COUNT(*) FROM transformed_sales) AS rows_inserted,
  'SUCCESS' AS status,
  'ETL completed successfully' AS message;
