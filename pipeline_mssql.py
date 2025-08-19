from enum import Enum
from time import sleep
import urllib
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np

# Connect to Database
SERVER = "localhost"
DATABASE = "ads"  # Database name created from sql script
UID = "sa"  # Config depend on mssql account
PWD = "12345"  # Config depend on mssql account

# Connection string
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={UID};"
    f"PWD={PWD};"
    f"TrustServerCertificate=Yes;"
)

# Check connect to database is success
try:
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Connected to database.")
except Exception as e:
    raise RuntimeError(f"Failed to connect DB")


# Retry
def read_excel_retry(
    file, sheet_name, retries=5, wait_seconds=5
):  # Retry 5 times, wait 5 seconds each retry
    for attempt in range(1, retries + 1):
        try:
            return pd.read_excel(file, sheet_name=sheet_name)
        except Exception as e:
            if attempt == retries:
                raise
            print(
                f"Error while reading sheet {sheet_name}: {e} — Retry {attempt}/{retries}"
            )
            sleep(wait_seconds)


## PULL FROM EXCEL
DATA_FILE = "Data Engineer - Round 2 Task.xlsx"
SHEET_GGADS = "SOURCE_GGAds data"
SHEET_DV360 = "SOURCE_DV360 data"
SHEET_ONE = "SOURCE_One data"
TABLE_RAW_GGADS = "raw_ggads"
TABLE_RAW_DV360 = "raw_dv360"
TABLE_RAW_ONE = "raw_one"

# Reset data from table avoid duplicate data
with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE raw_ggads"))
    conn.execute(text("TRUNCATE TABLE raw_dv360"))
    conn.execute(text("TRUNCATE TABLE raw_one"))
    conn.execute(text("TRUNCATE TABLE stg_ads_clean"))
print("Reset RAW & STAGING tables.")

# Insert SOURCE_GGAds data into database
ggads = read_excel_retry(DATA_FILE, sheet_name=SHEET_GGADS)
ggads.to_sql(
    TABLE_RAW_GGADS,
    con=engine,
    if_exists="append",
    index=False,
)
print("SOURCE_GGAds data has been recorded in the table raw_ggads.")

# Insert SOURCE_DV360 data into database
dv360 = read_excel_retry(DATA_FILE, sheet_name=SHEET_DV360)
dv360.to_sql(
    TABLE_RAW_DV360,
    con=engine,
    if_exists="append",
    index=False,
)
print("SOURCE_DV360 data has been recorded in the table raw_dv360.")

# Insert SOURCE_One data into database
one = read_excel_retry(DATA_FILE, sheet_name=SHEET_ONE)
one = one[one["Date"] != "Total"]  # Remove the last total line
one.to_sql(
    TABLE_RAW_ONE,
    con=engine,
    if_exists="append",
    index=False,
)
print("SOURCE_One data has been recorded in the table raw_one.")

# CLEAN & STANDARDIZE DATA
DEVICE_MAP = {
    # Desktop
    "computers": "Desktop",
    "desktop": "Desktop",
    "pc": "Desktop",
    # Phone
    "mobile phones": "Phone",
    "smart phone": "Phone",
    "phone": "Phone",
    # Tablet
    "tablets": "Tablet",
    "tablet": "Tablet",
    # Phone/Tablet combined
    "phone/tablet": "Phone/Tablet",
    # CTV
    "tv screens": "CTV",
    "connected tv": "CTV",
}


class Platform(str, Enum):
    GGADS = "GGADS"
    DV360 = "DV360"
    ONE = "ONE"


# Standard device name, if not exist return "N/A"
def standardize_device(v):
    if pd.isna(v):
        return "N/A"
    return DEVICE_MAP.get(str(v).strip().lower(), "N/A")


# Parse int, handle case large number have comma seperate and return 0 if null
def parse_int(x):
    if pd.isna(x):
        return 0
    if isinstance(x, (int, np.integer)):
        return int(x)
    s = str(x).strip().replace(",", "")
    return int(s) if s else 0


# Remove white space
def clean_str(s):
    if pd.isna(s):
        return None
    s = str(s).strip()
    return s if s != "" else None


# Handle datetime format 'YYYY-MM-DD' and 'YYYY/MM/DD'
def parse_date(s):
    if pd.isna(s):
        return None
    try:
        return pd.to_datetime(s, errors="coerce").date()
    except Exception:
        return None


# Standardize into same schema
gg_std = pd.DataFrame(
    {
        "date": ggads["Day"].map(parse_date),
        "platform": Platform.GGADS.value,
        "advertiser_account": ggads["Account name"].map(clean_str),
        "campaign": ggads["Campaign"].map(clean_str),
        "ad_group": ggads["Ad group"].map(clean_str),
        "insertion_order": None,
        "line_item": None,
        "flight": None,
        "creative": ggads["Ad name"].map(clean_str),
        "device_raw": ggads["Device"],
        "device_standardize": ggads["Device"].map(standardize_device),
        "impressions": ggads["Impr."].map(parse_int),
        "clicks": ggads["Clicks"].map(parse_int),
    }
)

dv_std = pd.DataFrame(
    {
        "date": dv360["Date"].map(parse_date),
        "platform": Platform.DV360.value,
        "advertiser_account": dv360["Advertiser"].map(clean_str),
        "campaign": dv360["Campaign"].map(clean_str),
        "ad_group": None,
        "insertion_order": dv360["Insertion Order"].map(clean_str),
        "line_item": dv360["Line Item"].map(clean_str),
        "flight": None,
        "creative": dv360["Creative"].map(clean_str),
        "device_raw": dv360["Device Type"],
        "device_standardize": dv360["Device Type"].map(standardize_device),
        "impressions": dv360["Impressions"].map(parse_int),
        "clicks": dv360["Clicks"].map(parse_int),
    }
)

one_std = pd.DataFrame(
    {
        "date": one["Date"].map(parse_date),
        "platform": Platform.ONE.value,
        "advertiser_account": one["Advertiser"].map(clean_str),
        "campaign": one["Campaign"].map(clean_str),
        "ad_group": None,
        "insertion_order": None,
        "line_item": None,
        "flight": one["Flight"].map(clean_str),
        "creative": one["Creative"].map(clean_str),
        "device_standardize": one["Device"].map(standardize_device),
        "impressions": one["Impression"].map(parse_int),
        "clicks": one["Click"].map(parse_int),
    }
)

# Merge all sources into one
fact = pd.concat([gg_std, dv_std, one_std], ignore_index=True)

# Filter the valid data
fact = fact[fact["date"].notna() & (fact["impressions"] >= 0) & (fact["clicks"] >= 0)]

# Remove white space if string
for col in [
    "advertiser_account",
    "campaign",
    "ad_group",
    "insertion_order",
    "line_item",
    "flight",
    "creative",
    "device_raw",
]:
    fact[col] = fact[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Group by to avoid duplicates, sum impressions and clicks
group_keys = [
    "date",
    "platform",
    "advertiser_account",
    "campaign",
    "ad_group",
    "insertion_order",
    "line_item",
    "flight",
    "creative",
    "device_standardize",
]
fact = fact.groupby(group_keys, dropna=False, as_index=False).agg(
    impressions=("impressions", "sum"), clicks=("clicks", "sum")
)

TARGET_TABLE = "stg_ads_clean"

if fact.empty:
    print("No records after cleaning & standardizing")
else:
    fact.to_sql(
        TARGET_TABLE,
        con=engine,
        if_exists="append",
        index=False,
    )
    print(f"Cleaned & standardized {len(fact)} datas into table {TARGET_TABLE}")
