# Dialetica AI Python SDK

Official Python SDK for the Dialetica AI platform - a multi-agent conversational AI system.

## Installation

```bash
pip install dialetica
```

## Quick Start

```python
from dialetica import Dialetica, AgentRequest, ContextRequest, MessageRequest

# Initialize the client
client = Dialetica(api_key="dai_your_api_key_here")
# Or use environment variable: DIALETICA_AI_API_KEY

# Create an agent
agent = client.agents.create(AgentRequest(
    name="Assistant",
    description="Helpful assistant",
    instructions=["Be helpful and concise"],
    model="gpt-4o"
))

# Create a context
context = client.contexts.create(ContextRequest(
    name="Support Chat",
    agents=[agent.id]
))

# Send a message
message = MessageRequest(
    role="user",
    sender_name="User",
    content="Hello!"
)

# Get response
responses = client.contexts.run(context, [message])
for response in responses:
    print(f"{response.sender_name}: {response.content}")
```

## Features

- **Multi-Agent Conversations**: Create contexts with multiple AI agents
- **Knowledge Management**: Store and query knowledge using semantic search
- **Streaming Support**: Real-time streaming responses with SSE
- **Type-Safe**: Full Pydantic models for request/response validation
- **Simple API**: Clean, intuitive interface following industry best practices

## Building and Publishing

To build the package:

```bash
cd backend
python -m build
```

To publish to PyPI (test first with TestPyPI):

```bash
# Test on TestPyPI first
python -m twine upload --repository testpypi dist/*

# Then publish to PyPI
python -m twine upload dist/*
```

## Documentation

For full documentation, visit [https://docs.dialetica-ai.com](https://docs.dialetica-ai.com)

## License

MIT License

