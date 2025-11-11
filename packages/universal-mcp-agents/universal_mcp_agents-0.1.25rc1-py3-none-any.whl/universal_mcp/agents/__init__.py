from typing import Literal
from universal_mcp.agents.codeact0 import CodeActPlaybookAgent
from universal_mcp.agents.react import ReactAgent
from universal_mcp.agents.simple import SimpleAgent


def get_agent(
    agent_name: Literal["react", "simple", "builder", "bigtool", "codeact-repl"],
):
    if agent_name == "react":
        return ReactAgent
    elif agent_name == "simple":
        return SimpleAgent
    elif agent_name == "codeact-repl":
        return CodeActPlaybookAgent
    else:
        raise ValueError(f"Unknown agent: {agent_name}. Possible values:  react, simple, codeact-repl")


__all__ = [
    "ReactAgent",
    "SimpleAgent",
    "CodeActPlaybookAgent",
    "get_agent",
]
