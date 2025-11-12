"""
Break Classifier - Analyzes incoming breaks and creates profiles for routing
"""
from typing import Dict, Any
from .schemas import BreakProfile, RiskTier, Materiality, Urgency


class BreakClassifier:
    """
    Classifies breaks and creates profiles for dynamic routing
    """
    
    def __init__(self):
        # Thresholds for classification
        self.low_risk_threshold = 5000
        self.medium_risk_threshold = 50000
        self.high_risk_threshold = 100000
        
        # Break types that always require pattern analysis
        self.pattern_required_types = [
            'PNL_RECONCILIATION',
            'REGULATORY_DATA',
            'LIFECYCLE_EVENT'
        ]
        
        # Break types that require compliance check
        self.compliance_required_types = [
            'REGULATORY_DATA',
            'BROKER_VS_INTERNAL'
        ]
        
        # Asset classes with higher complexity
        self.complex_asset_classes = [
            'DERIVATIVE',
            'STRUCTURED_PRODUCT',
            'EXOTIC_OPTION'
        ]
    
    def classify(self, break_data: Dict[str, Any]) -> BreakProfile:
        """
        Analyze break data and create a profile
        
        Args:
            break_data: Raw break data dictionary
        
        Returns:
            BreakProfile with routing hints
        """
        break_id = break_data.get('break_id', 'UNKNOWN')
        break_type = break_data.get('break_type', 'UNKNOWN')
        
        # Calculate exposure
        exposure = self._calculate_exposure(break_data)
        
        # Determine risk tier
        risk_tier = self._determine_risk_tier(exposure, break_type, break_data)
        
        # Determine asset class
        asset_class = self._determine_asset_class(break_data)
        
        # Extract source systems
        source_systems = self._extract_source_systems(break_data)
        
        # Determine materiality
        materiality = self._determine_materiality(exposure, break_type)
        
        # Determine urgency
        urgency = self._determine_urgency(risk_tier, break_type)
        
        # Determine routing requirements
        requires_matching = self._requires_matching(break_type)
        requires_pattern_analysis = self._requires_pattern_analysis(
            break_type, risk_tier, exposure
        )
        requires_compliance_check = self._requires_compliance_check(break_type)
        
        return BreakProfile(
            break_id=break_id,
            break_type=break_type,
            asset_class=asset_class,
            exposure=exposure,
            risk_tier=risk_tier,
            source_systems=source_systems,
            materiality=materiality,
            urgency=urgency,
            requires_enrichment=True,  # Almost always needed
            requires_matching=requires_matching,
            requires_pattern_analysis=requires_pattern_analysis,
            requires_compliance_check=requires_compliance_check,
            classification_confidence=1.0
        )
    
    def _calculate_exposure(self, break_data: Dict[str, Any]) -> float:
        """Calculate the exposure/amount at risk"""
        system_a = break_data.get('system_a', {})
        system_b = break_data.get('system_b', {})
        
        amount_a = abs(float(system_a.get('amount', 0)))
        amount_b = abs(float(system_b.get('amount', 0)))
        
        # Exposure is the difference
        exposure = abs(amount_a - amount_b)
        
        return exposure
    
    def _determine_risk_tier(
        self, 
        exposure: float, 
        break_type: str, 
        break_data: Dict[str, Any]
    ) -> RiskTier:
        """Determine risk tier based on exposure and type"""
        # Critical types always high risk
        if break_type in ['REGULATORY_DATA', 'LIFECYCLE_EVENT']:
            return RiskTier.CRITICAL
        
        # Amount-based risk
        if exposure < self.low_risk_threshold:
            risk_tier = RiskTier.LOW
        elif exposure < self.medium_risk_threshold:
            risk_tier = RiskTier.MEDIUM
        elif exposure < self.high_risk_threshold:
            risk_tier = RiskTier.HIGH
        else:
            risk_tier = RiskTier.CRITICAL
        
        # Elevate risk for complex asset classes
        asset_class = self._determine_asset_class(break_data)
        if asset_class in self.complex_asset_classes:
            if risk_tier == RiskTier.LOW:
                risk_tier = RiskTier.MEDIUM
            elif risk_tier == RiskTier.MEDIUM:
                risk_tier = RiskTier.HIGH
        
        return risk_tier
    
    def _determine_asset_class(self, break_data: Dict[str, Any]) -> str:
        """Determine asset class from break data"""
        entities = break_data.get('entities', {})
        instrument = entities.get('instrument', '')
        
        # Simple heuristics - in production, use reference data
        if instrument.startswith(('FX', 'USD', 'EUR', 'GBP')):
            return 'FX'
        elif instrument.endswith(('OPT', 'CALL', 'PUT')):
            return 'DERIVATIVE'
        elif instrument.endswith('.SW'):
            return 'STRUCTURED_PRODUCT'
        else:
            return 'EQUITY'  # Default
    
    def _extract_source_systems(self, break_data: Dict[str, Any]) -> list:
        """Extract source systems involved in the break"""
        systems = []
        
        if 'system_a' in break_data:
            sys_a = break_data['system_a'].get('source', 'UNKNOWN')
            if sys_a != 'UNKNOWN':
                systems.append(sys_a)
        
        if 'system_b' in break_data:
            sys_b = break_data['system_b'].get('source', 'UNKNOWN')
            if sys_b != 'UNKNOWN':
                systems.append(sys_b)
        
        return systems
    
    def _determine_materiality(self, exposure: float, break_type: str) -> Materiality:
        """Determine materiality level"""
        if exposure < self.low_risk_threshold:
            return Materiality.LOW
        elif exposure < self.medium_risk_threshold:
            return Materiality.MEDIUM
        else:
            return Materiality.HIGH
    
    def _determine_urgency(self, risk_tier: RiskTier, break_type: str) -> Urgency:
        """Determine urgency level"""
        if risk_tier == RiskTier.CRITICAL:
            return Urgency.CRITICAL
        elif risk_tier == RiskTier.HIGH:
            return Urgency.HIGH
        else:
            return Urgency.NORMAL
    
    def _requires_matching(self, break_type: str) -> bool:
        """Determine if matching is required"""
        matching_types = [
            'TRADE_OMS_MISMATCH',
            'BROKER_VS_INTERNAL',
            'FO_VS_BO',
            'CUSTODIAN_MISMATCH'
        ]
        return break_type in matching_types
    
    def _requires_pattern_analysis(
        self, 
        break_type: str, 
        risk_tier: RiskTier, 
        exposure: float
    ) -> bool:
        """Determine if pattern analysis is required"""
        # Always for specific types
        if break_type in self.pattern_required_types:
            return True
        
        # For high risk or high exposure
        if risk_tier in [RiskTier.HIGH, RiskTier.CRITICAL]:
            return True
        
        if exposure > self.medium_risk_threshold:
            return True
        
        return False
    
    def _requires_compliance_check(self, break_type: str) -> bool:
        """Determine if compliance check is required"""
        return break_type in self.compliance_required_types
