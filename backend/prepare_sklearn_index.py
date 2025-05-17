import pickle
from sklearn_indexer import SklearnIndexer
import time

print("🔁 Loading scraped_data_7.pkl...")
with open("scraped_data.pkl", "rb") as f:
    scraped_data = pickle.load(f)

print("🔧 Building Sklearn Indexer...")
indexer = SklearnIndexer()
start_time = time.time()
indexer.build_index(scraped_data)
end_time = time.time()

print(f"✅ Index built in {end_time - start_time:.2f}s.")

# Save to .pkl
with open("sklearn_index.pkl", "wb") as f:
    pickle.dump(indexer, f)

print("✅ Saved index as sklearn_index.pkl")
