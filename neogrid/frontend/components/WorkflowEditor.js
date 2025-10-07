import React, { useState, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  addEdge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { executeWorkflow } from '../utils/api';
import NodeCard from './NodeCard';

const initialNodes = [
  {
    id: '1',
    type: 'default',
    data: { label: 'Start' },
    position: { x: 250, y: 5 },
  },
];

const nodeTypes = {
  customNode: NodeCard,
};

const WorkflowEditor = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [nodeId, setNodeId] = useState(2);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addNode = () => {
    const newNode = {
      id: `${nodeId}`,
      type: 'customNode',
      data: {
        label: `Node ${nodeId}`,
        nodeType: 'text_analysis',
        params: { text: 'A default positive text' },
      },
      position: {
        x: Math.random() * 400,
        y: Math.random() * 400,
      },
    };
    setNodes((nds) => nds.concat(newNode));
    setNodeId(nodeId + 1);
  };

  const handleExecuteWorkflow = async () => {
    const workflow = {
      nodes: nodes
        .filter((node) => node.type === 'customNode')
        .map((node) => ({
          node_id: node.data.nodeType,
          params: node.data.params,
        })),
    };

    try {
      const result = await executeWorkflow(workflow);
      alert('Workflow Executed Successfully:\n' + JSON.stringify(result, null, 2));
    } catch (error) {
      alert('Workflow Execution Failed:\n' + error.message);
    }
  };

  return (
    <div style={{ height: '70vh', border: '1px solid #ccc', margin: '10px' }}>
      <div style={{ padding: '10px' }}>
        <button onClick={addNode} style={{ marginRight: '10px' }}>
          Add Text Analysis Node
        </button>
        <button onClick={handleExecuteWorkflow}>Execute Workflow</button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
};

export default WorkflowEditor;