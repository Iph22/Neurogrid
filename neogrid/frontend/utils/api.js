import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to set the auth token for subsequent requests
export const setAuthToken = (token) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
};

// --- Auth Endpoints ---
export const registerUser = (username, password) => {
  return apiClient.post('/auth/register', { username, password });
};

export const loginUser = (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  return apiClient.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

// --- Node Endpoints ---
export const getNodeRegistry = () => {
  return apiClient.get('/nodes/registry');
};

export const testNode = (nodeType, input) => {
  return apiClient.post(`/nodes/${nodeType}/infer`, { input });
};

// --- Workflow Endpoints ---
export const createWorkflow = (name, config) => {
  return apiClient.post('/workflows/', { name, config_json: config });
};

export const getUserWorkflows = () => {
  return apiClient.get('/workflows/');
};

export const executeWorkflow = (workflowId, inputs) => {
  return apiClient.post(`/workflow/${workflowId}/execute`, { inputs });
};