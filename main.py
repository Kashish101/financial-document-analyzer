from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()

from tools import read_data_tool

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis",
    version="1.0.0"
)

# Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def run_analysis(query: str, file_path: str) -> str:
    """Analyze financial document using Gemini directly."""
    
    # Read the PDF text
    document_text = read_data_tool.run(file_path)

    if not document_text:
        raise ValueError("Could not extract text from document.")

    prompt = f"""
You are a Senior Financial Analyst.

Analyze the following financial document and answer this query:
{query}

FINANCIAL DOCUMENT:
{document_text[:50000]}

Please provide:
1. Executive Summary
2. Key Financial Metrics (with actual numbers)
3. Trend Analysis
4. Notable Highlights and Risk Factors
5. Investment Insights

Base ALL findings strictly on the document.
Include disclaimer that this is for informational purposes only.
"""

    # ✅ ACTUAL GEMINI CALL (this was missing)
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )

    return response.text


@app.get("/")
async def root():
    return {
        "message": "Financial Document Analyzer API is running",
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    Analyze a financial document and provide comprehensive investment insights.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        with open(file_path, "wb") as f:
            f.write(content)

        if not query or not query.strip():
            query = "Analyze this financial document for investment insights"

        analysis_result = run_analysis(
            query=query.strip(),
            file_path=file_path
        )

        return {
            "status": "success",
            "query": query,
            "analysis": analysis_result,
            "file_processed": file.filename
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)