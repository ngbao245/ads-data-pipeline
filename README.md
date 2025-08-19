## 1/ Installation & Run

### Requirements
- Python 3.9+
- SQL Server (using ODBC Driver 17)
- File:
  - `pipeline_mssql.py`
  - `Data Engineer - Round 2 Task.xlsx`
  - `init_ads.sql` (script to create database, table, store procedure to query)

1. **Create virtual environment**
```bash
# Open Command Prompt at the project folder location
python -m venv .venv
```

2. **Activate Virtual Environment**
```bash
.venv\Scripts\Activate
```

3. **Install usage libraries**
```bash
pip install pandas numpy sqlalchemy pyodbc openpyxl
```

4. **Run SQL Script**
5. **Install usage libraries**
```bash
python pipeline_mssql.py
```

6. **Execute report**
- DESTINATION_device_report_template
```sql
EXEC dbo.sp_Load_Device_Report @MonthYear = '2025/06';
GO
SELECT * FROM DESTINATION_device_report_template
GO
```
- DESTINATION_daily_report_template
```sql
EXEC dbo.sp_Load_Daily_Report @StartDate = '2025-06-01', @EndDate = '2025-06-30';
GO
SELECT * FROM DESTINATION_device_report_template
GO
```

## 2/ Mapping between raw data and tables's columns
### First Step:
- Pull data Excel sheet to raw data table (No transformation)

### Second Step:
- Data is cleaned and standardized before loading into staging

| Column Name          | Raw Source                                                            | Transformation                                                       |
| -------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `date`               | GGAds: `Day` <br> DV360: `Date` <br> ONE: `Date`                      | Convert → `YYYY-MM-DD`                                               |
| `platform`           | Fixed per sheet                                                       | `GGADS`, `DV360`, `ONE`                                              |
| `advertiser_account` | GGAds: `Account name` <br> DV360: `Advertiser` <br> ONE: `Advertiser` | Trim whitespace, allow NULL                                          |
| `campaign`           | GGAds: `Campaign` <br> DV360: `Campaign` <br> ONE: `Campaign`         | Trim whitespace                                                      |
| `ad_group`           | GGAds: `Ad group` <br> DV360: NULL <br> ONE: NULL                     | Only GGAds                                                           |
| `insertion_order`    | GGAds: NULL <br> DV360: `Insertion Order` <br> ONE: NULL              | Only DV360                                                           |
| `line_item`          | GGAds: NULL <br> DV360: `Line Item` <br> ONE: NULL                    | Only DV360                                                           |
| `flight`             | GGAds: NULL <br> DV360: NULL <br> ONE: `Flight`                       | Only ONE                                                             |
| `creative`           | GGAds: `Ad name` <br> DV360: `Creative` <br> ONE: `Creative`          | Trim whitespace                                                      |
| `device_standardize` | GGAds: `Device` <br> DV360: `Device Type` <br> ONE: `Device`          | Map to `Desktop`, `Phone`, `Tablet`, `Phone/Tablet`, `CTV`, or `N/A` |
| `impressions`        | GGAds: `Impr.` <br> DV360: `Impressions` <br> ONE: `Impression`       | Convert string → int, strip commas, NULL → 0                         |
| `clicks`             | GGAds: `Clicks` <br> DV360: `Clicks` <br> ONE: `Click`                | Convert string → int, strip commas, NULL → 0                         |

## 3/ Source Code
See file pipeline_mssql.py

## 4/ Flow Chart
<img width="762" height="1072" alt="TAFlowChart drawio" src="https://github.com/user-attachments/assets/41291acf-bbaa-4404-8b8a-1b72d5a5c0f4" />

## 5/ Diagram Chart
<img width="1121" height="940" alt="DBDIAGRAM" src="https://github.com/user-attachments/assets/0d9b4d67-5287-4dff-a69f-346169062023" />

## 6/ Schema
See file schema.sql - attached.

## 7/ Query
See file query.sql - attached.

## 8/ Final Exported Database
See file ads.bak – attached.
