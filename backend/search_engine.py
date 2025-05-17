import pickle
from sklearn_indexer import SklearnIndexer
from serpapi import GoogleSearch

# Load prebuilt indexer
print("🔁 Loading sklearn_index.pkl...")
with open("sklearn_index.pkl", "rb") as f:
    indexer = pickle.load(f)
print("✅ SklearnIndexer loaded.")

# === Custom Search Methods ===

def search_documents_vector_space(query, top_k=5):
    return indexer.search(query, use_pagerank=False, use_hits=False, use_vector_space=True)[:top_k]

def search_documents_pagerank(query, top_k=5):
    return indexer.search(query, use_pagerank=True, use_hits=False,use_vector_space=False)[:top_k]

def search_documents_hits(query, top_k=5):
    return indexer.search(query, use_pagerank=False, use_hits=True,use_vector_space=False)[:top_k]

# ====== Real Google Search via SerpAPI ======

def search_google_serpapi(query, num_results=7):
    params = {
        "engine": "google",
        "q": query,
        "api_key": "6b291269522ef4ab9bb01b68112392186395eaf7be6380ae20bd87df8d0e6b16",
        "num": num_results,
        "location": "United States",   # 🆕 Fixed location
        "gl": "us",                    # 🆕 Country set to US
        "hl": "en",                    # 🆕 Language set to English
        "no_cache": True               # 🆕 Always get fresh results
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    return [
        {
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "snippet": result.get("snippet", "")
        }
        for result in results.get("organic_results", [])
    ]

# ====== Real Bing Search via SerpAPI ======

def search_bing_serpapi(query, num_results=7):
    params = {
        "engine": "bing",
        "q": query,
        "api_key": "6b291269522ef4ab9bb01b68112392186395eaf7be6380ae20bd87df8d0e6b16",
        "count": num_results,
        "location": "United States",
        # "cc": "US",    # cc = country code Bing uses
        # "setlang": "EN",  # Set language to English
        # "safeSearch": "Off",  # (Optional) You can set "Strict" or "Moderate"
        # "hl": "en",
        # "no_cache": True
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    if [
        {
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "snippet": result.get("snippet", "")
        }
        for result in results.get("organic_results", [])
    ]==[]:
        return search_google_serpapi(query)
    else:

        return [
            {
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", "")
            }
            for result in results.get("organic_results", [])
        ]
