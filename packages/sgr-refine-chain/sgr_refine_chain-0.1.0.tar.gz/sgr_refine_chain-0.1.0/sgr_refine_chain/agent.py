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
    Универсальный агент SGR-Refine для LangGraph.

    Алгоритм:
      1. Первый чанк анализируется по question_prompt_template → создаётся Schema.
      2. Каждый следующий чанк уточняет Schema по refine_prompt_template.
      3. Если указан merge_fn — объединяет два объекта Schema.
      4. Возвращает итоговый Pydantic-объект и (опционально) промежуточные результаты.
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
        self.q_prompt = PromptTemplate.from_template(self.question_prompt_template)
        self.r_prompt = PromptTemplate.from_template(self.refine_prompt_template)

    async def ainvoke(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        docs: Sequence[Document] = state.get(self.content_field, [])
        if not docs:
            raise ValueError(f"[SGRRefineAgent] Поле '{self.content_field}' пусто — нечего анализировать")

        base_inputs = dict(state)
        intermediate: list[T] = []

        # --- Первый чанк ---
        base_inputs["text"] = docs[0].page_content
        q_input = self.q_prompt.format(**base_inputs)

        try:
            result: T = await self.llm.ainvoke(q_input)  # type: ignore
        except Exception:
            logger.exception("[SGRRefineAgent] Ошибка structured LLM на первом шаге")
            raise

        intermediate.append(result)

        # --- Refine шаги ---
        for doc in docs[1:]:
            base_inputs["text"] = doc.page_content
            base_inputs["existing_answer"] = result.model_dump_json()
            refine_input = self.r_prompt.format(**base_inputs)

            try:
                new_result: T = await self.llm.ainvoke(refine_input)  # type: ignore
            except ValidationError as e:
                logger.warning(f"[SGRRefineAgent] Ошибка валидации {self.schema_class.__name__}: {e}")
                continue
            except Exception:
                logger.exception("[SGRRefineAgent] Ошибка structured LLM на refine-шаге")
                continue

            if self.merge_fn:
                try:
                    result = self.merge_fn(result, new_result)
                except Exception:
                    logger.exception("[SGRRefineAgent] Ошибка merge_fn — оставляем предыдущий результат")
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
    """Фабрика для создания универсального SGRRefineAgent."""
    return SGRRefineAgent(
        llm=llm,
        schema_class=schema_class,
        question_prompt_template=question_prompt_template,
        refine_prompt_template=refine_prompt_template,
        content_field=content_field,
        merge_fn=merge_fn,
        return_intermediate=return_intermediate,
    )
