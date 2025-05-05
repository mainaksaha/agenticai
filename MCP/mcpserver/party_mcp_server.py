from typing import List, Optional, Dict
import random
from fastmcp import FastMCP

# Initialize FastMCP for Party Management
authority = "PartyManagement"
mcp = FastMCP(authority)

# Dummy client store
_dummy_clients = [
    {"client_id": "client_123", "name": "Alice", "address": "123 Main St", "details": {"age": 30, "email": "alice@example.com"}, "households": ["spouse_1"]},
    {"client_id": "client_456", "name": "Bob", "address": "456 Oak Ave", "details": {"age": 40, "email": "bob@example.com"}, "households": ["spouse_2", "child_1"]},
]

# Define MCP tools
@mcp.tool(name="SearchClient", description="Search clients by name or ID")
def search_client(name: Optional[str] = None, client_id: Optional[str] = None) -> List[Dict]:
    results = _dummy_clients
    if client_id:
        results = [c for c in results if c["client_id"] == client_id]
    if name:
        results = [c for c in results if name.lower() in c["name"].lower()]
    return results

@mcp.tool(name="UpdateClientAddress", description="Update a client's address")
def update_client_address(client_id: str, address: str) -> Dict:
    for c in _dummy_clients:
        if c["client_id"] == client_id:
            c["address"] = address
            return {"status": "updated", "client_id": client_id, "new_address": address}
    return {"error": "client not found", "client_id": client_id}

@mcp.tool(name="RetrieveClientAdditionalDetails", description="Retrieve additional client details")
def retrieve_client_additional_details(client_id: str) -> Dict:
    for c in _dummy_clients:
        if c["client_id"] == client_id:
            return c.get("details", {})
    return {}

@mcp.tool(name="UpdateHouseholds", description="Update client's household list")
def update_households(client_id: str, households: List[str]) -> Dict:
    for c in _dummy_clients:
        if c["client_id"] == client_id:
            c["households"] = households
            return {"status": "updated", "client_id": client_id, "households": households}
    return {"error": "client not found", "client_id": client_id}

if __name__ == "__main__":
    print("Starting Party Management MCP Server (SSE transport) on default port 8003...")
    mcp.run(transport="sse", host="0.0.0.0", port=8003)
