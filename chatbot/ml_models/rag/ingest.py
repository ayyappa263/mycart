from langchain_community.document_loaders.dataframe import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, 'fashion_cleaned_dataset.csv'))

df['page_content'] = (
    "product_id: " + df['id'].astype(str) + '\n' +
    "product_name: " + df['product_name'].astype(str)
)

df['price'] = pd.to_numeric(df['price'], errors='coerce')
missing_price = df['price'].isna().sum()
if missing_price:
    print(f"Warning: {missing_price} rows have invalid/missing price and will be dropped.")
    df = df.dropna(subset=['price'])

metadata = ['gender', 'master_Category', 'sub_Category', 'article_Type', 'Colour', 'season', 'year', 'usage', 'price']
final_df = df[['page_content'] + metadata]

loader = DataFrameLoader(final_df, page_content_column="page_content")
docs = loader.lazy_load()

embeddingmodel = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
db_dir = os.path.join(BASE_DIR, "chroma_db")
db = Chroma(embedding_function=embeddingmodel, persist_directory=db_dir)

batch_size = 1000
batch = []
total_indexed = 0

for doc in docs:
    batch.append(doc)
    if len(batch) == batch_size:
        db.add_documents(documents=batch)
        total_indexed += len(batch)
        print(f"Indexed {total_indexed} documents so far...")
        batch = []

if batch:
    db.add_documents(documents=batch)
    total_indexed += len(batch)

print(f"Done. Total documents indexed: {total_indexed}")