import ujson as json
import pickle
import math
import time
from collections import defaultdict
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

class SklearnIndexer:
    def __init__(self):
        self.metadata_store = {}
        self.url_list = []
        self.url_to_id = {}
        self.graph = nx.DiGraph()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.pr_scores=None
        self.hubs=None
        self.authorities=None
        self.title_vectorizer = None
        self.title_tfidf_matrix = None
        self.body_vectorizer=None
        self.body_tfidf_matrix=None
        # self.term_boosts = {
        #     "libertarianism": 1.5,
        #     "socialism":      1.5,
        #     "conservatism":   1.5,
        #     "liberalism":     1.5,
            
        # }
        self.term_boosts = dict(self.load_term_boosts("terms.json"))
        # print(self.term_boosts)
        # Use list for stop_words as required by TfidfVectorizer
        self.stop_words = list(stopwords.words('english'))

    def load_term_boosts(self, filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
        
    def preprocess_text(self, metadata):
        # text_parts = [
        #     metadata.get("title", ""),
        #     metadata.get("description", ""),
        #     metadata.get("keywords", "")
        # ]

        # return ' '.join(text_parts).lower()
        title       = metadata.get("title", "")
        description = metadata.get("description", "")
        keywords    = metadata.get("keywords", "")
        # Repeat title 3×:
        boosted_title = ' '.join([title]*3)
        boosted_keywords = ' '.join([keywords]*3)
        return ' '.join([boosted_title ,boosted_keywords]).lower()

    def build_index(self, scraped_data):
        documents = []
        titles=[]
        bodies = []

        for idx, (url, data) in enumerate(scraped_data['web_graph'].items()):
            metadata = data.get("metadata", {})
            self.metadata_store[url] = metadata
            self.url_to_id[url] = idx
            self.url_list.append(url)
            doc = self.preprocess_text(metadata)
            bodies.append(metadata.get("description","").lower())
            titles.append(' '.join([metadata.get("title",""),metadata.get("keywords","")]).lower())
            documents.append(doc)

        # Pass stop_words as a list
        self.vectorizer = TfidfVectorizer(stop_words=self.stop_words)
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

        self.title_vectorizer=TfidfVectorizer(stop_words=self.stop_words)
        self.title_tfidf_matrix=self.title_vectorizer.fit_transform(titles)

        self.body_vectorizer=TfidfVectorizer(stop_words=self.stop_words)
        self.body_tfidf_matrix=self.body_vectorizer.fit_transform(bodies)

        # Build the link graph
        for url, data in scraped_data['web_graph'].items():
            from_id = self.url_to_id[url]
            for out_url in data.get("links", []):
                if out_url in self.url_to_id:
                    to_id = self.url_to_id[out_url]
                    self.graph.add_edge(from_id, to_id)

        self.pr_scores = nx.pagerank(self.graph, alpha=0.85)
        self.hubs, self.authorities = nx.hits(self.graph, max_iter = 50, normalized = True) 

    def search(self, query, use_pagerank,use_hits,use_vector_space, top_k=5):

        # q_vec = self.vectorizer.transform([query.lower()])

        # # 2) boost the columns corresponding to your ideology terms
        # for term, factor in self.term_boosts.items():
        #     if term in self.vectorizer.vocabulary_:
        #         idx = self.vectorizer.vocabulary_[term]
        #         # multiply that dimension by your boost factor
        #         q_vec[0, idx] *= factor
        #         print(q_vec[0, idx])

        # # 3) compute cosine similarity with each document
        # cosine_scores = cosine_similarity(q_vec, self.tfidf_matrix).flatten()

        # query_vec = self.vectorizer.transform([query])
        # cosine_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        query_title = self.title_vectorizer.transform([query])
        query_description = self.body_vectorizer.transform([query])
        # cosine_scores = cosine_similarity(query_title, self.tfidf_matrix).flatten()


        cosine_scores_title = cosine_similarity(query_title, self.title_tfidf_matrix).flatten()
        cosine_scores_body = cosine_similarity(query_description, self.body_tfidf_matrix).flatten()
        
        print(len(cosine_scores_title),len(cosine_scores_body))
        cosine_scores = (2.0 * cosine_scores_title)/3 + (1.0 * cosine_scores_body)/3

        scores = {idx: score for idx, score in enumerate(cosine_scores) if score > 0}
        top_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:50]

        if use_pagerank:
            print("Page Rank")
            
            for doc_id, _ in top_docs:
                scores[doc_id] = 0.7 * scores[doc_id] + 0.4 * self.pr_scores.get(doc_id, 0)

        elif use_hits:
            print("Hit Algorithm")
            
            # print(local_auths," = ",_,)
            for doc_id, _ in top_docs:
                scores[doc_id] = 0.7 * scores[doc_id] + 0.2 * self.authorities.get(doc_id, 0) + 0.2 * self.hubs.get(doc_id, 0)
        else:
            print("Vector Space")
            
        ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        seen_titles = set()
        results = []
       
        for doc_id, score in ranked_results:
            url = self.url_list[doc_id]
            # results[url] = self.metadata_store[url]
            meta = self.metadata_store[url]
            title = meta.get("title", "")[:200].strip()
            if title in seen_titles:
                continue
            seen_titles.add(title)
            results.append({
                "title": meta.get("title", "")[:200],
                "url": url,
                "score":score,
                "snippet": meta.get("description", "")[:300]
            })
        # print(results)
        return results

