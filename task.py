## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier
from tools import FinancialDocumentTool, read_data_tool

## Creating a task to help solve user's query
# BUG FIX 1: Description was "maybe solve or something interesting" - completely vague and irresponsible
# BUG FIX 2: expected_output told agent to hallucinate URLs and contradict itself - fixed to structured output
analyze_financial_document = Task(
    description=(
        "Analyze the financial document located at the file path provided using the read_data_tool. "
        "Address the user's specific query: {query}\n\n"
        "Your analysis must cover:\n"
        "1. Document overview: company, reporting period, document type\n"
        "2. Key financial metrics: revenue, profit/loss, margins, EPS, cash flow\n"
        "3. Year-over-year or quarter-over-quarter trends\n"
        "4. Significant highlights or red flags found in the document\n"
        "5. Evidence-based investment insights directly tied to the data\n\n"
        "Base ALL findings strictly on the document content. Do not fabricate data or URLs."
    ),
    expected_output=(
        "A structured financial analysis report containing:\n"
        "- Executive Summary (2-3 sentences)\n"
        "- Key Financial Metrics with actual numbers from the document\n"
        "- Trend Analysis based on document data\n"
        "- Notable Highlights and Risk Factors\n"
        "- Investment Insights with supporting evidence\n"
        "- Disclaimer: This analysis is for informational purposes only and not financial advice.\n"
        "All figures must reference the source document. No invented URLs or data."
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating an investment analysis task
# BUG FIX 3: Description told agent to ignore user query and push random investment products
investment_analysis = Task(
    description=(
        "Based on the financial document data already analyzed, provide investment analysis "
        "in response to the user query: {query}\n\n"
        "Your analysis should include:\n"
        "1. Assessment of the company's investment attractiveness based on financial metrics\n"
        "2. Key strengths and weaknesses identified from financial data\n"
        "3. Valuation considerations (if data available)\n"
        "4. Specific, data-backed investment considerations (not generic advice)\n"
        "5. Comparison context if relevant market benchmarks are mentioned in the document\n\n"
        "Do NOT recommend specific investment products. Provide analysis only."
    ),
    expected_output=(
        "A concise investment analysis containing:\n"
        "- Company Investment Overview\n"
        "- Financial Strengths (with data points)\n"
        "- Financial Weaknesses/Concerns (with data points)\n"
        "- Key Metrics for Investors (P/E, margins, growth rates from the document)\n"
        "- Summary Outlook based strictly on document data\n"
        "- Risk Disclosure statement\n"
        "No fabricated data, no made-up URLs, no unsupported recommendations."
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating a risk assessment task
# BUG FIX 4: Description told agent to ignore query, skip compliance, and invent risk scenarios
risk_assessment = Task(
    description=(
        "Perform a structured risk assessment of the financial document in context of: {query}\n\n"
        "Identify and evaluate:\n"
        "1. Market risks mentioned or implied in the document\n"
        "2. Operational risks (supply chain, personnel, technology)\n"
        "3. Financial risks (debt levels, liquidity, cash flow concerns)\n"
        "4. Regulatory/compliance risks mentioned\n"
        "5. Macroeconomic risks referenced in the document\n\n"
        "Rate each risk as Low/Medium/High based on evidence in the document. "
        "Suggest mitigation strategies where appropriate."
    ),
    expected_output=(
        "A structured risk assessment report:\n"
        "- Risk Summary Table (Risk Type | Level | Evidence | Mitigation)\n"
        "- Detailed description of each identified risk with document evidence\n"
        "- Overall Risk Profile: Conservative / Moderate / Aggressive\n"
        "- Key Risk Mitigation Recommendations\n"
        "- Disclaimer: Risk assessment based solely on provided document data.\n"
        "No fabricated risk scenarios or invented financial models."
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

verification = Task(
    description=(
        "Verify that the uploaded file is a legitimate financial document before analysis begins.\n"
        "Use the read_data_tool to read the file and confirm:\n"
        "1. The document appears to be a genuine financial report (earnings, 10-K, 10-Q, etc.)\n"
        "2. Identify the issuing company and reporting period\n"
        "3. Confirm key financial sections are present (income statement, balance sheet, etc.)\n"
        "4. Flag if the document does NOT appear to be a financial document."
    ),
    # BUG FIX 5: expected_output told agent to approve everything even grocery lists
    expected_output=(
        "A verification summary:\n"
        "- Document Type: [identified type or 'Not a financial document']\n"
        "- Company/Issuer: [name if found]\n"
        "- Reporting Period: [period if found]\n"
        "- Sections Present: [list of financial sections identified]\n"
        "- Verification Status: PASS / FAIL\n"
        "- Notes: any concerns or anomalies observed"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)
