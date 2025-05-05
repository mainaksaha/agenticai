import random
from typing import List, Optional
from fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("ModelPortfolio")

# Define MCP tools
@mcp.tool(name="ModelCreation", description="Create a new portfolio model")
def create_model(model_name: str, products: List[str]) -> dict:
    """Dummy model creation: returns a new model ID and echoes inputs."""
    model_id = f"model_{random.randint(1000,9999)}"
    return {"model_id": model_id, "model_name": model_name, "products": products}

@mcp.tool(name="RetrieveModels", description="Retrieve all existing models and their products")
def retrieve_models() -> List[dict]:
    """Returns a fixed list of portfolio models and their products."""
    return [
        {"model_id": "model_1001", "model_name": "Growth", "products": ["AAPL", "GOOG", "MSFT"]},
        {"model_id": "model_1002", "model_name": "Income", "products": ["T", "VZ", "JNJ"]},
    ]

@mcp.tool(name="RetrieveClientModels", description="Retrieve models assigned to a client")
def retrieve_client_models(client_id: str) -> List[dict]:
    """Returns models assigned to the given client ID."""
    if client_id == "client_123":
        return [
            {"model_id": "model_1001", "assignment_date": "2025-01-15"},
            {"model_id": "model_1002", "assignment_date": "2025-02-10"},
        ]
    return []

@mcp.tool(name="AssignModel", description="Assign a model to a client's portfolio")
def assign_model(client_id: str, model_id: str) -> dict:
    """Assigns the model to the client and returns an assignment record."""
    assignment_id = f"assign_{random.randint(2000,2999)}"
    return {"assignment_id": assignment_id, "client_id": client_id, "model_id": model_id, "status": "assigned"}

@mcp.tool(name="EvaluateModelDrift", description="Evaluate drift of a client's model")
def evaluate_model_drift(client_id: str, model_id: str) -> dict:
    """Calculates a dummy drift percentage for the specified client-model pair."""
    drift_pct = round(random.uniform(-0.1, 0.1), 4)
    return {"client_id": client_id, "model_id": model_id, "drift": drift_pct}

if __name__ == "__main__":
    print("Starting ModelPortfolio MCP server with SSE transport on port 8002...")
    mcp.run(transport="sse", host="0.0.0.0", port=8002)
