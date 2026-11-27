from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agent.agent import run_agent


app = FastAPI(
    title="Text-to-SQL Agent API",
    description="REST API for converting natural-language questions into SQL queries.",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Natural-language question about the database",
        examples=["How many customers are there?"],
    )


@app.get("/")
def home():
    return {
        "message": "Text-to-SQL Agent API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = run_agent(question)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )
