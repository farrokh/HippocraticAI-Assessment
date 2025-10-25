from datetime import datetime
from sqlmodel import Field, SQLModel

class Question(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str
    created_at: datetime = Field(default_factory=datetime.now)

    