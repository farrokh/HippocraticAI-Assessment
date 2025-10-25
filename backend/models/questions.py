from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

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