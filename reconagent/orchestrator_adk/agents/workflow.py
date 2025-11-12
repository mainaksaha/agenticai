"""
Workflow Agent - Google ADK Implementation
Integrates with ticketing and captures feedback
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig, ADKTool
from mcp.tools import workflow_tools


class WorkflowAgent(ADKAgent):
    """ADK Agent for workflow and feedback management"""
    
    def __init__(self):
        tools = [
            ADKTool(
                name="create_ticket",
                description="Create workflow ticket",
                function=workflow_tools.create_ticket,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "decision": {"type": "object", "description": "Decision"},
                    "case_data": {"type": "object", "description": "Complete case data"}
                }
            ),
            ADKTool(
                name="update_ticket",
                description="Update existing ticket",
                function=workflow_tools.update_ticket,
                parameters={
                    "ticket_id": {"type": "string", "description": "Ticket ID"},
                    "updates": {"type": "object", "description": "Updates"}
                }
            ),
            ADKTool(
                name="log_feedback",
                description="Log human feedback for learning",
                function=workflow_tools.log_feedback,
                parameters={
                    "break_id": {"type": "string", "description": "Break ID"},
                    "decision": {"type": "object", "description": "Agent decision"},
                    "human_action": {"type": "string", "description": "Human action"},
                    "human_notes": {"type": "string", "description": "Human notes"}
                }
            ),
            ADKTool(
                name="get_audit_trail",
                description="Get audit trail for break",
                function=workflow_tools.get_audit_trail,
                parameters={
                    "break_id": {"type": "string", "description": "Break ID"}
                }
            ),
            ADKTool(
                name="add_audit_event",
                description="Add event to audit trail",
                function=workflow_tools.add_audit_event,
                parameters={
                    "break_id": {"type": "string", "description": "Break ID"},
                    "event_type": {"type": "string", "description": "Event type"},
                    "event_data": {"type": "object", "description": "Event data"}
                }
            )
        ]
        
        config = ADKAgentConfig(
            name="workflow_feedback",
            description="Integrates with ticketing and captures feedback",
            model="gemini-2.0-flash-exp",
            tools=tools,
            instructions="""You are the Workflow & Feedback Agent.
Your responsibilities:
1. Create tickets for breaks
2. Update ticket status
3. Log human feedback for learning
4. Maintain audit trail
5. Capture all events for compliance

Ensure all actions are logged for audit and learning purposes."""
        )
        
        super().__init__(config)
    
    async def create_workflow(
        self,
        break_data: Dict[str, Any],
        decision: Dict[str, Any],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create workflow ticket
        
        Args:
            break_data: Break data
            decision: Final decision
            case_data: Complete case data
        
        Returns:
            Created ticket information
        """
        # Create ticket
        ticket_task = {
            'action': 'create_ticket',
            'parameters': {
                'break_data': break_data,
                'decision': decision,
                'case_data': case_data
            }
        }
        
        ticket_result = await self.process(ticket_task)
        
        if ticket_result['success']:
            ticket = ticket_result['result'].get('ticket', {})
            
            # Add audit event
            audit_task = {
                'action': 'add_audit_event',
                'parameters': {
                    'break_id': break_data.get('break_id'),
                    'event_type': 'WORKFLOW_CREATED',
                    'event_data': {
                        'ticket_id': ticket.get('ticket_id'),
                        'decision': decision.get('action'),
                        'status': ticket.get('status')
                    }
                }
            }
            
            await self.process(audit_task)
            
            return {
                'success': True,
                'ticket': ticket
            }
        else:
            return ticket_result
