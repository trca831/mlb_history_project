import sqlite3
import pandas as pd
import os

# --- CONNECT TO DATABASE ---
db_name = "mlb_history.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

print(f" Connected to {db_name}\n")

# --- IMPORT ALL CSV FILES IN 'data/' FOLDER ---
data_folder = "data"

for file in os.listdir(data_folder):
    if file.endswith(".csv"):
        table_name = file.replace(".csv", "")
        file_path = os.path.join(data_folder, file)

        print(f" Importing {file} into table '{table_name}'...")

        try:
            df = pd.read_csv(file_path)

            # Optional: force data types
            if "Year" in df.columns:
                df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f" Imported {len(df)} records into '{table_name}' table.\n")

        except Exception as e:
            print(f" Error importing {file}: {e}\n")

# --- VERIFY TABLES CREATED ---
print(" Tables created in the database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in cursor.fetchall():
    print(" -", row[0])

conn.close()
print("\n All CSV files imported successfully into mlb_history.db")