import asyncio
import os
import sys
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
import time
from contextvars import ContextVar

from arize.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace as otel_trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

current_seq_tracer = ContextVar("current_seq_tracer", default=None)


class ToolCallSpanProcessor(SpanProcessor):
    """Intercepts tool call spans to create sequential chain"""
    def on_start(self, span, parent_context):
        seq_tracer = current_seq_tracer.get()
        if seq_tracer and span.name and "tool" in span.name.lower():
            tool_name = span.name
            seq_tracer.register_tool_span(tool_name, span)
    
    def on_end(self, span):
        pass


tracer_provider = register(
    space_id = "U3BhY2U6MzA5ODU6NCt6QQ==",
    api_key = '',
    project_name = "Arize Test - Financial Agent - Query Level Tracing",
)

# Get the actual tracer provider from the trace API
actual_tracer_provider = otel_trace.get_tracer_provider()
if isinstance(actual_tracer_provider, TracerProvider):
    actual_tracer_provider.add_span_processor(ToolCallSpanProcessor())

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

os.environ["OPENAI_API_KEY"] = ''

if "OPENAI_API_KEY" not in os.environ:
    print("Error: Please set the OPENAI_API_KEY environment variable.")
    sys.exit(1)


FINANCIAL_MCP_SSE_URL = os.getenv("FINANCIAL_MCP_SSE_URL", "http://localhost:8000/sse")
UTILITIES_MCP_SSE_URL = os.getenv("UTILITIES_MCP_SSE_URL", "http://localhost:8001/sse")
MODEL_MCP_SSE_URL = os.getenv("MODEL_MCP_SSE_URL", "http://localhost:8002/sse")
PARTY_MCP_SSE_URL = os.getenv("PARTY_MCP_SSE_URL", "http://localhost:8003/sse")


def add_graph_attributes(span, node_id: str, parent_id: str = None):
    """
    Add agent graph metadata attributes to a span for Arize visualization.
    
    Args:
        span: The OpenTelemetry span to add attributes to
        node_id: Unique identifier for this node/component
        parent_id: Identifier of the parent node (None for root)
    """
    if span is None:
        return
    
    span.set_attribute("graph.node.id", node_id)
    if parent_id:
        span.set_attribute("graph.node.parent_id", parent_id)


class SequentialTracer:
    """Wrapper to track tool executions and create sequential chain tracing"""
    def __init__(self, tracer, query_id: str):
        self.tracer = tracer
        self.query_id = query_id
        self.tool_count = 0
        self.last_node_id = query_id
        self.tool_spans = []
    
    def register_tool_span(self, tool_name: str, original_span):
        """Register a tool span and add sequential attributes"""
        self.tool_count += 1
        tool_node_id = f"{self.query_id}_tool_{self.tool_count}_{tool_name.replace(' ', '_')}"
        
        add_graph_attributes(original_span, tool_node_id, self.last_node_id)
        original_span.set_attribute("tool.name", tool_name)
        original_span.set_attribute("tool.order", self.tool_count)
        original_span.set_attribute("span.kind", "tool")
        
        self.last_node_id = tool_node_id
        self.tool_spans.append((tool_node_id, tool_name))
    
    def create_end_span(self, result: str):
        """Create final end node"""
        end_node_id = f"{self.query_id}_end"
        span = self.tracer.start_span(end_node_id)
        add_graph_attributes(span, end_node_id, self.last_node_id)
        span.set_attribute("span.kind", "end")
        span.set_attribute("result", result[:500] if len(result) > 500 else result)
        span.set_attribute("total_tools_called", self.tool_count)
        span.set_status(Status(StatusCode.OK))
        span.end()
        return span


async def run_single_query(agent, query: str, query_id: str):
    """
    Execute a single query with sequential chain tracing: query -> tool1 -> tool2 -> ... -> end
    """
    tracer = otel_trace.get_tracer(__name__)
    
    with tracer.start_as_current_span(query_id) as query_span:
        add_graph_attributes(query_span, query_id)
        query_span.set_attribute("query.text", query)
        query_span.set_attribute("query.id", query_id)
        query_span.set_attribute("span.kind", "query")
        
        start = time.perf_counter()
        print(f"\n=== Query: {query}")
        
        seq_tracer = SequentialTracer(tracer, query_id)
        current_seq_tracer.set(seq_tracer)
        
        try:
            result = await Runner.run(starting_agent=agent, input=query)
            
            query_span.set_attribute("execution.status", "success")
            query_span.set_attribute("response.output", result.final_output[:500] if len(result.final_output) > 500 else result.final_output)
            query_span.set_status(Status(StatusCode.OK))
            
            seq_tracer.create_end_span(result.final_output)
            
            print(result.final_output)
            
        except Exception as e:
            query_span.set_status(Status(StatusCode.ERROR, str(e)))
            query_span.set_attribute("error.message", str(e))
            query_span.set_attribute("execution.status", "failed")
            print(f"Error: {e}")
        finally:
            current_seq_tracer.set(None)
        
        dt = time.perf_counter() - start
        query_span.set_attribute("execution.duration_seconds", dt)
        print(f"\n\n⏱  total time: {dt:.3f} s")


async def run_queries(fin_server, util_server, model_server, party_server):
    agent = Agent(
        name="MultiMCPCLI",
        instructions=(
            "You are a multi-server assistant. "
            "Use financial (Position, Orders, TaxLots, Activities), utilities (Email, Summarize, Translation, NoteAggregation, MeetingManager), "
            "model-portfolio (ModelCreation, RetrieveModels, RetrieveClientModels, AssignModel, EvaluateModelDrift), "
            "and party-management (SearchClient, UpdateClientAddress, RetrieveClientAdditionalDetails, UpdateHouseholds) tools. If you are not able to fetch the answer or perform the task,  DO NOT try to make answer, say I dont' know"
        ),
        mcp_servers=[fin_server, util_server, model_server, party_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    queries = [
        # "What is my current position in AAPL?",
        # "Show all pending orders for MSFT.",
        # "List my tax lots for GOOG.",
        # "What dividend activities have I received?",
        # "Send an email to ['advisor@wealth.com'] subject 'Portfolio Update' body 'Please review the latest positions.'",
        # "Summarize the text 'The market saw a 5% increase in tech stocks. Bonds remained stable.' in one sentence.",
        # "Translate 'Hello team, your meeting starts at 10 AM' to French.",
        # "Create a model named 'Balanced' with products ['AAPL','T','GOOG'].",
        # "Retrieve all existing models and list their products.",
        # "RetrieveClientModels for client_123.",
        # "AssignModel to client_456 for model_1001.",
        # "EvaluateModelDrift for client_123 and model_1002.",
        # "SearchClient by name 'Alice'.",
        # "RetrieveClientAdditionalDetails for client_456.",
        # "UpdateClientAddress for client_123 to '789 Pine Road'.",
        # "UpdateHouseholds for client_456 with ['spouse_2','child_1','child_2'].",
        # "List pending orders for MSFT and schedule a meeting titled 'MSFT Review' at '2025-05-10T09:00:00'.",
        # "Aggregate notes ['Review AAPL','Discuss MSFT orders'] and email them to ['team@wealth.com'] with subject 'Action Items'.",
        # "List my tax lots for GOOG and summarize the result in one sentence.",
        # "What dividend activities have I received and aggregate their descriptions into a note.",
        # "Retrieve all existing models and summarize their names in two sentences.",
        # "SearchClient by ID 'client_123' and list their AAPL positions.",
        # "RetrieveClientModels for client_123 and evaluate model drift for each assigned model.",
        # "RetrieveClientAdditionalDetails for client_456, summarize the details in one sentence.",
        # "Create a model named 'Conservative' with products ['VZ','JNJ'] and email the model details to ['pm@wealth.com'].",
        # "SearchClient by name 'Bob', list pending orders for their MSFT holdings, and schedule a follow-up meeting at '2025-05-20T14:00:00'.",
        # "Translate the aggregated notes for client_123 into German and list their current portfolio positions.",
        # "Send a summary of all clients whose tax lots include GOOG to create an aggregated note and email it to ['compliance@wealth.com'].",
        # "Assign the 'Income' model to client_456, then list updated household members and email the update to ['family@domain.com'].",
        # "Retrieve models for client_123, summarize model products list in one sentence, and translate that summary to Spanish.",
        # "SearchClient by name 'Alice', then evaluate drift on all her assigned models, and schedule a meeting to discuss any drifts.",
        "What's your outlook on Tesla stock for the next quarter?",
        "Provide a research summary for the S&P 500 current market conditions.",
        "Translate and summarize the Q2 earnings outlook for FAANG stocks.",
        "Compare the outlook on AAPL from research with actual positions in my portfolio.",
        "Email me a WealthOutlook QnA summary on the bond market to ['fixedincome@wealth.com'].",
        "Give me a summary of all meetings and model drifts for client_123.",
        "What is the address of client_456 and their latest portfolio tax lots?",
        "Schedule a meeting for 'Portfolio Review' and retrieve the current models for client_123.",
        "Summarize my AAPL position, translate it to Spanish, and assign a new model based on that summary.",
        "Analyze the outlook for gold and tech stocks, then summarize in one paragraph.",
        "Translate the Q4 earnings outlook for Amazon into French and compare it with GOOG tax lot data.",
        "Provide an outlook on the bond market and update the address of client_456.",
        "Create a note aggregation of client_123's emails, then run a wealth outlook query on biotech stocks.",
        "List all household members for client_123 and summarize the market outlook for each member's investment focus.",
    ]

    for idx, query in enumerate(queries):
        query_id = f"query_{idx}_{query[:30].replace(' ', '_')}"
        await run_single_query(agent, query, query_id)


async def main():
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
