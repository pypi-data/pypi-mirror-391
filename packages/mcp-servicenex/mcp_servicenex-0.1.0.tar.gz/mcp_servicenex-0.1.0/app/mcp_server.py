#!/usr/bin/env python3
"""
Enhanced ServiceNex MCP Server with Resources

This MCP server provides both tools and resources for accessing ServiceNex data.
"""

import asyncio
import logging
from typing import Any, Sequence
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
)

from app.loaders.my_api_loader import fetch_tickets, fetch_articles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("servicenex-server")


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources from ServiceNex."""
    return [
        Resource(
            uri="servicenex://articles/all",
            name="All Knowledge Base Articles",
            description="Complete list of published knowledge base articles",
            mimeType="application/json",
        ),
        Resource(
            uri="servicenex://tickets/recent",
            name="Recent Support Tickets",
            description="List of recent support tickets",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource by URI."""
    
    if uri == "servicenex://articles/all":
        try:
            results = fetch_articles()
            return json.dumps(results, indent=2)
        except Exception as e:
            logger.error(f"Error reading articles resource: {e}")
            return json.dumps({"error": str(e)})
    
    elif uri == "servicenex://tickets/recent":
        try:
            results = fetch_data()
            return json.dumps(results, indent=2)
        except Exception as e:
            logger.error(f"Error reading tickets resource: {e}")
            return json.dumps({"error": str(e)})
    
    else:
        return json.dumps({"error": f"Unknown resource URI: {uri}"})


@server.list_tools()
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
        Tool(
            name="get_article_by_id",
            description="Get detailed information about a specific article by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_id": {
                        "type": "string",
                        "description": "The ID of the article to retrieve"
                    }
                },
                "required": ["article_id"],
            },
        ),
    ]


@server.call_tool()
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
                response_text = f"📚 ServiceNex Knowledge Base\n"
                response_text += f"{'=' * 50}\n\n"
                response_text += f"Total Articles: {total} (Page {current_page} of {total_pages})\n"
                response_text += f"Showing: {len(articles)} articles\n\n"
                
                for idx, article in enumerate(articles, 1):
                    title = article.get('title', 'Untitled')
                    category = article.get('categoryName', 'Uncategorized')
                    author = article.get('authorName', 'Unknown Author')
                    status = article.get('status', 'Unknown')
                    article_id = article.get('id', 'N/A')
                    created_at = article.get('createdAt', 'N/A')
                    
                    response_text += f"{idx}. {title}\n"
                    response_text += f"   {'─' * 45}\n"
                    response_text += f"   ID: {article_id}\n"
                    response_text += f"   Category: {category}\n"
                    response_text += f"   Author: {author}\n"
                    response_text += f"   Status: {status}\n"
                    response_text += f"   Created: {created_at}\n\n"
                
                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text="❌ Invalid articles response format")]
                
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return [TextContent(type="text", text=f"❌ Error fetching articles: {str(e)}")]
    
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
            
            # Format the response with enhanced details
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
                assignee_id = ticket.get('assigneeId', 'Unassigned')
                sla_response_overdue = ticket.get('slaResponseOverdue', 0)
                sla_resolution_overdue = ticket.get('slaResolutionOverdue', 0)
                
                response_text += f"{idx}. {subject}\n"
                response_text += f"   {'─' * 45}\n"
                response_text += f"   Ticket #: {ticket_number}\n"
                response_text += f"   ID: {ticket_id}\n"
                response_text += f"   Type: {type_name}\n"
                response_text += f"   Status: {status}\n"
                response_text += f"   Priority: {priority}\n"
                response_text += f"   Customer: {customer_name}\n"
                response_text += f"   Assignee ID: {assignee_id}\n"
                response_text += f"   Created: {created_at}\n"
                
                # Add SLA information if overdue
                if sla_response_overdue or sla_resolution_overdue:
                    response_text += f"   ⚠️  SLA Status:"
                    if sla_response_overdue:
                        response_text += f" Response Overdue"
                    if sla_resolution_overdue:
                        response_text += f" Resolution Overdue"
                    response_text += "\n"
                
                response_text += "\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Error fetching tickets: {e}")
            return [TextContent(type="text", text=f"❌ Error fetching tickets: {str(e)}")]
    
    elif name == "search_articles":
        try:
            query = arguments.get("query", "").lower()
            if not query:
                return [TextContent(type="text", text="⚠️  Please provide a search query")]
            
            # Fetch more articles for better search results
            results = fetch_articles(category="all", page=1, limit=50)
            
            if isinstance(results, dict) and "articles" in results:
                articles = results["articles"]
                
                # Simple search filter
                filtered_articles = [
                    article for article in articles
                    if query in article.get('title', '').lower() or
                       query in article.get('categoryName', '').lower() or
                       query in article.get('content', '').lower()
                ]
                
                response_text = f"🔍 Search Results for '{query}'\n"
                response_text += f"{'=' * 50}\n\n"
                response_text += f"Found {len(filtered_articles)} matching articles:\n\n"
                
                for idx, article in enumerate(filtered_articles[:10], 1):
                    title = article.get('title', 'Untitled')
                    category = article.get('categoryName', 'Uncategorized')
                    article_id = article.get('id', 'N/A')
                    
                    response_text += f"{idx}. {title}\n"
                    response_text += f"   ID: {article_id}\n"
                    response_text += f"   Category: {category}\n\n"
                
                if not filtered_articles:
                    response_text = f"🔍 No articles found matching '{query}'"
                elif len(filtered_articles) > 10:
                    response_text += f"\n... and {len(filtered_articles) - 10} more results"
                
                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text="❌ Invalid articles response format")]
                
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return [TextContent(type="text", text=f"❌ Error searching articles: {str(e)}")]
    
    elif name == "get_article_by_id":
        try:
            article_id = arguments.get("article_id")
            if not article_id:
                return [TextContent(type="text", text="⚠️  Please provide an article ID")]
            
            # Fetch all articles to search by ID
            results = fetch_articles(category="all", page=1, limit=100)
            
            if isinstance(results, dict) and "articles" in results:
                articles = results["articles"]
                
                # Find article by ID
                article = next(
                    (a for a in articles if str(a.get('id')) == str(article_id)),
                    None
                )
                
                if article:
                    title = article.get('title', 'Untitled')
                    category = article.get('categoryName', 'Uncategorized')
                    author = article.get('authorName', 'Unknown')
                    status = article.get('status', 'Unknown')
                    content = article.get('content', 'No content available')
                    created_at = article.get('createdAt', 'N/A')
                    updated_at = article.get('updatedAt', 'N/A')
                    
                    response_text = f"📄 Article Details\n"
                    response_text += f"{'=' * 50}\n\n"
                    response_text += f"Title: {title}\n"
                    response_text += f"ID: {article_id}\n"
                    response_text += f"Category: {category}\n"
                    response_text += f"Author: {author}\n"
                    response_text += f"Status: {status}\n"
                    response_text += f"Created: {created_at}\n"
                    response_text += f"Updated: {updated_at}\n\n"
                    response_text += f"Content:\n{'-' * 50}\n{content}\n"
                    
                    return [TextContent(type="text", text=response_text)]
                else:
                    return [TextContent(type="text", text=f"❌ Article with ID '{article_id}' not found")]
            else:
                return [TextContent(type="text", text="❌ Invalid articles response format")]
                
        except Exception as e:
            logger.error(f"Error fetching article by ID: {e}")
            return [TextContent(type="text", text=f"❌ Error fetching article: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]


async def main():
    """Run the MCP server using stdio transport."""
    logger.info("Starting ServiceNex MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def cli():
    """Entry point for the mcp-servicenex command."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()

