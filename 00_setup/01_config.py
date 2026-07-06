CATALOG_NAME = "banklens"
# This is a full-line commen
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"
DATA_QUALITY_SCHEMA = "data_quality"
#////////////////////////////////////////////////////////////////////////////////////////////
RAW_BASE_PATH = "dbfs:/Volumes/banklens/bronze/raw_files"

STATIC_TABLES = [
    "merchant_reference",
    "market_rates"
]

MASTER_TABLES = [
    "customer_master",
    "account_master",
    "loan_master",
    "product_holdings"
]

DAILY_TABLES = [
    "transaction_fact",
    "card_transaction_fact",
    "account_balance_snapshot",
    "device_events",
    "digital_activity",
    "support_tickets"
]

TABLE_NAMES = (
    STATIC_TABLES
    + MASTER_TABLES
    + DAILY_TABLES
)
