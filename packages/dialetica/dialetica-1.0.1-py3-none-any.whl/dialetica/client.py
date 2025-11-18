"""
Python client SDK for the Dialetica AI API

Example usage:
    # Initialize with explicit API key
    client = Dialetica(api_key="dai_your_api_key_here")
    
    # Initialize with environment variable (recommended)
    # Set DIALETICA_AI_API_KEY in your environment
    client = Dialetica()
    
    # Custom base URL
    client = Dialetica(base_url="https://api.dialetica.ai")
"""
import os
import requests
from typing import List, Optional, Dict, Any, AsyncIterator
from datetime import datetime
import json
import httpx

from .models import (
    AgentRequest, AgentResponse,
    ContextRequest, ContextResponse,
    KnowledgeRequest, KnowledgeResponse,
    MessageRequest, MessageResponse,
    CronRequest, CronResponse,
    RouteResponse,
    ToolConfigRequest, ToolConfigResponse
)


class Dialetica:
    """
    Dialetica AI Client
    
    The client handles authentication and API communication with the Dialetica AI API.
    API keys should be kept secure and never committed to version control.
    
    Best Practices:
        - Store API keys in environment variables
        - Never hardcode API keys in source code
        - Use different API keys for different environments (dev, staging, prod)
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "http://localhost:8000"
    ):
        """
        Initialize the Dialetica AI client.
        
        Args:
            api_key: Your API key. If not provided, will look for DIALETICA_AI_API_KEY 
                    environment variable. Following the pattern of OpenAI and Anthropic SDKs.
            base_url: The base URL for the API. Defaults to localhost:8000 for development.
        
        Raises:
            ValueError: If no API key is provided and DIALETICA_AI_API_KEY is not set.
        
        Example:
            >>> # Using environment variable (recommended)
            >>> import os
            >>> os.environ["DIALETICA_AI_API_KEY"] = "dai_your_api_key"
            >>> client = Dialetica()
            
            >>> # Using explicit API key (not recommended for production)
            >>> client = Dialetica(api_key="dai_your_api_key")
        """
        # Follow OpenAI/Anthropic pattern: try explicit key, then environment variable
        self.api_key = api_key or os.environ.get("DIALETICA_AI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "No API key provided. Either pass api_key parameter or set "
                "DIALETICA_AI_API_KEY environment variable. "
                "Get your API key from your dashboard."
            )
        
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Initialize sub-clients
        self._setup_clients()
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to the API"""
        url = f"{self.base_url}/v1{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    class AgentsClient:
        """Client for agent operations"""
        
        def __init__(self, client: 'Dialetica'):
            self.client = client
        
        def create(self, agent: AgentRequest) -> AgentResponse:
            """
            Create a single agent.
            
            Args:
                agent: AgentRequest object (configuration only)
            
            Returns:
                AgentResponse with all fields
            
            Example:
                agent = AgentRequest(
                    name="Customer Support",
                    description="Handles inquiries",
                    instructions=["Be helpful"],
                    model="gpt-4o"
                )
                created = client.agents.create(agent)
            """
            response = self.client._make_request("POST", "/agents", agent.model_dump(mode = "json"))
            return AgentResponse(**response)
        
        def bulk_create(self, agents: List[AgentRequest]) -> List[AgentResponse]:
            """Create multiple agents at once"""
            created_agents = []
            for agent in agents:
                response = self.client._make_request("POST", "/agents", agent.model_dump(mode = "json"))
                created_agents.append(AgentResponse(**response))
            return created_agents
        
        def get(self, agent_id: str) -> Optional[AgentResponse]:
            """Get an agent by ID"""
            try:
                response = self.client._make_request("GET", f"/agents/{agent_id}")
                return AgentResponse(**response)
            except Exception:
                return None
        
        def list(self) -> List[AgentResponse]:
            """List all agents"""
            response = self.client._make_request("GET", "/agents")
            return [AgentResponse(**agent_data) for agent_data in response]
        
        def update(self, agent_id: str, agent: AgentRequest) -> Optional[AgentResponse]:
            """Update an agent"""
            try:
                response = self.client._make_request("PUT", f"/agents/{agent_id}", agent.model_dump(mode = "json"))
                return AgentResponse(**response)
            except Exception:
                return None
        
        def delete(self, agent_id: str) -> bool:
            """Delete an agent"""
            try:
                self.client._make_request("DELETE", f"/agents/{agent_id}")
                return True
            except Exception:
                return False
    
    class ContextsClient:
        """Client for context operations"""
        
        def __init__(self, client: 'Dialetica'):
            self.client = client
        
        def create(self, context: ContextRequest) -> ContextResponse:
            """
            Create a single context.
            
            Args:
                context: ContextRequest object
            
            Returns:
                ContextResponse with all fields
            
            Example:
                context = ContextRequest(
                    name="Customer Support",
                    description="Multi-agent support",
                    agents=[agent1.id, agent2.id],
                    knowledge=[policy.id]
                )
                created = client.contexts.create(context)
            """
            response = self.client._make_request("POST", "/contexts", context.model_dump(mode = "json"))
            return ContextResponse(**response)
        
        def bulk_create(self, contexts: List[ContextRequest]) -> List[ContextResponse]:
            """Create multiple contexts at once"""
            created_contexts = []
            for context in contexts:
                response = self.client._make_request("POST", "/contexts", context.model_dump(mode = "json"))
                created_contexts.append(ContextResponse(**response))
            return created_contexts
        
        def get(self, context_id: str) -> Optional[ContextResponse]:
            """Get a context by ID"""
            try:
                response = self.client._make_request("GET", f"/contexts/{context_id}")
                return ContextResponse(**response)
            except Exception:
                return None
        
        def list(self) -> List[ContextResponse]:
            """List all contexts"""
            response = self.client._make_request("GET", "/contexts")
            return [ContextResponse(**context_data) for context_data in response]
        
        def update(self, context_id: str, context: ContextRequest) -> Optional[ContextResponse]:
            """Update a context"""
            try:
                response = self.client._make_request("PUT", f"/contexts/{context_id}", context.model_dump(mode = "json"))
                return ContextResponse(**response)
            except Exception:
                return None
        
        def delete(self, context_id: str) -> bool:
            """Delete a context"""
            try:
                self.client._make_request("DELETE", f"/contexts/{context_id}")
                return True
            except Exception:
                return False
        
        def run(self, context: ContextResponse, messages: List[MessageRequest]) -> Optional[List[MessageResponse]]:
            """
            Run a context with messages.
            
            Args:
                context: The context to run
                messages: List of MessageRequest objects (minimal fields: role, sender_name, content)
            
            Returns:
                List of MessageResponse objects (includes metadata, excludes embeddings)
            
            Example:
                msg = MessageRequest(role="user", sender_name="Alice", content="Hello!")
                responses = client.contexts.run(context, [msg])
                for resp in responses:
                    print(f"{resp.sender_name}: {resp.content}")
            """
            try:
                data = {"messages": [msg.model_dump(mode = "json") for msg in messages]}
                response = self.client._make_request("POST", f"/contexts/{context.id}/run", data)
                return [MessageResponse(**msg_data) for msg_data in response]
            except Exception:
                return []
        
        async def run_streamed(self, context: ContextResponse, messages: List[MessageRequest]) -> AsyncIterator[Dict[str, Any]]:
            """
            Run a context with messages and stream the response in real-time using SSE.
            
            This method streams events as the agent processes the request, providing:
            - Token-by-token content streaming
            - Real-time tool call visibility
            - Progress updates
            - Agent handoff notifications (multi-agent contexts)
            
            Args:
                context: The context to run
                messages: List of MessageRequest objects
            
            Yields:
                Dict[str, Any]: Stream events with different types:
                    - context_started: Context execution begins
                    - agent_started: Agent starts processing
                    - content_delta: Token-by-token content (the main content stream)
                    - run_item: Tool calls, completions
                    - agent_updated: Agent handoff occurred
                    - agent_completed: Agent finished with complete response
                    - context_completed: Context execution finished
                    - error: An error occurred
            
            Example (simple):
                msg = MessageRequest(role="user", sender_name="User", content="Hello!")
                async for event in client.contexts.run_streamed(context, [msg]):
                    if event["type"] == "content_delta":
                        print(event["delta"], end="", flush=True)
                    elif event["type"] == "error":
                        print(f"Error: {event['error']}")
            
            Example (full event handling):
                async for event in client.contexts.run_streamed(context, [msg]):
                    event_type = event.get("type")
                    
                    if event_type == "context_started":
                        print(f"🎬 Context: {event['context_name']}")
                    
                    elif event_type == "agent_started":
                        print(f"🤖 Agent: {event['agent_name']}")
                    
                    elif event_type == "content_delta":
                        print(event["delta"], end="", flush=True)
                    
                    elif event_type == "agent_completed":
                        print(f"\\n✅ Complete: {len(event['content'])} chars")
                    
                    elif event_type == "error":
                        print(f"❌ Error: {event['error']}")
            
            Example (cancellation):
                # To cancel streaming, simply break out of the loop or cancel the task
                try:
                    async for event in client.contexts.run_streamed(context, [msg]):
                        if event["type"] == "content_delta":
                            print(event["delta"], end="", flush=True)
                        if some_cancel_condition:
                            break  # Automatically closes connection and cancels backend processing
                except asyncio.CancelledError:
                    print("Stream cancelled")
            
            Note:
                - This is an async generator and must be used with 'async for'.
                - Requires httpx library for async HTTP streaming.
                - Stream can be cancelled by breaking out of the loop or cancelling the asyncio task.
                - When cancelled, the HTTP connection is closed and backend processing stops.
            """
            url = f"{self.client.base_url}/v1/contexts/{context.id}/run/stream"
            data = {"messages": [msg.model_dump(mode="json") for msg in messages]}
            
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                async with http_client.stream(
                    "POST",
                    url,
                    headers=self.client.headers,
                    json=data
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield {
                            "type": "error",
                            "error": f"HTTP {response.status_code}: {error_text.decode()}",
                            "error_type": "HTTPError"
                        }
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                event = json.loads(line[6:])  # Remove "data: " prefix
                                yield event
                            except json.JSONDecodeError as e:
                                yield {
                                    "type": "error",
                                    "error": f"Failed to parse event: {e}",
                                    "error_type": "JSONDecodeError"
                                }
        
        def get_history(self, context: ContextResponse, sender_name: Optional[str] = None) -> List[MessageResponse]:
            """
            Get conversation history for a context.
            
            Args:
                context: The context to get history from
                sender_name: Optional filter by sender name
            
            Returns:
                List of MessageResponse objects (excludes embeddings for performance)
            
            Example:
                history = client.contexts.get_history(context)
                for msg in history:
                    print(f"[{msg.timestamp}] {msg.sender_name}: {msg.content}")
            """
            try:
                params = {}
                if sender_name:
                    params["sender_name"] = sender_name
                
                url = f"/contexts/{context.id}/history"
                if params:
                    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
                
                response = self.client._make_request("GET", url)
                return [MessageResponse(**msg_data) for msg_data in response["messages"]]
            except Exception:
                return []
        
        def route(self, context_id: str, messages: List[MessageRequest]) -> Optional[RouteResponse]:
            """
            Route messages in a context to determine the next speaker.
            
            This method analyzes the conversation history and uses the orchestrator
            to determine which agent (or user) should speak next based on the context
            configuration and conversation flow.
            
            Args:
                context_id: The ID of the context to route messages in
                messages: List of MessageRequest objects representing the conversation history
            
            Returns:
                RouteResponse containing the name of the next speaker, or None if error
            
            Example:
                messages = [
                    MessageRequest(
                        role="user",
                        sender_name="Alice",
                        content="I need help with billing"
                    )
                ]
                result = client.contexts.route("context-uuid", messages)
                if result:
                    print(f"Next speaker: {result.next_speaker}")
                    # Output might be: "Next speaker: Billing Agent"
            """
            try:
                data = [msg.model_dump(mode="json") for msg in messages]
                response = self.client._make_request("POST", f"/contexts/{context_id}/route", data)
                return RouteResponse(**response)
            except Exception:
                return None
    
    class CronsClient:
        """Client for cron job operations"""
        
        def __init__(self, client: 'Dialetica'):
            self.client = client
        
        def create(self, cron: CronRequest) -> CronResponse:
            """Create a new cron job"""
            response = self.client._make_request("POST", "/crons", cron.model_dump(mode="json"))
            return CronResponse(**response)
        
        def get(self, cron_id: str) -> Optional[CronResponse]:
            """Get a cron job by ID"""
            try:
                response = self.client._make_request("GET", f"/crons/{cron_id}")
                return CronResponse(**response)
            except Exception:
                return None
        
        def list(self) -> List[CronResponse]:
            """List all cron jobs for the authenticated user"""
            response = self.client._make_request("GET", "/crons")
            return [CronResponse(**cron_data) for cron_data in response]
        
        def update(self, cron_id: str, cron: CronRequest) -> Optional[CronResponse]:
            """Update a cron job"""
            try:
                response = self.client._make_request("PUT", f"/crons/{cron_id}", cron.model_dump(mode="json"))
                return CronResponse(**response)
            except Exception:
                return None
        
        def delete(self, cron_id: str) -> bool:
            """Delete a cron job"""
            try:
                self.client._make_request("DELETE", f"/crons/{cron_id}")
                return True
            except Exception:
                return False
    
    class KnowledgeClient:
        """Client for knowledge operations (unified recipes/memories/facts)"""
        
        def __init__(self, client: 'Dialetica'):
            self.client = client
        
        def create(self, knowledge: KnowledgeRequest) -> KnowledgeResponse:
            """
            Create a single knowledge entry.
            
            Args:
                knowledge: KnowledgeRequest object (minimal fields)
            
            Returns:
                KnowledgeResponse (excludes embedding)
            
            Example:
                knowledge = KnowledgeRequest(
                    knowledge="Always validate user input",
                    metadata={"category": "security"}
                )
                created = client.knowledge.create(knowledge)
                print(f"Created knowledge: {created.id}")
            """
            response = self.client._make_request("POST", "/knowledge", knowledge.model_dump(mode = "json"))
            return KnowledgeResponse(**response)
        
        def bulk_create(self, knowledge_items: List[KnowledgeRequest]) -> List[KnowledgeResponse]:
            """
            Create multiple knowledge entries at once.
            
            Args:
                knowledge_items: List of KnowledgeRequest objects
            
            Returns:
                List of KnowledgeResponse objects (excludes embeddings)
            """
            created_knowledge = []
            for knowledge in knowledge_items:
                response = self.client._make_request("POST", "/knowledge", knowledge.model_dump(mode = "json"))
                created_knowledge.append(KnowledgeResponse(**response))
            return created_knowledge
        
        def get(self, knowledge_id: str) -> Optional[KnowledgeResponse]:
            """
            Get knowledge by ID.
            
            Returns:
                KnowledgeResponse (excludes embedding)
            """
            try:
                response = self.client._make_request("GET", f"/knowledge/{knowledge_id}")
                return KnowledgeResponse(**response)
            except Exception:
                return None
        
        def list(self) -> List[KnowledgeResponse]:
            """
            List all knowledge.
            
            Returns:
                List of KnowledgeResponse objects (excludes embeddings)
            """
            response = self.client._make_request("GET", "/knowledge")
            return [KnowledgeResponse(**knowledge_data) for knowledge_data in response]
        
        def update(self, knowledge_id: str, knowledge: KnowledgeRequest) -> Optional[KnowledgeResponse]:
            """
            Update knowledge.
            
            Args:
                knowledge_id: ID of knowledge to update
                knowledge: KnowledgeRequest object with updated data
            
            Returns:
                KnowledgeResponse (excludes embedding)
            """
            try:
                response = self.client._make_request("PUT", f"/knowledge/{knowledge_id}", knowledge.model_dump(mode = "json"))
                return KnowledgeResponse(**response)
            except Exception:
                return None
        
        def delete(self, knowledge_id: str) -> bool:
            """Delete knowledge"""
            try:
                self.client._make_request("DELETE", f"/knowledge/{knowledge_id}")
                return True
            except Exception:
                return False
        
        def get_for_context(self, context_id: str, agent_id: Optional[str] = None) -> List[KnowledgeResponse]:
            """
            Get knowledge for a context.
            
            Args:
                context_id: The context ID
                agent_id: Optional agent ID to filter for agent-visible knowledge only
            
            Returns:
                List of KnowledgeResponse objects
            
            Example:
                # Get all knowledge in a context
                all_knowledge = client.knowledge.get_for_context(context_id)
                
                # Get knowledge visible to a specific agent
                agent_knowledge = client.knowledge.get_for_context(context_id, agent_id)
            """
            try:
                url = f"/contexts/{context_id}/knowledge"
                if agent_id:
                    url += f"?agent_id={agent_id}"
                response = self.client._make_request("GET", url)
                return [KnowledgeResponse(**k) for k in response]
            except Exception:
                return []
        
        def create_for_context(
            self, 
            context_id: str, 
            knowledge: str,
            agent_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
        ) -> KnowledgeResponse:
            """
            Helper to create knowledge for a context.
            
            Args:
                context_id: The context ID
                knowledge: The knowledge content
                agent_id: If provided, creates agent-specific knowledge; if None, creates context-wide knowledge
                metadata: Optional metadata
            
            Returns:
                KnowledgeResponse
            
            Example:
                # Create context-wide knowledge (all agents see)
                knowledge = client.knowledge.create_for_context(
                    context_id=context.id,
                    knowledge="All agents should validate input"
                )
                
                # Create agent-specific knowledge
                knowledge = client.knowledge.create_for_context(
                    context_id=context.id,
                    agent_id=agent.id,
                    knowledge="This agent remembers user preferences"
                )
            """
            knowledge_req = KnowledgeRequest(
                knowledge=knowledge,
                context_id=context_id,
                agent_id=agent_id,
                metadata=metadata
            )
            return self.create(knowledge_req)
        
        def query(
            self, 
            query: str,
            context_id: Optional[str] = None, 
            agent_id: Optional[str] = None,
            limit: int = 5
        ) -> List[KnowledgeResponse]:
            """
            Query knowledge in a context using semantic search.
            
            Args:
                context_id: The context to search in
                query: Search query string
                agent_id: If provided, searches knowledge visible to that agent
                limit: Maximum number of results (default 5)
            
            Returns:
                List of KnowledgeResponse objects ranked by semantic similarity
            
            Example:
                # Search all context-wide knowledge
                results = client.knowledge.query(
                    context_id=context.id,
                    query="email validation rules"
                )
                
                # Search knowledge visible to a specific agent
                results = client.knowledge.query(
                    context_id=context.id,
                    query="user preferences",
                    agent_id=agent.id
                )
            """
            try:
                url = f"/contexts/{context_id}/knowledge/query?query={query}&limit={limit}"
                if agent_id:
                    url += f"&agent_id={agent_id}"
                response = self.client._make_request("GET", url)
                return [KnowledgeResponse(**k) for k in response]
            except Exception:
                return []
    
    class ToolsClient:
        """Client for tool configuration operations"""
        
        def __init__(self, client: 'Dialetica'):
            self.client = client
        
        def create(self, tool_config: ToolConfigRequest) -> ToolConfigResponse:
            """
            Create a new tool configuration (MCP server connection).
            
            Args:
                tool_config: ToolConfigRequest with name, endpoint, auth_token, type, etc.
            
            Returns:
                ToolConfigResponse with the created tool configuration
            
            Example:
                tool = ToolConfigRequest(
                    name="Notion MCP",
                    description="Access Notion databases",
                    endpoint="https://mcp.notion.com/mcp",
                    auth_token="ntn_secret_...",
                    type="streamable_http"
                )
                created = client.tools.create(tool)
            """
            response = self.client._make_request("POST", "/tool-configs", tool_config.model_dump(mode="json"))
            return ToolConfigResponse(**response)
        
        def list(self) -> List[ToolConfigResponse]:
            """
            List all tool configurations for the authenticated user.
            
            Returns:
                List of ToolConfigResponse objects
            
            Example:
                tools = client.tools.list()
                for tool in tools:
                    print(f"{tool.name}: {tool.endpoint}")
            """
            response = self.client._make_request("GET", "/tool-configs")
            return [ToolConfigResponse(**config) for config in response]
        
        def get(self, tool_config_id: str) -> Optional[ToolConfigResponse]:
            """
            Get a specific tool configuration by ID.
            
            Args:
                tool_config_id: The tool configuration ID
            
            Returns:
                ToolConfigResponse or None if not found
            
            Example:
                tool = client.tools.get("tool-config-uuid")
                if tool:
                    print(f"Tool: {tool.name}")
            """
            try:
                response = self.client._make_request("GET", f"/tool-configs/{tool_config_id}")
                return ToolConfigResponse(**response)
            except Exception:
                return None
        
        def update(self, tool_config_id: str, tool_config: ToolConfigRequest) -> Optional[ToolConfigResponse]:
            """
            Update an existing tool configuration.
            
            Args:
                tool_config_id: The tool configuration ID to update
                tool_config: Updated ToolConfigRequest
            
            Returns:
                Updated ToolConfigResponse or None if not found
            
            Example:
                updated = ToolConfigRequest(
                    name="Notion MCP Updated",
                    description="Updated description",
                    endpoint="https://mcp.notion.com/mcp",
                    auth_token="new_token",
                    type="streamable_http"
                )
                result = client.tools.update(tool_id, updated)
            """
            try:
                response = self.client._make_request("PUT", f"/tool-configs/{tool_config_id}", tool_config.model_dump(mode="json"))
                return ToolConfigResponse(**response)
            except Exception:
                return None
        
        def delete(self, tool_config_id: str) -> bool:
            """
            Delete a tool configuration.
            
            Args:
                tool_config_id: The tool configuration ID to delete
            
            Returns:
                True if successful, False otherwise
            
            Example:
                success = client.tools.delete("tool-config-uuid")
                if success:
                    print("Tool config deleted")
            """
            try:
                self.client._make_request("DELETE", f"/tool-configs/{tool_config_id}")
                return True
            except Exception:
                return False
    
    # Initialize sub-clients when Dialetica is instantiated
    def _setup_clients(self):
        """Initialize all sub-clients for the SDK"""
        self.agents = self.AgentsClient(self)
        self.contexts = self.ContextsClient(self)
        self.knowledge = self.KnowledgeClient(self)
        self.crons = self.CronsClient(self)
        self.tools = self.ToolsClient(self)
