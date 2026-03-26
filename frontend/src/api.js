import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 120000,
});

export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function queryDocument(question, chatHistory = []) {
  const response = await api.post('/query', {
    question,
    chat_history: chatHistory,
  });
  return response.data;
}

export async function summarizeDocuments() {
  const response = await api.post('/summarize');
  return response.data;
}

export async function clearDocuments() {
  const response = await api.post('/clear');
  return response.data;
}
