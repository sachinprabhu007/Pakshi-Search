from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import ask
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

ENV = os.getenv("ENV", "development")

app = FastAPI(
    title="Pakshi Vectorless API",
    description="Vectorless Bird RAG using MongoDB Atlas Search",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    logging.info(f"[BOOT] Starting Pakshi Vectorless API ({ENV})")


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
    latency_seconds: float


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "pakshi-vectorless",
        "environment": ENV
    }


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        return ask(req.question)

    except Exception as e:
        logging.exception("[QUERY ERROR]")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# DEVELOPMENT ONLY ENDPOINTS
# These endpoints are available only when:
# ENV=development
# ==========================================================

if ENV == "development":

    from pymongo import MongoClient
    import ssl
    import pymongo
    import sys

    @app.get("/debug")
    def debug():
        uri = os.getenv("MONGO_URI")

        return {
            "exists": bool(uri),
            "length": len(uri) if uri else 0,
            "endswith_newline": uri.endswith("\n") if uri else False,
            "startswith_mongodb_srv": (
                uri.startswith("mongodb+srv://")
                if uri else False
            ),
        }


    @app.get("/mongo-debug")
    def mongo_debug():
        try:
            client = MongoClient(
                os.getenv("MONGO_URI"),
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=5000
            )

            client.admin.command("ping")

            return {
                "status": "connected"
            }

        except Exception as e:
            return {
                "type": type(e).__name__,
                "error": repr(e)
            }


    @app.get("/ssl-debug")
    def ssl_debug():
        return {
            "openssl": ssl.OPENSSL_VERSION
        }


    @app.get("/env-debug")
    def env_debug():
        return {
            "python": sys.version,
            "openssl": ssl.OPENSSL_VERSION,
            "pymongo": pymongo.version,
        }