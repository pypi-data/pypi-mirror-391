# models.py - Pydantic models for Memory Hub MCP Server

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any

# --- Pydantic Models ---
class MemoryItemIn(BaseModel):
    content: str = Field(..., description="The content to store in memory")
    metadata: Dict[str, Any] = Field(
        ...,
        description=(
            "Metadata with hierarchical structure. "
            "RULES: app_id is required. "
            "project_id requires app_id. "
            "ticket_id requires both app_id AND project_id. "
            "Example: {app_id: 'crossroads', project_id: 'auth', type: 'api_design'}"
        )
    )
    chunking: bool = Field(
        default=True,
        description=(
            "Enable semantic chunking (default: true). "
            "Set to false for large structured documents (e.g., AutoStack plans, specifications) "
            "that don't need semantic search and should be stored as a single unit."
        )
    )

class MemorySearchRequest(BaseModel):
    query_text: str = Field(..., description="The query text to search for")
    metadata_filters: Dict[str, str] = Field(default_factory=dict, description="Metadata filters for search")
    keyword_filters: List[str] = Field(default_factory=list, description="List of keywords that results must contain")
    limit: int = Field(default=10, description="Maximum number of results to return")
    cascade: bool = Field(
        default=True,
        description=(
            "Enable cascading retrieval (default: true). "
            "When false, only returns memories at the exact hierarchy level specified in metadata_filters. "
            "Use cascade=false for AutoStack checkpoint pattern to check if a specific address has data."
        )
    )

class RetrievedChunk(BaseModel):
    text_chunk: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str

class SearchResponse(BaseModel):
    synthesized_summary: Optional[str] = Field(default=None, description="AI-generated summary of results")
    retrieved_chunks: List[RetrievedChunk]
    total_results: int

class AddMemoryResponse(BaseModel):
    message: str
    chunks_stored: int
    original_content_hash: str

# --- New Introspection Models ---
class ListIdsResponse(BaseModel):
    ids: List[str] = Field(..., description="List of unique identifiers found")
    total_count: int = Field(..., description="Total number of unique identifiers")
    points_scanned: int = Field(..., description="Number of points scanned to extract IDs")

class MemoryTypeInfo(BaseModel):
    type_name: str = Field(..., description="The memory type name")
    count: int = Field(..., description="Number of memories with this type")
    latest_version: int = Field(..., description="Highest version number for this type")
    last_updated: str = Field(..., description="ISO timestamp of most recent memory")

class ListMemoryTypesResponse(BaseModel):
    memory_types: List[MemoryTypeInfo] = Field(..., description="List of memory types with metadata")
    total_types: int = Field(..., description="Total number of unique memory types")
    points_scanned: int = Field(..., description="Number of points scanned")

class GetProjectMemoriesRequest(BaseModel):
    app_id: str = Field(..., description="Required - Application identifier")
    project_id: Optional[str] = Field(
        None,
        description=(
            "Optional - Project identifier. "
            "CASCADING: When provided, returns app-level + project-level memories. "
            "Requires app_id."
        )
    )
    ticket_id: Optional[str] = Field(
        None,
        description=(
            "Optional - Ticket identifier. "
            "CASCADING: When provided, returns app-level + project-level + ticket-level memories. "
            "Requires both app_id AND project_id."
        )
    )
    limit: int = Field(default=50, description="Maximum number of results to return")
    sort_by: str = Field(default="timestamp", description="Sort field: 'timestamp' or 'score'")
    return_format: str = Field(
        default="both",
        description=(
            "Response format: 'summary_only', 'chunks_only', or 'both'. "
            "summary_only: AI-generated summary only (~80%% token reduction). "
            "chunks_only: Raw memory chunks without LLM interpretation. "
            "both: Summary + chunks (default, backward compatible)."
        )
    )
    cascade: bool = Field(
        default=True,
        description=(
            "Enable cascading retrieval (default: true). "
            "When true: ticket_id returns app + project + ticket levels. "
            "When false: returns ONLY the exact level specified (app-only, project-only, or ticket-only). "
            "Use cascade=false for AutoStack checkpoint pattern to check if a specific address has data."
        )
    )

class UpdateMemoryRequest(BaseModel):
    app_id: str = Field(..., description="Required - Application identifier")
    project_id: Optional[str] = Field(
        None,
        description="Optional - Project identifier (requires app_id)"
    )
    ticket_id: Optional[str] = Field(
        None,
        description="Optional - Ticket identifier (requires app_id AND project_id)"
    )
    memory_type: Optional[str] = Field(None, description="Optional - Memory type to identify which memory to update")
    new_content: str = Field(..., description="New content to replace the existing memory")
    metadata_updates: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata fields to update")

class GetRecentMemoriesRequest(BaseModel):
    app_id: Optional[str] = Field(None, description="Optional - Filter by application identifier")
    project_id: Optional[str] = Field(
        None,
        description="Optional - Filter by project identifier (requires app_id)"
    )
    hours: int = Field(default=24, description="Number of hours to look back (default: 24)")
    limit: int = Field(default=20, description="Maximum number of results to return")
    return_format: str = Field(
        default="both",
        description=(
            "Response format: 'summary_only', 'chunks_only', or 'both'. "
            "summary_only: AI-generated summary only (~80%% token reduction). "
            "chunks_only: Raw memory chunks without LLM interpretation. "
            "both: Summary + chunks (default, backward compatible)."
        )
    )
    cascade: bool = Field(
        default=True,
        description=(
            "Enable cascading retrieval (default: true). "
            "When false, returns ONLY memories at the exact level specified. "
            "Use cascade=false for AutoStack checkpoint pattern."
        )
    )

class ListMemoryTypesRequest(BaseModel):
    app_id: Optional[str] = Field(None, description="Optional - Filter by application identifier")
    project_id: Optional[str] = Field(None, description="Optional - Filter by project identifier")

class GetMemoryTypeGuideResponse(BaseModel):
    create_new_types: List[str] = Field(..., description="Memory types that should always CREATE new memories")
    update_types: List[str] = Field(..., description="Memory types that should typically be UPDATED")
    guidelines: str = Field(..., description="Guidelines for using memory types") 