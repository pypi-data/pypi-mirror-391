# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Memory Hub MCP Server is a local memory system for AI agents using the Model Context Protocol (MCP). It provides vector-based storage and retrieval through stdio transport, specifically designed for ZenCoder and other MCP clients.

## Essential Commands

### Development Setup
```bash
# Setup development environment
uv venv
source .venv/bin/activate
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Running the Server
```bash
# Run with default settings
memory-hub-mcp

# Run with custom configuration
memory-hub-mcp --log-level DEBUG --qdrant-url http://localhost:6333 --lm-studio-url http://localhost:1234/v1

# Run with UVX (recommended for distribution)
uvx memory-hub-mcp
```

### Development and Testing
```bash
# Code formatting and linting
black src/
ruff check src/

# Build distribution
uv build

# Publish to PyPI (requires token)
UV_PUBLISH_TOKEN=<token> uv publish dist/*
```

### Docker Environment
```bash
# Start Qdrant dependency
docker-compose up -d

# Development with hot reload
docker-compose -f docker-compose.dev.yml up
```

## Architecture

### Core Components

1. **MCP Server** (`src/memory_hub/mcp_server.py`): Main server implementation using stdio transport
2. **CLI Interface** (`src/memory_hub/cli.py`): Command-line entry point with argument parsing
3. **Core Services** (`src/memory_hub/core/services.py`): Handles Qdrant client and LM Studio integration
4. **Handlers** (`src/memory_hub/core/handlers/`): MCP tool implementations
5. **Models** (`src/memory_hub/core/models.py`): Pydantic data models

### Key Design Patterns

- **stdio transport**: Direct MCP protocol communication (no HTTP)
- **Hierarchical memory**: Flexible app_id → project_id → ticket_id organization
- **Hybrid search**: Vector similarity + keyword matching + LLM synthesis
- **Async-first**: All operations use async/await patterns

### External Dependencies

- **Qdrant**: Vector database for embeddings storage
- **LM Studio**: Provides embeddings and chat completions
- **MCP Protocol**: stdio transport for client communication

## MCP Tools Available

1. **add_memory**: Store content with hierarchical metadata
2. **search_memories**: Semantic search with keyword enhancement
3. **get_project_memories**: Retrieve ALL memories for a specific app_id/project_id without search queries
4. **update_memory**: Update existing memories with automatic version incrementing
5. **get_recent_memories**: Retrieve memories from the last N hours (perfect for resuming work)
6. **list_app_ids**: List all application identifiers
7. **list_project_ids**: List all project identifiers
8. **list_ticket_ids**: List all ticket identifiers
9. **list_memory_types**: List memory types currently in use (with counts and metadata)
10. **get_memory_type_guide**: Get the recommended memory type conventions
11. **health_check**: Server health verification

## Memory Retrieval Optimization

### Return Format Control

Both `get_project_memories` and `get_recent_memories` support a `return_format` parameter for optimizing token usage:

**Options:**
- `summary_only`: AI-generated summary only (~80% token reduction)
- `chunks_only`: Raw memory chunks without summarization
- `both`: Summary + chunks (default, backward compatible)

### Agent Usage Patterns

**1. Starting New Work** (use `summary_only`):
```python
get_project_memories(
    app_id="crossroads",
    return_format="summary_only"
)
# Returns: Concise overview, ~500-800 tokens vs ~3,000 tokens
```

**2. Deep Implementation** (use `chunks_only`):
```python
get_project_memories(
    app_id="crossroads",
    project_id="auth",
    return_format="chunks_only"
)
# Returns: Exact content, no LLM interpretation
# Use when extracting specific data, code, or facts
```

**3. Exploration/Debugging** (use `both`):
```python
get_project_memories(
    app_id="crossroads",
    return_format="both"
)
# Returns: Summary + full chunks for reference
```

### Token Efficiency Examples

| Memories | Format | Approx Tokens |
|----------|--------|---------------|
| 10 app-level | both | ~3,000 |
| 10 app-level | summary_only | ~600 |
| 50 project-level | both | ~15,000 |
| 50 project-level | summary_only | ~2,000 |

**Best Practice:** Default to `summary_only` for initial context loading, then request `chunks_only` when you need specific details.

## Chunking Control (v1.6.0+)

The `chunking` parameter on `add_memory` controls whether content is semantically chunked or stored as a single unit.

### When to Disable Chunking (`chunking=false`)

Use `chunking=false` for:
- **AutoStack plans**: Large markdown documents that should be retrieved as complete units
- **Specifications**: Technical documents that need to be read in full
- **Structured data**: JSON/YAML configs that should remain intact
- **Long-form content**: Articles, reports, or documentation that don't benefit from semantic chunking

### Performance Benefits

- **20-30x fewer embedding calls**: Single embedding vs 20-30 chunks
- **Faster storage**: Skip chunking overhead (~100ms saved)
- **Simpler retrieval**: No reassembly needed, single chunk returned

### Usage Example

```python
# AutoStack planning agent storing a plan
add_memory(
    content=full_plan_markdown,  # e.g., 2000-token plan
    metadata={
        "app_id": "covenant",
        "project_id": "portal",
        "ticket_id": "auth-flow",
        "type": "plan"
    },
    chunking=False  # ← Store as single unit
)
# Result: 1 chunk stored instead of 25 chunks
```

### Default Behavior (`chunking=true`)

Most memories should use default chunking for optimal semantic search:
```python
# Normal memory (code changes, decisions, etc.)
add_memory(
    content="Implemented JWT authentication with refresh tokens...",
    metadata={
        "app_id": "covenant",
        "project_id": "auth",
        "type": "feature_implementation"
    }
    # chunking=True by default - will create ~5-10 chunks
)
```

**Tradeoff**: Large single embeddings are less semantically precise for search, but perfect for documents that need to be retrieved whole.

## Configuration

### Environment Variables
- `QDRANT_URL`: Qdrant server URL (default: http://localhost:6333)
- `LM_STUDIO_BASE_URL`: LM Studio base URL (default: http://localhost:1234/v1)
- `MIN_SCORE_THRESHOLD`: Minimum similarity score for results (default: 0.60)
- `ENABLE_GEMMA_SUMMARIZATION`: Enable LLM summarization (default: true)

### CLI Arguments
- `--qdrant-url`: Override Qdrant URL
- `--lm-studio-url`: Override LM Studio URL  
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

## Development Notes

### Important File Locations
- `src/memory_hub/core/config.py`: Configuration constants and environment variables
- `src/memory_hub/core/chunking.py`: Semantic text chunking implementation
- `src/memory_hub/core/utils/search_utils.py`: Search enhancement utilities
- `pyproject.toml`: Package configuration and dependencies

### Testing Considerations
- No formal test suite currently exists
- Manual testing requires running Qdrant and LM Studio locally
- Debug script available: `debug_memory_hub.py`

### Version Management
- Version defined in `pyproject.toml`
- Must increment for PyPI publishing
- Semantic versioning: MAJOR.MINOR.PATCH

## Hierarchical Memory Structure

Memory Hub enforces a strict hierarchy with validation:

**Rules:**
- `app_id` is always required
- `project_id` requires `app_id` (cannot specify project without app)
- `ticket_id` requires both `app_id` AND `project_id` (cannot specify ticket without both)

**Cascading Retrieval:**
- `app_id` only → Returns app-level memories (no project_id)
- `app_id + project_id` → Returns app-level + project-level memories (cascading)
- `app_id + project_id + ticket_id` → Returns app-level + project-level + ticket-level memories (full cascade)

This ensures you always get relevant parent context when querying child levels.

## Agent Usage Patterns

### For Agents Saving Progress
When an agent needs to save work progress:
```
1. Use add_memory with:
   - app_id: Your application/domain (e.g., "eatzos", "motiv")
   - project_id: Specific project/feature (e.g., "next", "enhanced-chat")
   - type: Type of memory (e.g., "progress", "code_changes", "decisions")
   - content: Detailed progress, decisions, code changes, etc.

2. For updates to existing memories:
   - Use update_memory to increment version automatically
   - Specify app_id, project_id, and optionally memory_type
   - Provide new_content with the updated information

3. Hierarchy validation:
   - VALID: {app_id: "crossroads"}
   - VALID: {app_id: "crossroads", project_id: "auth"}
   - VALID: {app_id: "crossroads", project_id: "auth", ticket_id: "TICK-123"}
   - INVALID: {project_id: "auth"} ← Missing required app_id
   - INVALID: {ticket_id: "TICK-123"} ← Missing required app_id and project_id
```

### For Agents Resuming Work
When an agent needs to continue previous work:
```
1. Use get_project_memories to retrieve ALL context:
   - Specify app_id and project_id
   - No need to guess search terms!
   - Automatically gets latest versions

2. Use get_recent_memories to see what changed:
   - Optionally filter by app_id/project_id
   - Default: last 24 hours
   - Includes AI-generated summary

3. Use search_memories only when:
   - Looking for specific concepts across projects
   - Need keyword-enhanced semantic search
```

### Best Practices for Agent Continuity
1. **Consistent Naming**: Use consistent app_id and project_id across sessions
2. **Meaningful Types**: Use descriptive memory types (e.g., "api_design", "bug_fix", "feature_implementation")
3. **Regular Updates**: Update memories as work progresses, not just at the end
4. **Version Awareness**: The system handles versioning automatically - just update when needed

## AutoStack Usage Patterns

AutoStack is a formalized AI-First development methodology that uses Memory Hub as its state management backbone. Each AutoStack workflow (plan → build → wrap) stores execution state and artifacts at predictable memory addresses.

### Checkpoint Pattern with cascade=false

AutoStack orchestrators use **exact address matching** to check if work has been done at a specific checkpoint:

```python
# Orchestrator checks if planning is complete
get_project_memories({
  app_id: "covenant",
  project_id: "portal",
  ticket_id: "auth-flow",
  cascade: false,  # CRITICAL: Only return ticket-level memories
  metadata_filters: { type: "plan" },
  return_format: "chunks_only"  # Skip AI summarization
})

# Returns 0 results if no plan exists → Start planning phase
# Returns plan document if it exists → Skip to build phase
```

**Why cascade=false is critical:**
- Without it: Query returns ALL parent context (app + project + ticket) → 55k tokens
- With it: Query returns ONLY ticket-level data → 0 results if checkpoint is empty
- Enables lightweight "does this address have data?" checks

### AutoStack Memory Address Structure

AutoStack uses predictable `ticket_id` + `type` combinations:

```python
# State tracking (orchestrator writes this)
{
  app_id: "covenant",
  project_id: "portal",
  ticket_id: "auth-flow",
  type: "state",
  content: JSON.stringify({ phase: "build", plan_approved: true })
}

# Plan document (planner agent writes this)
{
  ticket_id: "auth-flow",
  type: "plan",
  content: "# Auth Flow Implementation Plan\n..."
}

# Backend results (backend agent writes this)
{
  ticket_id: "auth-flow",
  type: "backend-result",
  content: JSON.stringify({ files_created: [...], tests_passing: true })
}

# Frontend results (frontend agent writes this)
{
  ticket_id: "auth-flow",
  type: "frontend-result",
  content: JSON.stringify({ components: [...], playwright_passed: true })
}

# Wrap results (wrap agent writes this)
{
  ticket_id: "auth-flow",
  type: "wrap-result",
  content: JSON.stringify({ commit_message: "...", staged_files: [...] })
}
```

### Token Optimization for Structured Data

AutoStack stores structured JSON/YAML data that agents need to parse:

```python
# Retrieve plan without AI summarization
get_project_memories({
  ticket_id: "auth-flow",
  cascade: false,
  metadata_filters: { type: "plan" },
  return_format: "chunks_only"  # Returns verbatim chunks, no LLM processing
})

# Agent concatenates chunks and parses JSON
plan_chunks = response.retrieved_chunks
plan_text = "".join(chunk.text_chunk for chunk in plan_chunks)
plan_data = JSON.parse(plan_text)
```

### Cascading for Context Retrieval

When agents need full project context (not just checkpoint checking), use cascading:

```python
# Planner agent gathering historical context
get_recent_memories({
  app_id: "covenant",
  project_id: "portal",
  cascade: true,  # Include app-level + project-level memories
  hours: 168,  # Last week
  return_format: "summary_only"  # AI summary for quick overview
})
```

### AutoStack Tool Selection Guide

| Use Case | Tool | cascade | return_format |
|----------|------|---------|---------------|
| Check if checkpoint exists | `get_project_memories` | `false` | `chunks_only` |
| Retrieve structured artifact | `get_project_memories` | `false` | `chunks_only` |
| Get full project context | `get_project_memories` | `true` | `summary_only` |
| Resume after interruption | `get_recent_memories` | `true` | `both` |
| Find specific pattern | `search_memories` | `true` | `both` |

### Complete AutoStack Example

```python
# 1. Orchestrator checks current state
state_result = get_project_memories({
  app_id: "covenant",
  project_id: "portal",
  ticket_id: "auth-flow",
  cascade: false,
  metadata_filters: { type: "state" },
  return_format: "chunks_only"
})

if state_result.total_results == 0:
  # No state exists, start from planning
  invoke_agent("autostack-planner")
else:
  # Parse state and resume from checkpoint
  state = JSON.parse(state_result.retrieved_chunks[0].text_chunk)
  if state.phase == "build":
    invoke_agent("autostack-backend")

# 2. Backend agent retrieves plan
plan_result = get_project_memories({
  ticket_id: "auth-flow",
  cascade: false,
  metadata_filters: { type: "plan" },
  return_format: "chunks_only"
})
plan_text = concatenate_chunks(plan_result.retrieved_chunks)

# 3. Backend agent writes results
add_memory({
  content: JSON.stringify({
    files_created: ["routes/auth.ts"],
    tests_passing: true
  }),
  metadata: {
    app_id: "covenant",
    project_id: "portal",
    ticket_id: "auth-flow",
    type: "backend-result"
  }
})
```

## Troubleshooting

### Common Issues
1. **Qdrant connection errors**: Verify Qdrant is running and accessible
2. **LM Studio timeout**: Check LM Studio is running with appropriate models loaded
3. **Context length errors**: Reduce chunk size or query complexity
4. **Import errors**: Ensure all dependencies installed with `uv pip install -e .`

### Debugging
- Use `--log-level DEBUG` for verbose output
- Check `docker-compose.yml` for service configuration
- Review error messages in stdio output