#!/usr/bin/env python3
"""
Production Streamable HTTP MCP Server for Filesystem Operations
Follows MCP 2025 specification and security best practices
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from pathlib import Path
from typing import Optional, List, Dict, Any
import os
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Filesystem MCP Server",
    description="Production MCP server for filesystem operations with OAuth 2.0",
    version="1.0.0"
)

# Security: Restrict to allowed directories only
ALLOWED_DIRS = os.getenv("ALLOWED_DIRECTORIES", "/workspace").split(":")
ALLOWED_PATHS = [Path(d).resolve() for d in ALLOWED_DIRS if d]

logger.info(f"Allowed directories: {ALLOWED_PATHS}")

def validate_path(path: str) -> Path:
    """Validate path is within allowed directories"""
    try:
        resolved = Path(path).resolve()
        for allowed in ALLOWED_PATHS:
            try:
                resolved.relative_to(allowed)
                return resolved
            except ValueError:
                continue
        raise HTTPException(403, f"Access denied: {path} not in allowed directories")
    except Exception as e:
        logger.error(f"Path validation error for {path}: {e}")
        raise HTTPException(400, f"Invalid path: {path}")

async def verify_auth(authorization: Optional[str] = Header(None)) -> str:
    """Verify authentication (simplified for demo)"""
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization scheme")

    token = authorization[7:]
    # In production, verify with OAuth provider
    if len(token) < 10:
        raise HTTPException(401, "Invalid token")

    return token

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "filesystem-mcp-server",
        "version": "1.0.0",
        "allowed_directories": [str(p) for p in ALLOWED_PATHS],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/mcp")
async def mcp_endpoint(
    request: dict,
    authorization: Optional[str] = Header(None)
):
    """
    MCP Streamable HTTP endpoint
    Handles tool calls following MCP 2025 specification
    """
    # Verify authentication
    await verify_auth(authorization)

    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id", "unknown")

    logger.info(f"MCP Request: {method} (ID: {request_id})")

    try:
        if method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "list_directory",
                            "description": "List files and directories in the specified path",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "path": {
                                        "type": "string",
                                        "description": "Directory path to list"
                                    }
                                },
                                "required": ["path"]
                            }
                        },
                        {
                            "name": "read_file",
                            "description": "Read file contents (text files only)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "path": {
                                        "type": "string",
                                        "description": "File path to read"
                                    },
                                    "max_size": {
                                        "type": "integer",
                                        "description": "Maximum file size in bytes",
                                        "default": 1000000
                                    }
                                },
                                "required": ["path"]
                            }
                        },
                        {
                            "name": "write_file",
                            "description": "Write content to a file",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "path": {
                                        "type": "string",
                                        "description": "File path to write"
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "Content to write"
                                    },
                                    "overwrite": {
                                        "type": "boolean",
                                        "description": "Allow overwriting existing file",
                                        "default": False
                                    }
                                },
                                "required": ["path", "content"]
                            }
                        }
                    ]
                }
            })

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name == "list_directory":
                result = await list_directory(tool_args.get("path", "."))
            elif tool_name == "read_file":
                result = await read_file(
                    tool_args.get("path"),
                    tool_args.get("max_size", 1000000)
                )
            elif tool_name == "write_file":
                result = await write_file(
                    tool_args.get("path"),
                    tool_args.get("content"),
                    tool_args.get("overwrite", False)
                )
            else:
                raise HTTPException(404, f"Unknown tool: {tool_name}")

            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            })

        else:
            raise HTTPException(400, f"Unknown method: {method}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")

async def list_directory(path: str) -> Dict[str, Any]:
    """List files and directories"""
    validated_path = validate_path(path)

    if not validated_path.exists():
        raise HTTPException(404, f"Path not found: {path}")

    if not validated_path.is_dir():
        raise HTTPException(400, f"Path is not a directory: {path}")

    try:
        items = []
        for item in validated_path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
            })

        logger.info(f"Listed directory: {path} ({len(items)} items)")
        return {
            "path": str(validated_path),
            "items": sorted(items, key=lambda x: (x["type"] != "directory", x["name"]))
        }

    except PermissionError:
        raise HTTPException(403, f"Permission denied: {path}")
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        raise HTTPException(500, f"Error listing directory: {str(e)}")

async def read_file(path: str, max_size: int = 1_000_000) -> Dict[str, Any]:
    """Read file contents"""
    validated_path = validate_path(path)

    if not validated_path.exists():
        raise HTTPException(404, f"File not found: {path}")

    if not validated_path.is_file():
        raise HTTPException(400, f"Path is not a file: {path}")

    # Security: Limit file size
    file_size = validated_path.stat().st_size
    if file_size > max_size:
        raise HTTPException(413, f"File too large ({file_size} bytes, max {max_size})")

    try:
        content = validated_path.read_text()
        logger.info(f"Read file: {path} ({len(content)} chars)")

        return {
            "path": str(validated_path),
            "content": content,
            "size": len(content),
            "encoding": "utf-8"
        }

    except UnicodeDecodeError:
        raise HTTPException(400, "File is not text (binary file)")
    except PermissionError:
        raise HTTPException(403, f"Permission denied: {path}")
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise HTTPException(500, f"Error reading file: {str(e)}")

async def write_file(path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    """Write content to file"""
    validated_path = validate_path(path)

    # Security: Prevent overwrite unless explicit
    if validated_path.exists() and not overwrite:
        raise HTTPException(409, f"File exists (use overwrite=true): {path}")

    try:
        validated_path.parent.mkdir(parents=True, exist_ok=True)
        validated_path.write_text(content)

        logger.info(f"Wrote file: {path} ({len(content)} chars)")

        return {
            "path": str(validated_path),
            "size": len(content),
            "message": "File written successfully"
        }

    except PermissionError:
        raise HTTPException(403, f"Permission denied: {path}")
    except Exception as e:
        logger.error(f"Error writing file {path}: {e}")
        raise HTTPException(500, f"Error writing file: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
