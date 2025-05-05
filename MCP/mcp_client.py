import asyncio
import os
import sys
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings



# Ensure OPENAI_API_KEY is set
if "OPENAI_API_KEY" not in os.environ:
    print("Error: Please set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

# MCP SSE endpoint URLs for all servers
FINANCIAL_MCP_SSE_URL = os.getenv("FINANCIAL_MCP_SSE_URL", "http://localhost:8000/sse")
UTILITIES_MCP_SSE_URL = os.getenv("UTILITIES_MCP_SSE_URL", "http://localhost:8001/sse")
MODEL_MCP_SSE_URL = os.getenv("MODEL_MCP_SSE_URL", "http://localhost:8002/sse")
PARTY_MCP_SSE_URL = os.getenv("PARTY_MCP_SSE_URL", "http://localhost:8003/sse")

async def run_queries(fin_server, util_server, model_server, party_server):
    # Agent that can call tools from all MCP servers
    agent = Agent(
        name="MultiMCPCLI",
        instructions=(
            "You are a multi-server assistant. "
            "Use financial (Position, Orders, TaxLots, Activities), utilities (Email, Summarize, Translation, NoteAggregation, MeetingManager), "
            "model-portfolio (ModelCreation, RetrieveModels, RetrieveClientModels, AssignModel, EvaluateModelDrift), "
            "and party-management (SearchClient, UpdateClientAddress, RetrieveClientAdditionalDetails, UpdateHouseholds) tools."
        ),
        mcp_servers=[fin_server, util_server, model_server, party_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    queries = [
        # Financial queries
        "What is my current position in AAPL?",
        "Show all pending orders for MSFT.",
        "List my tax lots for GOOG.",
        "What dividend activities have I received?",
        # Utilities queries
        "Send an email to ['advisor@wealth.com'] subject 'Portfolio Update' body 'Please review the latest positions.'",
        "Summarize the text 'The market saw a 5% increase in tech stocks. Bonds remained stable.' in one sentence.",
        "Translate 'Hello team, your meeting starts at 10 AM' to French.",
        # Model-portfolio queries
        "Create a model named 'Balanced' with products ['AAPL','T','GOOG'].",
        "Retrieve all existing models and list their products.",
        "RetrieveClientModels for client_123.",
        "AssignModel to client_456 for model_1001.",
        "EvaluateModelDrift for client_123 and model_1002.",
        # Party-management queries
        "SearchClient by name 'Alice'.",
        "RetrieveClientAdditionalDetails for client_456.",
        "UpdateClientAddress for client_123 to '789 Pine Road'.",
        "UpdateHouseholds for client_456 with ['spouse_2','child_1','child_2'].",
        # Combined scenarios touching multiple servers
        "List pending orders for MSFT and schedule a meeting titled 'MSFT Review' at '2025-05-10T09:00:00'.",
        "Aggregate notes ['Review AAPL','Discuss MSFT orders'] and email them to ['team@wealth.com'] with subject 'Action Items'.",
        "List my tax lots for GOOG and summarize the result in one sentence.",
        "What dividend activities have I received and aggregate their descriptions into a note.",
        "Retrieve all existing models and summarize their names in two sentences.",
        "SearchClient by ID 'client_123' and list their AAPL positions.",
        "RetrieveClientModels for client_123 and evaluate model drift for each assigned model.",
        "RetrieveClientAdditionalDetails for client_456, summarize the details in one sentence.",
        "Create a model named 'Conservative' with products ['VZ','JNJ'] and email the model details to ['pm@wealth.com'].",
        "SearchClient by name 'Bob', list pending orders for their MSFT holdings, and schedule a follow-up meeting at '2025-05-20T14:00:00'.",
        # Ambiguous and challenging queries
        "Translate the aggregated notes for client_123 into German and list their current portfolio positions.",
        "Send a summary of all clients whose tax lots include GOOG to create an aggregated note and email it to ['compliance@wealth.com'].",
        "Assign the 'Income' model to client_456, then list updated household members and email the update to ['family@domain.com'].",
        "Retrieve models for client_123, summarize model products list in one sentence, and translate that summary to Spanish.",
        "SearchClient by name 'Alice', then evaluate drift on all her assigned models, and schedule a meeting to discuss any drifts.",
        # Research/QnA queries
        "What’s your outlook on Tesla stock for the next quarter?",
        "Provide a research summary for the S&P 500 current market conditions.",
        "Translate and summarize the Q2 earnings outlook for FAANG stocks.",
        "Compare the outlook on AAPL from research with actual positions in my portfolio.",
        "Email me a WealthOutlook QnA summary on the bond market to ['fixedincome@wealth.com'].",
        # Highly ambiguous queries to test tool selection
        "Give me a summary of all meetings and model drifts for client_123.",
        "What is the address of client_456 and their latest portfolio tax lots?",
        "Schedule a meeting for 'Portfolio Review' and retrieve the current models for client_123.",
        "Summarize my AAPL position, translate it to Spanish, and assign a new model based on that summary.",
        # Additional ambiguous research-triggering queries
        "Analyze the outlook for gold and tech stocks, then summarize in one paragraph.",
        "Translate the Q4 earnings outlook for Amazon into French and compare it with GOOG tax lot data.",
        "Provide an outlook on the bond market and update the address of client_456.",
        "Create a note aggregation of client_123's emails, then run a wealth outlook query on biotech stocks.",
        "List all household members for client_123 and summarize the market outlook for each member's investment focus.",
    ]

    for query in queries:
        print(f"\n=== Query: {query}")
        result = await Runner.run(starting_agent=agent, input=query)
        print(result.final_output)

async def main():
    # Connect to all MCP servers via SSE
    async with MCPServerSse(name="FinancialServer", params={"url": FINANCIAL_MCP_SSE_URL}) as fin, \
               MCPServerSse(name="UtilitiesServer", params={"url": UTILITIES_MCP_SSE_URL}) as util, \
               MCPServerSse(name="ModelServer", params={"url": MODEL_MCP_SSE_URL}) as model, \
               MCPServerSse(name="PartyServer", params={"url": PARTY_MCP_SSE_URL}) as party:
        trace_id = gen_trace_id()
        with trace(workflow_name="Quad-MCP CLI Session", trace_id=trace_id):
            print(f"Trace URL: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run_queries(fin, util, model, party)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
