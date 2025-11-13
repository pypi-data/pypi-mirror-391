import asyncio
import functools, operator
import logging
from typing import List, TypedDict, Annotated
from langchain_core.messages import BaseMessage

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from sgr_refine_chain.agent import create_sgr_refine_agent
from sgr_refine_chain.async_node import agent_node_async


# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


class LogSummary(BaseModel):
    """Structured summary of logs used inside the graph."""
    main_issue: str = Field(description="Main issue detected in the logs")
    affected_services: List[str] = Field(description="Services involved in the incident")
    timeline: List[str] = Field(description="Chronological list of key log events")
    resolution_hint: str = Field(description="Suggested resolution or next step")


async def main():
    # Initialize LLM with structured output support
    llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(LogSummary)

    # Create SGR Refine Agent
    log_analyzer_agent = create_sgr_refine_agent(
        llm=llm,
        schema_class=LogSummary,
        question_prompt_template=(
            "You are an SRE engineer. Analyze the first log fragment and "
            "produce a structured summary according to the LogSummary schema:\n\n{text}"
        ),
        refine_prompt_template=(
            "Here is the previous structured summary:\n{existing_answer}\n\n"
            "Update and refine it using the new log fragment:\n{text}\n\n"
            "Add any new details if necessary."
        ),
        content_field="remaining_chunks",
    )

    # Wrap the agent into a LangGraph node
    log_analyzer_node = functools.partial(
        agent_node_async, agent=log_analyzer_agent, name="log_analyzer"
    )

    # Define graph state schema
    class GraphState(TypedDict, total=False):
        remaining_chunks: List[Document]
        structured_output: LogSummary | None = None
        messages: Annotated[List[BaseMessage], operator.add]

    # Create a minimal LangGraph
    graph = StateGraph(GraphState)

    # Add nodes and transitions
    graph.add_node("analyze_logs", log_analyzer_node)
    graph.set_entry_point("analyze_logs")
    graph.add_edge("analyze_logs", END)

    # Compile the graph into an async app
    app = graph.compile()

    # Example logs split into chunks
    docs = [
        Document(page_content="[payments-api] Timeout while calling user-service"),
        Document(page_content="[user-service] Failed to connect to PostgreSQL"),
        Document(page_content="[monitoring] Detected increased latency"),
    ]

    # Execute the graph
    result = await app.ainvoke(GraphState(remaining_chunks=docs))
    print("\nFinal structured output:\n")
    print(result["structured_output"].model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
