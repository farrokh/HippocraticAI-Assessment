from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

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
    
    # Relationships
    question: Question = Relationship(back_populates="duels")
    winner: Optional[Generation] = Relationship(
        sa_relationship_kwargs={"overlaps": "duels"}
    )
    
    # Many-to-many relationship with Generation through junction table
    generations: List[Generation] = Relationship(
        back_populates="duels",
        link_model=DuelGeneration
    )
