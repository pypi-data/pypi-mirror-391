BEGIN TRY
    BEGIN TRANSACTION;

    -- Step 1: Remove exact duplicates from staging
    ;WITH Deduped AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY TransactionID ORDER BY (SELECT NULL)) AS rn
        FROM dbo.Sales_Staging
    )
    DELETE FROM Deduped WHERE rn > 1;

    -- Step 2: Insert transformed and validated data into destination
    INSERT INTO dbo.Sales_Fact (TransactionID, CustomerName, ProductCode, Quantity, SaleAmount, SaleDate)
    SELECT 
        s.TransactionID,
        LTRIM(RTRIM(s.CustomerName)) AS CustomerName,  -- clean whitespace
        UPPER(s.ProductCode) AS ProductCode,            -- standardize case
        ISNULL(NULLIF(s.Quantity, 0), 1) AS Quantity,   -- replace 0 with 1
        s.SaleAmount,
        TRY_CONVERT(DATE, s.SaleDate, 101) AS SaleDate  -- safely convert text to date
    FROM dbo.Sales_Staging s
    WHERE TRY_CONVERT(DATE, s.SaleDate, 101) IS NOT NULL -- reject bad dates
      AND s.TransactionID NOT IN (
            SELECT TransactionID FROM dbo.Sales_Fact
        ); -- avoid duplicates in target

    -- Step 3: Log ETL summary
    DECLARE @Inserted INT = @@ROWCOUNT;
    PRINT CONCAT('ETL completed successfully. ', @Inserted, ' rows inserted.');

    -- Step 4: Optionally clear staging table
    TRUNCATE TABLE dbo.Sales_Staging;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;

    DECLARE 
        @ErrorMessage NVARCHAR(4000),
        @ErrorSeverity INT,
        @ErrorState INT;

    SELECT 
        @ErrorMessage = ERROR_MESSAGE(),
        @ErrorSeverity = ERROR_SEVERITY(),
        @ErrorState = ERROR_STATE();

    RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
END CATCH;
