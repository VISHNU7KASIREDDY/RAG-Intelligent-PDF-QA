import React, { useCallback, useState } from 'react';
import { uploadPDF, summarizeDocuments } from '../api';

export default function Upload({ onUploadSuccess, onSummary, documents }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [summarizing, setSummarizing] = useState(false);

  const handleDrop = useCallback(async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    for (const file of files) {
      if (file.type === 'application/pdf') {
        await handleUpload(file);
      } else {
        setError('Only PDF files are accepted.');
      }
    }
  }, []);

  const handleFileInput = async (e) => {
    const files = Array.from(e.target.files);
    for (const file of files) {
      await handleUpload(file);
    }
    e.target.value = '';
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setError('');
    try {
      const result = await uploadPDF(file);
      onUploadSuccess(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleSummarize = async () => {
    setSummarizing(true);
    try {
      const result = await summarizeDocuments();
      onSummary(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Summarization failed.');
    } finally {
      setSummarizing(false);
    }
  };

  return (
    <div className="upload-section">
      <div className="upload-header">
        <div className="upload-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14,2 14,8 20,8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10,9 9,9 8,9" />
          </svg>
        </div>
        <h2>Documents</h2>
      </div>

      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && document.getElementById('file-input').click()}
      >
        {uploading ? (
          <div className="upload-loading">
            <div className="spinner" />
            <p>Processing PDF...</p>
          </div>
        ) : (
          <>
            <svg className="upload-cloud-icon" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17,8 12,3 7,8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p>Drop PDF here or <span className="browse-link">browse</span></p>
            <span className="drop-hint">Supports multiple PDF files</span>
          </>
        )}
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
      </div>

      {error && <div className="upload-error">{error}</div>}

      {documents.length > 0 && (
        <div className="document-list">
          <h3>Uploaded ({documents.length})</h3>
          {documents.map((doc, i) => (
            <div key={i} className="document-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14,2 14,8 20,8" />
              </svg>
              <div className="doc-info">
                <span className="doc-name">{doc.filename}</span>
                <span className="doc-chunks">{doc.num_chunks} chunks</span>
              </div>
            </div>
          ))}
          <button
            className="summarize-btn"
            onClick={handleSummarize}
            disabled={summarizing}
          >
            {summarizing ? (
              <><div className="spinner-sm" /> Summarizing...</>
            ) : (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="21" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="21" y1="18" x2="3" y2="18"/></svg> Summarize All</>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
