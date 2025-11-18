#!/usr/bin/env python3
"""
ServiceNex MCP Server

This MCP server provides access to ServiceNex knowledge base articles and tickets
through the Model Context Protocol.
"""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from app.loaders.my_api_loader import fetch_tickets, fetch_articles

# Configure logging - send to stderr to avoid interfering with stdio
logging.basicConfig(
    level=logging.WARNING,  # Reduce verbosity for faster initialization
    format='%(levelname)s:%(name)s:%(message)s',
    stream=__import__('sys').stderr  # Explicitly use stderr
)
logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("servicenex-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for accessing ServiceNex data."""
    return [
        Tool(
            name="get_knowledge_articles",
            description="Fetch knowledge base articles from ServiceNex. Returns published articles with title, category, author, and status information. Supports pagination and category filtering.",
            inputSchema={
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
                },
            },
        ),
        Tool(
            name="get_tickets",
            description="Fetch recent support tickets from ServiceNex. Returns ticket information including titles and status. Supports pagination and category filtering.",
            inputSchema={
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
                },
            },
        ),
        Tool(
            name="search_articles",
            description="Search for specific knowledge base articles by keyword or topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to find relevant articles"
                    }
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from MCP clients."""
    
    if name == "get_knowledge_articles":
        try:
            category = arguments.get("category", "all")
            page = arguments.get("page", 1)
            limit = arguments.get("limit", 10)
            results = fetch_articles(category=category, page=page, limit=limit)
            
            if isinstance(results, dict) and "articles" in results:
                articles = results["articles"][:limit]
                total = results.get("total", len(articles))
                current_page = results.get("currentPage", 1)
                total_pages = results.get("totalPages", 1)
                
                # Format articles as text content
                response_text = f"Found {total} articles (Page {current_page} of {total_pages}):\n\n"
                
                for idx, article in enumerate(articles, 1):
                    title = article.get('title', 'Untitled')
                    category = article.get('categoryName', 'Uncategorized')
                    author = article.get('authorName', 'Unknown Author')
                    status = article.get('status', 'Unknown')
                    article_id = article.get('id', 'N/A')
                    
                    response_text += f"{idx}. {title}\n"
                    response_text += f"   ID: {article_id}\n"
                    response_text += f"   Category: {category}\n"
                    response_text += f"   Author: {author}\n"
                    response_text += f"   Status: {status}\n\n"
                
                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text="Invalid articles response format")]
                
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return [TextContent(type="text", text=f"Error fetching articles: {str(e)}")]
    
    elif name == "get_tickets":
        try:
            category = arguments.get("category", "all")
            page = arguments.get("page", 1)
            limit = arguments.get("limit", 5)
            results = fetch_tickets(category=category, page=page, limit=limit)
            
            # Handle the actual API response structure
            if isinstance(results, dict) and "tickets" in results:
                tickets = results["tickets"]
                total = results.get("total", len(tickets))
                current_page = results.get("currentPage", page)
                total_pages = results.get("totalPages", 1)
            else:
                tickets = results if isinstance(results, list) else []
                total = len(tickets)
                current_page = page
                total_pages = 1
            
            # Format the response
            response_text = f"🎫 ServiceNex Support Tickets\n"
            response_text += f"{'=' * 50}\n\n"
            response_text += f"Total Tickets: {total} (Page {current_page} of {total_pages})\n"
            response_text += f"Showing: {len(tickets[:limit])} tickets\n\n"
            
            for idx, ticket in enumerate(tickets[:limit], 1):
                subject = ticket.get('subject', 'No Subject')
                ticket_number = ticket.get('ticketNumber', 'N/A')
                ticket_id = ticket.get('id', 'N/A')
                status = ticket.get('status', 'Unknown')
                priority = ticket.get('priority', 'Unknown')
                type_name = ticket.get('typeName', 'N/A')
                customer_name = ticket.get('customerName', 'N/A')
                created_at = ticket.get('createdAt', 'N/A')
                
                response_text += f"{idx}. {subject}\n"
                response_text += f"   {'─' * 45}\n"
                response_text += f"   Ticket #: {ticket_number}\n"
                response_text += f"   ID: {ticket_id}\n"
                response_text += f"   Type: {type_name}\n"
                response_text += f"   Status: {status}\n"
                response_text += f"   Priority: {priority}\n"
                response_text += f"   Customer: {customer_name}\n"
                response_text += f"   Created: {created_at}\n\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Error fetching tickets: {e}")
            return [TextContent(type="text", text=f"Error fetching tickets: {str(e)}")]
    
    elif name == "search_articles":
        try:
            query = arguments.get("query", "").lower()
            if not query:
                return [TextContent(type="text", text="Please provide a search query")]
            
            # Fetch more articles for better search results
            results = fetch_articles(category="all", page=1, limit=50)
            
            if isinstance(results, dict) and "articles" in results:
                articles = results["articles"]
                
                # Simple search filter
                filtered_articles = [
                    article for article in articles
                    if query in article.get('title', '').lower() or
                       query in article.get('categoryName', '').lower()
                ]
                
                response_text = f"Found {len(filtered_articles)} articles matching '{query}':\n\n"
                
                for idx, article in enumerate(filtered_articles[:10], 1):
                    title = article.get('title', 'Untitled')
                    category = article.get('categoryName', 'Uncategorized')
                    article_id = article.get('id', 'N/A')
                    
                    response_text += f"{idx}. {title}\n"
                    response_text += f"   ID: {article_id}\n"
                    response_text += f"   Category: {category}\n\n"
                
                if not filtered_articles:
                    response_text = f"No articles found matching '{query}'"
                
                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text="Invalid articles response format")]
                
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return [TextContent(type="text", text=f"Error searching articles: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server using stdio transport."""
    # Use unbuffered mode for faster response
    import sys
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
