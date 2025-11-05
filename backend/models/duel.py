from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from pydantic import BaseModel
from models.generation import Generation
from models.questions import Question


class DuelGeneration(SQLModel, table=True):
    """Junction table for many-to-many relationship between Duel and Generation"""
    duel_id: int = Field(foreign_key="duel.id", primary_key=True)
    generation_id: int = Field(foreign_key="generation.id", primary_key=True)
    role: str = Field()  # "generation_a", "generation_b", or "winner"


class Duel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    
    # Foreign keys for the database
    question_id: int = Field(foreign_key="question.id")
    winner_id: Optional[int] = Field(default=None, foreign_key="generation.id")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    decided_at: Optional[datetime] = Field(default=None)


class DecideDuelRequest(BaseModel):
    winner_id: int


class DuelWithGenerations(BaseModel):
    id: int
    winner_id: Optional[int]
    created_at: datetime
    decided_at: Optional[datetime]
    # Instead of question_id, we include the full question object
    question: Question
    generation_a: Generation
    generation_b: Generation
