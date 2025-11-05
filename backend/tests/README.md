# Backend Tests

This directory contains comprehensive tests for the backend API.

## Test Structure

- `conftest.py` - Test fixtures and configuration
- `test_models.py` - Database model tests
- `test_template_endpoints.py` - Template CRUD and performance endpoint tests
- `test_question_endpoints.py` - Question CRUD and duel management tests
- `test_llm_service.py` - LLM service tests with mocked OpenAI responses
- `test_background_tasks.py` - Background task tests
- `test_performance_service.py` - Performance calculation service tests
- `test_integration.py` - Integration tests for complete workflows

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# Using the test runner script
python run_tests.py

# Or directly with pytest
python -m pytest

# With verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_models.py

# Run specific test
python -m pytest tests/test_models.py::TestDatabaseModels::test_template_creation
```

### Test Coverage

The test suite covers:

1. **Database Models** - All SQLModel relationships and constraints
2. **Template Endpoints** - CRUD operations and performance calculations
3. **Question Endpoints** - CRUD operations and duel management
4. **LLM Service** - Template rendering and OpenAI integration (mocked)
5. **Background Tasks** - Generation and duel creation workflows
6. **Performance Services** - Win rate calculations and statistics
7. **Integration Tests** - Complete end-to-end workflows

### Test Features

- **Isolated Database** - Each test uses a temporary SQLite database
- **Mocked External Services** - OpenAI API calls are mocked for reliable testing
- **Comprehensive Coverage** - Tests cover happy paths, edge cases, and error conditions
- **Fast Execution** - Tests run quickly with mocked dependencies

### Test Data

Tests use fixtures defined in `conftest.py`:
- `sample_template` - Basic template for testing
- `sample_question` - Basic question for testing
- `sample_generation` - Basic generation for testing
- `mock_openai_response` - Mocked OpenAI API response

### Environment Variables

Tests automatically mock the `OPENAI_API_KEY` environment variable, so no real API key is required for testing.
