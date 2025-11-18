"""
Public data models for the Dialetica AI SDK

This module contains only the Request and Response models that are part of the public API.
Internal models are kept private in the foundation package.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# ==================== MESSAGE MODELS ====================

class MessageRequest(BaseModel):
    """
    Message creation request model.
    
    This is what SDK users provide when sending messages.
    Only includes the essential fields needed to create a message.
    
    Example:
        msg = MessageRequest(
            role="user",
            sender_name="Alice", 
            content="Hello!"
        )
    """
    role: str = Field(..., pattern=r'^(user|assistant)$', description="Message role: 'user' or 'assistant'")
    sender_name: str = Field(..., min_length=1, max_length=100, description="Name of the message sender")
    content: str = Field(..., min_length=1, description="Message content")


class MessageResponse(BaseModel):
    """
    Message response model - returned to API users.
    
    Includes metadata fields but excludes internal implementation details
    like embeddings (which can be 12KB+ per message).
    
    This keeps API responses clean and performant.
    """
    id: str
    context_id: str
    sender_id: str
    timestamp: datetime
    role: str
    sender_name: str
    content: str
    # Note: embedding field is intentionally excluded


# ==================== KNOWLEDGE MODELS ====================

class KnowledgeRequest(BaseModel):
    """
    Knowledge creation request model.
    
    This is what SDK users provide when creating knowledge entries.
    """
    knowledge: str = Field(..., min_length=1, description="Knowledge content/instruction")
    context_id: Optional[str] = Field(default=None, description="Context ID (None=user-level)")
    agent_id: Optional[str] = Field(default=None, description="Agent ID for agent-specific knowledge")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Flexible metadata")


class KnowledgeResponse(BaseModel):
    """
    Knowledge response model - returned to API users.
    
    Excludes embedding field to keep responses clean and performant.
    """
    id: str
    creator_id: str
    creator_type: str  # 'user' or 'agent'
    user_id: str
    context_id: Optional[str]
    agent_id: Optional[str]
    knowledge: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]
    # Note: embedding field is intentionally excluded


# ==================== AGENT MODELS ====================

class AgentRequest(BaseModel):
    """
    Agent creation request model.
    
    This is what SDK users provide when creating agents.
    Only includes configuration fields - system fields are set by the server.
    
    Example:
        agent = AgentRequest(
            name="Customer Support Agent",
            description="Handles customer inquiries",
            instructions=["Be professional", "Be helpful"],
            model="gpt-4o"
        )
    """
    # Core config
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: str = Field(default="", description="Agent description")
    instructions: List[str] = Field(default_factory=list, description="System instructions for the agent")
    
    # Model config
    model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, gemini, azure, etc.)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(default=1000, gt=0, le=100000, description="Max tokens per response")
    
    # Capabilities
    tools: List[str] = Field(default_factory=list, description="List of ToolConfig UUIDs that this agent can use")


class AgentResponse(BaseModel):
    """
    Agent response model - returned to API users.
    
    Includes all fields for transparency.
    """
    id: str
    creator_id: Optional[str]  # None for public agents (where creator_id IS NULL)
    name: str
    description: str
    instructions: List[str]
    model: str
    provider: str
    temperature: float
    max_tokens: int
    tools: List[str]  # List of ToolConfig UUIDs
    created_at: datetime
    updated_at: datetime


# ==================== CONTEXT MODELS ====================

class ContextRequest(BaseModel):
    """
    Context creation request model.
    
    This is what SDK users provide when creating contexts.
    
    Example:
        context = ContextRequest(
            name="Customer Support Chat",
            description="Multi-agent customer support",
            instructions=["Agent 1 handles technical", "Agent 2 handles billing"],
            agents=[agent1.id, agent2.id],
            is_public=False
        )
    """
    # Core
    name: str = Field(..., min_length=1, max_length=100, description="Context name")
    description: str = Field(default="", description="Context description")
    instructions: List[str] = Field(default_factory=list, description="System instructions for the context")
    
    # Participants (UUID arrays)
    agents: List[str] = Field(default_factory=list, description="List of agent IDs")
    users: Optional[List[str]] = Field(default_factory=list, description="List of user IDs")
    
    # Visibility
    is_public: bool = Field(default=False, description="If true, anyone with the link can access this context")

    def __init__(self, **data):
        agents = []
        for agent in data.get("agents", []):
            if isinstance(agent, str):
                agents.append(agent)
            elif hasattr(agent, "id"):
                agents.append(agent.id)
            else:
                raise ValueError(f"Invalid agent: {agent}")
        data["agents"] = agents
        users = []
        for user in data.get("users", []):
            if isinstance(user, str):
                users.append(user)
            elif hasattr(user, "id"):
                users.append(user.id)
            else:
                raise ValueError(f"Invalid user: {user}")
        data["users"] = users
        
        super().__init__(**data)


class ContextResponse(BaseModel):
    """
    Context response model - returned to API users.
    
    Includes all fields for transparency.
    """
    id: str
    creator_id: Optional[str]
    is_public: bool
    name: str
    description: str
    instructions: List[str]
    agents: List[str]
    users: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class RouteResponse(BaseModel):
    """
    Response model containing the routing decision.
    
    This model is returned when routing messages in a context. It indicates
    which agent (or user) should speak next based on the conversation flow.
    
    Attributes:
        next_speaker: The name of the agent or participant who should speak next.
                     This can be:
                     - An agent name (e.g., "Support Agent", "Billing Agent")
                     - "user" if the orchestrator determines a human should respond
                     - "none" if the conversation should end
    
    Example:
        {
            "next_speaker": "Billing Agent"
        }
    """
    next_speaker: str = Field(..., description="Name of the next speaker (agent name, 'user', or 'none')")


# ==================== TOOL CONFIG MODELS ====================

class ToolConfigRequest(BaseModel):
    """
    Tool configuration creation request model.
    
    This is what SDK users provide when creating tool configurations.
    
    Example:
        tool_config = ToolConfigRequest(
            name="Notion MCP",
            description="Notion integration via MCP",
            endpoint="https://mcp.notion.com/mcp",
            auth_token="ntn_...",
            type="streamable_http"
        )
    """
    name: str = Field(..., min_length=1, max_length=100, description="Tool configuration name")
    description: Optional[str] = Field(default=None, description="Tool configuration description")
    endpoint: str = Field(..., min_length=1, max_length=500, description="MCP server endpoint URL")
    auth_token: Optional[str] = Field(default=None, description="Authentication token for the MCP server")
    type: Literal["streamable_http", "sse"] = Field(..., description="MCP server type")


class ToolConfigResponse(BaseModel):
    """
    Tool configuration response model - returned to API users.
    
    Excludes auth_token for security (users should only see if it's set, not the value).
    """
    id: str
    creator_id: Optional[str]  # None for public tool configs (where creator_id IS NULL)
    name: str
    description: Optional[str]
    endpoint: str
    has_auth_token: bool  # Indicates if auth_token is set (but not the value)
    type: str
    created_at: datetime
    updated_at: datetime


# ==================== USAGE TRACKING MODELS ====================

class UsageSummary(BaseModel):
    """
    Usage summary response model - returned to API users.
    
    Aggregated usage data for dashboard display.
    """
    total_spend: float
    previous_period_spend: float
    total_tokens: int
    total_requests: int
    daily_usage: List[Dict[str, Any]]  # List of daily usage records
    capabilities: List[Dict[str, Any]]  # Breakdown by capability/model


# ==================== CRON MODELS ====================

class CronRequest(BaseModel):
    """
    Cron creation request model.
    
    This is what SDK users provide when creating cron jobs.
    
    Example:
        cron = CronRequest(
            name="Daily Report",
            prompt="Generate a daily summary",
            context_id="context-uuid",
            cron_expression="0 9 * * *"  # Daily at 9 AM
        )
        # Or for one-time execution at a specific time:
        cron = CronRequest(
            name="One-time Task",
            prompt="Run this once",
            context_id="context-uuid",
            scheduled_time="2024-12-25T09:00:00Z"  # Specific date/time
        )
    """
    name: str = Field(..., min_length=1, max_length=100, description="Cron job name")
    prompt: str = Field(..., min_length=1, description="Prompt to execute")
    context_id: str = Field(..., description="Context ID where the prompt will be executed")
    cron_expression: Optional[str] = Field(default=None, description="Standard cron expression (e.g., '0 9 * * *' for daily at 9 AM). If None, runs once at scheduled_time.")
    scheduled_time: Optional[datetime] = Field(default=None, description="Scheduled time for one-time execution (used when cron_expression is None). If None and no cron_expression, runs immediately.")


class CronResponse(BaseModel):
    """
    Cron response model - returned to API users.
    
    Includes all fields for transparency.
    """
    id: str
    creator_id: str
    owner_id: str
    name: str
    prompt: str
    context_id: str
    cron_expression: Optional[str]
    scheduled_time: Optional[datetime]
    cron_next_run: datetime
    cron_last_run: Optional[datetime]
    cron_status: str
    created_at: datetime
    updated_at: datetime

