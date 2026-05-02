"""
embed_abstracts.py

Usage:
    python embed_abstracts.py --csv data/cancer_abstracts.csv
"""

import argparse
import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

DB_PATH = "./chroma_db"
COLLECTION_NAME = "cancer_abstracts"


def load_data(csv_path):
    print("Loading data...")
    df = pd.read_csv(csv_path)

    # assume column is called 'abstract'
    if "abstract" not in df.columns:
        raise ValueError("CSV must contain an 'abstract' column")

    # basic cleaning
    df = df.dropna(subset=["abstract"])
    df["abstract"] = df["abstract"].astype(str).str.strip()

    # remove very short abstracts
    df = df[df["abstract"].str.len() > 50]

    # remove duplicates
    df = df.drop_duplicates(subset=["abstract"])

    print(f"Loaded {len(df)} abstracts after cleaning")
    return df


def build_chroma(df):
    print("Creating embeddings...")

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=DB_PATH)

    # overwrite collection if it exists
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )

    documents = df["abstract"].tolist()
    ids = [str(i) for i in range(len(documents))]

    collection.add(
        documents=documents,
        ids=ids
    )

    print(f"Done. Stored {collection.count()} documents.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        raise FileNotFoundError("CSV file not found")

    df = load_data(args.csv)
    build_chroma(df)


if __name__ == "__main__":
    main()
