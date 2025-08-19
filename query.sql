-- Create report store procedure 
IF OBJECT_ID('dbo.sp_Load_Daily_Report', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_Load_Daily_Report;
GO

CREATE PROCEDURE dbo.sp_Load_Daily_Report
    @StartDate DATE,
    @EndDate   DATE
AS
BEGIN
    DELETE d
    FROM dbo.DESTINATION_daily_report_template d

    INSERT INTO dbo.DESTINATION_daily_report_template
        (Date, [Platform], [Advertiser], [Campaign], [Ad Group], [Creative], [Impressions], [Clicks])
    SELECT
        date AS [Date],
        platform AS [Platform],
        advertiser_account AS [Advertiser],
        campaign AS [Campaign],
        ad_group AS [Ad Group],
        creative AS [Creative],
        impressions AS [Impressions],
        clicks AS [Clicks]
    FROM dbo.stg_ads_clean
    WHERE date BETWEEN @StartDate AND @EndDate;
END;
GO

IF OBJECT_ID('dbo.sp_Load_Device_Report', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_Load_Device_Report;
GO

CREATE PROCEDURE dbo.sp_Load_Device_Report
    @MonthYear CHAR(7)
AS
BEGIN
    DELETE d
    FROM dbo.DESTINATION_device_report_template d

    INSERT INTO dbo.DESTINATION_device_report_template
        ([MonthYear], [Platform], [Campaign], [Device], [Impressions], [Clicks])
    SELECT
        FORMAT(date, 'yyyy/MM') AS [MonthYear],
        platform AS [Platform],
        campaign AS [Campaign],
        device_standardize AS [Device],
        SUM(impressions) AS [Impressions],
        SUM(clicks) AS [Clicks]
    FROM dbo.stg_ads_clean
    WHERE FORMAT(date, 'yyyy/MM') = @MonthYear
    GROUP BY FORMAT(date, 'yyyy/MM'), platform, campaign, device_standardize;
END;
GO

-- Execute procedure
EXEC dbo.sp_Load_Device_Report @MonthYear = '2025/06';
GO
SELECT * FROM DESTINATION_device_report_template
GO

EXEC dbo.sp_Load_Daily_Report @StartDate = '2025-06-01', @EndDate = '2025-06-30';
GO
SELECT * FROM DESTINATION_daily_report_template
GO