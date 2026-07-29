import os
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


API_URL = "https://dummyjson.com/products"
DATA_DIR = Path(os.getenv("DATA_DIR", "/opt/airflow/data"))
RAW_PATH = DATA_DIR / "dummyjson_products_raw.json"
CSV_PATH = DATA_DIR / "dummyjson_products.csv"


def extract():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(API_URL, params={"limit": 100}, timeout=30)
    response.raise_for_status()
    products = response.json()["products"]

    with RAW_PATH.open("w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)

    print(f"{len(products)} produtos extraídos para {RAW_PATH}.")


def transform():
    with RAW_PATH.open("r", encoding="utf-8") as file:
        products = json.load(file)

    rows = []

    for product in products:
        rows.append(
            {
                "id": product["id"],
                "title": product["title"],
                "category": product["category"],
                "brand": product.get("brand"),
                "price": product["price"],
                "discount_percentage": product["discountPercentage"],
                "rating": product["rating"],
                "stock": product["stock"],
                "extracted_at": datetime.utcnow().isoformat(),
            }
        )

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["id"])
    df = df.dropna()

    print(f"{len(df)} produtos transformados.")
    return df.to_dict(orient="records")


def load(records=None, **context):
    if records is None:
        records = context["ti"].xcom_pull(task_ids="transformar")

    df = pd.DataFrame(records)
    df.to_csv(CSV_PATH, index=False)

    print(f"{len(df)} produtos carregados para {CSV_PATH}.")


if __name__ == "__main__":
    extract()
    transformed_records = transform()
    load(transformed_records)
