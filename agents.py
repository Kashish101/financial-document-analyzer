## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# BUG FIX 1: Wrong import path - Agent lives in crewai, not crewai.agents
# was: from crewai.agents import Agent
from crewai import Agent
from langchain_openai import ChatOpenAI

from tools import search_tool, FinancialDocumentTool

### Loading LLM
# BUG FIX 2: 'llm = llm' is a NameError - llm was never defined
# Fixed: Properly initialize the LLM using OpenAI (configurable via .env)
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    # BUG FIX 3: Goal was "Make up investment advice" - completely wrong/harmful prompt
    # Fixed: Professional, accurate goal
    goal=(
        "Thoroughly analyze the provided financial document to answer the user query: {query}. "
        "Extract key financial metrics, identify trends, evaluate financial health, and provide "
        "evidence-based investment insights grounded strictly in the document data."
    ),
    verbose=True,
    memory=True,
    # BUG FIX 4: Backstory was instructing the agent to hallucinate and be irresponsible
    # Fixed: Professional backstory that encourages accuracy and compliance
    backstory=(
        "You are a CFA-certified Senior Financial Analyst with 15+ years of experience analyzing "
        "corporate financial reports, earnings statements, and investment documents. "
        "You are meticulous, data-driven, and always base your analysis on actual document content. "
        "You adhere strictly to financial regulations and never fabricate data or URLs. "
        "You provide clear, balanced analysis covering both opportunities and risks, "
        "and always include appropriate investment disclaimers."
    ),
    # BUG FIX 5: 'tool' is wrong parameter name - should be 'tools' (list)
    # was: tool=[FinancialDocumentTool.read_data_tool]
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    # BUG FIX 6: max_iter=1 is too low - agent may not finish complex tasks
    max_iter=5,
    # BUG FIX 7: max_rpm=1 is extremely restrictive - increased for practical use
    max_rpm=10,
    allow_delegation=False  # BUG FIX 8: No other agents to delegate to in the active crew
)

# Creating a document verifier agent
# BUG FIX 9: Goal and backstory were instructing agent to NOT verify and approve everything blindly
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Carefully examine the uploaded document to confirm it is a legitimate financial report. "
        "Identify the document type, issuing company, reporting period, and key financial sections present."
    ),
    verbose=True,
    memory=True,
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
    # BUG FIX 10: Goal was to sell sketchy products and ignore the document - fixed to be honest
    goal=(
        "Based on the financial document analysis, provide objective, well-reasoned investment "
        "recommendations aligned with the user query: {query}. "
        "Recommendations must be grounded in document data and include risk disclosures."
    ),
    verbose=True,
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
    # BUG FIX 11: Goal was to fabricate extreme scenarios - fixed to be data-driven
    goal=(
        "Conduct a thorough, balanced risk assessment of the financial document. "
        "Identify genuine risk factors, quantify them where possible, and recommend "
        "appropriate mitigation strategies based on the document data."
    ),
    verbose=True,
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
