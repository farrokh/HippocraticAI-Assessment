from sqlmodel import SQLModel, create_engine, Session

# Import all models so they register with SQLModel.metadata
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session