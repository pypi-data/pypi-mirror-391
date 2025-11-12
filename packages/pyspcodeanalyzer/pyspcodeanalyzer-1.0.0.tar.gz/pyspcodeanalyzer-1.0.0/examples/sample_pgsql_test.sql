DO
$$
DECLARE
    v_inserted INT;
BEGIN
    -- Start ETL transaction
    BEGIN;

    -- Step 1: Deduplicate staging (keep smallest transaction_id row)
    WITH deduped AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY transaction_id) AS rn
        FROM sales_staging
    )
    DELETE FROM sales_staging
    WHERE transaction_id IN (
        SELECT transaction_id FROM deduped WHERE rn > 1
    );

    -- Step 2: Insert clean, transformed data into fact table
    INSERT INTO sales_fact (transaction_id, customer_name, product_code, quantity, sale_amount, sale_date)
    SELECT 
        s.transaction_id,
        INITCAP(TRIM(s.customer_name)) AS customer_name, -- standardize name format
        UPPER(TRIM(s.product_code)) AS product_code,      -- normalize product code
        COALESCE(NULLIF(s.quantity, 0), 1) AS quantity,   -- replace 0 with 1
        s.sale_amount,
        TO_DATE(s.sale_date, 'MM/DD/YYYY') AS sale_date   -- safely cast text to date
    FROM sales_staging s
    WHERE TO_DATE(s.sale_date, 'MM/DD/YYYY') IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM sales_fact f WHERE f.transaction_id = s.transaction_id
      );

    GET DIAGNOSTICS v_inserted = ROW_COUNT;

    -- Step 3: Log ETL summary
    INSERT INTO etl_log (rows_inserted, status, message)
    VALUES (v_inserted, 'SUCCESS', CONCAT('ETL completed: ', v_inserted, ' rows inserted.'));

    -- Step 4: Clear staging data
    TRUNCATE TABLE sales_staging;

    COMMIT;

EXCEPTION WHEN OTHERS THEN
    -- Rollback and log error
    ROLLBACK;
    INSERT INTO etl_log (rows_inserted, status, message)
    VALUES (0, 'FAILED', CONCAT('Error: ', SQLERRM));
END;
$$;
