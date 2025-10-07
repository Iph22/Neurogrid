import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Executes a workflow by sending it to the backend.
 * @param {object} workflow - The workflow object to execute.
 * @returns {Promise<object>} - The result from the backend.
 */
export const executeWorkflow = async (workflow) => {
  try {
    // We don't need a full request envelope here since the backend endpoint
    // for workflow execution has its own model.
    const response = await apiClient.post('/workflow/execute', workflow);
    return response.data;
  } catch (error) {
    console.error('Error executing workflow:', error);
    // Propagate a more informative error message
    throw new Error(error.response?.data?.detail || 'Failed to connect to the backend.');
  }
};

/**
 * A utility function to format payloads into the standard request envelope.
 * This would be used if calling individual nodes directly from the frontend.
 * @param {object} payload - The data payload.
 * @returns {object} - The formatted request envelope.
 */
export const createRequestEnvelope = (payload) => {
  return {
    id: uuidv4(),
    payload: payload,
    meta: {
      timestamp: new Date().toISOString(),
    },
  };
};