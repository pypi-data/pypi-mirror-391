DECLARE
    v_start_time   TIMESTAMP := SYSTIMESTAMP;
    v_rows_loaded  NUMBER := 0;
BEGIN
    DBMS_OUTPUT.PUT_LINE('===== ETL PROCESS STARTED AT ' || TO_CHAR(v_start_time, 'YYYY-MM-DD HH24:MI:SS') || ' =====');

    -- Step 1: Clean up or truncate target (optional)
    EXECUTE IMMEDIATE 'TRUNCATE TABLE sales_summary';

    -- Step 2: Insert aggregated and transformed data
    INSERT INTO sales_summary (customer_id, category, total_sales, total_orders, etl_run_date)
    SELECT
        s.customer_id,
        p.category,
        SUM(s.quantity * s.unit_price) AS total_sales,
        COUNT(DISTINCT s.sale_id) AS total_orders,
        SYSDATE AS etl_run_date
    FROM
        stg_sales s
        LEFT JOIN dim_product p ON s.product_id = p.product_id
    WHERE
        s.quantity IS NOT NULL
        AND s.unit_price IS NOT NULL
        AND s.sale_date IS NOT NULL
    GROUP BY
        s.customer_id, p.category
    HAVING
        SUM(s.quantity * s.unit_price) >= 100;

    v_rows_loaded := SQL%ROWCOUNT;
    DBMS_OUTPUT.PUT_LINE('Rows inserted into SALES_SUMMARY: ' || v_rows_loaded);

    -- Step 3: Add audit log entry (optional)
    INSERT INTO etl_audit_log (process_name, start_time, end_time, rows_loaded, status)
    VALUES ('SALES_ETL', v_start_time, SYSTIMESTAMP, v_rows_loaded, 'SUCCESS');

    COMMIT;

    DBMS_OUTPUT.PUT_LINE('===== ETL PROCESS COMPLETED SUCCESSFULLY =====');

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('ETL FAILED: ' || SQLERRM);

        -- Optional error logging
        INSERT INTO etl_audit_log (process_name, start_time, end_time, rows_loaded, status, error_message)
        VALUES ('SALES_ETL', v_start_time, SYSTIMESTAMP, v_rows_loaded, 'FAILED', SQLERRM);

        ROLLBACK;
END;
/
