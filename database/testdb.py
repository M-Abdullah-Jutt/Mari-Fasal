# from pathlib import Path
# import sqlite3

# BASE_DIR = Path(__file__).resolve().parent
# DB_PATH = BASE_DIR / "marifasalv1.db"

# print("Database:", DB_PATH)
# print("Exists:", DB_PATH.exists())

# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()

# cursor.execute("""
#     SELECT name
#     FROM sqlite_master
#     WHERE type='table'
# """)

# print("Tables:", cursor.fetchall())


from pathlib import Path
import sqlite3

# Database path
DB_PATH = Path(__file__).resolve().parent / "marifasalv2.db"

print("Database:", DB_PATH)
print("Exists:", DB_PATH.exists())

# Connect
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Show tables

print("\n--- TABLES ---")

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

for table in cursor.fetchall():
    print(table[0])


# Test Disease

crop = "Tomato"
disease = "Early Blight"

print(f"\n--- TEST ---")
print(f"Crop: {crop}")
print(f"Disease: {disease}")


# Causes

cursor.execute("""
    SELECT ca.cause
    FROM causes ca
    JOIN diseases d
        ON ca.disease_id = d.id
    JOIN crops c
        ON d.crop_id = c.id
    WHERE c.name = ?
      AND d.name = ?
""", (crop, disease))

causes = cursor.fetchall()

print("\nCauses:")

if causes:
    for cause in causes:
        print("-", cause[0])
else:
    print("No causes found.")


# Recommendations

cursor.execute("""
    SELECT r.recommendation
    FROM recommendations r
    JOIN diseases d
        ON r.disease_id = d.id
    JOIN crops c
        ON d.crop_id = c.id
    WHERE c.name = ?
      AND d.name = ?
""", (crop, disease))

recommendations = cursor.fetchall()

print("\nRecommendations:")

if recommendations:
    for recommendation in recommendations:
        print("-", recommendation[0])
else:
    print("No recommendations found.")


# Close

conn.close()