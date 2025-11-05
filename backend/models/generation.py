from sqlmodel import Field, SQLModel
from datetime import datetime


class Generation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="template.id")
    question_id: int = Field(foreign_key="question.id")
    output_text: str
    llm_model: str
    latency: float
    output_tokens: int
    input_tokens: int
    created_at: datetime = Field(default_factory=datetime.now)