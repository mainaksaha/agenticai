"""
A2A (Agent-to-Agent) Protocol Implementation
Defines message formats and communication utilities for agent interaction
"""
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class MessageType(str, Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    NOTIFICATION = "NOTIFICATION"
    ERROR = "ERROR"


class MessagePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class A2AMessage(BaseModel):
    """Base A2A message structure"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    message_type: MessageType
    priority: MessagePriority = MessagePriority.MEDIUM
    from_agent: str
    to_agent: str
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    reply_to: Optional[str] = None


class AgentRequest(BaseModel):
    """Request from one agent to another"""
    action: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Response from agent to requesting agent"""
    request_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None


class AgentNotification(BaseModel):
    """Notification sent by agent (no response expected)"""
    event_type: str
    event_data: Dict[str, Any]


class A2AProtocol:
    """Utility class for A2A communication"""
    
    @staticmethod
    def create_request(
        from_agent: str,
        to_agent: str,
        action: str,
        parameters: Dict[str, Any],
        conversation_id: str,
        priority: MessagePriority = MessagePriority.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ) -> A2AMessage:
        """Create a request message"""
        request = AgentRequest(
            action=action,
            parameters=parameters,
            context=context
        )
        return A2AMessage(
            conversation_id=conversation_id,
            message_type=MessageType.REQUEST,
            priority=priority,
            from_agent=from_agent,
            to_agent=to_agent,
            payload=request.model_dump()
        )
    
    @staticmethod
    def create_response(
        request_message: A2AMessage,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        processing_time_ms: Optional[float] = None
    ) -> A2AMessage:
        """Create a response message"""
        response = AgentResponse(
            request_id=request_message.message_id,
            success=success,
            result=result,
            error=error,
            processing_time_ms=processing_time_ms
        )
        return A2AMessage(
            conversation_id=request_message.conversation_id,
            message_type=MessageType.RESPONSE,
            priority=request_message.priority,
            from_agent=request_message.to_agent,
            to_agent=request_message.from_agent,
            payload=response.model_dump(),
            reply_to=request_message.message_id
        )
    
    @staticmethod
    def create_notification(
        from_agent: str,
        to_agent: str,
        event_type: str,
        event_data: Dict[str, Any],
        conversation_id: str,
        priority: MessagePriority = MessagePriority.LOW
    ) -> A2AMessage:
        """Create a notification message"""
        notification = AgentNotification(
            event_type=event_type,
            event_data=event_data
        )
        return A2AMessage(
            conversation_id=conversation_id,
            message_type=MessageType.NOTIFICATION,
            priority=priority,
            from_agent=from_agent,
            to_agent=to_agent,
            payload=notification.model_dump()
        )
    
    @staticmethod
    def create_error(
        request_message: A2AMessage,
        error_message: str
    ) -> A2AMessage:
        """Create an error message"""
        return A2AMessage(
            conversation_id=request_message.conversation_id,
            message_type=MessageType.ERROR,
            priority=MessagePriority.HIGH,
            from_agent=request_message.to_agent,
            to_agent=request_message.from_agent,
            payload={"error": error_message, "original_request_id": request_message.message_id},
            reply_to=request_message.message_id
        )


class MessageBus:
    """Simple in-memory message bus for A2A communication"""
    
    def __init__(self):
        self.messages: List[A2AMessage] = []
        self.subscribers: Dict[str, List[callable]] = {}
    
    def publish(self, message: A2AMessage):
        """Publish message to the bus"""
        self.messages.append(message)
        
        # Notify subscribers
        if message.to_agent in self.subscribers:
            for callback in self.subscribers[message.to_agent]:
                callback(message)
    
    def subscribe(self, agent_name: str, callback: callable):
        """Subscribe agent to receive messages"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
    
    def get_conversation_history(self, conversation_id: str) -> List[A2AMessage]:
        """Get all messages for a conversation"""
        return [msg for msg in self.messages if msg.conversation_id == conversation_id]
