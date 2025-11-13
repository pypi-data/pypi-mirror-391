import json
import logging
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


async def agent_node_async(state, agent, name: str):
    """
    Universal async node wrapper for LangGraph agents.

    Handles:
      - Safe serialization of structured (Pydantic) outputs
      - Logging of agent results
      - State propagation for next nodes
    """
    logger.info(f"\n--- Agent [{name}] started ---")

    result = await agent.ainvoke(state)
    output = result.get("output")

    # Safe serialization
    if isinstance(output, BaseModel):
        content = json.dumps(output.model_dump(), indent=2, ensure_ascii=False)
    elif isinstance(output, dict):
        content = json.dumps(output, indent=2, ensure_ascii=False)
    else:
        content = str(output)

    logger.info(f"\n--- Agent [{name}] result ---\n{content}\n")

    # Return updated graph state
    return {
        **state,
        "messages": [HumanMessage(content=content, name=name)],
        "structured_output": output,
    }
