# Dialetica AI Backend

A modern, foundation-based AI platform with FastAPI, featuring context-based conversations and sophisticated agent management.

## 🚀 Features

- **Context-Based Conversations**: Replace traditional chats with flexible contexts
- **Multi-Agent Management**: Sophisticated agent creation and management
- **HTTP-Based Messaging**: Simple, reliable HTTP messaging instead of WebSocket complexity
- **User Authentication**: Complete authentication system with guest users, registration, and login
- **Knowledge Management**: Semantic search and knowledge storage
- **API Key Management**: Secure API key generation and management
- **Type Safety**: Full Pydantic models with validation
- **Modern Architecture**: Clean separation of concerns with services and data layers

## 🏗️ Architecture

```
backend/
├── src/
│   └── foundation/           # Foundation package
│       ├── api_server.py     # Main FastAPI application
│       ├── client.py         # Python SDK client
│       ├── data/
│       │   └── models.py     # Pydantic data models
│       ├── services/         # Business logic services
│       │   ├── agent_service.py
│       │   ├── context_service.py
│       │   ├── user_service.py
│       │   ├── knowledge_service.py
│       │   └── api_key_service.py
│       ├── infra/
│       │   └── storage.py    # Data storage layer
│       ├── agent/            # Agent implementations
│       ├── context/          # Context management
│       └── tools/            # Agent tools and utilities
├── requirements.txt          # Python dependencies
└── README.md               # This file
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# API Security
PYTHON_GATEWAY_API_KEY=dummy-key

# Auth Security
AUTH_SECRET=your_auth_secret
```

### 3. Run the Server

```bash
cd src/foundation
python api_server.py
```

The server will start on `http://localhost:8000`

## 📡 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/guest` - Create guest user
- `POST /api/auth/google` - Create/find Google OAuth user

### User Management

- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

### Agent Management

- `POST /v1/agents` - Create agent
- `GET /v1/agents` - List user's agents
- `GET /v1/agents/{agent_id}` - Get specific agent
- `PUT /v1/agents/{agent_id}` - Update agent
- `DELETE /v1/agents/{agent_id}` - Delete agent

### Context Management (replaces chats)

- `POST /v1/contexts` - Create context
- `GET /v1/contexts` - List user's contexts
- `GET /v1/contexts/{context_id}` - Get specific context
- `PUT /v1/contexts/{context_id}` - Update context
- `DELETE /v1/contexts/{context_id}` - Delete context

### Messaging (HTTP-based)

- `POST /v1/contexts/{context_id}/run` - Send messages to context
- `GET /v1/contexts/{context_id}/history` - Get conversation history

### Knowledge Management

- `POST /v1/knowledge` - Create knowledge entry
- `GET /v1/knowledge` - List knowledge entries
- `GET /v1/knowledge/{knowledge_id}` - Get specific knowledge
- `PUT /v1/knowledge/{knowledge_id}` - Update knowledge
- `DELETE /v1/knowledge/{knowledge_id}` - Delete knowledge
- `GET /v1/contexts/{context_id}/knowledge/query` - Semantic search

### API Key Management

- `POST /v1/api-keys` - Create API key
- `GET /v1/api-keys` - List user's API keys
- `DELETE /v1/api-keys/{api_key}` - Delete API key

### Utility

- `GET /health` - Health check
- `GET /` - API information

## 🔧 Usage Examples

### 1. Create a Guest User

```bash
curl -X POST http://localhost:8000/api/auth/guest
```

### 2. Create an Agent

```bash
curl -X POST http://localhost:8000/v1/agents \
  -H "X-User-ID: your-user-id" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Debate Master",
    "description": "I engage in thoughtful debate and present balanced arguments.",
    "model": "gpt-4o-mini",
    "provider": "openai",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 3. Create a Context

```bash
curl -X POST http://localhost:8000/v1/contexts \
  -H "X-User-ID: your-user-id" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Debate Session",
    "description": "A context for debating renewable energy",
    "agents": ["agent-id-1", "agent-id-2"]
  }'
```

### 4. Send Messages to Context

```bash
curl -X POST http://localhost:8000/v1/contexts/context-id/run \
  -H "X-User-ID: your-user-id" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "sender_name": "Alice",
        "content": "What are the pros and cons of renewable energy?"
      }
    ]
  }'
```

### 5. Get Conversation History

```bash
curl -X GET http://localhost:8000/v1/contexts/context-id/history \
  -H "X-User-ID: your-user-id"
```

## 🎯 Key Concepts

### Contexts vs Chats

- **Contexts** are flexible conversation environments that can contain multiple agents
- **Agents** are AI personalities that can participate in contexts
- **Messages** are sent to contexts and processed by agents
- **Knowledge** can be stored at context or agent level for semantic search

### Authentication

The system supports two authentication patterns:

1. **User API Keys**: Users authenticate with Bearer tokens (`Authorization: Bearer dai_xxxxx`)
2. **Web Application**: Web app authenticates with X-User-ID headers

### Data Models

- **Request Models**: What users send (minimal fields)
- **Response Models**: What users receive (excludes internal fields like embeddings)
- **Internal Models**: Full database representation with all fields

## 🔒 Security Features

- **User Isolation**: All data is scoped to user ID
- **Password Hashing**: Secure password storage with salt
- **API Key Management**: Secure API key generation and validation
- **CORS Configuration**: Proper cross-origin resource sharing setup

## 🚀 Production Deployment

### Environment Setup

1. Set all required environment variables
2. Use a proper database instead of in-memory storage
3. Configure proper logging and monitoring
4. Set up reverse proxy (nginx) for production
5. Use HTTPS in production

### Database Migration

To use a real database:

1. Update `src/foundation/infra/storage.py` to use actual database client
2. Create database tables matching the data models
3. Implement proper connection pooling and error handling

## 🧪 Testing

### Basic API Tests

```bash
# Health check
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/guest

# Test agent creation
curl -X POST http://localhost:8000/v1/agents \
  -H "X-User-ID: test-user" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "description": "Test"}'
```

## 🤝 Integration with Frontend

This backend integrates seamlessly with the Next.js frontend:

- **Context Management**: Frontend manages contexts instead of chats
- **HTTP Messaging**: Simple HTTP requests instead of WebSocket complexity
- **Authentication**: Full integration with NextAuth.js
- **Type Safety**: Shared TypeScript types between frontend and backend

## 📊 Monitoring

- Health check endpoint for monitoring
- Structured logging with timestamps
- Error handling with proper HTTP status codes
- Request/response logging for debugging

---

**Status**: Production Ready ✅  
**Version**: 2.0.0 (Foundation-based)  
**Last Updated**: January 2025