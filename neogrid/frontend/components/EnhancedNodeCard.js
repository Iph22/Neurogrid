import React, { useState, useEffect } from 'react';
import { Handle } from 'reactflow';
import { testNode } from '../utils/api';

const EnhancedNodeCard = ({ id, data, selected }) => {
  const [testOutput, setTestOutput] = useState(null);
  const [testError, setTestError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showParams, setShowParams] = useState(false);
  const [nodeParams, setNodeParams] = useState(data.params || {});

  useEffect(() => {
    // Initialize default parameters based on node type
    const defaultParams = getDefaultParams(data.nodeType);
    setNodeParams(prev => ({ ...defaultParams, ...prev }));
  }, [data.nodeType]);

  const getDefaultParams = (nodeType) => {
    switch (nodeType) {
      case 'input_node':
        return { input_type: 'text' };
      case 'preprocessing_node':
        return { 
          operations: ['clean_text'], 
          filters: {} 
        };
      case 'postprocessing_node':
        return { 
          operations: ['format'], 
          aggregation_type: 'concat',
          confidence_threshold: 0.0,
          format_type: 'standard'
        };
      case 'output_node':
        return { 
          output_format: 'json', 
          include_summary: true 
        };
      // AI Model nodes - simpler parameter structure
      case 'summarizer':
      case 'image_caption':
      case 'code_analyzer':
      case 'sentiment':
        return { max_length: 100, temperature: 0.7 };
      default:
        return {};
    }
  };

  const handleInputChange = (e) => {
    if (data.onInputChange) {
      data.onInputChange(id, e.target.value);
    }
  };

  const handleParamChange = (paramName, value) => {
    const updatedParams = { ...nodeParams, [paramName]: value };
    setNodeParams(updatedParams);
    
    // Update node data with new parameters
    if (data.onParamChange) {
      data.onParamChange(id, updatedParams);
    }
  };

  const handleTestNode = async () => {
    setIsLoading(true);
    setTestError(null);
    setTestOutput(null);
    
    try {
      // Build test payload with current input and parameters
      const testPayload = {
        input: data.input || '',
        ...nodeParams
      };
      
      const response = await testNode(data.nodeType, testPayload.input);
      setTestOutput(response.data.output);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'An error occurred';
      setTestError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const renderParameterInputs = () => {
    const nodeType = data.nodeType;
    const registryParams = data.registryParams || [];
    
    // For AI model nodes, show simplified parameter controls
    if (data.category === 'ai_model') {
      return (
        <div style={{ marginTop: '10px' }}>
          <label style={{ display: 'block', fontSize: '11px', marginBottom: '5px' }}>
            Max Length:
            <input
              type="number"
              min="10"
              max="500"
              value={nodeParams.max_length || 100}
              onChange={(e) => handleParamChange('max_length', parseInt(e.target.value))}
              style={{ width: '100%', padding: '3px', fontSize: '11px' }}
            />
          </label>
          <label style={{ display: 'block', fontSize: '11px', marginTop: '5px' }}>
            Temperature:
            <input
              type="number"
              min="0"
              max="2"
              step="0.1"
              value={nodeParams.temperature || 0.7}
              onChange={(e) => handleParamChange('temperature', parseFloat(e.target.value))}
              style={{ width: '100%', padding: '3px', fontSize: '11px' }}
            />
          </label>
          {registryParams.length > 0 && (
            <div style={{ fontSize: '10px', marginTop: '5px', color: '#666' }}>
              <strong>Registry Params:</strong> {registryParams.join(', ')}
            </div>
          )}
        </div>
      );
    }
    
    if (nodeType === 'input_node') {
      return (
        <div style={{ marginTop: '10px' }}>
          <label style={{ display: 'block', fontSize: '11px', marginBottom: '5px' }}>
            Input Type:
            <select
              value={nodeParams.input_type || 'text'}
              onChange={(e) => handleParamChange('input_type', e.target.value)}
              style={{ width: '100%', padding: '3px', fontSize: '11px' }}
            >
              <option value="text">Text</option>
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="number">Number</option>
            </select>
          </label>
        </div>
      );
    }
    
    if (nodeType === 'preprocessing_node') {
      return (
        <div style={{ marginTop: '10px' }}>
          <label style={{ display: 'block', fontSize: '11px', marginBottom: '5px' }}>
            Operations:
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '3px' }}>
              {['clean_text', 'normalize_numbers', 'filter', 'remove_empty'].map(op => (
                <label key={op} style={{ fontSize: '10px', display: 'flex', alignItems: 'center' }}>
                  <input
                    type="checkbox"
                    checked={(nodeParams.operations || []).includes(op)}
                    onChange={(e) => {
                      const ops = nodeParams.operations || [];
                      const newOps = e.target.checked 
                        ? [...ops, op]
                        : ops.filter(o => o !== op);
                      handleParamChange('operations', newOps);
                    }}
                    style={{ marginRight: '3px' }}
                  />
                  {op}
                </label>
              ))}
            </div>
          </label>
        </div>
      );
    }
    
    if (nodeType === 'postprocessing_node') {
      return (
        <div style={{ marginTop: '10px' }}>
          <label style={{ display: 'block', fontSize: '11px', marginBottom: '3px' }}>
            Aggregation:
            <select
              value={nodeParams.aggregation_type || 'concat'}
              onChange={(e) => handleParamChange('aggregation_type', e.target.value)}
              style={{ width: '100%', padding: '2px', fontSize: '10px' }}
            >
              <option value="concat">Concatenate</option>
              <option value="average">Average</option>
              <option value="max_confidence">Max Confidence</option>
              <option value="merge">Merge</option>
            </select>
          </label>
          <label style={{ display: 'block', fontSize: '11px', marginTop: '5px' }}>
            Confidence Threshold:
            <input
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={nodeParams.confidence_threshold || 0}
              onChange={(e) => handleParamChange('confidence_threshold', parseFloat(e.target.value))}
              style={{ width: '100%', padding: '2px', fontSize: '10px' }}
            />
          </label>
        </div>
      );
    }
    
    if (nodeType === 'output_node') {
      return (
        <div style={{ marginTop: '10px' }}>
          <label style={{ display: 'block', fontSize: '11px', marginBottom: '3px' }}>
            Output Format:
            <select
              value={nodeParams.output_format || 'json'}
              onChange={(e) => handleParamChange('output_format', e.target.value)}
              style={{ width: '100%', padding: '2px', fontSize: '10px' }}
            >
              <option value="json">JSON</option>
              <option value="text">Text</option>
              <option value="csv">CSV</option>
              <option value="summary">Summary</option>
            </select>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', marginTop: '5px' }}>
            <input
              type="checkbox"
              checked={nodeParams.include_summary !== false}
              onChange={(e) => handleParamChange('include_summary', e.target.checked)}
              style={{ marginRight: '5px' }}
            />
            Include Summary
          </label>
        </div>
      );
    }
    
    return null;
  };

  const getNodeColor = () => {
    const category = data.category || 'ai_model';
    switch (category) {
      case 'workflow': return '#4CAF50';
      case 'ai_model': return '#2196F3';
      default: return '#555';
    }
  };

  const resultBoxStyle = {
    marginTop: '10px',
    padding: '8px',
    borderRadius: '4px',
    maxHeight: '150px',
    overflowY: 'auto',
    fontSize: '10px',
    wordBreak: 'break-all',
    whiteSpace: 'pre-wrap',
  };

  return (
    <div style={{
      border: `2px solid ${getNodeColor()}`,
      padding: '12px',
      borderRadius: '8px',
      background: selected ? '#f0f8ff' : '#fdfdfd',
      width: 280,
      fontSize: '12px',
      boxShadow: selected ? '0 0 10px rgba(33, 150, 243, 0.3)' : 'none',
      transform: selected ? 'scale(1.02)' : 'scale(1)',
      transition: 'all 0.2s ease'
    }}>
      <Handle type="target" position="top" style={{ background: getNodeColor() }} />
      
      <div style={{ 
        fontWeight: 'bold', 
        marginBottom: '8px', 
        color: getNodeColor(),
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span>{data.label}</span>
        <div style={{ display: 'flex', gap: '3px' }}>
          <button
            onClick={() => setShowParams(!showParams)}
            style={{
              background: 'none',
              border: '1px solid #ccc',
              borderRadius: '3px',
              padding: '2px 6px',
              fontSize: '10px',
              cursor: 'pointer'
            }}
          >
            {showParams ? '−' : '+'}
          </button>
          {data.onDelete && (
            <button
              onClick={() => data.onDelete(id)}
              style={{
                background: '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                padding: '2px 6px',
                fontSize: '10px',
                cursor: 'pointer'
              }}
              title="Delete Node"
            >
              ×
            </button>
          )}
        </div>
      </div>

      <label style={{ display: 'block', fontSize: '11px', color: '#333' }}>
        Input:
        <textarea
          value={data.input || ''}
          onChange={handleInputChange}
          style={{ 
            width: '100%', 
            boxSizing: 'border-box', 
            minHeight: '40px', 
            marginTop: '3px', 
            padding: '4px', 
            border: '1px solid #ccc', 
            borderRadius: '3px',
            fontSize: '11px'
          }}
          rows={2}
        />
      </label>

      {showParams && renderParameterInputs()}

      <button 
        onClick={handleTestNode} 
        disabled={isLoading} 
        style={{ 
          marginTop: '8px', 
          width: '100%', 
          padding: '6px', 
          background: getNodeColor(), 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px', 
          cursor: 'pointer',
          fontSize: '11px'
        }}
      >
        {isLoading ? 'Testing...' : 'Test Node'}
      </button>

      {/* Test results */}
      {(testOutput || testError) && (
        <div style={{
          ...resultBoxStyle, 
          background: testError ? '#fbe9e7' : '#e8f5e9', 
          border: `1px solid ${testError ? '#ffcdd2' : '#c8e6c9'}`
        }}>
          <strong>Test Result:</strong>
          {testError ? (
            <pre style={{ color: '#c62828' }}>{JSON.stringify(testError, null, 2)}</pre>
          ) : (
            <pre style={{ color: '#2e7d32' }}>{JSON.stringify(testOutput, null, 2)}</pre>
          )}
        </div>
      )}

      {/* Workflow results */}
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

      <Handle type="source" position="bottom" style={{ background: getNodeColor() }} />
    </div>
  );
};

export default EnhancedNodeCard;
