-- Use transaction for consistency
START TRANSACTION;

-- Step 1: Remove duplicates in staging (keep first occurrence)
DELETE s1 FROM sales_staging s1
JOIN sales_staging s2
  ON s1.transaction_id = s2.transaction_id
 AND s1.rowid > s2.rowid;

-- Step 2: Insert transformed and cleaned data
INSERT INTO sales_fact (transaction_id, customer_name, product_code, quantity, sale_amount, sale_date)
SELECT 
    s.transaction_id,
    TRIM(s.customer_name) AS customer_name,
    UPPER(s.product_code) AS product_code,
    IFNULL(NULLIF(s.quantity, 0), 1) AS quantity,
    s.sale_amount,
    STR_TO_DATE(s.sale_date, '%m/%d/%Y') AS sale_date
FROM sales_staging s
WHERE STR_TO_DATE(s.sale_date, '%m/%d/%Y') IS NOT NULL
  AND s.transaction_id NOT IN (
        SELECT transaction_id FROM sales_fact
    );

-- Step 3: Record summary in log table (optional)
CREATE TABLE IF NOT EXISTS etl_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    run_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    rows_inserted INT,
    status VARCHAR(20),
    message TEXT
);

INSERT INTO etl_log (rows_inserted, status, message)
SELECT ROW_COUNT(), 'SUCCESS', CONCAT('ETL completed successfully: ', ROW_COUNT(), ' rows inserted.');

-- Step 4: Clear staging table
TRUNCATE TABLE sales_staging;

COMMIT;
