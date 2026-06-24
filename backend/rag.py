from pymongo import MongoClient
from groq import Groq
from dotenv import load_dotenv
import os
import time

load_dotenv()

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

client = MongoClient(os.getenv("MONGO_URI"))
collection = client["pakshi_vectorless"]["bird_knowledge"]
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def route_query(question: str) -> str:
    """
    Route query to the right retrieval method.
    - factual: biology, habitat, behavior, diet → Atlas Search
    - observational: sightings, counts, locations → aggregation pipeline
    - general: broad questions → Atlas Search
    """
    prompt = f"""Classify this bird-related question into exactly one category:
- factual: asks about species biology, habitat, diet, behavior, appearance, migration, or conservation
- observational: asks about specific sightings, counts, locations, dates, or observation records
- general: broad or multi-species question

Question: {question}

Reply with only one word: factual | observational | general"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )
    route = response.choices[0].message.content.strip().lower()
    if route not in ["factual", "observational", "general"]:
        return "general"
    return route


def atlas_search(query: str, limit: int = 4) -> list:
    """Full-text search using MongoDB Atlas Search (BM25/Lucene)."""

    logging.info(f"[ATLAS SEARCH] Query: {query}")

    pipeline = [
        {
            "$search": {
                "index": "default",
                "text": {
                    "query": query,
                    "path": "content",
                    "fuzzy": {"maxEdits": 1}
                }
            }
        },
        {"$limit": limit},
        {
            "$project": {
                "species": 1,
                "content": 1,
                "metadata": 1,
                "score": {"$meta": "searchScore"}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))

    logging.info(
        f"[ATLAS SEARCH] Retrieved {len(results)} documents"
    )

    for doc in results:
        logging.info(
            f"  -> {doc.get('species')} "
            f"(score={round(doc.get('score', 0), 2)})"
        )

    return results

def structured_query(question: str, limit: int = 4) -> list:
    """Aggregation pipeline for observation-type queries."""
    # Extract species hint from question using LLM
    prompt = f"""Extract the bird species name from this question. 
If no specific species is mentioned, reply with 'none'.
Question: {question}
Reply with only the species name or 'none'."""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )
    species_hint = response.choices[0].message.content.strip()

    logging.info(f"[STRUCTURED QUERY] Species Hint: {species_hint}")

    if species_hint.lower() == "none":
        # Fall back to atlas search
        return atlas_search(question, limit)

    results = list(collection.find(
        {"species": {"$regex": species_hint, "$options": "i"}},
        {"species": 1, "content": 1, "metadata": 1}
    ).limit(limit))

    # If nothing found, fall back to atlas search
    if not results:
        return atlas_search(question, limit)
    
    logging.info(
    f"[STRUCTURED QUERY] Retrieved {len(results)} documents"
    )  

    return results


def generate_answer(question: str, docs: list) -> str:
    """Pass retrieved documents to Groq for answer generation."""

    logging.info(f"[GENERATION] Using {len(docs)} documents as context")
    
    context = "\n\n---\n\n".join([
        f"Species: {d.get('species', 'Unknown')}\n{d.get('content', '')[:5000]}"
        for d in docs
    ])


    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert ornithologist specializing in birds.\n\n"
                    "Answer questions using ONLY the provided context.\n"
                    "Do not use any outside knowledge.\n"
                    "You may summarize, paraphrase, and explain information found in the context.\n"
                    "If the context contains partially relevant information, provide the available information.\n"
                    "Only state that the information is unavailable if no relevant information exists in the context.\n"
                    "Be concise, accurate, and informative."
                )
            },
            {
            "role": "user",
            "content": (
                f"Use the context below to answer the question.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                f"Answer using only the provided context."
                 )
            }
        ],
        max_tokens=1000
    )
    logging.info("[GENERATION] Answer generated successfully")
    return response.choices[0].message.content


def ask(question: str) -> dict:
    """Full RAG pipeline: route → retrieve → generate."""

    start = time.time()

    # route = route_query(question)

    # logging.info("=" * 80)
    # logging.info(f"[QUESTION] {question}")
    # logging.info(f"[ROUTER] Selected route: {route}")

    # if route == "observational":
    #     docs = structured_query(question)
    #     retrieval_method = "MongoDB Aggregation Pipeline"
    # else:
    #     docs = atlas_search(question)
    #     retrieval_method = "Atlas Search (BM25 / Lucene)"

    # logging.info(f"[RETRIEVAL] Method: {retrieval_method}")

    # answer = generate_answer(question, docs)

    docs = atlas_search(question)
    retrieval_method = "Atlas Search (BM25 / Lucene)"

    answer = generate_answer(question, docs)

    latency = round(time.time() - start, 2)

    logging.info(f"[COMPLETE] {latency}s")
    logging.info("=" * 80)

    return {
        "answer": answer,
        "sources": [
            {
                "species": d.get("species"),
                "source": d.get("metadata", {}).get("source", "Wikipedia"),
                "url": d.get("metadata", {}).get("url", "")
            }
            for d in docs
        ],
        "retrieval_method": retrieval_method,
        # "route": route,
        "latency_seconds": latency
    }