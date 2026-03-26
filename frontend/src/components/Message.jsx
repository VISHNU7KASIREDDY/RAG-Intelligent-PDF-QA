import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import Sources from './Sources';

export default function Message({ message }) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}>
      <div className={`message-avatar ${isUser ? 'user-avatar' : 'ai-avatar'}`}>
        {isUser ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V6a4 4 0 0 1 4-4z" />
            <path d="M18 14a6 6 0 0 0-12 0v4a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4z" />
            <line x1="9" y1="18" x2="9" y2="18" />
            <line x1="15" y1="18" x2="15" y2="18" />
          </svg>
        )}
      </div>
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'ai-bubble'}`}>
        <div className="message-content">
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p style={{ margin: '0 0 0.5em 0' }}>{children}</p>,
                ul: ({ children }) => <ul style={{ paddingLeft: '1.2em', margin: '0.3em 0' }}>{children}</ul>,
                ol: ({ children }) => <ol style={{ paddingLeft: '1.2em', margin: '0.3em 0' }}>{children}</ol>,
                li: ({ children }) => <li style={{ marginBottom: '0.2em' }}>{children}</li>,
                strong: ({ children }) => <strong style={{ fontWeight: 700 }}>{children}</strong>,
                code: ({ inline, children }) =>
                  inline ? (
                    <code style={{ background: 'rgba(255,255,255,0.1)', borderRadius: '4px', padding: '1px 5px', fontFamily: 'monospace', fontSize: '0.9em' }}>{children}</code>
                  ) : (
                    <pre style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '0.8em', overflowX: 'auto', fontSize: '0.88em', margin: '0.5em 0' }}>
                      <code style={{ fontFamily: 'monospace' }}>{children}</code>
                    </pre>
                  ),
                h1: ({ children }) => <h1 style={{ fontSize: '1.2em', fontWeight: 700, margin: '0.4em 0' }}>{children}</h1>,
                h2: ({ children }) => <h2 style={{ fontSize: '1.1em', fontWeight: 700, margin: '0.4em 0' }}>{children}</h2>,
                h3: ({ children }) => <h3 style={{ fontSize: '1em', fontWeight: 700, margin: '0.3em 0' }}>{children}</h3>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources-toggle-wrapper">
            <button
              className="sources-toggle"
              onClick={() => setShowSources(!showSources)}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
              <svg
                className={`chevron ${showSources ? 'open' : ''}`}
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="6,9 12,15 18,9" />
              </svg>
            </button>
            {showSources && <Sources sources={message.sources} />}
          </div>
        )}
      </div>
    </div>
  );
}
