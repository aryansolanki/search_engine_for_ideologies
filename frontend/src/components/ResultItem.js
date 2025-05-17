import React, { useState } from 'react';

const ResultItem = ({ title, url, snippet }) => {
  const [expanded, setExpanded] = useState(false);

  const words = snippet.split(' ');
  const preview = words.slice(0, 30).join(' ');
  const isLong = words.length > 30;

  return (
    <div className="result-item">
      <a href={url} target="_blank" rel="noopener noreferrer">
        <strong>{title}</strong>
      </a>
      <p>
        {expanded || !isLong ? snippet : preview + '...'}
        {isLong && (
          <span
            onClick={() => setExpanded(!expanded)}
            style={{
              color: '#007bff',
              cursor: 'pointer',
              marginLeft: '0.5rem',
              fontWeight: 'bold',
            }}
          >
            {expanded ? ' Read less' : ' Read more'}
          </span>
        )}
      </p>
    </div>
  );
};

export default ResultItem;
