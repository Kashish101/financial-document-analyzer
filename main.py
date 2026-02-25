from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid

from crewai import Crew, Process
from agents import financial_analyst
# BUG FIX 1: Name collision - the imported task and the endpoint function both named
# 'analyze_financial_document'. Renamed the import to avoid shadowing.
from task import analyze_financial_document as analyze_task

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis using CrewAI agents",
    version="1.0.0"
)


def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """Run the CrewAI financial analysis crew."""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_task],
        process=Process.sequential,
        verbose=True,
    )
    # BUG FIX 2: file_path was passed to run_crew but never forwarded to the crew/task.
    # The task uses read_data_tool which needs the path. We inject it via the inputs dict.
    result = financial_crew.kickoff(inputs={'query': query, 'file_path': file_path})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running", "status": "healthy"}


@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    Analyze a financial document and provide comprehensive investment insights.

    - **file**: PDF financial document to analyze
    - **query**: Specific question or analysis focus (optional)
    """
    # BUG FIX 3: No file type validation - anyone could upload non-PDFs
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        content = await file.read()

        # BUG FIX 4: No file size check - could accept empty or enormous files
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        with open(file_path, "wb") as f:
            f.write(content)

        # Validate / default query
        if not query or not query.strip():
            query = "Analyze this financial document for investment insights"

        # Process the financial document with CrewAI
        response = run_crew(query=query.strip(), file_path=file_path)

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except HTTPException:
        raise  # re-raise our own HTTP errors unchanged

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
