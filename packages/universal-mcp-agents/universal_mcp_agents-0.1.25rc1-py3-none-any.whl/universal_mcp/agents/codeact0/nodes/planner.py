import uuid
from typing import cast

from langchain_core.messages import HumanMessage
from langgraph.types import StreamWriter

from universal_mcp.agents.codeact0.prompts import (
    AGENT_BUILDER_CODE_PATCH_PROMPT,
    AGENT_BUILDER_GENERATING_PROMPT,
    AGENT_BUILDER_META_PROMPT,
    AGENT_BUILDER_PLAN_PATCH_PROMPT,
    AGENT_BUILDER_PLANNING_PROMPT,
)
from universal_mcp.agents.codeact0.state import (
    AgentBuilderCode,
    AgentBuilderMeta,
    AgentBuilderPatch,
    AgentBuilderPlan,
    CodeActState,
)
from universal_mcp.agents.codeact0.utils import (
    apply_patch_or_use_proposed,
    extract_code_tools,
    extract_plan_parameters,
    sanitize_messages,
)
from universal_mcp.agents.utils import convert_tool_ids_to_dict


async def create_or_update_plan(self, state: CodeActState, writer: StreamWriter, plan: list[str] | None):
    """Sub-agent helper: create or patch-update the agent plan and emit UI updates.
    Returns: (plan: list[str], tool_result: str)
    """
    plan_id = str(uuid.uuid4())
    writer({"type": "custom", id: plan_id, "name": "planning", "data": {"update": bool(plan)}})

    # Determine existing plan (prefer persisted agent's plan) and base messages
    existing_plan_steps = (
        self.agent.instructions.get("plan") if self.agent and getattr(self.agent, "instructions", None) else None
    ) or plan
    base = sanitize_messages(state["messages"])

    def with_sys(text: str):
        return [{"role": "system", "content": text}] + base

    if existing_plan_steps:
        current = "\n".join(map(str, existing_plan_steps or []))
        sys_prompt = self.instructions + "\n" + AGENT_BUILDER_PLAN_PATCH_PROMPT
        msgs = with_sys(sys_prompt) + [HumanMessage(content=f"Current plan (one step per line):\n{current}")]
        patch_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderPatch)
        proposed = cast(AgentBuilderPatch, await patch_model.ainvoke(msgs)).patch
        updated = apply_patch_or_use_proposed(current, proposed)
        plan = [line for line in updated.splitlines() if line.strip()]
    else:
        sys_prompt = self.instructions + AGENT_BUILDER_PLANNING_PROMPT
        plan_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderPlan)
        plan = cast(AgentBuilderPlan, await plan_model.ainvoke(with_sys(sys_prompt))).steps

    writer({"type": "custom", id: plan_id, "name": "planning", "data": {"plan": plan}})
    tool_result = {"plan": plan, "update": bool(plan), "message": "Successfully generated the agent plan."}
    return plan, tool_result


async def build_or_patch_code(
    self,
    state: "CodeActState",
    writer: StreamWriter,
    plan: list[str] | None,
    agent_name: str | None,
    agent_description: str | None,
    effective_previous_add_context: dict,
):
    """Sub-agent helper: generate new code or patch existing code, save, and emit UI updates.
    Returns: (tool_result: str, effective_previous_add_context: dict, agent_name: str | None, agent_description: str | None)
    """
    generation_id = str(uuid.uuid4())
    writer({"type": "custom", "id": generation_id, "name": "generating", "data": {"update": bool(self.agent)}})

    base = sanitize_messages(state["messages"])

    def with_sys(text: str):
        return [{"role": "system", "content": text}] + base

    plan_text = "\n".join(map(str, plan)) if plan else None
    existing_code = (
        self.agent.instructions.get("script") if self.agent and getattr(self.agent, "instructions", None) else None
    )

    if self.agent:
        agent_name = getattr(self.agent, "name", None)
        agent_description = getattr(self.agent, "description", None)

    if not agent_name or not agent_description:
        meta_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderMeta)
        meta = cast(AgentBuilderMeta, await meta_model.ainvoke(with_sys(self.instructions + AGENT_BUILDER_META_PROMPT)))
        agent_name, agent_description = meta.name, meta.description

    writer(
        {
            "type": "custom",
            "id": generation_id,
            "name": "generating",
            "data": {"update": bool(self.agent), "name": agent_name, "description": agent_description},
        }
    )

    if existing_code:
        generating_instructions = self.instructions + AGENT_BUILDER_CODE_PATCH_PROMPT
        messages = with_sys(generating_instructions)
        if plan_text:
            messages.append(HumanMessage(content=f"Confirmed plan (one step per line):\n{plan_text}"))
        messages.append(HumanMessage(content=f"Current code to update:\n```python\n{existing_code}\n```"))
        patch_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderPatch)
        proposed = cast(AgentBuilderPatch, await patch_model.ainvoke(messages)).patch
        python_code = apply_patch_or_use_proposed(existing_code, proposed)
    else:
        code_model = self.agent_builder_model_instance.with_structured_output(AgentBuilderCode)
        python_code = cast(
            AgentBuilderCode,
            await code_model.ainvoke(
                with_sys(self.instructions + AGENT_BUILDER_GENERATING_PROMPT)
            ),
        ).code

    try:
        if not self.agent_builder_registry:
            raise ValueError("AgentBuilder registry is not configured")

        plan_params = extract_plan_parameters(state["plan"])
        instructions_payload = {
            "plan": state["plan"],
            "script": python_code,
            "params": plan_params,
        }
        extracted_tools = extract_code_tools(python_code)
        tool_dict = convert_tool_ids_to_dict(extracted_tools)
        res = self.agent_builder_registry.upsert_agent(
            name=agent_name,
            description=agent_description,
            instructions=instructions_payload,
            tools=tool_dict,
        )
        writer(
            {
                "type": "custom",
                "id": generation_id,
                "name": "generating",
                "data": {
                    "id": str(res.id),
                    "update": bool(self.agent),
                    "name": agent_name,
                    "description": agent_description,
                },
            }
        )
        tool_result = {
            "id": str(res.id),
            "update": bool(self.agent),
            "name": agent_name,
            "description": agent_description,
            "message": "Successfully saved the agent code and plan.",
        }
    except Exception:
        extracted_tools = extract_code_tools(python_code)
        tool_result = f"Displaying the final saved code:\n\n{python_code}\nFinal Name: {agent_name}\nDescription: {agent_description} Saved Tools: {extracted_tools}"

    if "functions" not in effective_previous_add_context:
        effective_previous_add_context["functions"] = []
    effective_previous_add_context["functions"].append(python_code)

    return tool_result, effective_previous_add_context, agent_name, agent_description
