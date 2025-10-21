# Chat-UI with MCP Integration - Production Deployment

Production-ready deployment of Hugging Face chat-ui with Model Context Protocol (MCP) tool calling via LiteLLM Proxy. Follows MCP 2025 specification and security best practices.

## Features

✅ **Zero chat-ui code changes** - Vanilla chat-ui, easy upgrades
✅ **Streamable HTTP transport** - Production-ready (NOT insecure stdio)
✅ **MCP 2025 compliant** - Follows official specification
✅ **Production security** - OAuth-ready, HTTPS-capable, tool whitelisting
✅ **User-friendly** - One command deployment
✅ **Extensible** - Easy to add custom MCP servers

## Quick Start

### Prerequisites

- Docker & Docker Compose
- HuggingFace token (free) OR OpenAI API key

### 1. Configure API Keys

```bash
cd chat-ui-mcp-deployment
cp .env.example .env
# Edit .env with your API keys
```

Required in `.env`:
```bash
LITELLM_MASTER_KEY=sk-litellm-YOUR_SECURE_KEY
HF_TOKEN=hf_YOUR_HUGGINGFACE_TOKEN  # Get from https://huggingface.co/settings/tokens
# OR
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY
```

### 2. Run Setup

```bash
./scripts/setup.sh
```

This will:
- Build the MCP filesystem server
- Start MongoDB, LiteLLM, chat-ui
- Run health checks
- Display access URLs

### 3. Use Chat-UI

1. Open http://localhost:3000
2. Start a conversation
3. Try these prompts:
   - "List files in my workspace"
   - "Read the README.md file"
   - "Create a new file called test.txt with content 'Hello MCP!'"

## Architecture

```
User Browser
     ↓
chat-ui (port 3000)
     ↓
LiteLLM Proxy (port 4000)
     ↓
MCP Servers (Streamable HTTP)
  - filesystem-server (port 8000)
```

**Key Design:**
- chat-ui → thinks it's talking to OpenAI
- LiteLLM → intercepts, adds MCP tools, routes to actual LLM
- MCP servers → execute tools securely via HTTP
- User → sees natural conversation with transparent tool execution

## What's Included

### Services

| Service | Port | Description |
|---------|------|-------------|
| chat-ui | 3000 | Main chat interface |
| LiteLLM | 4000 | MCP Gateway + LLM proxy |
| MongoDB | 27017 | Chat history persistence |
| filesystem-server | 8000 | MCP server for file operations |

### MCP Tools Available

**filesystem** server provides:
- `list_directory` - List files and folders
- `read_file` - Read text file contents
- `write_file` - Write content to files

Secured to `/workspace` directory only.

## Configuration

### LiteLLM Config (`litellm/config.yaml`)

```yaml
litellm_settings:
  enable_mcp: true
  mcp_servers:
    - name: filesystem
      type: streamable-http  # Production transport
      url: http://filesystem-server:8000/mcp
      allowed_tools:  # Security: whitelist
        - list_directory
        - read_file
        - write_file
```

### Adding Custom MCP Servers

1. Create server following [MCP spec](https://modelcontextprotocol.io/specification/2025-03-26)
2. Add to `litellm/config.yaml`:

```yaml
mcp_servers:
  - name: your-server
    type: streamable-http
    url: http://your-server:8080/mcp
    allowed_tools:
      - your_tool_1
      - your_tool_2
```

3. Add service to `docker-compose.yml`
4. Restart: `docker-compose restart litellm`

## Testing

### Manual Testing

```bash
# Test filesystem server directly
curl http://localhost:8000/health

# Test through LiteLLM
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3-70b",
    "messages": [{"role": "user", "content": "List files in workspace"}]
  }'
```

### In Browser

1. Open http://localhost:3000
2. Select `llama-3-70b` or `gpt-4` model
3. Type: "What files are in my workspace?"
4. Watch tool execution happen transparently

## Troubleshooting

### Services won't start

```bash
# Check logs
docker logs chat-ui-app
docker logs litellm-mcp-gateway
docker logs mcp-filesystem-server

# Check if ports are in use
lsof -i :3000  # chat-ui
lsof -i :4000  # LiteLLM
lsof -i :27017 # MongoDB
```

### Tools not working

1. **Check LiteLLM logs**: `docker logs litellm-mcp-gateway | grep MCP`
2. **Verify server health**: `curl http://localhost:8000/health`
3. **Test model supports tools**: Use `gpt-4` or `llama-3-70b`
4. **Check allowed_tools**: Ensure tool is whitelisted in config

### Permission errors

- Filesystem server is restricted to `/workspace`
- Check `ALLOWED_DIRECTORIES` in docker-compose.yml
- Verify file paths are within allowed directories

## Security Notes

### Current Setup (Development)

✅ Tool whitelisting (only approved tools execute)
✅ Path validation (restricted to /workspace)
✅ Non-root containers
⚠️ Simple bearer token auth (replace for production)
⚠️ HTTP only (add HTTPS for production)

### Production Hardening

For production deployment:

1. **Enable OAuth 2.0** for MCP servers
2. **Add HTTPS** (nginx reverse proxy with SSL)
3. **Use secrets manager** (not .env file)
4. **Enable audit logging**
5. **Add rate limiting**
6. **Deploy behind WAF**

See [PRP documentation](../PRPs/chat-ui-mcp-integration-production.md) for full production setup.

## Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f litellm-mcp-gateway
```

### Restart Services

```bash
# All
docker-compose restart

# Specific
docker-compose restart litellm
```

### Stop Everything

```bash
docker-compose down

# With data cleanup
docker-compose down -v
```

### Update

```bash
git pull
docker-compose pull
docker-compose up -d --build
```

## File Structure

```
chat-ui-mcp-deployment/
├── docker-compose.yml          # Main deployment
├── .env                        # Your API keys
├── litellm/
│   └── config.yaml             # MCP configuration
├── mcp-servers/
│   └── filesystem/
│       ├── server.py           # MCP server code
│       ├── Dockerfile
│       └── requirements.txt
├── scripts/
│   └── setup.sh                # Automated setup
├── workspace/                  # Accessible to MCP filesystem
└── README.md                   # This file
```

## Next Steps

1. **Try it out** - Test the filesystem tools in chat
2. **Add your MCP servers** - Extend with custom tools
3. **Enable monitoring** - Add Prometheus/Grafana (see PRP)
4. **Harden for production** - OAuth, HTTPS, audit logs
5. **Share with team** - Self-service MCP tool access

## Support

- **PRP Documentation**: `../PRPs/chat-ui-mcp-integration-production.md`
- **MCP Specification**: https://modelcontextprotocol.io/specification/2025-03-26
- **LiteLLM Docs**: https://docs.litellm.ai/docs/mcp_usage
- **Issue Tracker**: GitHub

## License

This deployment configuration follows the same licenses as:
- Hugging Face chat-ui (Apache 2.0)
- LiteLLM (MIT)
- MCP Specification (Apache 2.0)

---

**Built with**: MCP 2025 specification compliance, production best practices, zero chat-ui modifications ✨
