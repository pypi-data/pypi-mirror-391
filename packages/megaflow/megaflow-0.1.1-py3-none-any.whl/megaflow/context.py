"""
FunctionContext - Main SDK object providing all helper methods for function execution.
"""

import logging
from types import SimpleNamespace
from typing import Any, Optional, Callable, Dict
from .types import Items
from .resources import ResourceRegistry


class FunctionContext:
    """
    Main SDK object providing all helper methods for function execution.

    Functions receive a single FunctionContext instance that provides:
    - Input data access (port-based)        →  ctx.items (main) / ctx.get_input_data(port)
    - Parameter access (static per step)    →  ctx.params / ctx.get_parameter(name)
    - Multi-port output emission            →  ctx.emit(port, items) / ctx.emit_main(items)
    - Logging                               →  ctx.log (info/debug/warn/error)
    - Resource registry access              →  ctx.resource(kind, name)
    - Execution context information         →  ctx.execution_id, ctx.step_id, ...
    """

    def __init__(
        self,
        # Input data (port -> Items mapping)
        input_data: Optional[Dict[str, Items]] = None,
        # Static parameters (from function.yaml, resolved expressions)
        parameters: Optional[Dict[str, Any]] = None,
        # Execution context
        execution_id: str = "",
        workflow_id: str = "",
        node_id: str = "",
        step_id: Optional[str] = None,
        # Node definition
        node: Optional[dict] = None,
        # Function definition
        function: Optional[Any] = None,
        # Logger (python logger)
        logger: Optional[logging.Logger] = None,
        # Resource registry factory
        resource_registry_factory: Optional[Callable] = None,
        # Credentials access
        credentials: Optional[Dict[str, str]] = None,
        # Continue on fail setting
        continue_on_fail: bool = False,
        # Additional context
        context: Optional[Dict] = None,
        # ---- Back-compat / DX aliases ----
        items: Optional[Items] = None,             # alias for main port input
        params: Optional[Dict[str, Any]] = None,   # alias for parameters
        policy: Optional[Dict[str, Any]] = None,   # runtime policy (timeouts, retries, etc.)
        **kwargs,                                   # future-proof
    ):
        # --- Inputs ---
        _input_data = input_data or {}
        if items is not None:
            # explicit items alias wins for main port
            _input_data = dict(_input_data)
            _input_data.setdefault("main", items)
        self._input_data: Dict[str, Items] = _input_data

        # --- Params ---
        _parameters = parameters if parameters is not None else (params or {})
        self._parameters: Dict[str, Any] = _parameters
        self.params = SimpleNamespace(**_parameters)  # attr-style access

        # --- Policy (read-only view for function code) ---
        _policy = policy or {}
        self.policy = SimpleNamespace(**_policy)

        # --- IDs & defs ---
        self._execution_id = execution_id
        self._workflow_id = workflow_id
        self._node_id = node_id
        self._step_id = step_id or node_id
        self._node = node or {}
        self._function = function
        self._credentials = credentials or {}
        self._continue_on_fail = continue_on_fail
        self._context = context or {}

        # --- Logger facade ---
        self.logger = logger or logging.getLogger(f"megaflow.function.{self._node_id}")
        self.log = _LoggerFacade(self.logger)

        # --- Resource registry (lazy) ---
        self._resource_registry = None
        self._resource_registry_factory = resource_registry_factory

        # --- Outputs (by port) ---
        self._emitted_outputs: Dict[str, Items] = {}

        # # Optional: HTTP helper (uncomment when you add it)
        # from .http import HttpClient
        # self.http = HttpClient({"timeout_ms": getattr(self.policy, "timeout_ms", 5000)})

    # ---------- Conveniences ----------

    @property
    def items(self) -> Items:
        """Convenience for main port input (array-of-objects)."""
        return self._input_data.get("main", [])

    def emit_main(self, items: Items) -> None:
        """Emit to 'main' port."""
        self.emit("main", items)

    def resource(self, kind: str, name: str = "default"):
        """Shortcut over resources() for the common case."""
        reg = self.resources()
        return reg.get(kind, name)

    # ---------- Original API (kept for compatibility) ----------

    def get_input_data(self, port: str = "main") -> Items:
        return self._input_data.get(port, [])

    def get_parameter(self, name: str, default: Any = None) -> Any:
        return self._parameters.get(name, default)

    def emit(self, port: str, items: Items) -> None:
        if not isinstance(items, list):
            raise TypeError(f"emit() expects Items (list), got {type(items)}")
        self._emitted_outputs[port] = items

    def get_emitted_outputs(self) -> Dict[str, Items]:
        return self._emitted_outputs.copy()

    def get_execution_id(self) -> str:
        return self._execution_id

    def get_workflow_id(self) -> str:
        return self._workflow_id

    def get_node_id(self) -> str:
        return self._node_id

    def get_step_id(self) -> str:
        return self._step_id

    def get_node(self) -> Dict:
        return self._node

    def get_context(self) -> Dict:
        return self._context.copy()

    def get_credential(self, name: str) -> Optional[str]:
        return self._credentials.get(name)

    def continue_on_fail(self) -> bool:
        return self._continue_on_fail

    def resources(self) -> ResourceRegistry:
        if self._resource_registry is None:
            if self._resource_registry_factory:
                self._resource_registry = self._resource_registry_factory(
                    function=self._function,
                    context=self,
                )
            else:
                self._resource_registry = ResourceRegistry(function=self._function, context=self)
        return self._resource_registry


class _LoggerFacade:
    """Tiny facade to offer .info/.debug/.warn/.error on top of stdlib logger."""
    def __init__(self, logger: logging.Logger):
        self._lg = logger

    def info(self, msg: str, **kw):  self._lg.info(f"{msg} | {kw}" if kw else msg)
    def debug(self, msg: str, **kw): self._lg.debug(f"{msg} | {kw}" if kw else msg)
    def warn(self, msg: str, **kw):  self._lg.warning(f"{msg} | {kw}" if kw else msg)
    def error(self, msg: str, **kw): self._lg.error(f"{msg} | {kw}" if kw else msg)