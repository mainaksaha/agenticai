"""
Mock API Server for Reconciliation Data Sources
FastAPI-based mock endpoints returning sample data
"""
from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

app = FastAPI(title="Reconciliation Mock APIs", version="1.0.0")


# Sample data generators
def generate_break_id() -> str:
    return f"BRK-2025-11-{random.randint(10000, 99999)}"


def generate_trade_id() -> str:
    return f"T{random.randint(100000, 999999)}"


def generate_order_id() -> str:
    return f"O{random.randint(100000, 999999)}"


INSTRUMENTS = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "JPM", "BAC", "GS", "C"]
ACCOUNTS = ["ACC-12345", "ACC-67890", "ACC-54321", "ACC-98765"]
BROKERS = ["XYZ Broker", "ABC Securities", "DEF Capital", "GHI Trading"]


@app.get("/")
def root():
    return {"message": "Reconciliation Mock API Server", "version": "1.0.0"}


@app.get("/api/breaks")
def get_breaks(limit: int = 10, break_type: str = None) -> List[Dict[str, Any]]:
    """Get list of reconciliation breaks"""
    breaks = []
    break_types = ["TRADE_OMS_MISMATCH", "BROKER_VS_INTERNAL", "CASH_RECONCILIATION", "CUSTODIAN_MISMATCH"]
    
    for i in range(limit):
        selected_type = break_type if break_type else random.choice(break_types)
        instrument = random.choice(INSTRUMENTS)
        qty = random.randint(100, 10000)
        price = random.uniform(50, 500)
        
        breaks.append({
            "break_id": generate_break_id(),
            "break_type": selected_type,
            "status": "NEW",
            "system_a": {
                "system_name": "OMS",
                "quantity": qty,
                "amount": qty * price,
                "price": price,
                "currency": "USD",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            },
            "system_b": {
                "system_name": "Trade Capture",
                "quantity": qty + random.randint(-10, 10),
                "amount": (qty + random.randint(-10, 10)) * (price + random.uniform(-0.5, 0.5)),
                "price": price + random.uniform(-0.5, 0.5),
                "currency": "USD",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            },
            "entities": {
                "instrument": instrument,
                "account": random.choice(ACCOUNTS),
                "broker": random.choice(BROKERS),
                "trade_ids": [generate_trade_id()],
                "order_ids": [generate_order_id()]
            },
            "date": datetime.now().isoformat(),
            "source": "Reconciliation Engine"
        })
    
    return breaks


@app.get("/api/breaks/{break_id}")
def get_break_by_id(break_id: str) -> Dict[str, Any]:
    """Get specific break by ID"""
    instrument = random.choice(INSTRUMENTS)
    qty = random.randint(100, 10000)
    price = random.uniform(50, 500)
    
    return {
        "break_id": break_id,
        "break_type": "TRADE_OMS_MISMATCH",
        "status": "NEW",
        "system_a": {
            "system_name": "OMS",
            "quantity": qty,
            "amount": qty * price,
            "price": price,
            "currency": "USD",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        "system_b": {
            "system_name": "Trade Capture",
            "quantity": qty + 5,
            "amount": (qty + 5) * (price + 0.2),
            "price": price + 0.2,
            "currency": "USD",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        "entities": {
            "instrument": instrument,
            "account": random.choice(ACCOUNTS),
            "broker": random.choice(BROKERS),
            "trade_ids": [generate_trade_id()],
            "order_ids": [generate_order_id()]
        },
        "date": datetime.now().isoformat(),
        "source": "Reconciliation Engine"
    }


@app.get("/api/oms/orders/{order_id}")
def get_oms_order(order_id: str) -> Dict[str, Any]:
    """Get OMS order details"""
    return {
        "order_id": order_id,
        "instrument": random.choice(INSTRUMENTS),
        "quantity": random.randint(100, 10000),
        "filled_quantity": random.randint(50, 10000),
        "price": random.uniform(50, 500),
        "order_type": random.choice(["MARKET", "LIMIT", "STOP"]),
        "side": random.choice(["BUY", "SELL"]),
        "status": random.choice(["FILLED", "PARTIALLY_FILLED", "PENDING"]),
        "account": random.choice(ACCOUNTS),
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
        "broker": random.choice(BROKERS)
    }


@app.get("/api/trade-capture/trades/{trade_id}")
def get_trade_capture(trade_id: str) -> Dict[str, Any]:
    """Get trade capture details"""
    qty = random.randint(100, 10000)
    price = random.uniform(50, 500)
    
    return {
        "trade_id": trade_id,
        "instrument": random.choice(INSTRUMENTS),
        "quantity": qty,
        "price": price,
        "amount": qty * price,
        "currency": "USD",
        "side": random.choice(["BUY", "SELL"]),
        "counterparty": random.choice(BROKERS),
        "trade_date": datetime.now().date().isoformat(),
        "settlement_date": (datetime.now() + timedelta(days=2)).date().isoformat(),
        "status": "CONFIRMED",
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
    }


@app.get("/api/settlement/positions/{account}")
def get_settlement_data(account: str) -> Dict[str, Any]:
    """Get settlement position data"""
    return {
        "account": account,
        "positions": [
            {
                "instrument": inst,
                "quantity": random.randint(1000, 50000),
                "market_value": random.uniform(50000, 500000),
                "currency": "USD",
                "settlement_date": (datetime.now() + timedelta(days=2)).date().isoformat()
            }
            for inst in random.sample(INSTRUMENTS, 3)
        ],
        "cash_balance": random.uniform(10000, 1000000),
        "currency": "USD",
        "as_of_date": datetime.now().date().isoformat()
    }


@app.get("/api/custodian/holdings/{account}")
def get_custodian_holdings(account: str) -> Dict[str, Any]:
    """Get custodian holdings data"""
    return {
        "account": account,
        "custodian": "Global Custodian Services",
        "holdings": [
            {
                "instrument": inst,
                "quantity": random.randint(1000, 50000),
                "market_value": random.uniform(50000, 500000),
                "currency": "USD",
                "custody_location": random.choice(["US", "UK", "EU"])
            }
            for inst in random.sample(INSTRUMENTS, 4)
        ],
        "cash_balance": random.uniform(10000, 1000000),
        "as_of_date": datetime.now().date().isoformat()
    }


@app.get("/api/reference-data/instrument/{symbol}")
def get_reference_data(symbol: str) -> Dict[str, Any]:
    """Get instrument reference data"""
    return {
        "symbol": symbol,
        "isin": f"US{random.randint(100000000, 999999999)}",
        "cusip": f"{random.randint(100000000, 999999999)}",
        "name": f"{symbol} Inc.",
        "asset_class": "EQUITY",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "US",
        "sector": random.choice(["Technology", "Finance", "Healthcare", "Energy"]),
        "lot_size": 1
    }


@app.get("/api/broker/confirms/{trade_id}")
def get_broker_confirm(trade_id: str) -> Dict[str, Any]:
    """Get broker confirmation data"""
    qty = random.randint(100, 10000)
    price = random.uniform(50, 500)
    
    return {
        "confirm_id": f"CONF-{random.randint(100000, 999999)}",
        "trade_id": trade_id,
        "broker": random.choice(BROKERS),
        "instrument": random.choice(INSTRUMENTS),
        "quantity": qty,
        "price": price,
        "gross_amount": qty * price,
        "commission": random.uniform(10, 100),
        "net_amount": (qty * price) - random.uniform(10, 100),
        "currency": "USD",
        "trade_date": datetime.now().date().isoformat(),
        "settlement_date": (datetime.now() + timedelta(days=2)).date().isoformat(),
        "status": "CONFIRMED",
        "received_at": (datetime.now() - timedelta(hours=1)).isoformat()
    }


@app.get("/api/historical/patterns")
def get_historical_patterns(break_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Get historical break patterns"""
    patterns = []
    root_causes = ["timing_lag", "rounding_difference", "fx_conversion", "fee_mismatch", 
                   "partial_fill", "corporate_action", "system_error", "data_entry_error"]
    
    for i in range(limit):
        patterns.append({
            "pattern_id": f"PAT-{random.randint(1000, 9999)}",
            "break_type": break_type or random.choice(["TRADE_OMS_MISMATCH", "BROKER_VS_INTERNAL"]),
            "root_cause": random.choice(root_causes),
            "frequency": random.randint(1, 50),
            "resolution": random.choice(["AUTO_RESOLVED", "MANUAL_ADJUSTMENT", "ESCALATED"]),
            "average_amount": random.uniform(100, 10000),
            "confidence": random.uniform(0.7, 0.99)
        })
    
    return patterns


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
