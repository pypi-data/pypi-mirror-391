from enum import StrEnum, auto
from typing import Literal

from pydantic import BaseModel, Field


class EmbedderType(StrEnum):
    """Supported embedding providers."""

    OPENAI = auto()
    VERTEX = auto()
    AZURE_OPENAI = auto()
    OLLAMA = auto()


class Embedder(BaseModel):
    """Embedder configuration."""

    embedder_type: str = Field(default=EmbedderType.VERTEX)
    model_name: str = Field(default="text-embedding-ada-002")


class RetrieverOptions(BaseModel):
    """Retriever configuration options."""

    collection_name: str | None = Field(
        default=None,
        description="Collection name to use in vector DB. If not provided, defaults to project_id.",
    )
    filename_search: bool = Field(default=False, description="Enable filename search")
    composite_query_detection: bool = Field(
        default=False, description="Split composite query into several simple questions"
    )
    partial_search: bool = Field(
        default=False, description="Search by small chunks and take it`s neighbors."
    )
    query_rewrite: bool = Field(default=True, description="Enable rewriting user query")
    max_retrieved_docs: int = Field(
        default=4, description="Maximum number of documents to retrieve."
    )
    ranked_documents: int = Field(
        default=1, description="Number of ranked documents to return."
    )
    minimum_relevance: float = Field(
        default=0.5, description="Minimum relevance score for ranked documents."
    )


class RetrievalConfig(BaseModel):
    """Base retrieval configuration."""

    embedder: Embedder = Field(default_factory=Embedder)
    vector_database: Literal["qdrant", "chroma", "milvus"] = Field(default="qdrant")
    retriever_options: RetrieverOptions = Field(default_factory=RetrieverOptions)
