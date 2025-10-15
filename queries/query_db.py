import sqlite3
import pandas as pd

# --- CONNECT TO DATABASE ---
db_name = "mlb_history.db"
conn = sqlite3.connect(db_name)

print(f"\n Connected to {db_name}")
print("Type 'help' for examples or 'exit' to quit.\n")

while True:
    user_input = input("SQL> ").strip()

    # Exit command
    if user_input.lower() in ["exit", "quit", "q"]:
        print("\n Goodbye!")
        break

    # Help command
    elif user_input.lower() == "help":
        print("""
💡 Example queries you can try:
--------------------------------
1️  SELECT * FROM events LIMIT 5;
2️  SELECT * FROM statistics WHERE Year = 2023;
3️  SELECT * FROM years WHERE Year BETWEEN 2010 AND 2020;
4️  SELECT e.Year, e.Event, s.Player, s.Value
     FROM events e
     JOIN statistics s ON e.Year = s.Year
     WHERE s.Category LIKE '%Home Run%'
     LIMIT 10;
""")
        continue

    # Run user query
    try:
        df = pd.read_sql(user_input, conn)
        if df.empty:
            print(" No results found.\n")
        else:
            print(df.head(20).to_string(index=False))
            print(f"\n Returned {len(df)} record(s)\n")
    except Exception as e:
        print(f" Error: {e}\n")

conn.close()