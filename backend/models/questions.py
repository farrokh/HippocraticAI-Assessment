from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Relationship

from models.generation import Generation

if TYPE_CHECKING:
    from models.duel import Duel

class Question(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str
    created_at: datetime = Field(default_factory=datetime.now)
    selected_generation_id: Optional[int] = Field(default=None, foreign_key="generation.id")
    
    # Relationship
    duels: List["Duel"] = Relationship(
        back_populates="question",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class QuestionWithSelectedGeneration(BaseModel):
    id: int
    text: str
    created_at: datetime
    selected_generation_id: Optional[int]
    selected_generation: Optional[Generation]


class QuestionResults(BaseModel):
    question: Question
    selected_generation: Optional[Generation]
    generation_performance: List[Dict[str, Any]]
