"""
Policy loader - Loads and validates routing policies from YAML
"""
import yaml
import os
from typing import Dict, Any
from pathlib import Path


class PolicyLoader:
    """
    Loads routing policies from YAML files
    """
    
    def __init__(self, policy_file: str = None):
        if policy_file is None:
            # Default to routing_policies.yaml in same directory
            current_dir = Path(__file__).parent
            policy_file = current_dir / "routing_policies.yaml"
        
        self.policy_file = policy_file
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from YAML file"""
        try:
            with open(self.policy_file, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('policies', {})
        except FileNotFoundError:
            print(f"Warning: Policy file not found: {self.policy_file}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing policy file: {e}")
            return {}
    
    def get_policy(self, break_type: str, risk_tier: str) -> Dict[str, Any]:
        """
        Get policy for a specific break type and risk tier
        
        Args:
            break_type: Type of break (e.g., 'TRADE_OMS_MISMATCH')
            risk_tier: Risk tier (e.g., 'LOW', 'MEDIUM', 'HIGH')
        
        Returns:
            Policy dictionary or default policy
        """
        # Try to get specific policy
        if break_type in self.policies:
            type_policies = self.policies[break_type]
            if risk_tier in type_policies:
                return type_policies[risk_tier]
        
        # Fall back to DEFAULT policy
        if 'DEFAULT' in self.policies:
            default_policies = self.policies['DEFAULT']
            if risk_tier in default_policies:
                return default_policies[risk_tier]
        
        # Ultimate fallback - minimal policy
        return {
            'mandatory_agents': ['BREAK_INGESTION', 'DATA_ENRICHMENT', 'DECISIONING'],
            'optional_agents': [],
            'parallel_groups': [['DATA_ENRICHMENT'], ['DECISIONING']],
            'decision_checkpoints': [],
            'max_parallel': 2,
            'early_exit_enabled': False
        }
    
    def list_break_types(self) -> list:
        """List all break types with policies"""
        return list(self.policies.keys())
    
    def list_risk_tiers(self, break_type: str) -> list:
        """List risk tiers for a specific break type"""
        if break_type in self.policies:
            return list(self.policies[break_type].keys())
        return []
