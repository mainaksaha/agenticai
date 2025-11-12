"""
Policy Engine - Translates break profiles into execution plans
"""
import uuid
from typing import Dict, Any, List
from .schemas import (
    BreakProfile, ExecutionPlan, AgentNode, 
    DecisionCheckpoint, RiskTier
)
from .policies.policy_loader import PolicyLoader


class PolicyEngine:
    """
    Policy engine that generates execution plans based on break profiles
    """
    
    def __init__(self, policy_file: str = None):
        self.policy_loader = PolicyLoader(policy_file)
        
        # Agent name mapping (policy name -> actual agent class)
        self.agent_mapping = {
            'BREAK_INGESTION': 'break_ingestion',
            'DATA_ENRICHMENT': 'data_enrichment',
            'MATCHING_CORRELATION': 'matching_correlation',
            'RULES_TOLERANCE': 'rules_tolerance',
            'PATTERN_INTELLIGENCE': 'pattern_intelligence',
            'DECISIONING': 'decisioning',
            'WORKFLOW_FEEDBACK': 'workflow_feedback'
        }
    
    def create_execution_plan(self, break_profile: BreakProfile) -> ExecutionPlan:
        """
        Create an execution plan based on break profile
        
        Args:
            break_profile: Classified break profile
        
        Returns:
            ExecutionPlan with nodes and dependencies
        """
        # Get policy for this break type and risk tier
        policy = self.policy_loader.get_policy(
            break_profile.break_type,
            break_profile.risk_tier.value
        )
        
        # Build agent nodes
        nodes = self._build_nodes(policy, break_profile)
        
        # Build decision checkpoints
        checkpoints = self._build_checkpoints(policy)
        
        # Create execution plan
        plan = ExecutionPlan(
            plan_id=f"PLAN-{uuid.uuid4().hex[:8]}",
            break_profile=break_profile,
            nodes=nodes,
            decision_checkpoints=checkpoints,
            max_parallel=policy.get('max_parallel', 3),
            early_exit_enabled=policy.get('early_exit_enabled', True),
            policy_version="2.0.0"
        )
        
        return plan
    
    def _build_nodes(
        self, 
        policy: Dict[str, Any], 
        break_profile: BreakProfile
    ) -> List[AgentNode]:
        """
        Build agent nodes from policy
        
        Args:
            policy: Policy dictionary
            break_profile: Break profile for conditional logic
        
        Returns:
            List of AgentNode objects
        """
        nodes = []
        mandatory_agents = policy.get('mandatory_agents', [])
        optional_agents = policy.get('optional_agents', [])
        parallel_groups = policy.get('parallel_groups', [])
        
        # Track which agents have been added
        added_agents = set()
        
        # Create dependency structure based on parallel groups
        previous_group_agents = []
        
        for group_idx, group in enumerate(parallel_groups):
            for agent_name in group:
                # Skip if already added
                if agent_name in added_agents:
                    continue
                
                # Check if agent should be included
                if agent_name not in mandatory_agents and agent_name not in optional_agents:
                    continue
                
                # Determine if it's mandatory
                is_mandatory = agent_name in mandatory_agents
                
                # Optional agents may be skipped based on profile
                if not is_mandatory and not self._should_include_optional(agent_name, break_profile):
                    continue
                
                # Create node
                node = AgentNode(
                    node_id=f"N{len(nodes)+1}",
                    agent_name=agent_name,
                    depends_on=previous_group_agents.copy() if group_idx > 0 else [],
                    can_run_parallel=len(group) > 1,
                    is_mandatory=is_mandatory
                )
                
                nodes.append(node)
                added_agents.add(agent_name)
            
            # Update previous group for next iteration
            if group:
                previous_group_agents = [f"N{i+1}" for i, n in enumerate(nodes) if n.agent_name in group]
        
        return nodes
    
    def _should_include_optional(self, agent_name: str, break_profile: BreakProfile) -> bool:
        """
        Determine if optional agent should be included based on break profile
        
        Args:
            agent_name: Name of the optional agent
            break_profile: Break profile
        
        Returns:
            True if agent should be included
        """
        # MATCHING_CORRELATION - only if matching is required
        if agent_name == 'MATCHING_CORRELATION':
            return break_profile.requires_matching
        
        # PATTERN_INTELLIGENCE - only if pattern analysis is required
        if agent_name == 'PATTERN_INTELLIGENCE':
            return break_profile.requires_pattern_analysis
        
        # Default: include all optional agents
        return True
    
    def _build_checkpoints(self, policy: Dict[str, Any]) -> List[DecisionCheckpoint]:
        """
        Build decision checkpoints from policy
        
        Args:
            policy: Policy dictionary
        
        Returns:
            List of DecisionCheckpoint objects
        """
        checkpoints = []
        checkpoint_configs = policy.get('decision_checkpoints', [])
        
        for idx, config in enumerate(checkpoint_configs):
            checkpoint = DecisionCheckpoint(
                checkpoint_id=f"CP{idx+1}",
                after_nodes=config.get('after_nodes', []),
                condition=config.get('condition', 'always'),
                action=config.get('action', 'CONTINUE'),
                confidence_threshold=config.get('confidence_threshold', 0.9)
            )
            checkpoints.append(checkpoint)
        
        return checkpoints
    
    def get_agent_dependencies(self, plan: ExecutionPlan, node_id: str) -> List[str]:
        """
        Get all dependencies for a node
        
        Args:
            plan: Execution plan
            node_id: Node ID
        
        Returns:
            List of node IDs that this node depends on
        """
        for node in plan.nodes:
            if node.node_id == node_id:
                return node.depends_on
        return []
    
    def get_next_agents(self, plan: ExecutionPlan, completed: set) -> List[AgentNode]:
        """
        Get agents that are ready to execute (all dependencies met)
        
        Args:
            plan: Execution plan
            completed: Set of completed node IDs
        
        Returns:
            List of AgentNode objects ready to execute
        """
        ready = []
        for node in plan.nodes:
            # Skip if already completed
            if node.node_id in completed:
                continue
            
            # Check if all dependencies are met
            deps_met = all(dep in completed for dep in node.depends_on)
            
            if deps_met:
                ready.append(node)
        
        return ready
