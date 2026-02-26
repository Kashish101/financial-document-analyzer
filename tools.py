import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from langchain_community.document_loaders import PyPDFLoader

## Search tool - lazy import to avoid embedchain conflicts
def get_search_tool():
    from crewai_tools import SerperDevTool
    return SerperDevTool()

search_tool = None  # Only load if needed

@tool("read_financial_document")
def read_data_tool(path: str) -> str:
    """Reads and extracts text content from a PDF financial document.
    Use this tool to read the contents of a financial report or document.
    Pass the full file path to the PDF you want to read.

    Args:
        path (str): Full file path to the PDF document.

    Returns:
        str: Extracted text content from the PDF.
    """
    loader = PyPDFLoader(file_path=path)
    docs = loader.load()

    full_report = ""
    for data in docs:
        content = data.page_content
        while "\n\n" in content:
            content = content.replace("\n\n", "\n")
        full_report += content + "\n"

    return full_report


class FinancialDocumentTool:
    read_data_tool = read_data_tool