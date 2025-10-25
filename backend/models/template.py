from datetime import datetime
from sqlmodel import Field, SQLModel

class Template(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    key: str
    name: str
    template_text: str
    created_at: datetime = Field(default_factory=datetime.now)
