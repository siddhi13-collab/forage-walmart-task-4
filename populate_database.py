import pandas as pd
import sqlite3

# CONNECT TO DATABASE

conn = sqlite3.connect("shipment_database.db") 
cursor = conn.cursor()

# SPREADSHEET 0 (DIRECT INSERT)
df0 = pd.read_excel("spreadsheet_0.xlsx")

for _, row in df0.iterrows():
    cursor.execute("""
        INSERT INTO shipments (shipment_id, origin, destination, product, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        row["shipment_id"],
        row["origin"],
        row["destination"],
        row["product"],
        row["quantity"]
    ))

# SPREADSHEET 1 + 2 PROCESSING

df1 = pd.read_excel("spreadsheet_1.xlsx")
df2 = pd.read_excel("spreadsheet_2.xlsx")

# Merge using shipping identifier
merged = pd.merge(df1, df2, on="shipping_identifier")

# Group by shipment + product to count quantity
grouped = merged.groupby(
    ["shipping_identifier", "product", "origin", "destination"]
).size().reset_index(name="quantity")


# INSERT INTO DATABASE

for _, row in grouped.iterrows():
    cursor.execute("""
        INSERT INTO shipments (shipment_id, origin, destination, product, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        row["shipping_identifier"],
        row["origin"],
        row["destination"],
        row["product"],
        row["quantity"]
    ))

# SAVE CHANGES

conn.commit()
conn.close()

print("Database populated successfully!")
