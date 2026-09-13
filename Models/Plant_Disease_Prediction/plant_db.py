
import sqlite3
from pathlib import Path
from typing import Optional, TypedDict


class DiseaseInfo(TypedDict):
    crop: str
    disease: str
    causes: list[str]
    recommendations: list[str]


def get_disease_info(class_name: str, db_path: str) -> Optional[DiseaseInfo]:
    """
    Looks up crop/disease/causes/recommendations for a given model class name.
    Returns None if the class name isn't found in the database (e.g. a typo,
    or the model's CLASS_NAMES list drifted from the database's categories).
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT crops.name AS crop_name, diseases.name AS disease_name, diseases.id AS disease_id
        FROM categories
        JOIN crops ON crops.category_id = categories.id
        JOIN diseases ON diseases.crop_id = crops.id
        WHERE categories.name = ?
        """,
        (class_name,),
    )
    row = cur.fetchone()

    if row is None:
        conn.close()
        return None

    disease_id = row["disease_id"]

    cur.execute("SELECT cause FROM causes WHERE disease_id = ?", (disease_id,))
    causes = [r["cause"] for r in cur.fetchall()]

    cur.execute("SELECT recommendation FROM recommendations WHERE disease_id = ?", (disease_id,))
    recommendations = [r["recommendation"] for r in cur.fetchall()]

    conn.close()

    return {
        "crop": row["crop_name"],
        "disease": row["disease_name"],
        "causes": causes,
        "recommendations": recommendations,
    }
