from mcp.server.fastmcp import FastMCP
from typing import List, Optional

# Dummy data for tools
dummy_positions = [
    {"symbol": "AAPL", "quantity": 50, "avg_price": 150.0},
    {"symbol": "MSFT", "quantity": 30, "avg_price": 280.5},
    {"symbol": "GOOG", "quantity": 10, "avg_price": 2200.0},
]

dummy_orders = [
    {"order_id": 1, "symbol": "AAPL", "side": "buy", "quantity": 20, "status": "filled"},
    {"order_id": 2, "symbol": "MSFT", "side": "sell", "quantity": 10, "status": "pending"},
    {"order_id": 3, "symbol": "NFLX", "side": "buy", "quantity": 5, "status": "cancelled"},
]

dummy_tax_lots = [
    {"lot_id": "TL1", "symbol": "AAPL", "acquired_date": "2021-01-15", "quantity": 25, "cost_basis": 140.0},
    {"lot_id": "TL2", "symbol": "MSFT", "acquired_date": "2022-06-30", "quantity": 15, "cost_basis": 250.0},
    {"lot_id": "TL3", "symbol": "GOOG", "acquired_date": "2020-11-20", "quantity": 5, "cost_basis": 2100.0},
]

dummy_activities = [
    {"activity_id": "ACT1", "type": "dividend", "symbol": "AAPL", "amount": 50.0, "date": "2025-04-01"},
    {"activity_id": "ACT2", "type": "split", "symbol": "MSFT", "ratio": "2:1", "date": "2024-08-15"},
    {"activity_id": "ACT3", "type": "fee", "description": "Account maintenance", "amount": 10.0, "date": "2025-01-01"},
]

# Initialize MCP server
mcp = FastMCP("WealthManagement")

# Define MCP tools
@mcp.tool(name="Position", description="Fetch position information")
def position_tool(symbol: Optional[str] = None) -> List[dict]:
    results = dummy_positions
    if symbol:
        results = [pos for pos in results if pos["symbol"] == symbol]
    return results

@mcp.tool(name="Orders", description="Fetch orders information")
def orders_tool(order_id: Optional[int] = None, symbol: Optional[str] = None) -> List[dict]:
    results = dummy_orders
    if order_id is not None:
        results = [order for order in results if order["order_id"] == order_id]
    if symbol:
        results = [order for order in results if order["symbol"] == symbol]
    return results

@mcp.tool(name="TaxLots", description="Fetch tax lots information")
def taxlots_tool(lot_id: Optional[str] = None, symbol: Optional[str] = None) -> List[dict]:
    results = dummy_tax_lots
    if lot_id:
        results = [lot for lot in results if lot["lot_id"] == lot_id]
    if symbol:
        results = [lot for lot in results if lot["symbol"] == symbol]
    return results

@mcp.tool(name="Activities", description="Fetch account activities")
def activities_tool(activity_id: Optional[str] = None, type: Optional[str] = None) -> List[dict]:
    results = dummy_activities
    if activity_id:
        results = [act for act in results if act["activity_id"] == activity_id]
    if type:
        results = [act for act in results if act.get("type") == type]
    return results

# Run the MCP server with SSE transport
if __name__ == "__main__":
    # This will start a local SSE server on port 8000
    # Endpoints:
    #  - GET  /sse    : SSE handshake
    #  - POST /?session_id=<id> : tool invocation
    mcp.run(transport="sse")
