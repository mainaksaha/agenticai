"""
Configuration settings for the Reconciliation Agent System
"""
from pydantic_settings import BaseSettings
from typing import Dict, Any


class Settings(BaseSettings):
    # Application
    app_name: str = "Reconciliation Agent System"
    environment: str = "development"
    debug: bool = True
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"  # GPT-4.1
    
    # Mock API Settings
    mock_api_host: str = "127.0.0.1"
    mock_api_port: int = 8000
    mock_api_base_url: str = "http://127.0.0.1:8000"
    
    # MCP Settings
    mcp_server_host: str = "127.0.0.1"
    mcp_server_port: int = 8001
    
    # Agent Settings
    agent_timeout_seconds: int = 30
    max_retries: int = 3
    
    # Tolerance Settings
    default_amount_tolerance_bps: float = 0.5
    default_quantity_tolerance: float = 0.01
    fx_tolerance_bps: float = 2.0
    
    # Decision Thresholds
    auto_resolve_confidence_threshold: float = 0.90
    auto_resolve_max_amount: float = 10000.0
    escalation_amount_threshold: float = 100000.0
    high_risk_score_threshold: float = 0.75
    
    # Database (for future use)
    database_url: str = "sqlite:///./reconagent.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Agent Registry
AGENT_REGISTRY = {
    "break_ingestion": {
        "name": "Break Ingestion Agent",
        "description": "Normalizes incoming reconciliation breaks",
        "tools": ["get_breaks", "normalize_break", "validate_break"]
    },
    "data_enrichment": {
        "name": "Data Enrichment Agent",
        "description": "Gathers details from multiple systems",
        "tools": ["get_oms_data", "get_trade_capture", "get_settlement", 
                  "get_custodian_data", "get_reference_data", "get_broker_confirm"]
    },
    "matching_correlation": {
        "name": "Matching & Correlation Agent",
        "description": "Identifies candidate matches",
        "tools": ["find_match_candidates", "calculate_similarity", "correlate_trades"]
    },
    "rules_tolerance": {
        "name": "Rules & Tolerance Agent",
        "description": "Applies business rules and tolerance checks",
        "tools": ["check_tolerance", "apply_business_rules", "validate_rules"]
    },
    "pattern_intelligence": {
        "name": "Pattern & Root-Cause Intelligence Agent",
        "description": "Learns from history to infer probable causes",
        "tools": ["get_historical_patterns", "predict_root_cause", "suggest_fix"]
    },
    "decisioning": {
        "name": "Decisioning Agent",
        "description": "Combines insights and makes final decision",
        "tools": ["evaluate_decision", "calculate_risk_score", "determine_action"]
    },
    "workflow_feedback": {
        "name": "Workflow & Feedback Agent",
        "description": "Integrates with ticketing and captures feedback",
        "tools": ["create_ticket", "update_ticket", "log_feedback", "get_audit_trail"]
    }
}
