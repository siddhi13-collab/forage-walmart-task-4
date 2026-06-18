import pandas as pd
import sqlite3

# CONNECT TO DATABASE
conn = sqlite3.connect("shipment_database.db")
cursor = conn.cursor()

# CREATE TABLE IF NOT EXISTS
cursor.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        shipment_id TEXT,
        origin TEXT,
        destination TEXT,
        product TEXT,
        quantity INTEGER
    )
""")

# ── SPREADSHEET 0 (DIRECT INSERT) ──────────────────────────────────────────
df0 = pd.read_excel("spreadsheet_0.xlsx")

# Normalise column names (strip whitespace, lowercase)
df0.columns = df0.columns.str.strip().str.lower().str.replace(" ", "_")
print("Spreadsheet 0 columns:", df0.columns.tolist())

for _, row in df0.iterrows():
    cursor.execute("""
        INSERT INTO shipments (shipment_id, origin, destination, product, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        str(row["shipment_id"]),
        str(row["origin"]),
        str(row["destination"]),
        str(row["product"]),
        int(row["quantity"])
    ))

print(f"Spreadsheet 0: {len(df0)} rows inserted.")

# ── SPREADSHEET 1 + 2 (MERGE & GROUP) ──────────────────────────────────────
df1 = pd.read_excel("spreadsheet_1.xlsx")
df2 = pd.read_excel("spreadsheet_2.xlsx")

# Normalise column names
df1.columns = df1.columns.str.strip().str.lower().str.replace(" ", "_")
df2.columns = df2.columns.str.strip().str.lower().str.replace(" ", "_")
print("Spreadsheet 1 columns:", df1.columns.tolist())
print("Spreadsheet 2 columns:", df2.columns.tolist())

# Merge: df1 has products per shipment, df2 has origin/destination per shipment
merged = pd.merge(df1, df2, on="shipping_identifier")
print("Merged columns:", merged.columns.tolist())

# Group by shipment + product to count quantity
grouped = merged.groupby(
    ["shipping_identifier", "product", "origin", "destination"]
).size().reset_index(name="quantity")

for _, row in grouped.iterrows():
    cursor.execute("""
        INSERT INTO shipments (shipment_id, origin, destination, product, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        str(row["shipping_identifier"]),
        str(row["origin"]),
        str(row["destination"]),
        str(row["product"]),
        int(row["quantity"])
    ))

print(f"Spreadsheet 1+2: {len(grouped)} rows inserted.")

# SAVE & CLOSE
conn.commit()
conn.close()
print("Database populated successfully!")
