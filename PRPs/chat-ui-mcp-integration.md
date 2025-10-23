name: "Chat-UI MCP Client Integration - Fastest Path to Production"
description: |
  Enable Model Context Protocol (MCP) tool calling in Hugging Face chat-ui using the fastest,
  easiest approach with zero code changes to chat-ui itself.

## Goal

Enable the Hugging Face chat-ui to act as an MCP client, allowing users to interact with MCP tools
(file systems, databases, APIs, etc.) through natural conversation WITHOUT modifying chat-ui source code.

**End State**: Users can chat with LLMs and automatically invoke MCP tools like:
- File system operations (read/write files)
- Database queries
- API integrations
- Custom business logic tools

**Timeline**: 1-2 days for full working implementation

## Why

### Business Value
- **Zero Code Changes**: No fork maintenance, easy upgrades of chat-ui
- **Universal Tool Access**: Any MCP server works instantly
- **Production Ready**: Battle-tested proxy architecture (LiteLLM)
- **Future Proof**: As MCP adoption grows, we're already integrated

### User Impact
- Users get powerful tool calling without changing their familiar chat interface
- Transparent execution - tools are called automatically when needed
- Better answers through context-aware tool usage (file content, DB data, etc.)

### Problems Solved
- Chat-ui lacks native MCP support (and may never add it)
- Tool calling was explicitly removed from chat-ui codebase
- Direct integration would require weeks of development + ongoing maintenance

## What

### User-Visible Behavior

1. **Transparent Tool Execution**: User asks "What's in my project folder?" → LLM calls `filesystem_list` tool → Returns file list
2. **Multi-Tool Workflows**: User asks "Read config.json and update the API key" → Multiple tool calls orchestrated
3. **Error Handling**: Clear error messages when tools fail or permissions are denied
4. **Streaming Responses**: Maintains chat-ui's excellent streaming UX even with tool calls

### Technical Requirements

- LiteLLM Proxy deployed and running (Docker or direct)
- MCP servers configured in LiteLLM
- chat-ui environment variable updated to point to LiteLLM
- MongoDB for chat-ui (unchanged)
- OpenAI-compatible LLM backend (HuggingFace Router, OpenAI, etc.)

### Success Criteria

- [ ] LiteLLM Proxy running with MCP Gateway enabled
- [ ] At least 2 MCP servers connected (filesystem, fetch recommended)
- [ ] chat-ui successfully communicates through LiteLLM
- [ ] Tool calls execute and return results to LLM
- [ ] Streaming chat responses work correctly
- [ ] Multi-turn conversations with tools maintain context
- [ ] Error cases handled gracefully (timeout, tool failure, etc.)

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Include these in your context window

- url: https://docs.litellm.ai/docs/mcp_usage
  why: Official LiteLLM MCP Gateway documentation and configuration
  critical: Shows how to enable MCP, configure servers, and use with OpenAI API

- url: https://docs.litellm.ai/docs/proxy/quick_start
  why: LiteLLM Proxy quick start and setup
  critical: Docker deployment, environment variables, config file structure

- url: https://modelcontextprotocol.io/specification/2025-06-18
  why: MCP protocol specification and transport types
  critical: Understanding stdio vs SSE transports for server configuration

- url: https://github.com/modelcontextprotocol/servers
  why: Official MCP servers repository with pre-built tools
  critical: Ready-to-use servers for filesystem, git, databases, APIs

- url: https://github.com/huggingface/chat-ui/blob/main/README.md
  why: chat-ui configuration and environment variables
  critical: How OPENAI_BASE_URL works and model selection

- url: https://github.com/SecretiveShell/MCP-Bridge
  why: Alternative approach (reference only, we're using LiteLLM)
  critical: Architecture insights on OpenAI-compatible MCP integration

- file: /tmp/chat-ui/README.md
  why: Local clone of chat-ui with current architecture
  critical: Confirm OpenAI-compatible API usage and env var requirements

- file: /tmp/chat-ui/.env
  why: Template environment variables for chat-ui
  critical: Shows all configurable options including OPENAI_BASE_URL

- docfile: PRPs/ai_docs/mcp-litellm-integration.md
  why: [CREATE THIS] Curated LiteLLM MCP configuration examples
  critical: Working config files and common pitfalls
```

### Current Codebase Architecture (chat-ui)

```
chat-ui/ (at /tmp/chat-ui - cloned for reference)
├── src/
│   ├── routes/
│   │   ├── conversation/[id]/+server.ts  # Server-side streaming logic
│   │   └── api/                          # API endpoints
│   ├── lib/
│   │   ├── server/
│   │   │   ├── endpoints/
│   │   │   │   └── openai/              # OpenAI-compatible endpoint handler
│   │   │   ├── models.ts                # Model configuration (fetches from /models)
│   │   │   └── textGeneration/          # Text generation pipeline
│   │   ├── types/
│   │   │   ├── Message.ts               # Message type definitions
│   │   │   └── MessageUpdate.ts         # Streaming update types
│   │   └── utils/
│   │       └── messageUpdates.ts        # Client-side stream parsing
├── .env                                  # Environment config template
└── package.json                          # Dependencies (SvelteKit, MongoDB, etc.)

CRITICAL FINDINGS:
- Line src/lib/server/endpoints/openai/openAIChatToTextGenerationStream.ts:139
  Comment: "// Tools removed: ignore tool_calls deltas"
  → Tool calling was EXPLICITLY REMOVED from chat-ui
- OpenAI-compatible API via OPENAI_BASE_URL env var
- Fetches models from ${OPENAI_BASE_URL}/models endpoint
- Excellent streaming infrastructure (ReadableStream, JSON-Lines)
```

### Desired Architecture (LiteLLM Proxy Integration)

```
┌─────────────┐         ┌──────────────────┐         ┌──────────────┐
│  chat-ui    │────────▶│  LiteLLM Proxy   │────────▶│   LLM API    │
│  (SvelteKit)│◀────────│  (MCP Gateway)   │◀────────│ (OpenAI/HF)  │
└─────────────┘         └────────┬─────────┘         └──────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   MCP Servers   │
                        ├─────────────────┤
                        │ - filesystem    │
                        │ - fetch (HTTP)  │
                        │ - git           │
                        │ - database      │
                        │ - custom tools  │
                        └─────────────────┘

Flow:
1. User sends message in chat-ui
2. chat-ui → POST /v1/chat/completions to LiteLLM
3. LiteLLM enriches request with MCP tools
4. LiteLLM → Actual LLM API
5. LLM responds with tool_calls
6. LiteLLM executes tools via MCP servers
7. LiteLLM → LLM with tool results
8. LiteLLM streams final response → chat-ui
9. chat-ui renders streaming response to user
```

### New Files to Create

```
/home/user/PRPs-agentic-eng/
├── chat-ui-mcp-deployment/
│   ├── docker-compose.yml              # Full stack deployment
│   ├── litellm/
│   │   ├── config.yaml                 # LiteLLM configuration
│   │   ├── .env.litellm                # LiteLLM environment variables
│   │   └── mcp-servers/                # MCP server configs
│   │       ├── filesystem-config.json
│   │       ├── fetch-config.json
│   │       └── custom-tools-config.json
│   ├── chat-ui/
│   │   └── .env.local                  # chat-ui config pointing to LiteLLM
│   ├── scripts/
│   │   ├── setup.sh                    # Automated setup script
│   │   ├── test-mcp-connection.sh      # Test MCP tools via curl
│   │   └── health-check.sh             # Verify all services healthy
│   └── README.md                       # Deployment documentation
└── PRPs/ai_docs/
    └── mcp-litellm-integration.md      # Curated integration docs
```

### Known Gotchas & Library Quirks

```yaml
chat-ui Gotchas:
  - OPENAI_BASE_URL must NOT have trailing slash
  - Fetches models from /models endpoint automatically
  - Requires MongoDB even for simple testing
  - Uses streaming by default (must preserve this)
  - Tool calling was removed intentionally (don't try to re-add)

LiteLLM Gotchas:
  - MCP Gateway requires specific config structure
  - server_url: "litellm_proxy" is a magic value
  - MCP servers must be configured in config.yaml, NOT environment variables
  - Stdio transport requires command path resolution
  - Redis is optional but recommended for production
  - Default port 4000 (not 8000)

MCP Server Gotchas:
  - Stdio servers must be executable (chmod +x or via npx/uvx)
  - SSE servers need full HTTP URL
  - Tool names must be unique across all servers
  - Some servers require environment variables (API keys, paths)
  - Filesystem server security: MUST restrict allowed directories
  - Tool execution can timeout - configure appropriate limits

OpenAI API Compatibility:
  - Tool calls in streaming mode arrive as deltas
  - Must reassemble tool_calls from multiple chunks
  - Streaming + tools = complex state management (LiteLLM handles this)
  - Response format with tools differs from plain chat
```

## Implementation Blueprint

### Phase 1: LiteLLM Proxy Setup (Day 1, 2-3 hours)

#### Task 1: Create Project Structure

```bash
# Create deployment directory
mkdir -p /home/user/PRPs-agentic-eng/chat-ui-mcp-deployment/{litellm,chat-ui,scripts}
mkdir -p /home/user/PRPs-agentic-eng/chat-ui-mcp-deployment/litellm/mcp-servers

cd /home/user/PRPs-agentic-eng/chat-ui-mcp-deployment
```

#### Task 2: Create LiteLLM Configuration

CREATE `litellm/config.yaml`:

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: os.environ/OPENAI_API_KEY

  # Add HuggingFace Router
  - model_name: hf-router
    litellm_params:
      model: openai/meta-llama/Llama-3.3-70B-Instruct
      api_base: https://router.huggingface.co/v1
      api_key: os.environ/HF_TOKEN

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY

litellm_settings:
  enable_mcp: true
  mcp_servers:
    # Filesystem MCP Server (stdio transport)
    - name: filesystem
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-filesystem"
        - "/home/user/PRPs-agentic-eng"  # Restrict to project directory
      type: stdio

    # HTTP Fetch MCP Server (stdio transport)
    - name: fetch
      command: uvx
      args:
        - "mcp-server-fetch"
      type: stdio

    # Git MCP Server (example for version control operations)
    - name: git
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-git"
        - "--repository"
        - "/home/user/PRPs-agentic-eng"
      type: stdio
```

#### Task 3: Create LiteLLM Environment File

CREATE `litellm/.env.litellm`:

```bash
# LiteLLM Configuration
LITELLM_MASTER_KEY=sk-1234567890abcdef  # Change this!
DATABASE_URL=postgresql://user:pass@localhost:5432/litellm  # Optional
REDIS_HOST=localhost  # Optional but recommended
REDIS_PORT=6379

# LLM Provider Keys
OPENAI_API_KEY=sk-...  # Your OpenAI key
HF_TOKEN=hf_...        # Your HuggingFace token

# Logging
LITELLM_LOG=INFO
```

CRITICAL: Set secure LITELLM_MASTER_KEY - this is used for authentication

#### Task 4: Create Docker Compose for Full Stack

CREATE `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # MongoDB for chat-ui
  mongodb:
    image: mongo:7
    container_name: chat-ui-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: chat-ui
    networks:
      - chat-network

  # LiteLLM Proxy with MCP Gateway
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm-mcp-gateway
    ports:
      - "4000:4000"
    volumes:
      - ./litellm/config.yaml:/app/config.yaml
      - ./litellm/.env.litellm:/app/.env
      # Mount MCP server configs if needed
      - ./litellm/mcp-servers:/app/mcp-servers
    environment:
      - LITELLM_CONFIG=/app/config.yaml
    command: --config /app/config.yaml --port 4000
    networks:
      - chat-network
    depends_on:
      - mongodb

  # chat-ui (SvelteKit)
  chat-ui:
    image: ghcr.io/huggingface/chat-ui:latest
    container_name: chat-ui-app
    ports:
      - "3000:3000"
    environment:
      # Point to LiteLLM Proxy instead of direct LLM
      - OPENAI_BASE_URL=http://litellm:4000/v1
      - OPENAI_API_KEY=sk-1234567890abcdef  # LiteLLM master key
      - MONGODB_URL=mongodb://mongodb:27017
      - MONGODB_DB_NAME=chat-ui
      - PUBLIC_APP_NAME=ChatUI with MCP
      - PUBLIC_APP_DESCRIPTION=AI Chat with Tool Calling via MCP
    networks:
      - chat-network
    depends_on:
      - mongodb
      - litellm

networks:
  chat-network:
    driver: bridge

volumes:
  mongodb_data:
```

PATTERN: Note how chat-ui's OPENAI_BASE_URL points to litellm:4000

### Phase 2: Local Development Setup (Day 1, 1-2 hours)

#### Task 5: Create Setup Script

CREATE `scripts/setup.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up chat-ui with MCP integration..."

# Check dependencies
echo "📋 Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose not found"; exit 1; }

# Install MCP servers globally (for testing)
echo "📦 Installing MCP servers..."
npm install -g @modelcontextprotocol/server-filesystem
pip install mcp-server-fetch  # or: uvx mcp-server-fetch

# Create .env files if they don't exist
if [ ! -f litellm/.env.litellm ]; then
  echo "⚙️  Creating litellm/.env.litellm from template..."
  cp litellm/.env.litellm.example litellm/.env.litellm
  echo "⚠️  Please edit litellm/.env.litellm with your API keys!"
  exit 1
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Health checks
echo "🏥 Running health checks..."
curl -f http://localhost:4000/health || echo "⚠️  LiteLLM not ready"
curl -f http://localhost:3000 || echo "⚠️  chat-ui not ready"

echo "✅ Setup complete!"
echo ""
echo "🌐 Access Points:"
echo "   - chat-ui: http://localhost:3000"
echo "   - LiteLLM: http://localhost:4000"
echo "   - MongoDB: mongodb://localhost:27017"
echo ""
echo "📚 Next steps:"
echo "   1. Edit litellm/.env.litellm with your API keys"
echo "   2. Test MCP connection: ./scripts/test-mcp-connection.sh"
echo "   3. Open http://localhost:3000 and start chatting!"
```

```bash
chmod +x scripts/setup.sh
```

#### Task 6: Create Test Script

CREATE `scripts/test-mcp-connection.sh`:

```bash
#!/bin/bash

echo "🧪 Testing MCP integration..."

LITELLM_URL="http://localhost:4000"
MASTER_KEY="sk-1234567890abcdef"  # From .env.litellm

# Test 1: LiteLLM health
echo "1️⃣ Testing LiteLLM health..."
curl -s "$LITELLM_URL/health" | jq '.'

# Test 2: List available models (should include MCP-enhanced models)
echo ""
echo "2️⃣ Listing available models..."
curl -s -H "Authorization: Bearer $MASTER_KEY" \
  "$LITELLM_URL/v1/models" | jq '.data[] | {id, owned_by}'

# Test 3: Chat completion with MCP tools
echo ""
echo "3️⃣ Testing chat with MCP tools..."
curl -s "$LITELLM_URL/v1/chat/completions" \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hf-router",
    "messages": [
      {"role": "user", "content": "List files in the current directory using the filesystem tool"}
    ],
    "tools": [
      {
        "type": "mcp",
        "server_label": "filesystem",
        "server_url": "litellm_proxy"
      }
    ],
    "stream": false
  }' | jq '.'

echo ""
echo "✅ MCP connection tests complete!"
```

```bash
chmod +x scripts/test-mcp-connection.sh
```

### Phase 3: Integration Testing (Day 2, 2-3 hours)

#### Task 7: Verify End-to-End Flow

```bash
# Start all services
cd /home/user/PRPs-agentic-eng/chat-ui-mcp-deployment
./scripts/setup.sh

# Wait for services
sleep 15

# Test MCP through LiteLLM
./scripts/test-mcp-connection.sh
```

Expected Output:
```json
{
  "id": "chatcmpl-...",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Here are the files in the directory:\n- file1.py\n- file2.js\n...",
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "list_directory",
            "arguments": "{\"path\": \".\"}"
          }
        }
      ]
    }
  }]
}
```

#### Task 8: Manual UI Testing

1. Open http://localhost:3000
2. Create new conversation
3. Test Tool Calling Queries:

```
Query 1: "What files are in the PRPs directory?"
Expected: LLM uses filesystem tool to list files

Query 2: "Read the contents of CLAUDE.md"
Expected: LLM uses filesystem read tool

Query 3: "Fetch the latest MCP specification from modelcontextprotocol.io"
Expected: LLM uses fetch tool to get web content

Query 4: "What's the latest commit in this git repository?"
Expected: LLM uses git tool to check commit history
```

#### Task 9: Test Error Handling

```bash
# Test with invalid tool call
curl "$LITELLM_URL/v1/chat/completions" \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hf-router",
    "messages": [
      {"role": "user", "content": "Read /etc/shadow"}
    ],
    "tools": [{"type": "mcp", "server_label": "filesystem", "server_url": "litellm_proxy"}]
  }'
```

Expected: Permission denied error, gracefully handled

### Phase 4: Production Hardening (Day 2, 2-3 hours)

#### Task 10: Security Configuration

UPDATE `litellm/config.yaml` with security settings:

```yaml
litellm_settings:
  enable_mcp: true

  # Tool execution limits
  mcp_tool_timeout: 30  # seconds
  max_parallel_tools: 3

  # Allowed tools (whitelist)
  allowed_tools:
    - list_directory
    - read_file
    - write_file
    - fetch_url
    - git_log
    - git_diff

  # Tool approval requirement
  require_approval: "never"  # or "always" for manual approval

  mcp_servers:
    - name: filesystem
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-filesystem"
        - "/home/user/PRPs-agentic-eng"  # RESTRICTED PATH
      type: stdio
      # Security: Only allow access to specific directory
      environment:
        ALLOWED_DIRECTORIES: "/home/user/PRPs-agentic-eng"
```

CRITICAL: Restrict filesystem access to prevent directory traversal attacks

#### Task 11: Create Health Check Script

CREATE `scripts/health-check.sh`:

```bash
#!/bin/bash

FAIL=0

# Check LiteLLM
curl -sf http://localhost:4000/health > /dev/null || { echo "❌ LiteLLM down"; FAIL=1; }

# Check chat-ui
curl -sf http://localhost:3000 > /dev/null || { echo "❌ chat-ui down"; FAIL=1; }

# Check MongoDB
docker exec chat-ui-mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null || { echo "❌ MongoDB down"; FAIL=1; }

if [ $FAIL -eq 0 ]; then
  echo "✅ All services healthy"
else
  echo "⚠️  Some services unhealthy"
  exit 1
fi
```

```bash
chmod +x scripts/health-check.sh
```

#### Task 12: Create Documentation

CREATE `README.md`:

```markdown
# chat-ui with MCP Integration

Production deployment of Hugging Face chat-ui with Model Context Protocol (MCP) tool calling via LiteLLM Proxy.

## Architecture

```
User → chat-ui → LiteLLM Proxy (MCP Gateway) → LLM + MCP Servers
```

## Quick Start

1. **Configure API Keys**
   ```bash
   cp litellm/.env.litellm.example litellm/.env.litellm
   # Edit .env.litellm with your keys
   ```

2. **Start Services**
   ```bash
   ./scripts/setup.sh
   ```

3. **Test MCP Integration**
   ```bash
   ./scripts/test-mcp-connection.sh
   ```

4. **Access chat-ui**
   Open http://localhost:3000

## Available MCP Tools

- **filesystem**: Read/write files, list directories
- **fetch**: Make HTTP requests to external APIs
- **git**: Git repository operations

## Configuration

### Adding New MCP Servers

Edit `litellm/config.yaml`:

```yaml
mcp_servers:
  - name: your-server
    command: npx
    args: ["-y", "@modelcontextprotocol/server-yourserver"]
    type: stdio
```

### Changing LLM Provider

Edit `litellm/config.yaml`:

```yaml
model_list:
  - model_name: your-model
    litellm_params:
      model: provider/model-name
      api_key: os.environ/YOUR_API_KEY
```

## Troubleshooting

### chat-ui not connecting to LiteLLM
- Check `OPENAI_BASE_URL=http://litellm:4000/v1` in docker-compose
- Verify LiteLLM is healthy: `curl http://localhost:4000/health`

### Tools not executing
- Check LiteLLM logs: `docker logs litellm-mcp-gateway`
- Verify MCP servers installed: `npx @modelcontextprotocol/server-filesystem --version`

### Permission errors
- Check allowed directories in `config.yaml`
- Ensure MCP server has access to required paths

## Monitoring

```bash
# Check all services
./scripts/health-check.sh

# View LiteLLM logs
docker logs -f litellm-mcp-gateway

# View chat-ui logs
docker logs -f chat-ui-app
```

## Production Deployment

1. **Set secure master key** in `.env.litellm`
2. **Enable Redis** for better performance
3. **Configure allowed_tools** whitelist
4. **Set up SSL/TLS** (nginx reverse proxy)
5. **Enable authentication** in chat-ui
```

## Integration Points

```yaml
ENVIRONMENT:
  chat-ui:
    - OPENAI_BASE_URL: "http://litellm:4000/v1"
    - OPENAI_API_KEY: "${LITELLM_MASTER_KEY}"
    - MONGODB_URL: "mongodb://mongodb:27017"

  litellm:
    - LITELLM_CONFIG: "/app/config.yaml"
    - DATABASE_URL: "postgresql://..." # optional
    - REDIS_HOST: "localhost" # optional

DOCKER:
  - Network: chat-network (bridge)
  - Volumes: mongodb_data
  - Port Mappings:
    - 3000:3000 (chat-ui)
    - 4000:4000 (LiteLLM)
    - 27017:27017 (MongoDB)

MCP_SERVERS:
  - filesystem: @modelcontextprotocol/server-filesystem
  - fetch: mcp-server-fetch (pip package)
  - git: @modelcontextprotocol/server-git
```

## Validation Loop

### Level 1: Service Health

```bash
# Check all services are running
docker-compose ps

# Expected output:
# NAME                    STATUS    PORTS
# chat-ui-app            Up        0.0.0.0:3000->3000/tcp
# litellm-mcp-gateway    Up        0.0.0.0:4000->4000/tcp
# chat-ui-mongodb        Up        0.0.0.0:27017->27017/tcp

# If any service is down: docker-compose logs <service-name>
```

### Level 2: LiteLLM MCP Gateway Test

```bash
# Run MCP connection tests
./scripts/test-mcp-connection.sh

# Expected:
# ✅ Health check passes
# ✅ Models list includes configured models
# ✅ Tool call executes successfully

# If failing:
# - Check litellm/config.yaml syntax
# - Verify API keys in .env.litellm
# - Check MCP servers are installed: npx @modelcontextprotocol/server-filesystem --version
```

### Level 3: End-to-End UI Test

Manual testing in browser:

```
1. Navigate to http://localhost:3000
2. Create new conversation
3. Send: "What files are in the current directory?"
4. Verify:
   ✅ Response includes file list
   ✅ Response time < 5 seconds
   ✅ No error messages
5. Send: "Read the CLAUDE.md file"
6. Verify:
   ✅ File contents appear in response
   ✅ Streaming works (text appears progressively)
```

If failing:
- Check browser console for errors
- Verify OPENAI_BASE_URL is correct in docker-compose.yml
- Check LiteLLM logs: `docker logs litellm-mcp-gateway`

### Level 4: Security & Error Handling

```bash
# Test 1: Directory traversal prevention
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hf-router",
    "messages": [{"role": "user", "content": "Read /etc/passwd"}],
    "tools": [{"type": "mcp", "server_label": "filesystem", "server_url": "litellm_proxy"}]
  }'

# Expected: Permission denied error, not file contents

# Test 2: Tool timeout handling
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hf-router",
    "messages": [{"role": "user", "content": "Fetch https://httpbin.org/delay/60"}],
    "tools": [{"type": "mcp", "server_label": "fetch", "server_url": "litellm_proxy"}]
  }'

# Expected: Timeout error after 30 seconds (per config)

# Test 3: Invalid tool call
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hf-router",
    "messages": [{"role": "user", "content": "Execute rm -rf /"}],
    "tools": [{"type": "mcp", "server_label": "filesystem", "server_url": "litellm_proxy"}]
  }'

# Expected: Graceful error, no actual execution
```

### Level 5: Performance Testing

```bash
# Install hey (HTTP load testing tool)
# Ubuntu: sudo apt install hey
# macOS: brew install hey

# Test concurrent requests
hey -n 100 -c 10 \
  -m POST \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"hf-router","messages":[{"role":"user","content":"Hello"}]}' \
  http://localhost:4000/v1/chat/completions

# Expected:
# - Success rate: >95%
# - Average response time: <2s
# - No OOM errors in logs
```

## Final Validation Checklist

- [ ] All Docker services running: `docker-compose ps`
- [ ] LiteLLM health check passes: `curl http://localhost:4000/health`
- [ ] MCP servers configured: Check `litellm/config.yaml`
- [ ] chat-ui accessible: Open http://localhost:3000
- [ ] Tool calls work: Test "List files in directory" query
- [ ] Streaming works: Responses appear progressively
- [ ] Error handling works: Permission denied for /etc/passwd
- [ ] Timeout handling works: Long-running tools timeout gracefully
- [ ] Security validated: Directory traversal blocked
- [ ] Performance acceptable: <2s average response time
- [ ] Documentation complete: README.md updated
- [ ] Scripts executable: `chmod +x scripts/*.sh`

---

## Anti-Patterns to Avoid

- ❌ **Don't modify chat-ui source code** - Use proxy pattern to preserve upgradability
- ❌ **Don't expose LiteLLM without authentication** - Always use LITELLM_MASTER_KEY
- ❌ **Don't allow unrestricted filesystem access** - Always set ALLOWED_DIRECTORIES
- ❌ **Don't skip health checks** - Automated monitoring prevents silent failures
- ❌ **Don't hardcode API keys** - Always use environment variables
- ❌ **Don't run MCP servers as root** - Use least-privilege principle
- ❌ **Don't ignore tool execution timeouts** - Set reasonable limits (30s default)
- ❌ **Don't trust LLM tool calls** - Validate and sanitize all tool inputs
- ❌ **Don't use stdio transport in production** - Consider SSE for better scalability
- ❌ **Don't forget to whitelist tools** - Use allowed_tools to prevent abuse

---

## Alternative Approaches (Not Recommended for Fastest Path)

### Approach 2: Direct SvelteKit Integration (2-3 weeks)

Would require:
- Fork chat-ui repository
- Add @vercel/mcp-adapter dependency
- Modify src/lib/server/endpoints/ to add MCP support
- Re-enable tool calling in streaming logic
- Add UI components for tool execution display
- Maintain fork with upstream updates

**Why Not**: Much more work, fork maintenance burden, breaks on upgrades

### Approach 3: MCP-Bridge Proxy (1 week)

Would use https://github.com/SecretiveShell/MCP-Bridge

**Why Not**: Project is soft-deprecated (Open WebUI has native support), LiteLLM is more mature

---

## Research References

- LiteLLM MCP Documentation: https://docs.litellm.ai/docs/mcp_usage
- MCP Specification: https://modelcontextprotocol.io/specification/2025-06-18
- Official MCP Servers: https://github.com/modelcontextprotocol/servers
- chat-ui Repository: https://github.com/huggingface/chat-ui
- SvelteKit MCP Starter: https://github.com/axel-rock/sveltekit-mcp-starter
- ChatMCP Reference: https://github.com/daodao97/chatmcp
- OpenAI Responses API: https://neurlcreators.substack.com/p/buildaiers-talking-9

---

## Success Metrics

**Technical Metrics:**
- Zero chat-ui code changes ✅
- Tool execution latency <500ms (excluding LLM) ✅
- Streaming maintained (progressive token rendering) ✅
- 99.9% uptime with health checks ✅

**User Experience Metrics:**
- Transparent tool usage (user doesn't see raw JSON) ✅
- Multi-turn conversations with context ✅
- Clear error messages on tool failure ✅
- Sub-3-second end-to-end response time ✅

**Operational Metrics:**
- One-command deployment (`docker-compose up`) ✅
- Automated health monitoring ✅
- Easy MCP server additions (config file edit) ✅
- No vendor lock-in (standard protocols) ✅
