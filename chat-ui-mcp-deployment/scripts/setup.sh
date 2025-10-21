#!/bin/bash
set -e

echo "🚀 Setting up chat-ui with MCP (Production)"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check dependencies
echo "📋 Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker not found${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose not found${NC}"; exit 1; }
echo -e "${GREEN}✅ Dependencies OK${NC}"

# Check for .env file
if [ ! -f .env ]; then
  echo -e "${YELLOW}⚠️  No .env file found${NC}"
  echo "Creating from .env.example..."
  cp .env.example .env

  # Generate secure key
  if command -v openssl >/dev/null 2>&1; then
    LITELLM_KEY="sk-litellm-$(openssl rand -hex 32)"
    sed -i "s/LITELLM_MASTER_KEY=.*/LITELLM_MASTER_KEY=$LITELLM_KEY/" .env
    echo -e "${GREEN}✅ Generated secure LITELLM_MASTER_KEY${NC}"
  fi

  echo -e "${YELLOW}⚠️  Please edit .env with your API keys!${NC}"
  echo "Required keys:"
  echo "  - HF_TOKEN (get from https://huggingface.co/settings/tokens)"
  echo "  - OR OPENAI_API_KEY (if using OpenAI)"
  echo ""
  read -p "Press Enter after editing .env..."
fi

# Validate .env
source .env
if [ -z "$LITELLM_MASTER_KEY" ] || [ "$LITELLM_MASTER_KEY" = "sk-litellm-REPLACE_WITH_SECURE_KEY" ]; then
  echo -e "${RED}❌ Please set LITELLM_MASTER_KEY in .env${NC}"
  exit 1
fi

if [ -z "$HF_TOKEN" ] && [ -z "$OPENAI_API_KEY" ]; then
  echo -e "${RED}❌ Please set either HF_TOKEN or OPENAI_API_KEY in .env${NC}"
  exit 1
fi

# Create workspace directory
mkdir -p workspace
echo "# Welcome to MCP Workspace" > workspace/README.md
echo "This directory is accessible to the filesystem MCP server." >> workspace/README.md

# Build MCP servers
echo ""
echo "🏗️  Building MCP filesystem server..."
docker-compose build filesystem-server

# Start services
echo ""
echo "🐳 Starting services..."
docker-compose up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 20

# Health checks
echo ""
echo "🏥 Running health checks..."

check_health() {
  local service=$1
  local url=$2
  local max_attempts=10
  local attempt=1

  while [ $attempt -le $max_attempts ]; do
    if curl -sf "$url" > /dev/null 2>&1; then
      echo -e "${GREEN}✅ $service is healthy${NC}"
      return 0
    fi
    echo "Waiting for $service (attempt $attempt/$max_attempts)..."
    sleep 3
    attempt=$((attempt + 1))
  done

  echo -e "${RED}❌ $service failed to start${NC}"
  echo "Check logs: docker logs $service"
  return 1
}

check_health "MongoDB" "http://localhost:27017" || echo "Note: MongoDB doesn't expose HTTP"
check_health "Filesystem Server" "http://localhost:8000/health" || docker logs mcp-filesystem-server
check_health "LiteLLM" "http://localhost:4000/health" || docker logs litellm-mcp-gateway
check_health "chat-ui" "http://localhost:3000" || docker logs chat-ui-app

# Display access info
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "🌐 Access Points:"
echo "   - chat-ui:    http://localhost:3000"
echo "   - LiteLLM:    http://localhost:4000"
echo ""
echo "📚 Next steps:"
echo "   1. Open http://localhost:3000"
echo "   2. Start a conversation"
echo "   3. Try: 'List files in my workspace'"
echo "   4. Try: 'Read the README.md file'"
echo ""
echo "🔍 View logs:"
echo "   - docker logs chat-ui-app"
echo "   - docker logs litellm-mcp-gateway"
echo "   - docker logs mcp-filesystem-server"
echo ""
echo "🛑 Stop services:"
echo "   - docker-compose down"
