BEGIN TRANSACTION;

-- Step 1: Deduplicate staging data
CREATE TEMP TABLE tmp_deduped AS
SELECT
    transaction_id,
    MAX(sale_date) AS sale_date
FROM staging.sales_staging
GROUP BY transaction_id;

-- Step 2: Transform and clean data
CREATE TEMP TABLE tmp_transformed AS
SELECT
    s.transaction_id,
    INITCAP(TRIM(s.customer_name)) AS customer_name,
    UPPER(TRIM(s.product_code)) AS product_code,
    CASE WHEN s.quantity IS NULL OR s.quantity = 0 THEN 1 ELSE s.quantity END AS quantity,
    s.sale_amount,
    TRY_CAST(s.sale_date AS DATE) AS sale_date,
    GETDATE() AS load_timestamp
FROM staging.sales_staging s
JOIN tmp_deduped d
  ON s.transaction_id = d.transaction_id
WHERE TRY_CAST(s.sale_date AS DATE) IS NOT NULL;

-- Step 3: Incremental load (insert new transactions only)
INSERT INTO analytics.sales_fact (
    transaction_id, customer_name, product_code, quantity, sale_amount, sale_date, load_timestamp
)
SELECT
    t.transaction_id, t.customer_name, t.product_code, t.quantity, t.sale_amount, t.sale_date, t.load_timestamp
FROM tmp_transformed t
LEFT JOIN analytics.sales_fact f
  ON t.transaction_id = f.transaction_id
WHERE f.transaction_id IS NULL;

-- Step 4: Log ETL run summary
INSERT INTO analytics.etl_log (run_id, run_timestamp, rows_inserted, status, message)
SELECT
    MD5(RANDOM()::TEXT) AS run_id,
    GETDATE() AS run_timestamp,
    (SELECT COUNT(*) FROM tmp_transformed) AS rows_inserted,
    'SUCCESS' AS status,
    'ETL completed successfully' AS message;

-- Step 5: Cleanup staging data
TRUNCATE TABLE staging.sales_staging;

END TRANSACTION;
