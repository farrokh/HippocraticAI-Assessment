# Backend - LLM Tournament API

FastAPI backend for the LLM Tournament Widget application.

## Setup

### Prerequisites
- Python 3.13+
- OpenAI API Key

### Installation

1. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   pip install uv
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Initialize database:**
   ```bash
   python seed.py
   ```

4. **Run the server:**
   ```bash
   # Using uv (recommended)
   uv run main.py
   
   # Or with Python
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database

Uses SQLite with SQLModel ORM. The database file (`database.db`) is created automatically on first run.

## Project Structure

```
backend/
├── main.py           # FastAPI app entry point
├── db.py             # Database configuration
├── seed.py           # Database seeding script
├── models/           # SQLModel models
│   ├── template.py
│   ├── questions.py
│   ├── generation.py
│   └── duel.py
├── routers/          # API route handlers
│   ├── templates.py
│   └── questions.py
└── services/         # Business logic
    ├── llm.py
    ├── question.py
    └── performance.py
```
