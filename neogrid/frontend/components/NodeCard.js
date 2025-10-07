import React from 'react';
import { Handle } from 'reactflow';

const NodeCard = ({ data }) => {
  return (
    <div style={{
      border: '1px solid #777',
      padding: '10px',
      borderRadius: '5px',
      background: 'white',
      width: 150,
    }}>
      <Handle type="target" position="top" />
      <div>
        <strong>{data.label}</strong>
      </div>
      <div style={{ fontSize: '12px', marginTop: '5px' }}>
        <p>Type: {data.nodeType}</p>
        <p>Params: {JSON.stringify(data.params)}</p>
      </div>
      <Handle type="source" position="bottom" />
    </div>
  );
};

export default NodeCard;