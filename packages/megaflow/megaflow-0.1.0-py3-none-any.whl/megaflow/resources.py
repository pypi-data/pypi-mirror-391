"""
Resource Registry - Typed resource handles for accessing external capabilities.

Resources are accessed via typed interfaces, not vendor SDKs.
This enables provider-agnostic function code.
"""

from typing import Any, Optional, List, Dict
from abc import ABC, abstractmethod


class LanguageModel(ABC):
    """Interface for AI language model resources."""
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send chat messages to the language model.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional model-specific parameters
        
        Returns:
            Response dictionary (typically with 'content' or 'text' key)
        """
        pass
    
    @abstractmethod
    async def embed(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text strings
            **kwargs: Additional model-specific parameters
        
        Returns:
            List of embedding vectors
        """
        pass


class EmbeddingModel(ABC):
    """Interface for embedding model resources."""
    
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text strings
        
        Returns:
            List of embedding vectors
        """
        pass


class VectorStore(ABC):
    """Interface for vector store resources."""
    
    @abstractmethod
    async def upsert(self, points: List[Dict[str, Any]]) -> None:
        """
        Upsert vector points into the store.
        
        Args:
            points: List of point dictionaries (must include 'id' and 'vector')
        """
        pass
    
    @abstractmethod
    async def query(self, vector: List[float], top_k: int = 10) -> List[Any]:
        """
        Query similar vectors.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
        
        Returns:
            List of similar points
        """
        pass


class SqlDb(ABC):
    """Interface for SQL database resources."""
    
    @abstractmethod
    async def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query.
        
        Args:
            sql: SQL query string
            params: Optional parameter dictionary for parameterized queries
        
        Returns:
            List of result rows as dictionaries
        """
        pass


class KvStore(ABC):
    """Interface for key-value store resources."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: Key string
        
        Returns:
            Value or None if not found
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """
        Set a key-value pair.
        
        Args:
            key: Key string
            value: Value to store
        """
        pass


class SmtpMailer(ABC):
    """Interface for SMTP mailer resources."""
    
    @abstractmethod
    async def send(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        **kwargs
    ) -> None:
        """
        Send an email.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body
            **kwargs: Additional email options (cc, bcc, attachments, etc.)
        """
        pass


class ResourceRegistry:
    """
    Resource registry providing typed resource handles.
    
    Resources are accessed via methods like:
    - resources().lm() -> LanguageModel
    - resources().vector() -> VectorStore
    - resources().db() -> SqlDb
    """
    
    def __init__(self, function: Optional[Any] = None, context: Optional[Any] = None):
        self._function = function
        self._context = context
        self._resources: Dict[str, Any] = {}
    
    def lm(self) -> LanguageModel:
        """
        Get language model resource (ai.language_model).
        
        Returns:
            LanguageModel instance
        """
        if "lm" not in self._resources:
            # TODO: Implement actual resource loading based on function.yaml resources section
            raise NotImplementedError("Language model resource not yet implemented")
        return self._resources["lm"]
    
    def embedding(self) -> EmbeddingModel:
        """
        Get embedding model resource (ai.embedding_model).
        
        Returns:
            EmbeddingModel instance
        """
        if "embedding" not in self._resources:
            raise NotImplementedError("Embedding model resource not yet implemented")
        return self._resources["embedding"]
    
    def vector(self) -> VectorStore:
        """
        Get vector store resource (vector.store).
        
        Returns:
            VectorStore instance
        """
        if "vector" not in self._resources:
            raise NotImplementedError("Vector store resource not yet implemented")
        return self._resources["vector"]
    
    def db(self) -> SqlDb:
        """
        Get SQL database resource (db.sql).
        
        Returns:
            SqlDb instance
        """
        if "db" not in self._resources:
            raise NotImplementedError("SQL database resource not yet implemented")
        return self._resources["db"]
    
    def kv(self) -> KvStore:
        """
        Get key-value store resource (kv.store).
        
        Returns:
            KvStore instance
        """
        if "kv" not in self._resources:
            raise NotImplementedError("Key-value store resource not yet implemented")
        return self._resources["kv"]
    
    def mail(self) -> SmtpMailer:
        """
        Get SMTP mailer resource (mail.smtp).
        
        Returns:
            SmtpMailer instance
        """
        if "mail" not in self._resources:
            raise NotImplementedError("SMTP mailer resource not yet implemented")
        return self._resources["mail"]

