"""
FunctionContext - Main SDK object providing all helper methods for function execution.
"""

import logging
from typing import Any, Optional, Callable, Dict
from .types import Items
from .resources import ResourceRegistry


class FunctionContext:
    """
    Main SDK object providing all helper methods for function execution.
    
    Functions receive a single FunctionContext instance that provides:
    - Input data access (port-based)
    - Parameter access (static per step)
    - Multi-port output emission
    - Logging
    - Resource registry access
    - Execution context information
    """
    
    def __init__(
        self,
        # Input data (port -> Items mapping)
        input_data: Dict[str, Items],
        # Static parameters (from function.yaml, resolved expressions)
        parameters: Dict[str, Any],
        # Execution context
        execution_id: str,
        workflow_id: str,
        node_id: str,
        step_id: Optional[str] = None,
        # Node definition
        node: Optional[dict] = None,
        # Function definition
        function: Optional[Any] = None,
        # Logger
        logger: Optional[logging.Logger] = None,
        # Resource registry factory
        resource_registry_factory: Optional[Callable] = None,
        # Credentials access
        credentials: Optional[Dict[str, str]] = None,
        # Continue on fail setting
        continue_on_fail: bool = False,
        # Additional context
        context: Optional[Dict] = None,
    ):
        self._input_data = input_data or {}
        self._parameters = parameters or {}
        self._execution_id = execution_id
        self._workflow_id = workflow_id
        self._node_id = node_id
        self._step_id = step_id or node_id
        self._node = node or {}
        self._function = function
        self._credentials = credentials or {}
        self._continue_on_fail = continue_on_fail
        self._context = context or {}
        
        # Logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(f"megaflow.function.{node_id}")
        
        # Resource registry (lazy loaded)
        self._resource_registry = None
        self._resource_registry_factory = resource_registry_factory
        
        # Multi-port output tracking
        self._emitted_outputs: Dict[str, Items] = {}
    
    def get_input_data(self, port: str = "main") -> Items:
        """
        Get input data for a specific port.
        
        Args:
            port: Port name (default: "main")
        
        Returns:
            Items: Array of objects (List[Dict[str, Any]])
        """
        return self._input_data.get(port, [])
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """
        Get a static parameter value (from function.yaml, resolved expressions).
        
        Args:
            name: Parameter name
            default: Default value if parameter not found
        
        Returns:
            Parameter value
        """
        return self._parameters.get(name, default)
    
    def emit(self, port: str, items: Items) -> None:
        """
        Emit output to a specific port (for multi-port outputs).
        
        Args:
            port: Output port name
            items: Items to emit (array of objects)
        """
        if not isinstance(items, list):
            raise TypeError(f"emit() expects Items (list), got {type(items)}")
        self._emitted_outputs[port] = items
    
    def get_emitted_outputs(self) -> Dict[str, Items]:
        """
        Get all emitted outputs (for multi-port functions).
        
        Returns:
            Dictionary mapping port names to Items
        """
        return self._emitted_outputs.copy()
    
    def get_execution_id(self) -> str:
        """Get execution instance ID."""
        return self._execution_id
    
    def get_workflow_id(self) -> str:
        """Get workflow ID."""
        return self._workflow_id
    
    def get_node_id(self) -> str:
        """Get node ID."""
        return self._node_id
    
    def get_step_id(self) -> str:
        """Get step ID (usually same as node_id)."""
        return self._step_id
    
    def get_node(self) -> Dict:
        """Get node definition dictionary."""
        return self._node
    
    def get_context(self) -> Dict:
        """Get additional context dictionary."""
        return self._context.copy()
    
    def get_credential(self, name: str) -> Optional[str]:
        """
        Get a credential value by name.
        
        Args:
            name: Credential name
        
        Returns:
            Credential value or None if not found
        """
        return self._credentials.get(name)
    
    def continue_on_fail(self) -> bool:
        """
        Check if function should continue on failure.
        
        Returns:
            True if errors should be handled gracefully, False to raise
        """
        return self._continue_on_fail
    
    def resources(self) -> ResourceRegistry:
        """
        Get resource registry for accessing typed resource handles.
        
        Returns:
            ResourceRegistry instance
        """
        if self._resource_registry is None:
            if self._resource_registry_factory:
                self._resource_registry = self._resource_registry_factory(
                    function=self._function,
                    context=self
                )
            else:
                # Default empty registry
                self._resource_registry = ResourceRegistry(function=self._function, context=self)
        return self._resource_registry
    
    def get_data_store(self):
        """
        Advanced: Get data store for large data handling.
        Not commonly used by function developers.
        """
        # TODO: Implement data store access if needed
        raise NotImplementedError("Data store access not yet implemented")

