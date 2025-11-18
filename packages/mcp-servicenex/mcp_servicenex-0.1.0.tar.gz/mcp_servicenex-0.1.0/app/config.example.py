import os
import sys

# Read from environment variables (set by Claude Desktop config or system)
# Throws error if not set - no fallback to prevent using wrong credentials

MY_API_BASE_URL = os.getenv("MY_API_BASE_URL")
if not MY_API_BASE_URL:
    print("ERROR: MY_API_BASE_URL environment variable is not set!", file=sys.stderr)
    print("Please set it in your Claude Desktop config:", file=sys.stderr)
    print('  "env": { "MY_API_BASE_URL": "https://qa.servicenex.io/api" }', file=sys.stderr)
    sys.exit(1)

MY_API_KEY = os.getenv("MY_API_KEY")
if not MY_API_KEY:
    print("ERROR: MY_API_KEY environment variable is not set!", file=sys.stderr)
    print("Please set it in your Claude Desktop config:", file=sys.stderr)
    print('  "env": { "MY_API_KEY": "your-api-key-here" }', file=sys.stderr)
    sys.exit(1)

# Instructions:
# 1. Copy this file to config.py: cp config.example.py config.py
# 2. Set environment variables in Claude Desktop config:
#    ~/.config/claude/claude_desktop_config.json (Linux)
#    ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
#    %APPDATA%\Claude\claude_desktop_config.json (Windows)
#
# Example config:
# {
#   "mcpServers": {
#     "servicenex": {
#       "command": "/path/to/venv/bin/python",
#       "args": ["-m", "app.mcp_server"],
#       "env": {
#         "MY_API_BASE_URL": "https://qa.servicenex.io/api",
#         "MY_API_KEY": "your-actual-api-key"
#       }
#     }
#   }
# }
