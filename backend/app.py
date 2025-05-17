from flask import Flask, request, jsonify
from flask_cors import CORS
from search_engine import (
    search_documents_vector_space,
    search_documents_pagerank,
    search_documents_hits,
    search_google_serpapi,
    search_bing_serpapi
)

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    algorithm = data.get('ranking_algorithm', 'tfidf')

    # Custom Search Engine based on algorithm
    if algorithm == 'pagerank':
        custom_results = search_documents_pagerank(query)
    elif algorithm == 'hits':
        custom_results = search_documents_hits(query)
    else:
        custom_results = search_documents_vector_space(query)


    # Real Google and Bing search via SerpAPI
    google_results = search_google_serpapi(query)
    bing_results = search_bing_serpapi(query)

    return jsonify({
        "custom": custom_results,
        "google": google_results,
        "bing": bing_results
    })

if __name__ == '__main__':
    app.run(debug=True)
