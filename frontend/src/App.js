import React, { useState } from 'react';
import './App.css';
import ResultItem from './components/ResultItem';
import ParticlesBackground from './components/ParticlesBackground';


function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState({ custom: [], google: [], bing: [] });
  const [loading, setLoading] = useState(false);
  const [ranking, setRanking] = useState('vector_space');


  const handleSearch = async () => {
    setLoading(true);
    const res = await fetch('http://127.0.0.1:5000/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, ranking_algorithm: ranking })
    });
    const data = await res.json();
    setResults(data);
    setLoading(false);
  };

  return (
    <div className="App">
      <ParticlesBackground />
      <h1>Ideologies Search Engine</h1>
      <p className="subtitle">Search the world of beliefs, systems, and thought.</p>



      <div className="search-bar">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter a query..."
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      <div className="ranking-select">
        <label htmlFor="ranking-select">Ranking Algorithm:</label>
        <select
          id="ranking-select"
          value={ranking}
          onChange={(e) => setRanking(e.target.value)}
        >
          <option value="vector_space">Vector Space</option>
          <option value="pagerank">PageRank</option>
          <option value="hits">HITS</option>
        </select>
      </div>


      {loading && <p>Loading results...</p>}

      <div className="results-container">
        <div className="results-pane">
          <h2>Custom Results</h2>
          {results.custom.map((res, i) => (
            <ResultItem key={i} title={res.title} url={res.url} snippet={res.snippet} />
          ))}
        </div>

        <div className="results-pane">
          <h2>Google Results</h2>
          {results.google.map((res, i) => (
            <ResultItem key={i} title={res.title} url={res.url} snippet={res.snippet} />
          ))}
        </div>

        <div className="results-pane">
          <h2>Bing Results</h2>
          {results.bing.map((res, i) => (
            <ResultItem key={i} title={res.title} url={res.url} snippet={res.snippet} />
          ))}
        </div>
      </div>
      <footer style={{ marginTop: "3rem", fontStyle: "italic", color: "#777" }}>
        “An ideology is not a story about the world — it is a story we tell ourselves.”
      </footer>

    </div>
  );
}

export default App;
