from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Duel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    generation_a_id: int = Field(foreign_key="generation.id")
    generation_b_id: int = Field(foreign_key="generation.id")
    winner_id: Optional[int] = Field(default=None, foreign_key="generation.id")
    created_at: datetime = Field(default_factory=datetime.now)
    decided_at: Optional[datetime] = Field(default=None)