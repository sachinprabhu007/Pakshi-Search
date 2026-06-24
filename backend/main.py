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
    
from urllib.parse import urlparse

@app.get("/debug")
def debug():
    uri = os.getenv("MONGO_URI")

    return {
        "exists": bool(uri),
        "length": len(uri) if uri else 0,
        "endswith_newline": uri.endswith("\n") if uri else False,
        "startswith_mongodb_srv": uri.startswith("mongodb+srv://") if uri else False,
    }

from pymongo import MongoClient
import os

@app.get("/mongo-debug")
def mongo_debug():
    try:
        client = MongoClient(
            os.getenv("MONGO_URI"),
            serverSelectionTimeoutMS=5000
        )
        client.admin.command("ping")
        return {"status": "connected"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}