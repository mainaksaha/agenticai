"""
Agent 7: Workflow & Feedback Agent
Integrates with ticketing and captures feedback
"""
from agents.base_agent import BaseReconAgent
from mcp.tools.workflow_tools import WORKFLOW_TOOLS
from typing import Dict, Any


class WorkflowFeedbackAgent(BaseReconAgent):
    """Agent responsible for workflow management and feedback collection"""
    
    def __init__(self, message_bus=None):
        super().__init__(
            agent_name="workflow_feedback",
            agent_description="Integrates with ticketing systems, captures feedback, and maintains audit trail",
            tools=WORKFLOW_TOOLS,
            message_bus=message_bus
        )
    
    def create_workflow(
        self,
        break_data: Dict[str, Any],
        decision: Dict[str, Any],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create workflow ticket and audit trail
        
        Args:
            break_data: Break data
            decision: Decision data
            case_data: Full case data
        
        Returns:
            Workflow ticket and audit info
        """
        # Create ticket
        create_func = self.tools["create_ticket"]["function"]
        ticket = create_func(
            break_id=break_data.get("break_id"),
            decision=decision,
            case_data=case_data
        )
        
        # Add audit event
        audit_func = self.tools["add_audit_event"]["function"]
        audit_event = audit_func(
            break_id=break_data.get("break_id"),
            event_type="WORKFLOW_CREATED",
            agent_name=self.agent_name,
            details={
                "ticket_id": ticket.get("ticket_id"),
                "action": decision.get("action"),
                "requires_hil": decision.get("requires_hil")
            }
        )
        
        return {
            "break_id": break_data.get("break_id"),
            "ticket": ticket,
            "audit_event": audit_event,
            "status": "WORKFLOW_CREATED"
        }
    
    def log_case_feedback(
        self,
        break_id: str,
        decision: Dict[str, Any],
        human_action: str = None,
        human_notes: str = None
    ) -> Dict[str, Any]:
        """
        Log feedback for learning
        
        Args:
            break_id: Break ID
            decision: Agent decision
            human_action: Human action taken
            human_notes: Human notes
        
        Returns:
            Feedback record
        """
        log_func = self.tools["log_feedback"]["function"]
        feedback = log_func(break_id, decision, human_action, human_notes)
        
        return {
            "break_id": break_id,
            "feedback": feedback,
            "status": "FEEDBACK_LOGGED"
        }
