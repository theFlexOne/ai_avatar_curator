---
name: manage-tmp-files
description: Manages creation and cleanup of temporary files (mock images, scratchpads, test fixtures) in the workspace.
---

# Manage Tmp Files

## When to Use
- When creating mock data (e.g., `numpy` images) for testing.
- When you need a temporary scratchpad for complex command output.
- To clean up temporary artifacts before making a commit.
- When `make clean` is insufficient for specialized task-based cleanup.

## Procedure

1. **Identify Scope**: Determine if the file is a long-term test fixture (`tests/fixtures/`) or a transient temporary file (`/tmp/` or a local `.tmp/`).
2. **Trace Log Lifecycle**:
   - If managing an Audit Loop, ensure `.tmp/audit_trace.jsonl` exists.
   - Parse or append JSONL formatted lines to the trace log as directed by the Curator or subagents.
   - Aggregate trace logs into an end-of-audit summary, then clear the file to prevent infinite growth.
3. **Create Temporary File**:
   - Use `run_in_terminal` to create directories if needed.
   - For images, use a Python snippet via `run_in_terminal` or `mcp_pylance_mcp_s_pylanceRunCodeSnippet` to generate valid `numpy` arrays/files.
4. **Track for Cleanup**: Maintain a list of files created during the session.
5. **Cleanup**: 
   - Before completing the user's request, verify if any created temporary files should be removed.
   - Use `rm -rf` via `run_in_terminal` for cleanup.
   - **Safety First**: Never use broad wildcards (like `rm -rf *`) without explicit file path verification.

## Best Practices
- **Isolation**: Use a dedicated `.tmp/` directory in the root (ensure it's in `.gitignore`).
- **Naming**: Use descriptive prefixes (e.g., `tmp_test_google_scraper_results.json`).
- **Permissions**: Respect existing file permissions.
