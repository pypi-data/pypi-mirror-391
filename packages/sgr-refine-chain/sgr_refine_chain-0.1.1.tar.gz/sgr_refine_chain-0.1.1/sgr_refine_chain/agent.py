from __future__ import annotations

import logging
from typing import Any, Type, TypeVar, Generic, Callable, Optional
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from pydantic import BaseModel, ValidationError
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


@dataclass(slots=True, repr=True)
class SGRRefineAgent(Generic[T]):
    """
    Universal SGR-Refine Agent for LangGraph.

    Algorithm:
      1. The first chunk is processed with `question_prompt_template` → produces the base schema.
      2. Each subsequent chunk refines the schema using `refine_prompt_template`.
      3. If `merge_fn` is provided, merges the previous and new schema objects.
      4. Returns the final Pydantic object and (optionally) intermediate results.
    """

    llm: ChatOpenAI
    schema_class: Type[T]
    question_prompt_template: str
    refine_prompt_template: str
    content_field: str = "remaining_chunks"
    merge_fn: Optional[Callable[[T, T], T]] = None
    return_intermediate: bool = True
    q_prompt: PromptTemplate = field(init=False)
    r_prompt: PromptTemplate = field(init=False)

    def __post_init__(self):
        """Compile prompt templates."""
        self.q_prompt = PromptTemplate.from_template(self.question_prompt_template)
        self.r_prompt = PromptTemplate.from_template(self.refine_prompt_template)

    async def ainvoke(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Run the SGR-Refine cascade asynchronously."""
        # Support both dict and Pydantic-based state objects
        if hasattr(state, self.content_field):
            docs: Sequence[Document] = getattr(state, self.content_field) or []
        else:
            docs: Sequence[Document] = state.get(self.content_field, []) or []

        if not docs:
            raise ValueError(f"[SGRRefineAgent] Field '{self.content_field}' is empty — nothing to analyze")

        base_inputs = dict(state)
        intermediate: list[T] = []

        # --- Initial chunk ---
        base_inputs["text"] = docs[0].page_content
        q_input = self.q_prompt.format(**base_inputs)

        try:
            result: T = await self.llm.ainvoke(q_input)  # type: ignore
        except Exception:
            logger.exception("[SGRRefineAgent] Structured LLM error on initial step")
            raise

        intermediate.append(result)

        # --- Refinement steps ---
        for doc in docs[1:]:
            base_inputs["text"] = doc.page_content
            base_inputs["existing_answer"] = result.model_dump_json()
            refine_input = self.r_prompt.format(**base_inputs)

            try:
                new_result: T = await self.llm.ainvoke(refine_input)  # type: ignore
            except ValidationError as e:
                logger.warning(f"[SGRRefineAgent] Validation error in {self.schema_class.__name__}: {e}")
                continue
            except Exception:
                logger.exception("[SGRRefineAgent] Structured LLM error on refine step")
                continue

            if self.merge_fn:
                try:
                    result = self.merge_fn(result, new_result)
                except Exception:
                    logger.exception("[SGRRefineAgent] merge_fn error — keeping previous result")
            else:
                result = new_result

            intermediate.append(result)

        output: dict[str, Any] = {"output": result}
        if self.return_intermediate:
            output["intermediate_schemas"] = [r.model_dump() for r in intermediate]
        return output


def create_sgr_refine_agent(
    llm: ChatOpenAI,
    schema_class: Type[T],
    question_prompt_template: str,
    refine_prompt_template: str,
    content_field: str = "remaining_chunks",
    merge_fn: Optional[Callable[[T, T], T]] = None,
    return_intermediate: bool = True,
) -> SGRRefineAgent[T]:
    """Factory function to create a universal SGRRefineAgent instance."""
    return SGRRefineAgent(
        llm=llm,
        schema_class=schema_class,
        question_prompt_template=question_prompt_template,
        refine_prompt_template=refine_prompt_template,
        content_field=content_field,
        merge_fn=merge_fn,
        return_intermediate=return_intermediate,
    )
