import pickle
import ujson as json
# First time only
with open("web_graph.json", 'r') as f:
    data = json.load(f)
with open("scraped_data.pkl", "wb") as f:
    pickle.dump(data, f)
 