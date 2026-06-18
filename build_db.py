import sqlite3
import pandas as pd

csv_path = "data/netflix_titles.csv"
db_path = "data/netflix_analysis.db"

print("Reading Netflix CSV file...")
try:
    df = pd.read_csv(csv_path)
    df = df.drop_duplicates()

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)

    print("Saving rows into SQLite table 'netflix_titles'...")
    df.to_sql("netflix_titles", conn, if_exists="replace", index=False)
    conn.close()

    print("==================================================")
    print(f"SUCCESS! Loaded {len(df)} rows into your local database.")
    print("==================================================")
except Exception as e:
    print(f"Error building database: {e}")
