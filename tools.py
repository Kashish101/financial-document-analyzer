## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# BUG FIX 1: Wrong import - 'tools' is not a valid import from crewai_tools
# was: from crewai_tools import tools
from crewai_tools import SerperDevTool

# BUG FIX 2: SerperDevTool was imported from wrong submodule path
# was: from crewai_tools.tools.serper_dev_tool import SerperDevTool
# fix: use the top-level import above

# BUG FIX 3: Pdf class was never imported - added langchain_community import
from langchain_community.document_loaders import PyPDFLoader

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class FinancialDocumentTool():
    # BUG FIX 4: Method was async but called synchronously by CrewAI tools - changed to sync
    # BUG FIX 5: Missing @staticmethod decorator - caused TypeError (self not passed)
    @staticmethod
    def read_data_tool(path: str = 'data/sample.pdf') -> str:
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Financial Document file
        """
        # BUG FIX 6: Pdf(...).load() is not valid - PyPDFLoader is the correct class
        loader = PyPDFLoader(file_path=path)
        docs = loader.load()

        full_report = ""
        for data in docs:
            # Clean and format the financial document data
            content = data.page_content

            # Remove extra whitespaces and format properly
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")

            full_report += content + "\n"

        return full_report


## Creating Investment Analysis Tool
class InvestmentTool:
    # BUG FIX 7: async not needed for a simple data processing utility
    @staticmethod
    def analyze_investment_tool(financial_document_data: str) -> str:
        """Analyze investment opportunities from financial document data."""
        # Process and clean the financial document data
        processed_data = financial_document_data

        # Clean up the data format (remove double spaces)
        i = 0
        result = []
        prev_space = False
        for char in processed_data:
            if char == ' ':
                if not prev_space:
                    result.append(char)
                prev_space = True
            else:
                result.append(char)
                prev_space = False
        processed_data = ''.join(result)

        return processed_data


## Creating Risk Assessment Tool
class RiskTool:
    # BUG FIX 8: async not needed for a simple utility
    @staticmethod
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        """Create risk assessment from financial document data."""
        return financial_document_data
