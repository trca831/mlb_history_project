import sqlite3
import pandas as pd
import os

# --- Connect to database ---
db_path = "mlb_history.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print(f" Connected to {db_path}")

# --- Drop existing tables to refresh data ---
tables = ["statistics", "years", "events"]
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
print(" Old tables dropped (if they existed).")

# --- Helper function to import CSVs ---
def import_csv_to_table(csv_path, table_name):
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f" Imported {len(df)} records into '{table_name}' table.")
    else:
        print(f"⚠️ File not found: {csv_path}")

# --- Import CSVs ---
import_csv_to_table("data/statistics.csv", "statistics")
import_csv_to_table("data/years.csv", "years")
import_csv_to_table("data/events.csv", "events")

# --- Show all tables ---
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("\n Tables in database:")
for (table_name,) in cursor.fetchall():
    print(" -", table_name)

conn.close()
print("\n All CSV files imported successfully into mlb_history.db")