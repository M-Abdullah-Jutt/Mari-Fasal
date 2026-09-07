import sqlite3
import csv
from pathlib import Path

# Paths

BASE_DIR = Path(__file__).resolve().parent

CAUSES_CSV = BASE_DIR / "Causes" / "v1" / "Plant_Disease_Causes_Pakistan.csv"
RECOMMENDATIONS_CSV = BASE_DIR  / "Recommendations" / "v1" / "Plant_Disease_Recommendations_Pakistan.csv"

DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "marifasalv2.db"



# Create Database

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Remove old tables if they exist
cursor.executescript("""
DROP TABLE IF EXISTS causes;
DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS diseases;
DROP TABLE IF EXISTS crops;
DROP TABLE IF EXISTS categories;
""")


# Create Tables

cursor.executescript("""
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    UNIQUE(name, category_id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    crop_id INTEGER NOT NULL,
    UNIQUE(name, crop_id),
    FOREIGN KEY (crop_id) REFERENCES crops(id)
);

CREATE TABLE causes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id INTEGER NOT NULL,
    cause TEXT NOT NULL,
    FOREIGN KEY (disease_id) REFERENCES diseases(id)
);

CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id INTEGER NOT NULL,
    recommendation TEXT NOT NULL,
    FOREIGN KEY (disease_id) REFERENCES diseases(id)
);
""")


# Helper Functions

def get_or_create_category(category):
    cursor.execute(
        "SELECT id FROM categories WHERE name = ?",
        (category,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        "INSERT INTO categories (name) VALUES (?)",
        (category,)
    )

    return cursor.lastrowid


def get_or_create_crop(crop, category_id):
    cursor.execute(
        """
        SELECT id FROM crops
        WHERE name = ? AND category_id = ?
        """,
        (crop, category_id)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO crops (name, category_id)
        VALUES (?, ?)
        """,
        (crop, category_id)
    )

    return cursor.lastrowid


def get_or_create_disease(disease, crop_id):
    cursor.execute(
        """
        SELECT id FROM diseases
        WHERE name = ? AND crop_id = ?
        """,
        (disease, crop_id)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO diseases (name, crop_id)
        VALUES (?, ?)
        """,
        (disease, crop_id)
    )

    return cursor.lastrowid


# Import Causes

def import_causes():

    with open(CAUSES_CSV, "r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            category = row["Category"].strip()
            crop = row["Crop"].strip()
            disease = row["Disease"].strip()
            cause = row["Causes"].strip()

            if not all([category, crop, disease, cause]):
                continue

            category_id = get_or_create_category(category)

            crop_id = get_or_create_crop(
                crop,
                category_id
            )

            disease_id = get_or_create_disease(
                disease,
                crop_id
            )

            cursor.execute(
                """
                INSERT INTO causes (disease_id, cause)
                VALUES (?, ?)
                """,
                (disease_id, cause)
            )


# Import Recommendations

def import_recommendations():

    with open(
        RECOMMENDATIONS_CSV,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            category = row["Category"].strip()
            crop = row["Crop"].strip()
            disease = row["Disease"].strip()
            recommendation = row["Recommendations"].strip()

            if not all([
                category,
                crop,
                disease,
                recommendation
            ]):
                continue

            category_id = get_or_create_category(category)

            crop_id = get_or_create_crop(
                crop,
                category_id
            )

            disease_id = get_or_create_disease(
                disease,
                crop_id
            )

            cursor.execute(
                """
                INSERT INTO recommendations
                (disease_id, recommendation)
                VALUES (?, ?)
                """,
                (disease_id, recommendation)
            )


# Run Import

import_causes()
import_recommendations()

conn.commit()


# Create Indexes

cursor.executescript("""
CREATE INDEX idx_crops_category
ON crops(category_id);

CREATE INDEX idx_diseases_crop
ON diseases(crop_id);

CREATE INDEX idx_causes_disease
ON causes(disease_id);

CREATE INDEX idx_recommendations_disease
ON recommendations(disease_id);
""")

conn.commit()



print("\nKnowledge Base Created Successfully!")

for table in [
    "categories",
    "crops",
    "diseases",
    "causes",
    "recommendations"
]:

    cursor.execute(f"SELECT COUNT(*) FROM {table}")

    count = cursor.fetchone()[0]

    print(f"{table}: {count}")


print(f"\nDatabase: {DB_PATH}")

conn.close()