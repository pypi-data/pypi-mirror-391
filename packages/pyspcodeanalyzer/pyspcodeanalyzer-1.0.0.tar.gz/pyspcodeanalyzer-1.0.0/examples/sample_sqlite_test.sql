BEGIN TRANSACTION;

-- Step 1: Deduplicate staging data
DROP TABLE IF EXISTS tmp_deduped;
CREATE TEMP TABLE tmp_deduped AS
SELECT
    transaction_id,
    MAX(rowid) AS latest_row
FROM stg_sales
GROUP BY transaction_id;

-- Step 2: Transform and clean data
DROP TABLE IF EXISTS tmp_transformed;
CREATE TEMP TABLE tmp_transformed AS
SELECT
    s.transaction_id,
    TRIM(UPPER(s.customer_name)) AS customer_name,
    UPPER(TRIM(s.product_code)) AS product_code,
    CASE WHEN s.quantity IS NULL OR s.quantity = 0 THEN 1 ELSE s.quantity END AS quantity,
    s.sale_amount,
    DATE(s.sale_date) AS sale_date,
    CURRENT_TIMESTAMP AS load_timestamp
FROM stg_sales s
JOIN tmp_deduped d
  ON s.rowid = d.latest_row
WHERE DATE(s.sale_date) IS NOT NULL;

-- Step 3: Incremental load (insert only new records)
INSERT INTO sales_fact (transaction_id, customer_name, product_code, quantity, sale_amount, sale_date, load_timestamp)
SELECT
    t.transaction_id,
    t.customer_name,
    t.product_code,
    t.quantity,
    t.sale_amount,
    t.sale_date,
    t.load_timestamp
FROM tmp_transformed t
LEFT JOIN sales_fact f
  ON t.transaction_id = f.transaction_id
WHERE f.transaction_id IS NULL;

-- Step 4: Log ETL summary
INSERT INTO etl_log (run_id, run_timestamp, rows_inserted, status, message)
SELECT
    hex(randomblob(16)) AS run_id,
    CURRENT_TIMESTAMP AS run_timestamp,
    (SELECT COUNT(*) FROM tmp_transformed) AS rows_inserted,
    'SUCCESS' AS status,
    'ETL completed successfully' AS message;

-- Step 5: Clean up staging
DELETE FROM stg_sales;

COMMIT;
