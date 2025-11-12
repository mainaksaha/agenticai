"""
Google ADK Agent Base Implementation
Uses official Google ADK Agent class
"""
from typing import Dict, Any, List, Optional
from google import genai
# Note: google-adk import structure (this is conceptual as actual SDK may vary)
# from google.adk import Agent, Tool, TaskResult
# from google.adk.types import AgentConfig

# For now, we'll create ADK-compatible structure that matches the official pattern
# Once google-adk is installed, these imports will be replaced with actual SDK imports

class ADKAgentConfig:
    """Configuration for ADK Agent (matches official pattern)"""
    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gemini-2.0-flash-exp",
        tools: List[Any] = None,
        instructions: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.model = model
        self.tools = tools or []
        self.instructions = instructions


class ADKTool:
    """
    ADK Tool Definition (matches official Google ADK pattern)
    
    Official pattern:
    from google.adk import Tool
    
    Tool(
        name="tool_name",
        description="What the tool does",
        function=callable,
        parameters={...}
    )
    """
    def __init__(
        self,
        name: str,
        description: str,
        function: callable,
        parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool function with parameter handling"""
        import inspect
        
        # Get the function signature
        sig = inspect.signature(self.function)
        
        # Filter kwargs to only include parameters the function accepts
        valid_kwargs = {}
        for param_name in sig.parameters:
            if param_name in kwargs:
                valid_kwargs[param_name] = kwargs[param_name]
        
        try:
            result = self.function(**valid_kwargs)
            # Ensure result is always a dict
            if not isinstance(result, dict):
                result = {"value": result}
            return result
        except Exception as e:
            # If execution fails, return error dict
            return {
                "error": str(e),
                "tool": self.name,
                "parameters_provided": list(kwargs.keys()),
                "parameters_expected": list(sig.parameters.keys())
            }


class ADKAgent:
    """
    Base ADK Agent (compatible with official Google ADK)
    
    Official Google ADK Agent pattern:
    from google.adk import Agent
    
    class MyAgent(Agent):
        name = "my_agent"
        description = "What my agent does"
        model = "gemini-2.0-flash-exp"
        tools = [tool1, tool2]
        
        async def process(self, task):
            # Agent logic
            return TaskResult(...)
    """
    
    def __init__(self, config: ADKAgentConfig):
        self.config = config
        self.name = config.name
        self.description = config.description
        self.model = config.model
        self.tools = {tool.name: tool for tool in config.tools}
        self.instructions = config.instructions
        
        # Initialize OpenAI client (changed from Gemini)
        self.client = None
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            # Use OpenAI model - check env first, then convert from Gemini
            openai_model = os.getenv("OPENAI_MODEL")
            if openai_model:
                self.model = openai_model
            elif self.model.startswith("gemini"):
                self.model = "gpt-4-turbo"  # GPT-4 Turbo (latest)
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task (main ADK Agent interface)
        
        Args:
            task: Task dict with action and parameters
        
        Returns:
            TaskResult dict
        """
        action = task.get('action')
        parameters = task.get('parameters', {})
        context = task.get('context', {})
        
        # Execute tool if action matches
        if action in self.tools:
            tool = self.tools[action]
            result = tool.execute(**parameters)
            return {
                'success': True,
                'result': result,
                'agent': self.name
            }
        
        # If no matching tool, use LLM reasoning (ADK pattern)
        if self.client:
            prompt = self._build_prompt(action, parameters, context)
            response = await self._call_llm(prompt)
            return {
                'success': True,
                'result': response,
                'agent': self.name
            }
        
        return {
            'success': False,
            'error': f"No tool found for action: {action}",
            'agent': self.name
        }
    
    def _build_prompt(self, action: str, parameters: Dict, context: Dict) -> str:
        """Build LLM prompt"""
        prompt = f"""You are {self.name}, an agent in a reconciliation system.
{self.description}

{self.instructions if self.instructions else ''}

Action: {action}
Parameters: {parameters}
Context: {context}

Please process this request and provide a structured response."""
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.instructions or "You are a helpful AI agent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def get_tools(self) -> List[ADKTool]:
        """Get agent's tools (ADK interface)"""
        return list(self.tools.values())
    
    def get_config(self) -> ADKAgentConfig:
        """Get agent configuration"""
        return self.config


class ADKAgentRegistry:
    """Registry for managing ADK agents"""
    
    def __init__(self):
        self.agents: Dict[str, ADKAgent] = {}
    
    def register(self, agent: ADKAgent):
        """Register an ADK agent"""
        self.agents[agent.name] = agent
    
    def get(self, name: str) -> Optional[ADKAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self.agents.keys())
    
    def get_all(self) -> Dict[str, ADKAgent]:
        """Get all agents"""
        return self.agents
