import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from langchain_openai import ChatOpenAI
from tools import FinancialDocumentTool, read_data_tool

### Loading LLM
# Use Gemini via its OpenAI-compatible endpoint - bypasses litellm/VertexAI completely
llm = ChatOpenAI(
    model="gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    temperature=0.3
)

financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Thoroughly analyze the provided financial document to answer the user query: {query}. "
        "Extract key financial metrics, identify trends, evaluate financial health, and provide "
        "evidence-based investment insights grounded strictly in the document data."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a CFA-certified Senior Financial Analyst with 15+ years of experience analyzing "
        "corporate financial reports, earnings statements, and investment documents. "
        "You are meticulous, data-driven, and always base your analysis on actual document content. "
        "You adhere strictly to financial regulations and never fabricate data or URLs. "
        "You provide clear, balanced analysis covering both opportunities and risks, "
        "and always include appropriate investment disclaimers."
    ),
    tools=[read_data_tool],
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False
)

verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Carefully examine the uploaded document to confirm it is a legitimate financial report. "
        "Identify the document type, issuing company, reporting period, and key financial sections present."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a meticulous financial compliance officer with deep expertise in corporate financial "
        "reporting standards (GAAP, IFRS). You carefully validate documents before analysis begins, "
        "ensuring the content is genuinely financial in nature and properly structured."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

investment_advisor = Agent(
    role="Investment Advisor",
    goal=(
        "Based on the financial document analysis, provide objective, well-reasoned investment "
        "recommendations aligned with the user query: {query}. "
        "Recommendations must be grounded in document data and include risk disclosures."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a licensed Investment Advisor (Series 65) with deep experience in equity research "
        "and portfolio management. You provide unbiased recommendations based solely on financial "
        "fundamentals and the specific data in the analyzed document. "
        "You always include appropriate disclaimers and never recommend products without due diligence."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

risk_assessor = Agent(
    role="Risk Assessment Analyst",
    goal=(
        "Conduct a thorough, balanced risk assessment of the financial document. "
        "Identify genuine risk factors, quantify them where possible, and recommend "
        "appropriate mitigation strategies based on the document data."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a Chartered Risk Analyst with expertise in financial risk modeling, including "
        "market risk, credit risk, liquidity risk, and operational risk. "
        "You base all assessments on actual data from financial reports and follow established "
        "risk frameworks (Basel III, COSO). You provide balanced, realistic risk profiles."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)
