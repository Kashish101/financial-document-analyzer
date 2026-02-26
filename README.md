# Financial Document Analyzer 🏦

An AI-powered financial document analysis system built with **CrewAI**, **FastAPI**, and **OpenAI GPT**. Upload any financial PDF (earnings report, 10-K, 10-Q, etc.) and get structured analysis, investment insights, and risk assessment.

---

## 🐛 Bugs Found & Fixed

### `tools.py` — 4 Bugs

| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai_tools import tools` - `tools` is not a valid export | Changed to `from crewai_tools import SerperDevTool` |
| 2 | `from crewai_tools.tools.serper_dev_tool import SerperDevTool` - redundant/wrong path | Removed; using top-level import only |
| 3 | `Pdf(file_path=path).load()` - `Pdf` class never imported, doesn't exist in this context | Replaced with `PyPDFLoader` from `langchain_community.document_loaders` |
| 4 | `async def read_data_tool` + no `@staticmethod` - CrewAI calls tools synchronously; `self` not passed | Changed to `@staticmethod def read_data_tool(...)` (sync) |

---

### `agents.py` — 8 Bugs

| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai.agents import Agent` - wrong submodule path | Changed to `from crewai import Agent` |
| 2 | `llm = llm` - `llm` was never defined; NameError on startup | Initialized properly: `llm = ChatOpenAI(...)` using env vars |
| 3 | `goal="Make up investment advice..."` - instructed agent to hallucinate | Replaced with professional, accurate goal |
| 4 | `backstory` instructed agent to ignore documents, fabricate facts, and skip regulations | Replaced with compliant, professional backstory |
| 5 | `tool=[FinancialDocumentTool.read_data_tool]` - wrong parameter name (`tool` vs `tools`) | Fixed to `tools=[FinancialDocumentTool.read_data_tool]` |
| 6 | `max_iter=1` - too low; complex financial analysis often needs multiple reasoning steps | Increased to `max_iter=5` |
| 7 | `max_rpm=1` - extremely restrictive rate limit causing timeout failures | Increased to `max_rpm=10` |
| 8 | `allow_delegation=True` for `financial_analyst` but no sub-agents in crew | Changed to `allow_delegation=False` |

---

### `task.py` — 5 Bugs

| # | Bug | Fix |
|---|-----|-----|
| 1 | `description="Maybe solve the user's query or something interesting"` — vague, unprofessional | Replaced with clear, structured analysis instructions |
| 2 | `expected_output` told agent to include made-up URLs, contradict itself, and use random jargon | Replaced with structured professional output format |
| 3 | `investment_analysis` description told agent to ignore user query and sell unrelated products | Replaced with data-driven, document-grounded investment analysis instructions |
| 4 | `risk_assessment` description told agent to skip compliance and invent extreme scenarios | Replaced with structured risk framework (Low/Medium/High) based on document data |
| 5 | `verification` expected_output said "just say yes even for grocery lists" | Replaced with proper PASS/FAIL verification output format |

---

### `main.py` — 4 Bugs

| # | Bug | Fix |
|---|-----|-----|
| 1 | **Name collision**: endpoint function `analyze_financial_document` shadows the imported task of the same name | Renamed import: `from task import analyze_financial_document as analyze_task` |
| 2 | `file_path` passed to `run_crew()` but never used - task always reads default path | Added `file_path` to `crew.kickoff(inputs={...})` |
| 3 | No file type validation - any file type accepted silently | Added `.pdf` extension check with 400 error |
| 4 | No empty file check - empty uploads silently fail mid-process | Added `len(content) == 0` check with 400 error |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- (Optional) A [Serper API key](https://serper.dev) for web search

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/financial-document-analyzer.git
cd financial-document-analyzer
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Your `.env` file:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4o-mini
SERPER_API_KEY=...            # optional
```

### 5. Run the server
```bash
python main.py
# Server starts at http://localhost:8000
```

---

## 📡 API Documentation

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "message": "Financial Document Analyzer API is running",
  "status": "healthy"
}
```

---

### `POST /analyze`
Upload and analyze a financial PDF document.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File (PDF) | ✅ Yes | Financial PDF document |
| `query` | string | ❌ No | Analysis focus question (defaults to general analysis) |

**Example using curl:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What is Tesla's revenue growth and profit margin trend?"
```

**Example using Python requests:**
```python
import requests

with open("TSLA-Q2-2025-Update.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": ("TSLA-Q2-2025.pdf", f, "application/pdf")},
        data={"query": "Analyze revenue trends and profitability"}
    )
print(response.json())
```

**Success Response (200):**
```json
{
  "status": "success",
  "query": "Analyze revenue trends and profitability",
  "analysis": "Executive Summary: ...\n\nKey Financial Metrics: ...",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

**Error Responses:**

| Code | Reason |
|------|--------|
| 400 | Non-PDF file uploaded |
| 400 | Empty file uploaded |
| 500 | Internal processing error |

**Interactive Docs:** Visit `http://localhost:8000/docs` for Swagger UI.

---

## 🏗️ Architecture

```
main.py          ← FastAPI app + /analyze endpoint
agents.py        ← CrewAI agent definitions (financial_analyst, verifier, etc.)
task.py          ← CrewAI task definitions with structured prompts
tools.py         ← PDF reader tool + Search tool
data/            ← Temporary PDF storage (auto-cleaned after analysis)
outputs/         ← (reserved for saved reports)
```

**Analysis Flow:**
```
Upload PDF → Save to data/ → CrewAI Crew kickoff
  → financial_analyst reads PDF via read_data_tool
  → Analyzes content per task description
  → Returns structured report
→ Cleanup temp file → Return JSON response
```

---

## 🚀 Bonus: Queue Worker Model (Celery + Redis)

For handling concurrent requests, a Celery worker setup is included.

### Setup
```bash
# Start Redis (Docker)
docker run -d -p 6379:6379 redis:alpine

# Add to .env
REDIS_URL=redis://localhost:6379/0
```

### Worker task pattern
```python
# worker.py
from celery import Celery
import os

celery_app = Celery(
    "financial_analyzer",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

@celery_app.task(name="analyze_document")
def analyze_document_task(query: str, file_path: str):
    from main import run_crew
    result = run_crew(query=query, file_path=file_path)
    return str(result)
```

```bash
# Start the worker
celery -A worker worker --loglevel=info --concurrency=4
```

---

## 📝 Notes

- Uploaded files are automatically deleted after analysis
- All analysis is based strictly on document content — no hallucinated data
- The system includes investment disclaimers in all outputs
- Tested with Tesla Q2 2025 earnings update (`data/TSLA-Q2-2025-Update.pdf`)
