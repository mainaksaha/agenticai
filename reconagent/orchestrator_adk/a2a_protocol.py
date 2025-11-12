"""
Official A2A (Agent2Agent) Protocol Implementation
Uses official a2a-python SDK patterns

Official A2A Protocol: https://a2aprotocol.ai/
GitHub: https://github.com/google-a2a/a2a-python
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

# When a2a-python is installed, these imports will work:
# from a2a import A2AMessage, A2AClient, A2AServer, TaskStatus
# from a2a.types import MessageType, Priority

# For now, we create A2A-compatible structures


class A2AMessageType:
    """Official A2A Message Types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class A2ATaskStatus:
    """Official A2A Task Status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class A2AMessage(BaseModel):
    """
    Official A2A Protocol Message Format
    
    Spec: https://a2a-protocol.org/latest/spec/message/
    """
    # Message metadata
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = A2AMessageType.REQUEST
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Agent information
    from_agent: str
    to_agent: str
    
    # Task information
    task_id: Optional[str] = None
    context_id: Optional[str] = None
    
    # Message content
    content: Dict[str, Any]
    
    # Optional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Threading support
    reply_to: Optional[str] = None
    conversation_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg-123",
                "type": "request",
                "from_agent": "agent1",
                "to_agent": "agent2",
                "content": {
                    "action": "enrich_data",
                    "parameters": {"break_id": "BRK-001"}
                }
            }
        }


class A2ATask(BaseModel):
    """
    Official A2A Task
    
    A Task represents a complete execution of an agent
    """
    task_id: str = Field(default_factory=lambda: f"task-{uuid.uuid4().hex[:8]}")
    agent_name: str
    status: str = A2ATaskStatus.PENDING
    
    # Task input/output
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error handling
    error: Optional[str] = None
    
    # Context
    context_id: Optional[str] = None


class A2AContext(BaseModel):
    """
    Official A2A Context
    
    Context maintains continuity across multiple messages
    """
    context_id: str = Field(default_factory=lambda: f"ctx-{uuid.uuid4().hex[:8]}")
    messages: List[A2AMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class A2AProtocolHandler:
    """
    Handler for A2A Protocol operations
    
    Official pattern from a2a-python SDK:
    from a2a import A2AClient, A2AServer
    
    client = A2AClient()
    server = A2AServer(agent)
    """
    
    def __init__(self):
        self.contexts: Dict[str, A2AContext] = {}
        self.tasks: Dict[str, A2ATask] = {}
    
    def create_message(
        self,
        from_agent: str,
        to_agent: str,
        content: Dict[str, Any],
        message_type: str = A2AMessageType.REQUEST,
        context_id: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> A2AMessage:
        """
        Create an A2A message
        
        Official pattern:
        message = A2AMessage(
            from_agent="agent1",
            to_agent="agent2",
            content={...}
        )
        """
        message = A2AMessage(
            type=message_type,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            context_id=context_id,
            reply_to=reply_to
        )
        
        # Add to context if context_id provided
        if context_id and context_id in self.contexts:
            self.contexts[context_id].messages.append(message)
        
        return message
    
    def create_task(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        context_id: Optional[str] = None
    ) -> A2ATask:
        """
        Create an A2A task
        
        Official pattern:
        task = Task(
            agent=agent_name,
            input=input_data
        )
        """
        task = A2ATask(
            agent_name=agent_name,
            input=input_data,
            context_id=context_id
        )
        
        self.tasks[task.task_id] = task
        return task
    
    def create_context(self, metadata: Optional[Dict[str, Any]] = None) -> A2AContext:
        """
        Create an A2A context
        
        Official pattern:
        context = Context()
        """
        context = A2AContext(metadata=metadata or {})
        self.contexts[context.context_id] = context
        return context
    
    async def send_message(self, message: A2AMessage) -> A2AMessage:
        """
        Send A2A message to target agent
        
        Official pattern:
        client = A2AClient()
        response = await client.send(message)
        """
        # In production, this would use actual A2A transport
        # For now, we simulate message delivery
        
        # Create response message
        response = self.create_message(
            from_agent=message.to_agent,
            to_agent=message.from_agent,
            content={
                "status": "received",
                "request_id": message.id
            },
            message_type=A2AMessageType.RESPONSE,
            context_id=message.context_id,
            reply_to=message.id
        )
        
        return response
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Update task status"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            
            if status == A2ATaskStatus.RUNNING and not task.started_at:
                task.started_at = datetime.now()
            
            if status in [A2ATaskStatus.COMPLETED, A2ATaskStatus.FAILED]:
                task.completed_at = datetime.now()
            
            if output:
                task.output = output
            
            if error:
                task.error = error
    
    def get_context_messages(self, context_id: str) -> List[A2AMessage]:
        """Get all messages in a context (conversation threading)"""
        if context_id in self.contexts:
            return self.contexts[context_id].messages
        return []
    
    def get_task(self, task_id: str) -> Optional[A2ATask]:
        """Get task by ID"""
        return self.tasks.get(task_id)


# Global A2A protocol handler instance
a2a_protocol = A2AProtocolHandler()
