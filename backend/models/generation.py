from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from models.duel import Duel

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
    
    # Many-to-many relationship with Duel
    duels: List["Duel"] = Relationship(back_populates="generations")