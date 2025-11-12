"""
Base Agent class with A2A communication and MCP tool integration
"""
import time
from typing import Dict, Any, List, Callable, Optional
from openai import OpenAI
from shared.a2a_protocol import A2AMessage, A2AProtocol, MessageType, MessagePriority
from shared.config import settings
import os


class BaseReconAgent:
    """Base class for all reconciliation agents"""
    
    def __init__(
        self,
        agent_name: str,
        agent_description: str,
        tools: Dict[str, Dict[str, Any]],
        message_bus: Any = None
    ):
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.tools = tools
        self.message_bus = message_bus
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            print(f"Warning: OPENAI_API_KEY not set for {agent_name}")
        
        # Convert tools to ADK format
        self.adk_tools = self._prepare_adk_tools()
        
        # Subscribe to message bus
        if self.message_bus:
            self.message_bus.subscribe(self.agent_name, self._handle_message)
    
    def _prepare_adk_tools(self) -> List[Dict[str, Any]]:
        """Prepare tools in ADK-compatible format"""
        adk_tools = []
        
        for tool_name, tool_def in self.tools.items():
            # Create function declaration for ADK
            parameters = {}
            for param_name, param_def in tool_def.get("parameters", {}).items():
                parameters[param_name] = {
                    "type": param_def.get("type", "string"),
                    "description": param_def.get("description", "")
                }
            
            adk_tools.append({
                "name": tool_name,
                "description": tool_def.get("description", ""),
                "parameters": parameters,
                "function": tool_def.get("function")
            })
        
        return adk_tools
    
    def _handle_message(self, message: A2AMessage):
        """Handle incoming A2A message"""
        if message.message_type == MessageType.REQUEST:
            self._process_request(message)
        elif message.message_type == MessageType.RESPONSE:
            self._process_response(message)
        elif message.message_type == MessageType.NOTIFICATION:
            self._process_notification(message)
    
    def _process_request(self, message: A2AMessage):
        """Process incoming request"""
        print(f"[{self.agent_name}] Processing request: {message.payload.get('action')}")
        
        action = message.payload.get("action")
        parameters = message.payload.get("parameters", {})
        
        start_time = time.time()
        
        try:
            # Execute requested action
            result = self.execute_action(action, parameters)
            processing_time = (time.time() - start_time) * 1000
            
            # Send response
            response = A2AProtocol.create_response(
                request_message=message,
                success=True,
                result=result,
                processing_time_ms=processing_time
            )
            
            if self.message_bus:
                self.message_bus.publish(response)
        
        except Exception as e:
            # Send error response
            error_response = A2AProtocol.create_error(message, str(e))
            if self.message_bus:
                self.message_bus.publish(error_response)
    
    def _process_response(self, message: A2AMessage):
        """Process incoming response"""
        print(f"[{self.agent_name}] Received response: {message.payload.get('success')}")
    
    def _process_notification(self, message: A2AMessage):
        """Process incoming notification"""
        print(f"[{self.agent_name}] Received notification: {message.payload.get('event_type')}")
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action using available tools
        
        Args:
            action: Action name (tool name)
            parameters: Action parameters
        
        Returns:
            Action result
        """
        # Find matching tool
        for tool in self.adk_tools:
            if tool["name"] == action:
                function = tool["function"]
                return function(**parameters)
        
        raise ValueError(f"Unknown action: {action}")
    
    def send_request(
        self,
        to_agent: str,
        action: str,
        parameters: Dict[str, Any],
        conversation_id: str,
        priority: MessagePriority = MessagePriority.MEDIUM
    ) -> A2AMessage:
        """Send request to another agent"""
        message = A2AProtocol.create_request(
            from_agent=self.agent_name,
            to_agent=to_agent,
            action=action,
            parameters=parameters,
            conversation_id=conversation_id,
            priority=priority
        )
        
        if self.message_bus:
            self.message_bus.publish(message)
        
        return message
    
    def send_notification(
        self,
        to_agent: str,
        event_type: str,
        event_data: Dict[str, Any],
        conversation_id: str
    ):
        """Send notification to another agent"""
        message = A2AProtocol.create_notification(
            from_agent=self.agent_name,
            to_agent=to_agent,
            event_type=event_type,
            event_data=event_data,
            conversation_id=conversation_id
        )
        
        if self.message_bus:
            self.message_bus.publish(message)
    
    def process_with_llm(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        use_tools: bool = True
    ) -> str:
        """
        Process request using OpenAI GPT-4.1 LLM
        
        Args:
            prompt: Prompt text
            context: Optional context data
            use_tools: Whether to enable tool use
        
        Returns:
            LLM response
        """
        if not self.client:
            return "Error: OpenAI client not initialized"
        
        # Build full prompt with context
        full_prompt = f"""You are {self.agent_name}, a specialized agent in a reconciliation system.
Your role: {self.agent_description}

{f'Context: {context}' if context else ''}

{prompt}
"""
        
        try:
            # Use OpenAI GPT-4.1 (gpt-4-turbo-preview)
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # GPT-4.1
                messages=[
                    {"role": "system", "content": f"You are {self.agent_name}. {self.agent_description}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error: {str(e)}"
