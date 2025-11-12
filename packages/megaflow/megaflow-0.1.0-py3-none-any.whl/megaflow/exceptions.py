"""
Megaflow SDK exceptions.
"""


class NodeOperationError(Exception):
    """
    Structured error for function failures.
    
    Args:
        node: Node definition dictionary
        error: Original exception that caused the failure
    """
    
    def __init__(self, node: dict, error: Exception):
        self.node = node
        self.error = error
        super().__init__(f"Node operation failed: {str(error)}")
    
    def __repr__(self):
        return f"NodeOperationError(node={self.node}, error={self.error})"

