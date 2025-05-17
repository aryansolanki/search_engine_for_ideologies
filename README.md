# 🔍 Search Engine for Ideologies

A custom-built vertical search engine that focuses on retrieving and ranking web content related to political ideologies such as **Liberalism**, **Conservatism**, **Socialism**, and **Libertarianism**. The engine includes components for asynchronous crawling, metadata extraction, vector-based indexing, and a responsive user interface.

---

## 🧠 Project Overview

This project demonstrates a complete search engine pipeline, including:

- **Web Crawling:** An asynchronous crawler built using `aiohttp` and `lxml` efficiently collects content from the web while avoiding duplicates, non-English pages, and low-information documents.
- **Metadata Extraction:** Extracts page title, description, and keywords using BeautifulSoup and heuristics, ensuring meaningful indexing.
- **Indexing:** Builds both a custom term-frequency index and a Scikit-learn-based TF-IDF vector space model.
- **Storage:** Preprocessed and indexed data are stored in `.pkl` (Pickle) files and JSON to avoid re-computation and enable faster search execution.
- **Search Engine Logic:** Supports keyword-based retrieval using cosine similarity and TF-IDF scores.
- **Frontend UI:** A React.js-based user interface for entering queries and viewing ranked results.

---

## 💾 Why Use `.pkl` Files and Precomputed Index?

- ⚡ **Efficiency:** Parsing and indexing thousands of documents is computationally expensive. Using `.pkl` files allows fast loading of precomputed Python objects like vectorizers and indexes.
- 🔁 **Repeatability:** With precomputed indexes, users can re-run the search engine without crawling or indexing from scratch.
- 🧠 **Experimentation:** Storing intermediate states makes it easier to test different ranking strategies or interface designs without reprocessing data.

---

## 📁 Directory Structure

```
search_engine_for_ideologies/
├── backend/
│   ├── app.py                  # Flask server
│   ├── search_engine.py        # Main search functions
│   ├── sklearn_indexer.py      # Vector-based TF-IDF index logic
│   ├── prepare_sklearn_index.py# Precomputes and serializes vector index
│   ├── conver_pkl.py           # Converts raw data into .pkl format
│   ├── terms.json              # Optional term dictionary for lookup
│   ├── requirements.txt        # Backend Python dependencies
|
├── frontend/
│   ├── public/                 # HTML template and icons
│   └── src/                    # React components and styles
│
├── .gitignore
└── README.md
```

---

## 🚀 Features

- 🌐 Asynchronous crawling with respect for page relevance and uniqueness
- 🧾 Rich metadata extraction with fallbacks for incomplete pages
- 🧮 Dual-index support: Custom term frequency + TF-IDF vectorizer
- 🔍 Real-time search over pre-indexed data using cosine similarity
- ⚛️ React UI for query input, result rendering, and future comparisons with Google/Bing

---

## ⚙️ How to Run

### 🐍 Backend (Flask)

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate      # Mac/Linux
pip install -r requirements.txt
python app.py
```

### ⚛️ Frontend (React)

```bash
cd frontend
npm install
npm start
```

---

## 🔍 How the Search Works

- User submits a query through the React UI
- Query is sent to the Flask backend
- Backend loads precomputed TF-IDF index from `.pkl` file
- Computes cosine similarity between query vector and indexed documents
- Returns ranked results to the frontend for display

---

## 📦 Tech Stack

| Component   | Technology                        |
|-------------|-----------------------------------|
| Crawler     | Python, aiohttp, lxml, BeautifulSoup |
| Indexer     | Scikit-learn, JSON, Pickle        |
| Backend     | Flask                             |
| Frontend    | React.js                          |
| Data Store  | .json, .pkl                       |

---

## 🧑‍💻 Author

- Aryan Solanki – [GitHub](https://github.com/aryansolanki)

---

## 📄 License

This project is licensed under the **MIT License** – you’re free to use and modify it.

---

That's it!