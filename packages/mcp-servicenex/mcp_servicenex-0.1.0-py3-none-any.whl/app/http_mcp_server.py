#!/usr/bin/env python3
"""
HTTP/HTTPS MCP Server for ServiceNex

This exposes the MCP server functionality over HTTP/HTTPS using FastAPI.
Can be deployed to Cloud Run or any HTTP hosting service.
"""

import asyncio
import json
import logging
import os
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.mcp_server import server
from app.config import MY_API_BASE_URL, MY_API_KEY
from app.loaders.my_api_loader import fetch_tickets, fetch_articles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request models
class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any]


class ResourceReadRequest(BaseModel):
    uri: str


# Global server instance
mcp_server = server


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI."""
    logger.info("Starting HTTP MCP Server...")
    yield
    logger.info("Shutting down HTTP MCP Server...")


# Create FastAPI app
app = FastAPI(
    title="ServiceNex MCP Server",
    description="HTTP/HTTPS interface for ServiceNex MCP tools and resources",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_api_key_from_header(request: Request) -> Optional[str]:
    """Extract API key from request headers."""
    # Check Authorization header (Bearer token)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    
    # Check X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key
    
    # Check X-ServiceNex-API-Key header
    api_key = request.headers.get("X-ServiceNex-API-Key")
    if api_key:
        return api_key
    
    return None


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "ServiceNex MCP Server",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    Server-Sent Events endpoint for MCP over HTTP transport.
    This allows Claude Desktop (newer versions) to connect via HTTP/SSE.
    """
    async def event_generator():
        """Generate SSE events for MCP protocol."""
        try:
            # Send initial connection event
            yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"
            
            # Keep connection alive
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                # Send heartbeat every 30 seconds
                await asyncio.sleep(30)
                yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"
                
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/mcp/tools")
async def list_tools(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """List available MCP tools."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Return hardcoded tools list (matching MCP server tools)
        return {
            "tools": [
                {
                    "name": "get_knowledge_articles",
                    "description": "Fetch knowledge base articles from ServiceNex. Returns published articles with title, category, author, and status information. Supports pagination and category filtering.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by category name (default: 'all' for all categories)",
                                "default": "all"
                            },
                            "page": {
                                "type": "integer",
                                "description": "Page number for pagination (default: 1)",
                                "default": 1
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of articles per page (default: 10)",
                                "default": 10
                            }
                        }
                    }
                },
                {
                    "name": "get_tickets",
                    "description": "Fetch recent support tickets from ServiceNex. Returns ticket information including titles and status. Supports pagination and category filtering.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by category name (default: 'all' for all categories)",
                                "default": "all"
                            },
                            "page": {
                                "type": "integer",
                                "description": "Page number for pagination (default: 1)",
                                "default": 1
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of tickets per page (default: 5)",
                                "default": 5
                            }
                        }
                    }
                },
                {
                    "name": "search_articles",
                    "description": "Search for specific knowledge base articles by keyword or topic.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant articles"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_article_by_id",
                    "description": "Get detailed information about a specific article by its ID.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "article_id": {
                                "type": "string",
                                "description": "The ID of the article to retrieve"
                            }
                        },
                        "required": ["article_id"]
                    }
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/call")
async def call_tool(
    tool_request: ToolCallRequest,
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Call an MCP tool."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Route to appropriate function based on tool name
        if tool_request.name == "get_tickets":
            result = fetch_tickets(
                category=tool_request.arguments.get("category", "all"),
                page=tool_request.arguments.get("page", 1),
                limit=tool_request.arguments.get("limit", 5)
            )
            return {
                "tool": tool_request.name,
                "content": [{"type": "text", "text": str(result)}]
            }
        
        elif tool_request.name == "get_knowledge_articles":
            result = fetch_articles(
                category=tool_request.arguments.get("category", "all"),
                page=tool_request.arguments.get("page", 1),
                limit=tool_request.arguments.get("limit", 10)
            )
            return {
                "tool": tool_request.name,
                "content": [{"type": "text", "text": str(result)}]
            }
        
        elif tool_request.name == "search_articles":
            query = tool_request.arguments.get("query", "").lower()
            if not query:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide a search query"}]
                }
            result = fetch_articles(category="all", page=1, limit=50)
            # Simple search filter
            if isinstance(result, dict) and "articles" in result:
                articles = result["articles"]
                filtered_articles = [
                    article for article in articles
                    if query in article.get('title', '').lower() or
                       query in article.get('categoryName', '').lower()
                ]
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": str(filtered_articles[:10])}]
                }
        
        elif tool_request.name == "get_article_by_id":
            article_id = tool_request.arguments.get("article_id")
            if not article_id:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide an article ID"}]
                }
            result = fetch_articles(category="all", page=1, limit=100)
            if isinstance(result, dict) and "articles" in result:
                articles = result["articles"]
                article = next(
                    (a for a in articles if str(a.get('id')) == str(article_id)),
                    None
                )
                if article:
                    return {
                        "tool": tool_request.name,
                        "content": [{"type": "text", "text": str(article)}]
                    }
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"Article with ID '{article_id}' not found"}]
                }
        
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_request.name}")
            
    except Exception as e:
        logger.error(f"Error calling tool {tool_request.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/resources")
async def list_resources(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """List available MCP resources."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Return hardcoded resources list (matching MCP server resources)
        return {
            "resources": [
                {
                    "uri": "servicenex://articles/all",
                    "name": "All Knowledge Base Articles",
                    "description": "Complete list of published knowledge base articles",
                    "mimeType": "application/json"
                },
                {
                    "uri": "servicenex://tickets/recent",
                    "name": "Recent Support Tickets",
                    "description": "List of recent support tickets",
                    "mimeType": "application/json"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/resources/read")
async def read_resource(
    resource_request: ResourceReadRequest,
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Read an MCP resource."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Route to appropriate data loader based on URI
        if resource_request.uri == "servicenex://articles/all":
            result = fetch_articles(category="all", page=1, limit=100)
            content = json.dumps(result, indent=2)
        
        elif resource_request.uri == "servicenex://tickets/recent":
            result = fetch_tickets(category="all", page=1, limit=50)
            content = json.dumps(result, indent=2)
        
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown resource URI: {resource_request.uri}"
            )
        
        return {
            "uri": resource_request.uri,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading resource {resource_request.uri}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Convenience endpoints for specific tools
@app.get("/api/tickets")
async def get_tickets_api(
    request: Request,
    limit: int = 5,
    page: int = 1,
    category: str = "all",
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Get tickets - REST API endpoint."""
    try:
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Call the data loader directly
        result = fetch_tickets(category=category, page=page, limit=limit)
        
        return {"data": result}
    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles")
async def get_articles_api(
    request: Request,
    limit: int = 10,
    page: int = 1,
    category: str = "all",
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Get articles - REST API endpoint."""
    try:
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Call the data loader directly
        result = fetch_articles(category=category, page=page, limit=limit)
        
        return {"data": result}
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

