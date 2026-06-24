from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import ask
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Pakshi Vectorless API",
    description="Vectorless Bird RAG using MongoDB Atlas Search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list
    retrieval_method: str
    # route: str
    latency_seconds: float


@app.get("/health")
def health():
    return {"status": "ok", "service": "pakshi-vectorless"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        result = ask(req.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))