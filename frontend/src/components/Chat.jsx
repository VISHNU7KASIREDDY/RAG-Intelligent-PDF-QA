import React, { useState, useRef, useEffect } from 'react';
import { queryDocument } from '../api';
import Message from './Message';

export default function Chat({ hasDocuments }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading) return;

    const userMessage = { role: 'user', content: question };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Build chat history for context
      const chatHistory = messages.map(m => ({
        role: m.role,
        content: m.content,
      }));

      const result = await queryDocument(question, chatHistory);

      const aiMessage = {
        role: 'assistant',
        content: result.answer,
        sources: result.sources,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: err.response?.data?.detail || 'Sorry, something went wrong. Please try again.',
        sources: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Public method to add messages from outside (e.g. summary)
  Chat.addMessage = (message) => {
    setMessages((prev) => [...prev, message]);
  };

  return (
    <div className="chat-section">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="empty-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <h3>Ask anything about your documents</h3>
            <p>Upload a PDF and start asking questions. The AI will answer based only on the document content.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <Message key={i} message={msg} />
        ))}

        {loading && (
          <div className="message-row assistant-row">
            <div className="message-avatar ai-avatar">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V6a4 4 0 0 1 4-4z" />
                <path d="M18 14a6 6 0 0 0-12 0v4a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4z" />
              </svg>
            </div>
            <div className="message-bubble ai-bubble loading-bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <div className="chat-input-wrapper">
        <div className="chat-input-container">
          <textarea
            id="chat-input"
            className="chat-input"
            placeholder={hasDocuments ? "Ask a question about your documents..." : "Upload a PDF first to start asking questions..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!hasDocuments || loading}
            rows={1}
          />
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={!input.trim() || loading || !hasDocuments}
            title="Send message"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22,2 15,22 11,13 2,9" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
