# CodeAct Agent Refactoring Checklist

This document outlines a series of small, incremental refactoring tasks to improve the structure and readability of the `CodeAct` agent. Each task is designed to be small enough for easy review.

### Part 1: Decouple Graph Nodes into a Dedicated Directory

The goal is to move the core logic of each graph step into its own file within a `nodes` directory, following advanced LangChain practices for modularity.

- [x] Create a new directory: `src/universal_mcp/agents/codeact0/nodes/`.
- [x] Create an `__init__.py` file in the new `nodes` directory to make it a package.
- [x] Create a new file: `src/universal_mcp/agents/codeact0/nodes/call_model.py`.
- [x] In `agent.py`, move the `call_model` method into `call_model.py` as a standalone function.
- [x] Update the new `call_model` function to accept necessary dependencies (e.g., `model_instance`) as arguments instead of using `self`.
- [x] Create a new file: `src/universal_mcp/agents/codeact0/nodes/execute_tools.py`.
- [x] In `agent.py`, move the `execute_tools` method into `execute_tools.py` as a standalone function.
- [x] Update the new `execute_tools` function to accept dependencies (e.g., `sandbox`, `tools_context`) as arguments.
- [x] Create a new file: `src/universal_mcp/agents/codeact0/nodes/route_entry.py`.
- [x] In `agent.py`, move the `route_entry` method into `route_entry.py` as a standalone function.
- [x] Update the new `route_entry` function to accept necessary dependencies as arguments.
- [x] In `agent.py`, update the `_build_graph` method to import and use the new node functions from the `nodes` package.

### Part 2: Isolate the "Agent Builder" Sub-Agent

The logic for creating and updating agent plans and code is a distinct responsibility and should be encapsulated in its own module.

- [ ] Create a new file: `src/universal_mcp/agents/codeact0/agent_builder.py`.
- [ ] In `agent.py`, move the `_create_or_update_plan` method to the new `agent_builder.py` file.
- [ ] Refactor `_create_or_update_plan` in its new file to be a standalone function, accepting state and dependencies as arguments.
- [ ] In `agent.py`, move the `_build_or_patch_code` method to the `agent_builder.py` file.
- [ ] Refactor `_build_or_patch_code` in its new file to be a standalone function.
- [ ] Update the `execute_tools` function in `nodes/execute_tools.py` to import and call the plan/code functions from `agent_builder.py`.

### Part 3: Centralize Tool Management Utilities

Consolidate tool-loading logic into a dedicated utility module to keep the agent class focused on orchestration.

- [ ] Create a new file: `src/universal_mcp/agents/codeact0/tool_utils.py`.
- [ ] In `agent.py`, move the `_load_tools` method into `tool_utils.py` as a standalone function.
- [ ] Refactor the new `_load_tools` function to accept dependencies (e.g., `registry`, `sandbox`) as arguments.
- [ ] Update the `route_entry` function in `nodes/route_entry.py` to use the new utility function from `tool_utils.py`.

### Part 4: Final Review and Simplification

After decoupling the components, the main agent class should be a lean orchestrator.

- [ ] Review the `CodeActPlaybookAgent` class in `agent.py`.
- [ ] Confirm that its primary responsibilities are now limited to initialization (`__init__`) and graph assembly (`_build_graph`).
- [ ] Remove any unused imports from `agent.py` and add necessary imports to the new modules.
