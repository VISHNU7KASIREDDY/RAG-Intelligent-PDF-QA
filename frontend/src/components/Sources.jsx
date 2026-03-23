import React from 'react';

export default function Sources({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-panel">
      <div className="sources-header">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <span>Sources</span>
      </div>
      <div className="sources-list">
        {sources.map((source, i) => (
          <div key={i} className="source-item">
            <div className="source-badge">
              <span className="page-label">Page {source.page}</span>
              {source.filename && (
                <span className="file-label">{source.filename}</span>
              )}
            </div>
            <p className="source-text">{source.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
