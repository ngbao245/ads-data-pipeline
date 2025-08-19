-- Create Database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'ads')
BEGIN
  CREATE DATABASE ads;
END;
GO

USE ads
GO

-- Create raw tables
CREATE TABLE raw_ggads (
	[Day] DATE
	,[Account Name] NVARCHAR(100)
	,[Campaign] NVARCHAR(100)
	,[Ad group] NVARCHAR(100)
	,[Auto-applied ad suggestion] NVARCHAR(50)
	,[Ad name] NVARCHAR(100)
	,[Ad type] NVARCHAR(100)
	,[Device] NVARCHAR(100)
	,[Impr.] INT
	,[Clicks] INT 
);
GO

CREATE TABLE raw_dv360 (
	[Date] DATE
	,[Advertiser] NVARCHAR(100)
	,[Campaign] NVARCHAR(100)
	,[Insertion Order] NVARCHAR(100)
	,[Line Item] NVARCHAR(100)
	,[Creative] NVARCHAR(100)
	,[Device Type] NVARCHAR(100)
	,[Impressions] INT
	,[Clicks] INT
);
GO

CREATE TABLE raw_one (
	[Date] DATE
	,[Advertiser] NVARCHAR(100)
	,[Campaign] NVARCHAR(100)
	,[Flight] NVARCHAR(100)
	,[Creative] NVARCHAR(100)
	,[Device] NVARCHAR(100)
	,[Impression] INT
	,[Click] INT 
);
GO

CREATE TABLE dbo.stg_ads_clean (
    date DATE NOT NULL,
    platform NVARCHAR(50) NOT NULL,
    advertiser_account NVARCHAR(100) NULL,
    campaign NVARCHAR(100) NULL,
    ad_group NVARCHAR(100) NULL,
    insertion_order NVARCHAR(100) NULL,
    line_item NVARCHAR(100) NULL,
    flight NVARCHAR(100) NULL,
    creative NVARCHAR(100) NULL,
    device_standardize NVARCHAR(100) NOT NULL,
    impressions INT NOT NULL,
    clicks INT NOT NULL
);
GO

-- Create report tables
CREATE TABLE dbo.DESTINATION_daily_report_template (
  [Date] date NOT NULL,
  [Platform] NVARCHAR(50) NOT NULL,
  [Advertiser] NVARCHAR(100) NULL,
  [Campaign] NVARCHAR(100) NULL,
  [Ad Group] NVARCHAR(100) NULL,
  [Creative] NVARCHAR(100) NULL,
  [Impressions] INT NOT NULL,
  [Clicks] INT NOT NULL
);
GO

IF OBJECT_ID('dbo.DESTINATION_device_report_template','U') IS NULL
CREATE TABLE dbo.DESTINATION_device_report_template (
  [MonthYear] CHAR(7) NOT NULL,
  [Platform] NVARCHAR(50) NOT NULL,
  [Campaign] NVARCHAR(100) NULL,
  [Device] NVARCHAR(100) NOT NULL,
  [Impressions] INT NOT NULL,
  [Clicks] INT NOT NULL
);
GO