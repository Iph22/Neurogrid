import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  addEdge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  getNodeRegistry,
  executeWorkflow,
  createWorkflow,
  getUserWorkflows,
  loginUser,
  registerUser,
  setAuthToken,
} from '../utils/api';
import EnhancedNodeCard from './EnhancedNodeCard';

const initialNodes = [];

const nodeTypes = {
  customNode: EnhancedNodeCard,
};

const WorkflowEditor = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [nodeRegistry, setNodeRegistry] = useState([]);
  const [nodeId, setNodeId] = useState(1);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showConfigPanel, setShowConfigPanel] = useState(false);

  // Auth and Workflow state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [userWorkflows, setUserWorkflows] = useState([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(null);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [authError, setAuthError] = useState('');


  useEffect(() => {
    // Fetch the node registry when the component mounts
    const fetchRegistry = async () => {
      try {
        const response = await getNodeRegistry();
        setNodeRegistry(response.data.nodes || []);
        console.log("Node registry loaded successfully:", response.data);
      } catch (error) {
        console.error("Failed to fetch node registry:", {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          url: error.config?.url,
          method: error.config?.method
        });
        // Set empty array as fallback to prevent UI issues
        setNodeRegistry([]);
      }
    };
    fetchRegistry();
  }, []);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
    setShowConfigPanel(true);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    setShowConfigPanel(false);
  }, []);

  const onNodeInputChange = (nodeId, inputValue) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              input: inputValue,
            },
          };
        }
        return node;
      })
    );
  };

  const onNodeParamChange = (nodeId, params) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              params: params,
            },
          };
        }
        return node;
      })
    );
  };

  const addNode = (nodeType, label, category) => {
    // Find node metadata from registry
    const nodeMetadata = nodeRegistry.find(n => n.id === nodeType) || {};
    
    const newNode = {
      id: `${nodeId}`,
      type: 'customNode',
      data: {
        label: label,
        nodeType: nodeType,
        category: category,
        description: nodeMetadata.description || '',
        registryParams: nodeMetadata.params || [],
        input: '',
        params: {},
        onInputChange: onNodeInputChange,
        onParamChange: onNodeParamChange,
        onDelete: deleteNode,
      },
      position: {
        x: Math.random() * 400,
        y: Math.random() * 200,
      },
    };
    setNodes((nds) => nds.concat(newNode));
    setNodeId(nodeId + 1);
  };

  const deleteNode = useCallback((nodeId) => {
    setNodes((nds) => nds.filter(node => node.id !== nodeId));
    setEdges((eds) => eds.filter(edge => edge.source !== nodeId && edge.target !== nodeId));
    if (selectedNode && selectedNode.id === nodeId) {
      setSelectedNode(null);
      setShowConfigPanel(false);
    }
  }, [selectedNode]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const response = await loginUser(username, password);
      setAuthToken(response.data.access_token);
      setIsAuthenticated(true);
      fetchUserWorkflows();
    } catch (error) {
      setAuthError('Login failed. Please check your credentials.');
      console.error(error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      await registerUser(username, password);
      // Automatically log in after successful registration
      await handleLogin(e);
    } catch (error) {
        setAuthError('Registration failed. Username might be taken.');
        console.error(error);
    }
  };

  const fetchUserWorkflows = async () => {
    try {
        const response = await getUserWorkflows();
        setUserWorkflows(response.data);
    } catch (error) {
        console.error("Failed to fetch workflows:", error);
    }
  };

  const handleSaveWorkflow = async () => {
    if (!newWorkflowName) {
        alert("Please enter a name for the workflow.");
        return;
    }
    const workflowConfig = {
        nodes: nodes.map(n => ({ id: n.id, type: n.type, data: n.data, position: n.position })),
        edges,
    };
    try {
        await createWorkflow(newWorkflowName, workflowConfig);
        setNewWorkflowName('');
        fetchUserWorkflows(); // Refresh the list of workflows
        alert("Workflow saved successfully!");
    } catch (error) {
        alert("Failed to save workflow.");
        console.error(error);
    }
  };

  const handleExecuteWorkflow = async () => {
    if (!selectedWorkflowId) {
        alert("Please select a workflow to run.");
        return;
    }

    // Collect inputs from all nodes
    const inputs = nodes.reduce((acc, node) => {
        acc[node.id] = node.data.input;
        return acc;
    }, {});

    try {
      const response = await executeWorkflow(selectedWorkflowId, inputs);
      const results = response.data.output_json;

      // Update nodes with their results
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: {
            ...node.data,
            workflowResult: results[node.id] || null,
          },
        }))
      );
      alert('Workflow Executed Successfully!');
    } catch (error) {
      alert('Workflow Execution Failed:\n' + (error.response?.data?.detail || error.message));
    }
  };

  const loadWorkflow = (workflow) => {
    const loadedNodes = workflow.config_json.nodes.map(node => ({
        ...node,
        data: {
            ...node.data,
            onInputChange: onNodeInputChange,
            onParamChange: onNodeParamChange,
        }
    }));
    setNodes(loadedNodes);
    setEdges(workflow.config_json.edges || []);
    setSelectedWorkflowId(workflow.id);
  };

  const AuthForm = React.memo(() => (
    <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px', marginBottom: '10px' }}>
      <h3>User Authentication</h3>
      <form onSubmit={(e) => e.preventDefault()}>
        <div style={{ marginBottom: '10px' }}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ width: '100%', padding: '8px', marginBottom: '5px' }}
            required
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: '100%', padding: '8px', marginBottom: '5px' }}
            required
          />
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          <button
            type="button"
            onClick={handleLogin}
            style={{ flex: 1, padding: '8px 10px', cursor: 'pointer' }}
          >
            Login
          </button>
          <button
            type="button"
            onClick={handleRegister}
            style={{ flex: 1, padding: '8px 10px', cursor: 'pointer' }}
          >
            Register
          </button>
        </div>
      </form>
      {authError && <p style={{ color: 'red', marginTop: '10px' }}>{authError}</p>}
    </div>
  ));

  const WorkflowControls = () => (
    <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <h3>Workflow Management</h3>
        <div style={{ marginBottom: '10px' }}>
            <input
                type="text"
                placeholder="New Workflow Name"
                value={newWorkflowName}
                onChange={(e) => setNewWorkflowName(e.target.value)}
                style={{ marginRight: '10px', padding: '5px' }}
            />
            <button onClick={handleSaveWorkflow} style={{ padding: '5px 10px' }}>Save Current Workflow</button>
        </div>
        <div style={{ marginBottom: '10px' }}>
            <select
                onChange={(e) => {
                    const wf = userWorkflows.find(w => w.id === parseInt(e.target.value));
                    if (wf) loadWorkflow(wf);
                }}
                value={selectedWorkflowId || ''}
                style={{ marginRight: '10px', padding: '5px' }}
            >
                <option value="">Select a workflow to load</option>
                {userWorkflows.map(wf => (
                    <option key={wf.id} value={wf.id}>{wf.name}</option>
                ))}
            </select>
            <button onClick={handleExecuteWorkflow} style={{ padding: '5px 10px' }}>Run Selected Workflow</button>
        </div>
    </div>
  );

  return (
    <div style={{ display: 'flex', height: '85vh', gap: '10px', padding: '10px' }}>
      <div style={{ width: '250px', border: '1px solid #ccc', padding: '10px', borderRadius: '5px', background: '#f9f9f9' }}>
        {!isAuthenticated ? (
            <AuthForm />
        ) : (
            <>
                <h3>Add Nodes</h3>
                
                {/* Workflow Nodes */}
                <div style={{ marginBottom: '15px' }}>
                  <h4 style={{ margin: '0 0 8px 0', color: '#4CAF50', fontSize: '14px' }}>Workflow Nodes</h4>
                  {nodeRegistry.filter(node => node.category === 'workflow').map((node) => (
                    <button 
                      key={node.id} 
                      onClick={() => addNode(node.id, node.label, node.category)} 
                      style={{ 
                        display: 'block', 
                        width: '100%', 
                        marginBottom: '5px', 
                        padding: '8px', 
                        backgroundColor: '#E8F5E8',
                        border: '1px solid #4CAF50',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      {node.label}
                    </button>
                  ))}
                </div>

                {/* AI Model Nodes */}
                <div style={{ marginBottom: '15px' }}>
                  <h4 style={{ margin: '0 0 8px 0', color: '#2196F3', fontSize: '14px' }}>AI Model Nodes</h4>
                  {nodeRegistry.filter(node => node.category === 'ai_model').map((node) => (
                    <button 
                      key={node.id} 
                      onClick={() => addNode(node.id, node.label, node.category)} 
                      style={{ 
                        display: 'block', 
                        width: '100%', 
                        marginBottom: '5px', 
                        padding: '8px', 
                        backgroundColor: '#E3F2FD',
                        border: '1px solid #2196F3',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      {node.label}
                    </button>
                  ))}
                </div>

                <hr style={{ margin: '20px 0' }}/>
                <WorkflowControls />
                
                {/* Node Configuration Panel */}
                {showConfigPanel && selectedNode && (
                  <div style={{ 
                    marginTop: '20px', 
                    border: '1px solid #ccc', 
                    padding: '15px', 
                    borderRadius: '5px',
                    background: '#f5f5f5'
                  }}>
                    <h3 style={{ margin: '0 0 10px 0', fontSize: '14px' }}>Configure Node</h3>
                    <div style={{ fontSize: '12px', marginBottom: '10px' }}>
                      <strong>Type:</strong> {selectedNode.data.label}<br/>
                      <strong>ID:</strong> {selectedNode.id}<br/>
                      {selectedNode.data.description && (
                        <><strong>Description:</strong> {selectedNode.data.description}<br/></>
                      )}
                    </div>
                    <button 
                      onClick={() => deleteNode(selectedNode.id)}
                      style={{
                        background: '#f44336',
                        color: 'white',
                        border: 'none',
                        padding: '5px 10px',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '11px'
                      }}
                    >
                      Delete Node
                    </button>
                  </div>
                )}
            </>
        )}
      </div>
      <div style={{ flex: 1, border: '1px solid #ccc', borderRadius: '5px' }}>
        <ReactFlow
          nodes={nodes.map(node => ({
            ...node,
            selected: selectedNode && selectedNode.id === node.id
          }))}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          nodesDraggable={true}
          nodesConnectable={true}
          elementsSelectable={true}
        >
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  );
};

export default WorkflowEditor;