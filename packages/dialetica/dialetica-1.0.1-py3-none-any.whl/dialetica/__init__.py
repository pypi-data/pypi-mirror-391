"""
Dialetica AI SDK - Public API

This package provides the public API for the Dialetica AI SDK.
Only the client and models are exposed - internal implementation details are kept private.

Example usage:
    from dialetica import Dialetica, AgentRequest, ContextRequest, MessageRequest
    
    client = Dialetica(api_key="dai_your_api_key")
    agent = client.agents.create(AgentRequest(name="Assistant", model="gpt-4o"))
"""
# Import from local modules (self-contained public API)
from .client import Dialetica
from .models import (
    # Request models (what users send)
    AgentRequest,
    ContextRequest,
    KnowledgeRequest,
    MessageRequest,
    ToolConfigRequest,
    CronRequest,
    # Response models (what users receive)
    AgentResponse,
    ContextResponse,
    KnowledgeResponse,
    MessageResponse,
    ToolConfigResponse,
    CronResponse,
    UsageSummary,
    RouteResponse,
)

__version__ = "1.0.0"
__all__ = [
    # Client
    "Dialetica",
    # Request models
    "AgentRequest",
    "ContextRequest",
    "KnowledgeRequest",
    "MessageRequest",
    "ToolConfigRequest",
    "CronRequest",
    # Response models
    "AgentResponse",
    "ContextResponse",
    "KnowledgeResponse",
    "MessageResponse",
    "ToolConfigResponse",
    "CronResponse",
    "UsageSummary",
    "RouteResponse",
]

