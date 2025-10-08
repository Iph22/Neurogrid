"""
Enhanced Workflow Execution Engine
Handles sequential node processing with proper data passing between connected nodes.
"""

import httpx
import json
from typing import Dict, List, Any, Tuple
from fastapi import HTTPException
import asyncio

class WorkflowEngine:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def build_execution_graph(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, List[str]]:
        """
        Build a dependency graph from workflow nodes and edges.
        Returns a dictionary mapping node_id -> list of dependent node_ids
        """
        graph = {node["id"]: [] for node in nodes}
        
        # Build adjacency list based on edges
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                graph[source].append(target)
        
        return graph
    
    def topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Perform topological sort to determine execution order.
        Returns nodes in execution order.
        """
        # Calculate in-degrees
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node in in_degree if in_degree[node] == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            # Remove edges from current node
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(execution_order) != len(graph):
            raise ValueError("Workflow contains cycles - cannot execute")
        
        return execution_order
    
    def get_node_inputs(self, node_id: str, node_data: Dict, results: Dict[str, Any], 
                       edges: List[Dict], user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine inputs for a node based on connections and user inputs.
        """
        # Find incoming edges to this node
        incoming_edges = [edge for edge in edges if edge.get("target") == node_id]
        
        if not incoming_edges:
            # No incoming connections - use user input or node's default input
            user_input = user_inputs.get(node_id, node_data.get("input", ""))
            return {"input": user_input}
        
        # Has incoming connections - use output from source nodes
        if len(incoming_edges) == 1:
            # Single input
            source_id = incoming_edges[0]["source"]
            source_result = results.get(source_id, {})
            
            if isinstance(source_result, dict) and "output" in source_result:
                return {"input": source_result["output"]}
            else:
                return {"input": source_result}
        
        else:
            # Multiple inputs - aggregate them
            inputs = []
            for edge in incoming_edges:
                source_id = edge["source"]
                source_result = results.get(source_id, {})
                
                if isinstance(source_result, dict) and "output" in source_result:
                    inputs.append(source_result["output"])
                else:
                    inputs.append(source_result)
            
            return {"input": inputs}
    
    def merge_node_parameters(self, node_data: Dict, computed_inputs: Dict) -> Dict:
        """
        Merge computed inputs with node-specific parameters.
        """
        payload = computed_inputs.copy()
        
        # Add node-specific parameters
        node_params = node_data.get("params", {})
        if isinstance(node_params, dict):
            payload.update(node_params)
        
        # Handle special parameter cases
        node_type = node_data.get("nodeType", "")
        
        if node_type == "input_node":
            payload["input_type"] = node_params.get("input_type", "text")
        
        elif node_type == "preprocessing_node":
            payload["operations"] = node_params.get("operations", ["clean_text"])
            payload["filters"] = node_params.get("filters", {})
        
        elif node_type == "postprocessing_node":
            payload["operations"] = node_params.get("operations", ["format"])
            payload["aggregation_type"] = node_params.get("aggregation_type", "concat")
            payload["confidence_threshold"] = node_params.get("confidence_threshold", 0.0)
            payload["format_type"] = node_params.get("format_type", "standard")
        
        elif node_type == "output_node":
            payload["output_format"] = node_params.get("output_format", "json")
            payload["include_summary"] = node_params.get("include_summary", True)
        
        return payload
    
    async def execute_node(self, node: Dict, payload: Dict, client: httpx.AsyncClient) -> Dict:
        """
        Execute a single node with the given payload.
        """
        node_type = node["data"]["nodeType"]
        node_url = f"{self.base_url}/nodes/{node_type}/infer"
        
        try:
            response = await client.post(node_url, json=payload, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
            # Add execution metadata
            result["_execution_metadata"] = {
                "node_id": node["id"],
                "node_type": node_type,
                "status": "success"
            }
            
            return result
            
        except Exception as e:
            error_result = {
                "error": f"Error executing node '{node_type}' ({node['id']}): {str(e)}",
                "_execution_metadata": {
                    "node_id": node["id"],
                    "node_type": node_type,
                    "status": "error"
                }
            }
            return error_result
    
    async def execute_workflow(self, nodes: List[Dict], edges: List[Dict], 
                             user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the entire workflow with proper sequential processing and data passing.
        """
        try:
            # Build execution graph and determine order
            graph = self.build_execution_graph(nodes, edges)
            execution_order = self.topological_sort(graph)
            
            # Create node lookup
            node_lookup = {node["id"]: node for node in nodes}
            
            results = {}
            
            async with httpx.AsyncClient() as client:
                for node_id in execution_order:
                    if node_id not in node_lookup:
                        continue
                    
                    node = node_lookup[node_id]
                    
                    # Determine inputs for this node
                    computed_inputs = self.get_node_inputs(
                        node_id, node["data"], results, edges, user_inputs
                    )
                    
                    # Merge with node parameters
                    payload = self.merge_node_parameters(node["data"], computed_inputs)
                    
                    # Execute the node
                    result = await self.execute_node(node, payload, client)
                    results[node_id] = result
                    
                    # Stop execution if there's an error (optional - can be configured)
                    if isinstance(result, dict) and result.get("error"):
                        print(f"Error in node {node_id}: {result['error']}")
                        # Continue execution for now, but mark the error
            
            return results
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

# Global workflow engine instance
workflow_engine = WorkflowEngine()
