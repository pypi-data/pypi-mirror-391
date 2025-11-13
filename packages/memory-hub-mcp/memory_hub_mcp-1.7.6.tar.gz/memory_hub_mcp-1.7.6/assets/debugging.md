Forwarded the run_id argument from the MCP tool into the handler and removed the module-level logging configuration so the CLI-owned file handler can write to /tmp/memory-hub-mcp.log.

Fixes

get_project_memories tool requests now include run_id, so cascade=false queries build the four-level exact-match filter instead of falling back to ticket scope (src/memory_hub/mcp_server.py (lines 383-391)).
Dropped the unconditional logging.basicConfig in mcp_server so importing the module no longer overrides the CLI’s file-based logging configuration; the module simply reuses the shared logger (src/memory_hub/mcp_server.py (lines 41-44)).
Verification

Not run (manual MCP/Qdrant scenario required to verify run_id filtering).
Next Steps

Restart the MCP server via memory_hub.cli and rerun the failing get_project_memories calls to confirm only the targeted runs (3 + 2 memories) are returned.
Inspect /tmp/memory-hub-mcp.log after those calls to ensure the filter-debug lines and counts are recorded as expected.