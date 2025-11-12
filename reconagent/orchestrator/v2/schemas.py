"""
Schemas for Dynamic Orchestration v2
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class RiskTier(str, Enum):
    """Risk tier classification"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Materiality(str, Enum):
    """Materiality level"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Urgency(str, Enum):
    """Urgency level"""
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BreakProfile(BaseModel):
    """
    Profile of a break used for routing decisions
    """
    break_id: str
    break_type: str
    asset_class: str = "UNKNOWN"
    exposure: float = 0.0
    risk_tier: RiskTier = RiskTier.MEDIUM
    source_systems: List[str] = Field(default_factory=list)
    materiality: Materiality = Materiality.MEDIUM
    urgency: Urgency = Urgency.NORMAL
    
    # Routing hints
    requires_enrichment: bool = True
    requires_matching: bool = True
    requires_pattern_analysis: bool = False
    requires_compliance_check: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    classification_confidence: float = 1.0


class AgentNode(BaseModel):
    """
    Represents an agent in the execution graph
    """
    node_id: str
    agent_name: str
    depends_on: List[str] = Field(default_factory=list)
    can_run_parallel: bool = True
    is_mandatory: bool = True
    skip_conditions: List[str] = Field(default_factory=list)
    timeout_seconds: int = 30


class DecisionCheckpoint(BaseModel):
    """
    Decision checkpoint in the execution plan
    """
    checkpoint_id: str
    after_nodes: List[str]
    condition: str
    action: str  # AUTO_RESOLVE, HIL_REVIEW, ESCALATE, CONTINUE
    confidence_threshold: float = 0.9


class ExecutionPlan(BaseModel):
    """
    Execution plan for a break - defines which agents to run and in what order
    """
    plan_id: str
    break_profile: BreakProfile
    nodes: List[AgentNode]
    decision_checkpoints: List[DecisionCheckpoint] = Field(default_factory=list)
    max_parallel: int = 3
    early_exit_enabled: bool = True
    policy_version: str = "2.0.0"
    created_at: datetime = Field(default_factory=datetime.now)


class NodeExecution(BaseModel):
    """
    Execution record for a single node
    """
    node_id: str
    agent_name: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    skip_reason: Optional[str] = None


class ExecutionGraph(BaseModel):
    """
    Complete execution graph with all node executions
    """
    break_id: str
    plan_id: str
    executions: List[NodeExecution] = Field(default_factory=list)
    decision: Optional[Dict[str, Any]] = None
    early_exit: bool = False
    early_exit_reason: Optional[str] = None
    total_duration_ms: float = 0.0
    agents_invoked: int = 0
    agents_skipped: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class RoutingPolicy(BaseModel):
    """
    Routing policy for a specific break type/risk combination
    """
    policy_id: str
    break_type: str
    risk_tier: RiskTier
    mandatory_agents: List[str]
    optional_agents: List[str] = Field(default_factory=list)
    parallel_groups: List[List[str]] = Field(default_factory=list)
    decision_checkpoints: List[Dict[str, Any]] = Field(default_factory=list)
    max_parallel: int = 3
    early_exit_enabled: bool = True
