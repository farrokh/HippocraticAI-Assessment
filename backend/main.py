from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from routers import templates, questions, generations

app = FastAPI(
    title="Interview API",
    description="API for managing templates, questions, generations, and duels",
    version="1.0.0"
)

# Include routers
app.include_router(templates.router)
app.include_router(questions.router)
app.include_router(generations.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Interview API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
