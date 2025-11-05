import pytest
import tempfile
import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import all models so they register with SQLModel.metadata
from models.template import Template
from models.questions import Question
from models.generation import Generation
from models.duel import Duel, DuelGeneration

from main import app


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary database for each test - optimized with NullPool"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Create engine with NullPool to avoid connection pool issues
    engine = create_engine(
        f"sqlite:///{db_path}",
        poolclass=NullPool,  # Don't pool connections - each test gets fresh connection
        connect_args={"timeout": 1}  # Quick timeout for locks
    )
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except:
        pass  # Ignore cleanup errors


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a database session for testing"""
    with Session(test_db) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with a temporary database"""
    from db import get_db
    
    # Override the get_db dependency
    def override_get_db():
        with Session(test_db) as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up override
    app.dependency_overrides.clear()


@pytest.fixture
def sample_template():
    """Create a sample template for testing"""
    return Template(
        key="test_template",
        name="Test Template",
        template_text="Answer this question: {{question}}"
    )


@pytest.fixture
def sample_question():
    """Create a sample question for testing"""
    return Question(
        text="What is the capital of France?"
    )


@pytest.fixture
def sample_generation(sample_template, sample_question):
    """Create a sample generation for testing"""
    return Generation(
        template_id=sample_template.id,
        question_id=sample_question.id,
        output_text="The capital of France is Paris.",
        llm_model="gpt-4o-mini",
        latency=0.5,
        output_tokens=10,
        input_tokens=20
    )


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked response"
    mock_response.usage.completion_tokens = 10
    mock_response.usage.prompt_tokens = 20
    return mock_response


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client"""
    with patch('services.llm.OpenAI') as mock_client:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_openai_response
        mock_client.return_value = mock_instance
        yield mock_instance
