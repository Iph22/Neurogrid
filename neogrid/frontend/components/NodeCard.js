import React, { useState, useEffect } from 'react';
import { Handle } from 'reactflow';
import { testNode } from '../utils/api';

const NodeCard = ({ id, data }) => {
  const [testOutput, setTestOutput] = useState(null);
  const [testError, setTestError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    if (data.onInputChange) {
      data.onInputChange(id, e.target.value);
    }
  };

  const handleTestNode = async () => {
    setIsLoading(true);
    setTestError(null);
    setTestOutput(null);
    try {
      const response = await testNode(data.nodeType, data.input);
      setTestOutput(response.data.output);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'An error occurred';
      setTestError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const resultBoxStyle = {
    marginTop: '10px',
    padding: '8px',
    borderRadius: '4px',
    maxHeight: '200px',
    overflowY: 'auto',
    fontSize: '11px',
    wordBreak: 'break-all',
    whiteSpace: 'pre-wrap',
  };

  return (
    <div style={{
      border: '2px solid #555',
      padding: '15px',
      borderRadius: '8px',
      background: '#fdfdfd',
      width: 300,
    }}>
      <Handle type="target" position="top" style={{ background: '#555' }} />
      <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>{data.label}</div>

      <label style={{ display: 'block', fontSize: '12px', color: '#333' }}>
        Input:
        <textarea
          value={data.input || ''}
          onChange={handleInputChange}
          style={{ width: '100%', boxSizing: 'border-box', minHeight: '50px', marginTop: '5px', padding: '5px', border: '1px solid #ccc', borderRadius: '4px' }}
          rows={3}
        />
      </label>

      <button onClick={handleTestNode} disabled={isLoading} style={{ marginTop: '10px', width: '100%', padding: '8px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
        {isLoading ? 'Testing...' : 'Test Node'}
      </button>

      {/* Display for single node test results */}
      {(testOutput || testError) && (
        <div style={{...resultBoxStyle, background: testError ? '#fbe9e7' : '#e8f5e9', border: `1px solid ${testError ? '#ffcdd2' : '#c8e6c9'}`}}>
          <strong>Test Result:</strong>
          {testError ? (
            <pre style={{ color: '#c62828' }}>{JSON.stringify(testError, null, 2)}</pre>
          ) : (
            <pre style={{ color: '#2e7d32' }}>{JSON.stringify(testOutput, null, 2)}</pre>
          )}
        </div>
      )}

      {/* Display for workflow execution results */}
      {data.workflowResult && (
        <div style={{...resultBoxStyle, background: '#e3f2fd', border: '1px solid #bbdefb'}}>
          <strong>Workflow Output:</strong>
          {data.workflowResult.error ? (
              <pre style={{ color: 'red' }}>{JSON.stringify(data.workflowResult.error, null, 2)}</pre>
          ) : (
              <pre style={{ color: 'navy' }}>{JSON.stringify(data.workflowResult.output, null, 2)}</pre>
          )}
        </div>
      )}

      <Handle type="source" position="bottom" style={{ background: '#555' }} />
    </div>
  );
};

export default NodeCard;