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
import NodeCard from './NodeCard';

const initialNodes = [];

const nodeTypes = {
  customNode: NodeCard,
};

const WorkflowEditor = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [nodeRegistry, setNodeRegistry] = useState([]);
  const [nodeId, setNodeId] = useState(1);

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
      } catch (error) {
        console.error("Failed to fetch node registry:", error);
      }
    };
    fetchRegistry();
  }, []);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

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

  const addNode = (nodeType, label) => {
    const newNode = {
      id: `${nodeId}`,
      type: 'customNode',
      data: {
        label: label,
        nodeType: nodeType,
        input: '',
        onInputChange: onNodeInputChange,
      },
      position: {
        x: Math.random() * 400,
        y: Math.random() * 200,
      },
    };
    setNodes((nds) => nds.concat(newNode));
    setNodeId(nodeId + 1);
  };

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
        }
    }));
    setNodes(loadedNodes);
    setEdges(workflow.config_json.edges || []);
    setSelectedWorkflowId(workflow.id);
  };

  const AuthForm = () => (
    <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px', marginBottom: '10px' }}>
      <h3>User Authentication</h3>
      <form>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <button onClick={handleLogin} style={{ marginRight: '5px', padding: '5px 10px' }}>Login</button>
        <button onClick={handleRegister} style={{ padding: '5px 10px' }}>Register</button>
      </form>
      {authError && <p style={{ color: 'red', marginTop: '10px' }}>{authError}</p>}
    </div>
  );

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
                {nodeRegistry.map((node) => (
                  <button key={node.id} onClick={() => addNode(node.id, node.label)} style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '10px' }}>
                    {node.label}
                  </button>
                ))}
                <hr style={{ margin: '20px 0' }}/>
                <WorkflowControls />
            </>
        )}
      </div>
      <div style={{ flex: 1, border: '1px solid #ccc', borderRadius: '5px' }}>
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
    </div>
  );
};

export default WorkflowEditor;