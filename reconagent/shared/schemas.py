"""
Shared Pydantic schemas for the Reconciliation Agent System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class BreakType(str, Enum):
    TRADE_OMS_MISMATCH = "TRADE_OMS_MISMATCH"
    BROKER_VS_INTERNAL = "BROKER_VS_INTERNAL"
    FO_VS_BO = "FO_VS_BO"
    CUSTODIAN_MISMATCH = "CUSTODIAN_MISMATCH"
    CASH_RECONCILIATION = "CASH_RECONCILIATION"
    PNL_RECONCILIATION = "PNL_RECONCILIATION"
    LIFECYCLE_EVENT = "LIFECYCLE_EVENT"
    REGULATORY_DATA = "REGULATORY_DATA"


class ActionType(str, Enum):
    AUTO_RESOLVE = "AUTO_RESOLVE"
    HIL_REVIEW = "HIL_REVIEW"
    ESCALATE = "ESCALATE"
    REJECTED = "REJECTED"


class BreakEntities(BaseModel):
    instrument: str
    account: Optional[str] = None
    broker: Optional[str] = None
    trade_ids: List[str] = Field(default_factory=list)
    order_ids: List[str] = Field(default_factory=list)
    counterparty: Optional[str] = None


class SystemData(BaseModel):
    system_name: str
    quantity: Optional[float] = None
    amount: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    timestamp: Optional[datetime] = None
    raw_fields: Dict[str, Any] = Field(default_factory=dict)


class Break(BaseModel):
    break_id: str
    break_type: BreakType
    status: str = "NEW"
    system_a: SystemData
    system_b: SystemData
    entities: BreakEntities
    date: datetime = Field(default_factory=datetime.now)
    source: str
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class EnrichedData(BaseModel):
    break_id: str
    oms_data: Optional[Dict[str, Any]] = None
    trade_capture_data: Optional[Dict[str, Any]] = None
    settlement_data: Optional[Dict[str, Any]] = None
    custodian_data: Optional[Dict[str, Any]] = None
    reference_data: Optional[Dict[str, Any]] = None
    broker_confirm_data: Optional[Dict[str, Any]] = None


class MatchCandidate(BaseModel):
    candidate_id: str
    match_type: str
    similarity_score: float
    matched_fields: List[str]
    differences: Dict[str, Any] = Field(default_factory=dict)


class RulesEvaluation(BaseModel):
    within_tolerance: bool
    violated_rules: List[str] = Field(default_factory=list)
    tolerance_checks: Dict[str, Any] = Field(default_factory=dict)
    business_rules_applied: List[str] = Field(default_factory=list)


class MLInsights(BaseModel):
    probable_root_cause: str
    confidence: float
    historical_patterns: List[str] = Field(default_factory=list)
    suggested_fix: Optional[str] = None


class Decision(BaseModel):
    break_id: str
    action: ActionType
    labels: List[str] = Field(default_factory=list)
    explanation: str
    confidence: float
    risk_score: float
    requires_hil: bool
    auto_resolvable: bool


class Case(BaseModel):
    break_id: str
    break_data: Break
    enriched_data: Optional[EnrichedData] = None
    match_candidates: List[MatchCandidate] = Field(default_factory=list)
    rules_evaluation: Optional[RulesEvaluation] = None
    ml_insights: Optional[MLInsights] = None
    decision: Optional[Decision] = None
    workflow_status: str = "IN_PROGRESS"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowTicket(BaseModel):
    ticket_id: str
    break_id: str
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
