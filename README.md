# 🪶 Pakshi Search

Pakshi Search is a vectorless Retrieval-Augmented Generation (RAG) application for exploring Indian bird species.

Instead of embeddings and vector databases, the system uses MongoDB Atlas Search (Apache Lucene / BM25) for retrieval and Groq Llama 3 for answer generation.

---

## Live Demo

Frontend: Coming Soon

Backend API: Coming Soon

---

## Features

- Vectorless RAG architecture
- MongoDB Atlas Search (BM25 / Lucene)
- FastAPI backend
- React + Vite frontend
- Groq Llama 3 powered responses
- Wikipedia-based bird knowledge base
- Source attribution for answers

---

## Architecture

```text
Wikipedia Articles
        ↓
    scraper.py
        ↓
MongoDB Atlas Collection
        ↓
Atlas Search Index (BM25)
        ↓
     User Query
        ↓
      FastAPI
        ↓
   Atlas Search
        ↓
Retrieved Documents
        ↓
   Groq Llama 3
        ↓
      Answer
        ↓
      React UI
```

---

## Why Vectorless RAG?

Most RAG systems rely on embeddings and vector similarity search.

Pakshi Search demonstrates an alternative approach using traditional information retrieval through BM25 ranking.

### Advantages

- No embedding generation
- No vector database
- Lower infrastructure complexity
- Explainable retrieval scores
- Faster ingestion pipeline

### Tradeoffs

- Retrieval is keyword-dependent
- Semantic matching may be weaker than vector search
- Performance depends on document quality and search terms

---

## Tech Stack

| Layer | Technology |
|---------|------------|
| Retrieval | MongoDB Atlas Search (BM25 / Lucene) |
| Generation | Groq Llama 3 |
| Backend | FastAPI |
| Frontend | React + Vite |
| Database | MongoDB Atlas |
| Data Source | Wikipedia |
| Deployment | Render + Vercel |

---

## Project Structure

```text
pakshi-search/
├── backend/
│   ├── scraper.py
│   ├── rag.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    ├── package-lock.json
    ├── index.html
    └── .env.example
```

---

## Setup

### 1. Create MongoDB Atlas Cluster

Create a free MongoDB Atlas M0 cluster.

### 2. Create Database User

Create a database user with read/write permissions.

### 3. Configure Network Access

Add your current IP address under:

```text
Security → Network Access
```

### 4. Create Database and Collection

Database:

```text
pakshi_vectorless
```

Collection:

```text
bird_knowledge
```

### 5. Install Backend Dependencies

```bash
conda create -n pakshi-search python=3.11 -y
conda activate pakshi-search

cd backend
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file:

```env
MONGO_URI=your_mongodb_connection_string
GROQ_API_KEY=your_groq_api_key
```

### 7. Ingest Bird Knowledge

```bash
python scraper.py
```

This will scrape bird species information from Wikipedia and store it in MongoDB Atlas.

### 8. Verify Data Ingestion

Count all documents:

```javascript
db.bird_knowledge.countDocuments()
```

View a sample document:

```javascript
db.bird_knowledge.findOne(
  { species: "Indian Peafowl" }
)
```

Example document:

```json
{
  "species": "Indian Peafowl",
  "content": "...",
  "metadata": {
    "source": "Wikipedia",
    "url": "https://en.wikipedia.org/wiki/Indian_peafowl"
  }
}
```

### 9. Create Atlas Search Index

Navigate to:

```text
Atlas → Search → Create Search Index
```

Index Name:

```text
default
```

Configuration:

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "content": {
        "type": "string"
      },
      "species": {
        "type": "string"
      }
    }
  }
}
```

### 10. Verify Atlas Search

Run the following aggregation in Atlas Query Editor:

```javascript
db.bird_knowledge.aggregate([
  {
    $search: {
      index: "default",
      text: {
        query: "Indian Peafowl",
        path: "content"
      }
    }
  },
  {
    $project: {
      species: 1,
      score: { $meta: "searchScore" }
    }
  },
  {
    $limit: 5
  }
])
```

Expected result:

```text
Indian Peafowl
score: ...
```

This confirms that Atlas Search is functioning correctly.

### 11. Run Backend

```bash
uvicorn main:app --reload
```

Backend:

```text
http://localhost:8000
```

### 12. Run Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## API Endpoints

### Health Check

```http
GET /health
```

### Query

```http
POST /query
```

Request:

```json
{
  "question": "Where was the Great Hornbill recorded in the 1860s?"
}
```

Response:

```json
{
  "answer": "The Great Hornbill was recorded in the Kolli Hills during the 1860s.",
  "sources": [
    {
      "species": "Great Hornbill",
      "source": "Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Great_hornbill"
    }
  ],
  "retrieval_method": "Atlas Search (BM25 / Lucene)",
  "latency_seconds": 1.2
}
```

---

## Example Questions

- What do Indian Peafowl eat?
- Describe the habitat of the Sarus Crane.
- Where was the Great Hornbill recorded in the 1860s?
- What are the conservation threats faced by the Great Indian Bustard?
- What is the conservation status of the Sarus Crane?
- Describe the behavior of the Shikra.

---

## Future Improvements

- Passage-level retrieval
- Hybrid BM25 + Vector Search
- Bird image enrichment
- Additional ornithology datasets

---

## Related Project

### Pakshi AI

An AI-powered bird identification and knowledge assistant.

Features:

- Bird image classification
- Bird audio recognition
- FAISS vector search
- LangChain-powered RAG
- Hugging Face deployment

Repository:

```text
https://github.com/sachinprabhu007/Pakshi-AI
```

---

## Data Source

Wikipedia bird species articles (CC BY-SA 4.0)

---

## License

MIT License

---
## Author

Made with ❤️ by Sachin Prabhu