from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from routers import templates, questions

app = FastAPI(
    title="LLM Tournament Widget API",
    description="LLM Tournament Widget API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)

# Include routers
app.include_router(templates.router)
app.include_router(questions.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the LLM Tournament Widget API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
