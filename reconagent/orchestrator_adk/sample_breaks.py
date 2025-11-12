"""
Sample Break Data - 15 Diverse Scenarios
Covers various break types, complexities, and expected outcomes
"""

SAMPLE_BREAKS = [
    {
        "break_id": "BRK-001",
        "break_type": "SETTLEMENT_DISCREPANCY",
        "description": "Simple amount tolerance issue",
        "system_a": {"amount": 1000.00, "quantity": 100, "currency": "USD", "settle_date": "2024-11-10"},
        "system_b": {"amount": 1000.50, "quantity": 100, "currency": "USD", "settle_date": "2024-11-10"},
        "status": "OPEN",
        "expected_outcome": "AUTO_RESOLVE",
        "expected_agents": ["ingestion", "enrichment", "rules", "decision", "workflow"]
    },
    {
        "break_id": "BRK-002",
        "break_type": "TRADE_OMS_MISMATCH",
        "description": "Trade missing in OMS, needs matching",
        "system_a": {"trade_id": "T-12345", "amount": 50000.00, "instrument": "AAPL", "quantity": 500},
        "system_b": {"trade_id": None, "amount": 0, "instrument": "AAPL", "quantity": 0},
        "status": "OPEN",
        "expected_outcome": "HIL_REVIEW",
        "expected_agents": ["ingestion", "enrichment", "matching", "rules", "pattern", "decision", "workflow"]
    },
    {
        "break_id": "BRK-003",
        "break_type": "FX_RATE_DIFF",
        "description": "Minor FX rate difference",
        "system_a": {"amount": 1000.00, "currency": "USD", "fx_rate": 1.0850},
        "system_b": {"amount": 1085.00, "currency": "EUR", "fx_rate": 1.0852},
        "status": "OPEN",
        "expected_outcome": "AUTO_RESOLVE",
        "expected_agents": ["ingestion", "enrichment", "rules", "decision"]
    },
    {
        "break_id": "BRK-004",
        "break_type": "BROKER_VS_INTERNAL",
        "description": "Broker confirmation mismatch with internal records",
        "system_a": {"broker_confirm": "BC-789", "amount": 25000.00, "price": 150.50},
        "system_b": {"internal_record": "IR-456", "amount": 25500.00, "price": 150.50},
        "status": "OPEN",
        "expected_outcome": "HIL_REVIEW",
        "expected_agents": ["ingestion", "enrichment", "matching", "rules", "pattern", "decision", "workflow"]
    },
    {
        "break_id": "BRK-005",
        "break_type": "SETTLEMENT_DISCREPANCY",
        "description": "Large amount difference - exceeds tolerance",
        "system_a": {"amount": 100000.00, "quantity": 1000, "currency": "USD"},
        "system_b": {"amount": 105000.00, "quantity": 1000, "currency": "USD"},
        "status": "OPEN",
        "expected_outcome": "ESCALATE",
        "expected_agents": ["ingestion", "enrichment", "rules", "pattern", "decision", "workflow"]
    },
    {
        "break_id": "BRK-006",
        "break_type": "QUANTITY_MISMATCH",
        "description": "Quantity mismatch within tolerance",
        "system_a": {"quantity": 1000, "amount": 50000.00, "instrument": "MSFT"},
        "system_b": {"quantity": 1001, "amount": 50050.00, "instrument": "MSFT"},
        "status": "OPEN",
        "expected_outcome": "AUTO_RESOLVE",
        "expected_agents": ["ingestion", "enrichment", "rules", "decision"]
    },
    {
        "break_id": "BRK-007",
        "break_type": "FO_VS_BO",
        "description": "Front office vs back office mismatch",
        "system_a": {"fo_trade": "FO-123", "amount": 75000.00, "status": "CONFIRMED"},
        "system_b": {"bo_trade": "BO-456", "amount": 75000.00, "status": "PENDING"},
        "status": "OPEN",
        "expected_outcome": "HIL_REVIEW",
        "expected_agents": ["ingestion", "enrichment", "matching", "rules", "decision", "workflow"]
    },
    {
        "break_id": "BRK-008",
        "break_type": "SETTLEMENT_DISCREPANCY",
        "description": "Recurring pattern - systematic issue",
        "system_a": {"amount": 10000.00, "account": "ACC-999", "counter_party": "CP-AAA"},
        "system_b": {"amount": 10010.00, "account": "ACC-999", "counter_party": "CP-AAA"},
        "status": "OPEN",
        "recurring": True,
        "expected_outcome": "HIL_REVIEW",
        "expected_agents": ["ingestion", "enrichment", "rules", "pattern", "decision", "workflow"]
    },
    {
        "break_id": "BRK-009",
        "break_type": "PRICE_DIFF",
        "description": "Price difference within market tolerance",
        "system_a": {"price": 150.25, "quantity": 100, "amount": 15025.00},
        "system_b": {"price": 150.28, "quantity": 100, "amount": 15028.00},
        "status": "OPEN",
        "expected_outcome": "AUTO_RESOLVE",
        "expected_agents": ["ingestion", "enrichment", "rules", "decision"]
    },
    {
        "break_id": "BRK-010",
        "break_type": "TRADE_OMS_MISMATCH",
        "description": "Duplicate trade entry",
        "system_a": {"trade_id": "T-555", "amount": 30000.00, "count": 2},
        "system_b": {"trade_id": "T-555", "amount": 30000.00, "count": 1},
        "status": "OPEN",
        "expected_outcome": "ESCALATE",
        "expected_agents": ["ingestion", "enrichment", "matching", "rules", "pattern", "decision", "workflow"]
    },
    {
        "break_id": "BRK-011",
        "break_type": "CUSTODIAN_MISMATCH",
        "description": "Custodian holdings vs internal records",
        "system_a": {"custodian": "CUST-A", "holdings": 5000, "value": 250000.00},
        "system_b": {"internal": "INT-B", "holdings": 5000, "value": 250100.00},
        "status": "OPEN",
        "expected_outcome": "AUTO_RESOLVE",
        "expected_agents": ["ingestion", "enrichment", "rules", "decision"]
    },
    {
        "break_id": "BRK-012",
        "break_type": "SETTLEMENT_FAIL",
        "description": "Settlement failed - operational issue",
        "system_a": {"settle_status": "FAILED", "amount": 100000.00, "reason": "INSUFFICIENT_FUNDS"},
        "system_b": {"settle_status": "PENDING", "amount": 100000.00, "reason": None},
        "status": "OPEN",
        "expected_outcome": "ESCALATE",
        "expected_agents": ["ingestion", "enrichment", "rules", "pattern", "decision", "workflow"]
    },
    {
        "break_id": "BRK-013",
        "break_type": "BROKER_VS_INTERNAL",
        "description": "Minor broker confirmation timing issue",
        "system_a": {"broker_time": "09:30:15", "amount": 45000.00},
        "system_b": {"internal_time": "09:30:18", "amount": 45000.00},
        "status": "OPEN",
        "expected_outcome": "AUTO_RESOLVE",
        "expected_agents": ["ingestion", "enrichment", "matching", "rules", "decision"]
    },
    {
        "break_id": "BRK-014",
        "break_type": "CORPORATE_ACTION",
        "description": "Corporate action not reflected in both systems",
        "system_a": {"pre_action": 1000, "post_action": 1000, "action": None},
        "system_b": {"pre_action": 1000, "post_action": 1200, "action": "STOCK_SPLIT_1.2"},
        "status": "OPEN",
        "expected_outcome": "HIL_REVIEW",
        "expected_agents": ["ingestion", "enrichment", "rules", "pattern", "decision", "workflow"]
    },
    {
        "break_id": "BRK-015",
        "break_type": "SETTLEMENT_DISCREPANCY",
        "description": "Multiple currency settlement with rounding",
        "system_a": {"amount": 1234.567, "currency": "JPY"},
        "system_b": {"amount": 1234.57, "currency": "JPY"},
        "status": "OPEN",
        "expected_outcome": "AUTO_RESOLVE",
        "expected_agents": ["ingestion", "enrichment", "rules", "decision"]
    }
]


def get_sample_breaks():
    """Get all sample breaks"""
    return SAMPLE_BREAKS


def get_break_by_id(break_id: str):
    """Get specific break by ID"""
    for brk in SAMPLE_BREAKS:
        if brk['break_id'] == break_id:
            return brk
    return None


def get_breaks_by_outcome(expected_outcome: str):
    """Get breaks by expected outcome"""
    return [brk for brk in SAMPLE_BREAKS if brk.get('expected_outcome') == expected_outcome]


def get_break_statistics():
    """Get statistics about sample breaks"""
    total = len(SAMPLE_BREAKS)
    auto_resolve = len(get_breaks_by_outcome('AUTO_RESOLVE'))
    hil_review = len(get_breaks_by_outcome('HIL_REVIEW'))
    escalate = len(get_breaks_by_outcome('ESCALATE'))
    
    break_types = {}
    for brk in SAMPLE_BREAKS:
        bt = brk['break_type']
        break_types[bt] = break_types.get(bt, 0) + 1
    
    return {
        'total': total,
        'auto_resolve': auto_resolve,
        'hil_review': hil_review,
        'escalate': escalate,
        'break_types': break_types,
        'auto_resolve_pct': (auto_resolve / total * 100) if total > 0 else 0,
        'hil_review_pct': (hil_review / total * 100) if total > 0 else 0,
        'escalate_pct': (escalate / total * 100) if total > 0 else 0
    }
