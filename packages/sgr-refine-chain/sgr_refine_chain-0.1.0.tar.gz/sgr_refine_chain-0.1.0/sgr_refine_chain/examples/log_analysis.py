import asyncio
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from sgr_refine_chain.agent import create_sgr_refine_agent


class LogSummary(BaseModel):
    """Structured summary of key events in system logs."""
    main_issue: str = Field(description="Main issue detected in the logs")
    affected_services: List[str] = Field(description="Services involved in the incident")
    timeline: List[str] = Field(description="Chronological list of key log events")
    resolution_hint: str = Field(description="Suggested resolution or next investigation step")


async def main():
    # Initialize the LLM with structured output enabled
    llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(LogSummary)

    # Create an SGR Refine Agent
    agent = create_sgr_refine_agent(
        llm=llm,
        schema_class=LogSummary,
        question_prompt_template=(
            "You are an SRE engineer. Analyze the following log fragment and produce "
            "a structured summary according to the LogSummary schema:\n\n{text}"
        ),
        refine_prompt_template=(
            "Here is the previous analysis:\n{existing_answer}\n\n"
            "Now update and refine it with the new log fragment:\n{text}\n\n"
            "Add new details if needed (e.g., new services, updated sequence of events)."
        ),
        content_field="remaining_chunks",
    )

    # Example: long logs split into several chunks
    docs = [
        Document(page_content="2025-11-12 14:02:10 [payments-api] Timeout while calling user-service"),
        Document(page_content="2025-11-12 14:02:11 [user-service] Failed to connect to PostgreSQL database"),
        Document(page_content="2025-11-12 14:02:14 [monitoring] Detected increased latency in payments-api"),
    ]

    # Run the iterative SGR refine process
    result = await agent.ainvoke({"remaining_chunks": docs})
    summary = result["output"]

    print("\nFinal Log Analysis:")
    print(summary.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
