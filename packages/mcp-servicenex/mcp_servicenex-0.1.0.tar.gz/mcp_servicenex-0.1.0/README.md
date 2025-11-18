# servicenex-mcp-server

A Model Context Protocol (MCP) server that provides AI assistants with secure access to ServiceNex knowledge base articles and support tickets.

## 🌟 Features

- **MCP Tools**: Execute actions like fetching articles, searching, and retrieving tickets
- **MCP Resources**: Access knowledge base data through structured resource URIs
- **Real-time Data**: Connect directly to ServiceNex API for live data
- **AI-Ready**: Formatted responses optimized for AI assistant consumption

## 🏗️ Architecture

This server implements the Model Context Protocol (MCP), allowing AI assistants like Claude to:

1. **Discover** available tools and resources
2. **Invoke** tools to fetch ServiceNex data
3. **Access** resources via URIs

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│  AI Client  │ ◄─MCP──►│  MCP Server      │ ◄─API──►│ ServiceNex  │
│  (Claude)   │         │  (This Project)  │         │  Platform   │
└─────────────┘         └──────────────────┘         └─────────────┘
```

## 📦 Installation

### Option 1: Using uvx (Recommended)

`uvx` allows you to run the MCP server without installing it globally. Install `uv` first:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the MCP server directly with uvx
uvx mcp-servicenex
```

No installation needed! `uvx` will automatically download and run the package when published.

### Option 2: Install from PyPI

Alternatively, you can install the package globally:

```bash
pip install mcp-servicenex
```

Or using `uv`:

```bash
uv pip install mcp-servicenex
```

### Option 3: Install from Source

1. **Clone the repository**:
```bash
git clone <repository-url>
cd servicenex-mcp-server
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

> **Note**: If you encounter an error about `ensurepip` not being available (common on Debian/Ubuntu), first install the venv package:
> ```bash
> sudo apt install python3.12-venv
> ```
> Then recreate the virtual environment.

3. **Install in development mode**:
```bash
pip install -e .
```

Or install dependencies directly:
```bash
pip install -r requirements.txt
```

### Configuration

Configure API credentials via environment variables (recommended) or edit `app/config.py`:

**Using environment variables** (recommended):
```bash
export MY_API_BASE_URL="https://qa.servicenex.io/api"
export MY_API_KEY="your-api-key-here"
```

**Or create a `.env` file** (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your credentials
```

## 🚀 Usage

### Running the MCP Server

The MCP server uses stdio transport for communication with MCP clients:

**Using uvx (Recommended):**
```bash
uvx mcp-servicenex
```

**If installed from PyPI:**
```bash
mcp-servicenex
```

**If installed from source:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run the MCP server
python -m app.mcp_server
```

Or use the convenience script:

```bash
./run_server.sh
```

### Docker Deployment

Run the MCP server in Docker:

```bash
# Build and run
./docker-run.sh

# Or manually
docker build -t servicenex-mcp-server .
docker run -it --rm \
    -e MY_API_BASE_URL="https://qa.servicenex.io/api" \
    -e MY_API_KEY="your-api-key-here" \
    servicenex-mcp-server
```

### Cloud Deployment

For persistent, remote deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Google Compute Engine setup
- Remote MCP via SSH
- Production best practices

### Available MCP Tools

#### 1. `get_knowledge_articles`
Fetch knowledge base articles with optional limit.

**Parameters**:
- `limit` (integer, optional): Maximum number of articles to return (default: 10)

**Example Response**:
```
📚 ServiceNex Knowledge Base
==================================================

Total Articles: 45 (Page 1 of 5)
Showing: 10 articles

1. Getting Started with ServiceNex
   ─────────────────────────────────────────────
   ID: 12345
   Category: Tutorials
   Author: John Doe
   Status: Published
   Created: 2024-01-15
```

#### 2. `get_tickets`
Fetch recent support tickets.

**Parameters**:
- `limit` (integer, optional): Maximum number of tickets to return (default: 5)

**Example Response**:
```
🎫 Recent Support Tickets
==================================================

Found 5 recent tickets:

1. Cannot login to dashboard
   ─────────────────────────────────────────────
   ID: TKT-001
   Status: Open
   Priority: High
   Assignee: Support Team
```

#### 3. `search_articles`
Search for articles by keyword.

**Parameters**:
- `query` (string, required): Search query to find relevant articles

**Example**:
```json
{
  "query": "authentication"
}
```

#### 4. `get_article_by_id`
Get detailed information about a specific article.

**Parameters**:
- `article_id` (string, required): The ID of the article to retrieve

### Available MCP Resources

Resources provide direct access to data through URIs:

#### 1. `servicenex://articles/all`
Complete list of published knowledge base articles in JSON format.

#### 2. `servicenex://tickets/recent`
List of recent support tickets in JSON format.

## 🔌 Integration with AI Assistants

### Claude Desktop Integration

Add this server to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/claude/claude_desktop_config.json`

#### Using uvx (Recommended)

This is the recommended method - no installation needed:

```json
{
  "mcpServers": {
    "servicenex": {
      "command": "uvx",
      "args": ["mcp-servicenex"],
      "env": {
        "MY_API_BASE_URL": "https://qa.servicenex.io/api",
        "MY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Note:** Make sure `uv` is installed. Install it with:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Standard Installation (PyPI)

If installed via `pip install mcp-servicenex`:

```json
{
  "mcpServers": {
    "servicenex": {
      "command": "mcp-servicenex",
      "env": {
        "MY_API_BASE_URL": "https://qa.servicenex.io/api",
        "MY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Local Python Installation (Development)

```json
{
  "mcpServers": {
    "servicenex": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "/path/to/servicenex-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/servicenex-mcp-server",
        "PATH": "/path/to/servicenex-mcp-server/venv/bin",
        "MY_API_BASE_URL": "https://qa.servicenex.io/api",
        "MY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Docker Installation

```json
{
  "mcpServers": {
    "servicenex": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "MY_API_BASE_URL=https://qa.servicenex.io/api",
        "-e",
        "MY_API_KEY=your-api-key-here",
        "servicenex-mcp-server"
      ]
    }
  }
}
```

**Note**: Replace `/path/to/servicenex-mcp-server` with your actual path and `your-api-key-here` with your ServiceNex API key.

### Using with MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure server parameters
server_params = StdioServerParameters(
    command="python",
    args=["-m", "app.mcp_server"],
    cwd="/path/to/servicenex-mcp-server"
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize connection
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in tools.tools]}")
        
        # Call a tool
        result = await session.call_tool(
            "get_knowledge_articles",
            arguments={"limit": 5}
        )
        print(result.content[0].text)
```

## 📁 Project Structure

```
servicenex-mcp-server/
├── app/
│   ├── __init__.py
│   ├── mcp_server.py        # MCP server (tools + resources)
│   ├── agent.py             # Legacy agent handlers (deprecated)
│   ├── config.py            # API configuration
│   └── loaders/
│       └── my_api_loader.py # ServiceNex API client
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker container configuration
├── docker-run.sh           # Docker deployment script
├── deploy-gce.sh           # Google Compute Engine deployment
├── DEPLOYMENT.md           # Detailed deployment guide
├── README.md               # This file
└── venv/                   # Virtual environment
```

## 🔧 Development

### Adding New Tools

To add a new tool, update the `list_tools()` and `call_tool()` functions in `app/mcp_server.py`:

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools
        Tool(
            name="your_new_tool",
            description="Description of what your tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param1"],
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    if name == "your_new_tool":
        # Implement your tool logic here
        return [TextContent(type="text", text="Tool response")]
```

### Adding New Resources

To add a new resource, update `app/mcp_server.py`:

```python
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        # ... existing resources
        Resource(
            uri="servicenex://your/resource",
            name="Your Resource Name",
            description="Resource description",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "servicenex://your/resource":
        # Fetch and return resource data
        return json.dumps(data)
```

## 🔐 Security

- **API Keys**: Store sensitive credentials in environment variables or secure config files
- **Network**: The MCP server communicates via stdio, not exposed network ports
- **Access Control**: Implement proper authentication in the ServiceNex API layer

## 📝 License

[Add your license information here]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions:
- Create an issue in this repository
- Contact: [Your contact information]

## 🔗 Related Links

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [ServiceNex Platform](https://servicenex.io)
- [Claude Desktop](https://claude.ai/desktop)

