BEGIN ATOMIC

    DECLARE v_run_id VARCHAR(36);
    DECLARE v_rowcount INT DEFAULT 0;

    -- Generate run ID (UUID)
    SET v_run_id = SYSIBM.GUID();

    -- Step 1: Deduplicate data (keep latest record per TRANSACTION_ID)
    CREATE TEMP TABLE TMP_DEDUPED AS
    (
        SELECT TRANSACTION_ID,
               MAX(SALE_DATE) AS SALE_DATE
        FROM RAW.STG_SALES
        GROUP BY TRANSACTION_ID
    ) WITH DATA;

    -- Step 2: Transform and clean data
    CREATE TEMP TABLE TMP_TRANSFORMED AS
    (
        SELECT
            S.TRANSACTION_ID,
            INITCAP(TRIM(S.CUSTOMER_NAME)) AS CUSTOMER_NAME,
            UPPER(TRIM(S.PRODUCT_CODE)) AS PRODUCT_CODE,
            CASE WHEN S.QUANTITY IS NULL OR S.QUANTITY = 0 THEN 1 ELSE S.QUANTITY END AS QUANTITY,
            S.SALE_AMOUNT,
            CASE
                WHEN LENGTH(TRIM(S.SALE_DATE)) = 10 THEN DATE(TO_DATE(S.SALE_DATE, 'MM/DD/YYYY'))
                ELSE NULL
            END AS SALE_DATE
        FROM RAW.STG_SALES S
        JOIN TMP_DEDUPED D
          ON S.TRANSACTION_ID = D.TRANSACTION_ID
    ) WITH DATA;

    -- Step 3: Incremental load (insert new transactions)
    INSERT INTO ANALYTICS.SALES_FACT (TRANSACTION_ID, CUSTOMER_NAME, PRODUCT_CODE, QUANTITY, SALE_AMOUNT, SALE_DATE)
    SELECT
        T.TRANSACTION_ID,
        T.CUSTOMER_NAME,
        T.PRODUCT_CODE,
        T.QUANTITY,
        T.SALE_AMOUNT,
        T.SALE_DATE
    FROM TMP_TRANSFORMED T
    WHERE NOT EXISTS (
        SELECT 1
        FROM ANALYTICS.SALES_FACT F
        WHERE F.TRANSACTION_ID = T.TRANSACTION_ID
    );

    -- Capture inserted row count
    GET DIAGNOSTICS v_rowcount = ROW_COUNT;

    -- Step 4: Log ETL activity
    INSERT INTO ANALYTICS.ETL_LOG (RUN_ID, RUN_TIMESTAMP, ROWS_INSERTED, STATUS, MESSAGE)
    VALUES (
        v_run_id,
        CURRENT_TIMESTAMP,
        v_rowcount,
        'SUCCESS',
        'ETL completed successfully'
    );

    -- Step 5: Cleanup staging table
    TRUNCATE TABLE RAW.STG_SALES IMMEDIATE;

END;
