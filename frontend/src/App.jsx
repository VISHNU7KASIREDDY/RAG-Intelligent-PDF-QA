import React, { useState, useRef } from 'react';
import Upload from './components/Upload';
import Chat from './components/Chat';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const chatRef = useRef(null);

  const handleUploadSuccess = (result) => {
    setDocuments((prev) => [...prev, result]);
  };

  const handleSummary = (result) => {
    // Add summary as an AI message in the chat
    if (Chat.addMessage) {
      Chat.addMessage({
        role: 'user',
        content: '📋 Summarize all uploaded documents',
      });
      Chat.addMessage({
        role: 'assistant',
        content: result.answer,
        sources: result.sources,
      });
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14,2 14,8 20,8" />
              <circle cx="12" cy="15" r="3" />
            </svg>
          </div>
          <div>
            <h1>PDF Q&A</h1>
            <p className="header-subtitle">Intelligent Document Assistant</p>
          </div>
        </div>
        <div className="header-badge">
          <span className="badge-dot" />
          Powered by Gemini AI
        </div>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <Upload
            onUploadSuccess={handleUploadSuccess}
            onSummary={handleSummary}
            documents={documents}
          />
        </aside>
        <section className="chat-area">
          <Chat ref={chatRef} hasDocuments={documents.length > 0} />
        </section>
      </main>
    </div>
  );
}
