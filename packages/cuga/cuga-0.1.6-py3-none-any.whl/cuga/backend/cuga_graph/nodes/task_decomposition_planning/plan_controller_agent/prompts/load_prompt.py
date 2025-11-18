from typing import List, Literal, Union
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, field_validator


class PlanControllerOutput(BaseModel):
    thoughts: List[str] = Field(..., description="Your thoughts")
    subtasks_progress: List[Literal['completed', 'not-started', 'in-progress']] = Field(
        ..., description="Subtasks progress"
    )
    next_subtask: str = Field(
        default="", description="next subtask description (empty if conclude_task is true)"
    )
    next_subtask_type: Union[Literal['api', 'web'], None, Literal[""]] = Field(
        default=None, description="next subtask type (null or empty if conclude_task is true)"
    )
    next_subtask_app: str = Field(default="", description="next subtask app (empty if conclude_task is true)")
    conclude_task: bool = Field(..., description="Should the original task be concluded?")
    conclude_final_answer: str = Field(..., description="Final answer in case final task is concluded")

    @field_validator('next_subtask_type', mode='before')
    @classmethod
    def convert_empty_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


parser = PydanticOutputParser(pydantic_object=PlanControllerOutput)
